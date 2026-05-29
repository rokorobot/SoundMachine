import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db, Preset, BlueprintSnapshot, GenerationHistory
from app.schemas import (
    CompositionBlueprint, 
    PresetResponse, 
    PresetCreate, 
    GenerateRequest, 
    GenerateResponse
)
from app.composition_engine import CompositionEngine
from app.prompt_engine import PromptEngine
from app.export_engine import ExportEngine
from app.motif_engine import MotifEngine
from app.arrangement_engine import ArrangementEngine
from app.scoring_engine import ScoringEngine

router = APIRouter(prefix="/api")

@router.get("/presets", response_model=List[PresetResponse])
def get_presets(db: Session = Depends(get_db)):
    presets = db.query(Preset).all()
    results = []
    for p in presets:
        results.append(
            PresetResponse(
                id=p.id,
                name=p.name,
                bank=p.bank,
                blueprint=CompositionBlueprint(**json.loads(p.blueprint_json)),
                created_at=p.created_at
            )
        )
    return results

@router.get("/presets/{preset_id}", response_model=PresetResponse)
def get_preset(preset_id: int, db: Session = Depends(get_db)):
    p = db.query(Preset).filter(Preset.id == preset_id).first()
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset with ID {preset_id} not found"
        )
    return PresetResponse(
        id=p.id,
        name=p.name,
        bank=p.bank,
        blueprint=CompositionBlueprint(**json.loads(p.blueprint_json)),
        created_at=p.created_at
    )

@router.post("/presets", response_model=PresetResponse)
def save_preset(preset: PresetCreate, db: Session = Depends(get_db)):
    # Check if a preset with the same name already exists
    existing = db.query(Preset).filter(Preset.name == preset.name).first()
    blueprint_str = json.dumps(preset.blueprint.model_dump())
    
    if existing:
        # Overwrite existing
        existing.blueprint_json = blueprint_str
        existing.bank = preset.bank
        db.commit()
        db.refresh(existing)
        p = existing
    else:
        # Create new
        p = Preset(
            name=preset.name,
            bank=preset.bank,
            blueprint_json=blueprint_str
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        
    return PresetResponse(
        id=p.id,
        name=p.name,
        bank=p.bank,
        blueprint=CompositionBlueprint(**json.loads(p.blueprint_json)),
        created_at=p.created_at
    )

@router.post("/generate", response_model=GenerateResponse)
def generate_prompt(request: GenerateRequest, db: Session = Depends(get_db)):
    try:
        # 1. Feed into Composition Engine
        enriched = CompositionEngine.process(request)
        
        # 2. Feed into Prompt Engine
        prompts = PromptEngine.generate(enriched, target_model=request.target_model)
        
        # 3. Motif Block Generation
        motif_block = MotifEngine.generate_block(
            request.motif_type, 
            request.motif_presence, 
            request.motif_behavior, 
            request.harmony_mode
        )
        
        # 4. Arrangement Timeline
        timeline = ArrangementEngine.generate_timeline(
            request.bpm,
            request.energy,
            request.genre,
            request.glitch_density,
            request.drum_intensity
        )
        
        # 5. Evaluate Governance Diagnostics
        eval_metrics = ScoringEngine.evaluate(request, prompts)
        
        # 6. Embed Motif Block into active prompt_body
        for model in ["suno", "udio"]:
            original_body = prompts[model]["prompt_body"]
            prompts[model]["prompt_body"] = f"{motif_block}\n\n{original_body}"
            
        # 7. Generate versioned snapshot and save to database
        raw_name = request.parent_preset_name or "CUSTOM"
        # Sanitize to uppercase alphanumeric and underscores
        import re
        lineage_name = "".join(c if c.isalnum() else "_" for c in raw_name).upper()
        lineage_name = re.sub(r'_+', '_', lineage_name).strip('_')
        if not lineage_name:
            lineage_name = "CUSTOM"

        # Query version sequence count
        latest_snap = db.query(BlueprintSnapshot).filter(BlueprintSnapshot.lineage_name == lineage_name).order_by(BlueprintSnapshot.version.desc()).first()
        next_ver = 1 if not latest_snap else (latest_snap.version + 1)
        snapshot_id = f"{lineage_name}_{next_ver:04d}"
        
        # Exclude metadata fields from saved blueprint json
        blueprint_data = request.model_dump(exclude={"parent_preset_name", "parent_preset_id"})
        blueprint_json = json.dumps(blueprint_data)

        # Commit snapshot
        db_snapshot = BlueprintSnapshot(
            snapshot_id=snapshot_id,
            lineage_name=lineage_name,
            version=next_ver,
            parent_preset_id=request.parent_preset_id,
            blueprint_json=blueprint_json
        )
        db.add(db_snapshot)
        db.flush()

        # Commit history prompts and scores
        db_history = GenerationHistory(
            snapshot_id=snapshot_id,
            prompts_json=json.dumps(prompts),
            scores_json=json.dumps({
                "overall": eval_metrics["overall"],
                "motif_clarity": eval_metrics["motif_clarity"],
                "genre_focus": eval_metrics["genre_focus"],
                "prompt_density": eval_metrics["prompt_density"],
                "model_compatibility": eval_metrics["model_compatibility"],
                "negative_prompt_quality": eval_metrics["negative_prompt_quality"]
            })
        )
        db.add(db_history)
        db.commit()

        return GenerateResponse(
            blueprint=request,
            prompts=prompts,
            motif_block=motif_block,
            arrangement_timeline=timeline,
            scores={
                "overall": eval_metrics["overall"],
                "motif_clarity": eval_metrics["motif_clarity"],
                "genre_focus": eval_metrics["genre_focus"],
                "prompt_density": eval_metrics["prompt_density"],
                "model_compatibility": eval_metrics["model_compatibility"],
                "negative_prompt_quality": eval_metrics["negative_prompt_quality"]
            },
            recommendations=eval_metrics["recommendations"],
            snapshot_id=snapshot_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error generating prompts: {str(e)}"
        )

@router.post("/export")
def export_prompt(payload: Dict[str, Any]):
    """
    Export endpoint returning copy-pasteable txt layout and project json configuration.
    """
    preset_name = payload.get("preset_name", "Custom Preset")
    blueprint_data = payload.get("blueprint")
    prompts_data = payload.get("prompts")
    target_model = payload.get("target_model", "suno")
    
    if not blueprint_data or not prompts_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing blueprint or prompts data for export"
        )
        
    txt_content = ExportEngine.format_text_prompt(preset_name, target_model, prompts_data)
    json_content = ExportEngine.format_project_json(preset_name, blueprint_data, prompts_data)
    
    safe_name = preset_name.lower().replace(" ", "_")
    
    return {
        "txt_content": txt_content,
        "json_content": json_content,
        "filename_txt": f"{safe_name}_prompt.txt",
        "filename_json": f"{safe_name}_project.json"
    }
