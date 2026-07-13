import json
from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db, Preset
from app.errors import APIError
from app.schemas import (
    CompositionBlueprint, PresetResponse, PresetCreate,
    PreviewRequest, PreviewResponse, SnapshotSaveRequest, SnapshotRecord,
)
from app.export_engine import ExportEngine
from app.snapshot_service import preview as run_preview, save_snapshot

router = APIRouter(prefix="/api")


@router.get("/presets", response_model=List[PresetResponse])
def get_presets(db: Session = Depends(get_db)):
    results = []
    for p in db.query(Preset).all():
        results.append(PresetResponse(
            id=p.id, name=p.name, bank=p.bank,
            blueprint=CompositionBlueprint(**json.loads(p.blueprint_json)),
            created_at=p.created_at,
        ))
    return results


@router.get("/presets/{preset_id}", response_model=PresetResponse)
def get_preset(preset_id: int, db: Session = Depends(get_db)):
    p = db.query(Preset).filter(Preset.id == preset_id).first()
    if not p:
        raise APIError(404, "PRESET_NOT_FOUND", f"preset {preset_id} not found")
    return PresetResponse(
        id=p.id, name=p.name, bank=p.bank,
        blueprint=CompositionBlueprint(**json.loads(p.blueprint_json)),
        created_at=p.created_at,
    )


@router.post("/presets", response_model=PresetResponse)
def save_preset(preset: PresetCreate, db: Session = Depends(get_db)):
    existing = db.query(Preset).filter(Preset.name == preset.name).first()
    blueprint_str = json.dumps(preset.blueprint.model_dump())
    if existing:
        existing.blueprint_json = blueprint_str
        existing.bank = preset.bank
        db.commit()
        db.refresh(existing)
        p = existing
    else:
        p = Preset(name=preset.name, bank=preset.bank, blueprint_json=blueprint_str)
        db.add(p)
        db.commit()
        db.refresh(p)
    return PresetResponse(
        id=p.id, name=p.name, bank=p.bank,
        blueprint=CompositionBlueprint(**json.loads(p.blueprint_json)),
        created_at=p.created_at,
    )


@router.post("/preview", response_model=PreviewResponse)
def preview_prompt(request: PreviewRequest):
    """Non-persistent live preview (R2). Performs zero database writes."""
    bp = CompositionBlueprint(**request.model_dump(exclude={"client_revision"}))
    return run_preview(bp, client_revision=request.client_revision)


@router.post("/snapshots", response_model=SnapshotRecord)
def create_snapshot(request: SnapshotSaveRequest, db: Session = Depends(get_db)):
    """Explicit, server-authoritative, immutable save (R3/R22)."""
    return save_snapshot(db, request.blueprint, request.lineage)


@router.post("/export")
def export_prompt(payload: Dict[str, Any]):
    preset_name = payload.get("preset_name", "Custom Preset")
    blueprint_data = payload.get("blueprint")
    prompts_data = payload.get("prompts")
    target_model = payload.get("target_model", "suno")
    if not blueprint_data or not prompts_data:
        raise APIError(400, "EXPORT_INCOMPLETE", "Missing blueprint or prompts data for export")
    txt_content = ExportEngine.format_text_prompt(preset_name, target_model, prompts_data)
    json_content = ExportEngine.format_project_json(preset_name, blueprint_data, prompts_data)
    safe_name = preset_name.lower().replace(" ", "_")
    return {
        "txt_content": txt_content,
        "json_content": json_content,
        "filename_txt": f"{safe_name}_prompt.txt",
        "filename_json": f"{safe_name}_project.json",
    }
