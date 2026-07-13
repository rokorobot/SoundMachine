"""Server-authoritative snapshot lifecycle (R22/R40/R41/R42, C1).

Owns the engine pipeline, ordered origin/parent/lineage validation, atomic
persistence with discriminated retry, and record reconstruction (STORED vs
LEGACY_RECONSTRUCTED).
"""
import json

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.database import Preset, BlueprintSnapshot, GenerationHistory, Lineage
from app.errors import APIError
from app.composition_engine import CompositionEngine
from app.prompt_engine import PromptEngine
from app.scoring_engine import ScoringEngine
from app.motif_engine import MotifEngine
from app.arrangement_engine import ArrangementEngine
from app.pipeline_version import PIPELINE_VERSION
from app.lineage import (
    sanitize_slug, effective_key, new_lineage_key, compose_snapshot_id,
)

_SCORE_KEYS = ["overall", "motif_clarity", "genre_focus", "prompt_density",
               "model_compatibility", "negative_prompt_quality"]


def run_pipeline(bp):
    """Deterministic authoritative generation. Returns the full artifact set with
    the motif block embedded into both prompt bodies (as the legacy generator did)."""
    enriched = CompositionEngine.process(bp)
    prompts = PromptEngine.generate(enriched, target_model=bp.target_model)
    metrics = ScoringEngine.evaluate(bp, prompts)
    motif_block = MotifEngine.generate_block(
        bp.motif_type, bp.motif_presence, bp.motif_behavior, bp.harmony_mode)
    timeline = ArrangementEngine.generate_timeline(
        bp.bpm, bp.energy, bp.genre, bp.glitch_density, bp.drum_intensity)
    for model in ("suno", "udio"):
        prompts[model]["prompt_body"] = f"{motif_block}\n\n{prompts[model]['prompt_body']}"
    scores = {k: metrics[k] for k in _SCORE_KEYS}
    return {
        "prompts": prompts,
        "scores": scores,
        "recommendations": metrics["recommendations"],
        "motif_block": motif_block,
        "arrangement_timeline": timeline,
    }


def preview(bp, client_revision=None):
    art = run_pipeline(bp)
    return {
        "prompts": art["prompts"],
        "motif_block": art["motif_block"],
        "arrangement_timeline": art["arrangement_timeline"],
        "scores": art["scores"],
        "recommendations": art["recommendations"],
        "client_revision": client_revision,
    }


# --- lineage resolution ---

def _lineage_by_key(db, key):
    return db.query(Lineage).filter(Lineage.key == key).first()


def _unique_slug(db, base_slug):
    slug = base_slug
    n = 2
    while db.query(Lineage).filter(Lineage.slug == slug).first() is not None:
        slug = f"{base_slug}_{n}"
        n += 1
    return slug


def _get_or_create_preset_lineage(db, preset):
    existing = db.query(Lineage).filter(Lineage.preset_id == preset.id).first()
    if existing:
        return existing
    slug = _unique_slug(db, sanitize_slug(preset.name))
    for _ in range(3):
        row = Lineage(key=new_lineage_key(), display_name=preset.name, slug=slug, preset_id=preset.id)
        db.add(row)
        try:
            db.flush()
            return row
        except IntegrityError:
            db.rollback()
            # PK (uuid) collision is astronomically unlikely; retry with a fresh key.
    raise APIError(500, "INTERNAL", "Could not allocate lineage key")


def _create_custom_lineage(db, display_name):
    name = (display_name or "CUSTOM").strip() or "CUSTOM"
    slug = _unique_slug(db, sanitize_slug(name))
    for _ in range(3):
        row = Lineage(key=new_lineage_key(), display_name=name, slug=slug, preset_id=None)
        db.add(row)
        try:
            db.flush()
            return row
        except IntegrityError:
            db.rollback()
    raise APIError(500, "INTERNAL", "Could not allocate lineage key")


def _next_version(db, lineage_row):
    maxv = db.query(func.max(BlueprintSnapshot.version)).filter(
        BlueprintSnapshot.lineage_key == lineage_row.key).scalar() or 0
    if lineage_row.key.startswith("legacy:"):
        legacy_name = lineage_row.key.split("legacy:", 1)[1]
        legacy_max = db.query(func.max(BlueprintSnapshot.version)).filter(
            BlueprintSnapshot.lineage_key.is_(None),
            BlueprintSnapshot.lineage_name == legacy_name).scalar() or 0
        maxv = max(maxv, legacy_max)
    return maxv + 1


def _validate_and_resolve_lineage(db, lineage):
    """Ordered validation (R41 §6 + C1). Returns the resolved Lineage row.
    Raises APIError (zero writes are guaranteed by the caller's rollback)."""
    origin_type = lineage.origin_type
    origin_ref = lineage.origin_ref
    parent_id = lineage.parent_snapshot_id

    # 2. origin validation
    if origin_type == "preset":
        if not origin_ref or not str(origin_ref).isdigit():
            raise APIError(422, "ORIGIN_INVALID", "preset origin requires an integer origin_ref")
        preset = db.query(Preset).filter(Preset.id == int(origin_ref)).first()
        if not preset:
            raise APIError(422, "ORIGIN_INVALID", f"preset {origin_ref} does not exist")
    elif origin_type == "snapshot":
        if not origin_ref:
            raise APIError(422, "ORIGIN_INVALID", "snapshot origin requires origin_ref")
    elif origin_type == "custom":
        if origin_ref is not None:
            raise APIError(422, "ORIGIN_INVALID", "custom origin must have a null origin_ref")

    # 3. origin/parent consistency
    if origin_type in ("preset", "custom") and parent_id is not None:
        raise APIError(422, "ORIGIN_PARENT_MISMATCH", f"{origin_type} origin must have a null parent")
    if origin_type == "snapshot" and (parent_id is None or origin_ref != parent_id):
        raise APIError(422, "ORIGIN_PARENT_MISMATCH", "snapshot origin_ref must equal parent_snapshot_id")

    # 4. parent validation
    parent_snap = None
    if parent_id is not None:
        parent_snap = db.query(BlueprintSnapshot).filter(
            BlueprintSnapshot.snapshot_id == parent_id).first()
        if not parent_snap:
            raise APIError(409, "PARENT_NOT_FOUND", f"parent snapshot {parent_id} not found")

    # 5. lineage resolution (+ C1)
    if origin_type == "snapshot":
        parent_eff = effective_key(parent_snap.lineage_key, parent_snap.lineage_name)
        if not lineage.lineage_key:
            raise APIError(409, "LINEAGE_REQUIRED",
                           "snapshot origin requires the parent's lineage_key")
        if lineage.lineage_key != parent_eff:
            raise APIError(409, "PARENT_LINEAGE_MISMATCH",
                           "lineage_key must match the parent's effective lineage")
        row = _lineage_by_key(db, parent_eff)
        if row is None:
            # Legacy lineages are seeded at migration; absence means an unknown lineage.
            raise APIError(409, "LINEAGE_UNKNOWN", f"lineage {parent_eff} does not exist")
        return row

    if origin_type == "preset":
        preset = db.query(Preset).filter(Preset.id == int(origin_ref)).first()
        return _get_or_create_preset_lineage(db, preset)

    return _create_custom_lineage(db, lineage.display_name)


def save_snapshot(db, blueprint, lineage):
    """Atomic, server-authoritative save. Returns a SnapshotRecord dict."""
    lineage_row = _validate_and_resolve_lineage(db, lineage)
    art = run_pipeline(blueprint)
    blueprint_json = json.dumps(blueprint.model_dump())
    prompts_json = json.dumps(art["prompts"])
    scores_json = json.dumps(art["scores"])
    artifacts_json = json.dumps({
        "motif_block": art["motif_block"],
        "arrangement_timeline": art["arrangement_timeline"],
        "recommendations": art["recommendations"],
    })
    parent_preset_id = int(lineage.origin_ref) if lineage.origin_type == "preset" else None

    last_exc = None
    for _ in range(3):
        version = _next_version(db, lineage_row)
        snapshot_id = compose_snapshot_id(lineage_row.slug, version)
        snap = BlueprintSnapshot(
            snapshot_id=snapshot_id, lineage_name=lineage_row.display_name, version=version,
            parent_preset_id=parent_preset_id, blueprint_json=blueprint_json,
            lineage_key=lineage_row.key, parent_snapshot_id=lineage.parent_snapshot_id,
            origin_type=lineage.origin_type, origin_ref=lineage.origin_ref,
        )
        db.add(snap)
        db.add(GenerationHistory(
            snapshot_id=snapshot_id, prompts_json=prompts_json, scores_json=scores_json,
            artifacts_json=artifacts_json, engine_version=PIPELINE_VERSION,
        ))
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            last_exc = exc
            msg = str(getattr(exc, "orig", exc))
            if ("ux_snapshots_lineagekey_version" in msg
                    or "blueprint_snapshots.snapshot_id" in msg or ".snapshot_id" in msg):
                continue  # recognized version/id collision -> retry
            # Any other integrity failure is not blindly retried.
            raise APIError(500, "INTERNAL", "Snapshot could not be persisted")
        db.refresh(snap)
        return build_record(db, snap)

    raise APIError(409, "VERSION_CONFLICT", "Could not allocate a unique snapshot version")


# --- record building (save response + detail) ---

def _reconstruct_artifacts(bp):
    art = run_pipeline(bp)
    return art["motif_block"], art["arrangement_timeline"], art["recommendations"]


def build_record(db, snap):
    from app.schemas import CompositionBlueprint
    bp = CompositionBlueprint(**json.loads(snap.blueprint_json))
    hist = db.query(GenerationHistory).filter(
        GenerationHistory.snapshot_id == snap.snapshot_id).first()

    prompts, scores = {}, {}
    if hist:
        prompts = json.loads(hist.prompts_json) if hist.prompts_json else {}
        scores = json.loads(hist.scores_json) if hist.scores_json else {}

    if hist and hist.artifacts_json:
        art = json.loads(hist.artifacts_json)
        motif = art.get("motif_block", "")
        timeline = art.get("arrangement_timeline", [])
        recommendations = art.get("recommendations", [])
        provenance = "STORED"
        engine_version = hist.engine_version
    else:
        # Legacy row: rebuild motif/timeline/recommendations with current engines.
        motif, timeline, recommendations = _reconstruct_artifacts(bp)
        provenance = "LEGACY_RECONSTRUCTED"
        engine_version = None

    return {
        "snapshot_id": snap.snapshot_id,
        "lineage_key": effective_key(snap.lineage_key, snap.lineage_name),
        "lineage_display": snap.lineage_name,
        "version": snap.version,
        "parent_snapshot_id": snap.parent_snapshot_id,
        "origin_type": snap.origin_type,
        "origin_ref": snap.origin_ref,
        "blueprint": bp,
        "prompts": prompts,
        "scores": scores,
        "recommendations": recommendations,
        "motif_block": motif,
        "arrangement_timeline": timeline,
        "engine_version": engine_version,
        "artifacts_provenance": provenance,
        "created_at": snap.created_at,
    }


def list_snapshots(db, limit=50, before_id=None):
    limit = max(1, min(200, limit))
    q = db.query(BlueprintSnapshot, GenerationHistory).outerjoin(
        GenerationHistory, GenerationHistory.snapshot_id == BlueprintSnapshot.snapshot_id)
    if before_id is not None:
        q = q.filter(BlueprintSnapshot.id < before_id)
    rows = q.order_by(BlueprintSnapshot.id.desc()).limit(limit).all()
    total = db.query(func.count(BlueprintSnapshot.id)).scalar()

    from app.schemas import CompositionBlueprint
    items = []
    for snap, hist in rows:
        try:
            bp = CompositionBlueprint(**json.loads(snap.blueprint_json))
        except Exception:
            continue  # legacy row incompatible with current schema is skipped, not fatal
        overall = 0
        engine_version = None
        if hist:
            try:
                overall = json.loads(hist.scores_json).get("overall", 0)
            except Exception:
                overall = 0
            engine_version = hist.engine_version
        items.append({
            "id": snap.id,
            "snapshot_id": snap.snapshot_id,
            "lineage_key": effective_key(snap.lineage_key, snap.lineage_name),
            "lineage_name": snap.lineage_name,
            "version": snap.version,
            "parent_snapshot_id": snap.parent_snapshot_id,
            "blueprint": bp,
            "overall_score": overall,
            "engine_version": engine_version,
            "created_at": snap.created_at,
        })
    next_cursor = rows[-1][0].id if len(rows) == limit and rows else None
    return {"items": items, "total": total, "next_cursor": next_cursor}


def get_snapshot_record(db, snapshot_id):
    snap = db.query(BlueprintSnapshot).filter(
        BlueprintSnapshot.snapshot_id == snapshot_id).first()
    if not snap:
        raise APIError(404, "SNAPSHOT_NOT_FOUND", f"snapshot {snapshot_id} not found")
    return build_record(db, snap)
