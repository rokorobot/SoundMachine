"""Lineage identity helpers (R24 / R39 / R42) and canonical blueprint keying.

Relational identity is the stable ``lineage_key`` (a uuid4 string for new
lineages, or ``legacy:<NAME>`` for the seeded legacy lineages). Display names
and slugs are never relational identity.
"""
import json
import re
import uuid

# The 13 blueprint fields, in the fixed canonical order used for dirtiness and
# fingerprinting. Must match the frontend canonicalKey ordering exactly.
BLUEPRINT_FIELDS = [
    "genre", "bpm", "energy", "motif_type", "motif_presence", "motif_behavior",
    "harmony_mode", "harmony_complexity", "bass_aggression", "glitch_density",
    "drum_intensity", "atmosphere_depth", "target_model",
]


def canonical_key(blueprint):
    """Deterministic fingerprint of a blueprint over the 13 fields in fixed order."""
    if hasattr(blueprint, "model_dump"):
        blueprint = blueprint.model_dump()
    ordered = [(f, blueprint.get(f)) for f in BLUEPRINT_FIELDS]
    return json.dumps(ordered, separators=(",", ":"), ensure_ascii=False)


def sanitize_slug(raw):
    """Uppercase alphanumeric+underscore token used to compose snapshot IDs."""
    s = "".join(c if c.isalnum() else "_" for c in (raw or "")).upper()
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "CUSTOM"


def effective_key(lineage_key, lineage_name):
    """R24: legacy rows (no lineage_key) map to a synthetic 'legacy:<NAME>' key."""
    if lineage_key:
        return lineage_key
    return "legacy:" + (lineage_name or "CUSTOM")


def new_lineage_key():
    """R42: 128-bit random identity; PK constraint is the collision backstop."""
    return str(uuid.uuid4())


def compose_snapshot_id(slug, version):
    return f"{slug}_{version:04d}"
