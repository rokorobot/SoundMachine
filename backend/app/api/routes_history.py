import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, BlueprintSnapshot, GenerationHistory
from app.schemas import CompositionBlueprint, SnapshotResponse, SnapshotDetailResponse
from app.motif_engine import MotifEngine
from app.arrangement_engine import ArrangementEngine

router = APIRouter(prefix="/api")

@router.get("/snapshots", response_model=List[SnapshotResponse])
def get_snapshots(db: Session = Depends(get_db)):
    snaps = db.query(BlueprintSnapshot).order_by(BlueprintSnapshot.created_at.desc()).all()
    results = []
    
    for s in snaps:
        hist = db.query(GenerationHistory).filter(GenerationHistory.snapshot_id == s.snapshot_id).first()
        score = 0
        if hist:
            try:
                score_data = json.loads(hist.scores_json)
                score = score_data.get("overall", 0)
            except Exception:
                pass
                
        try:
            blueprint = CompositionBlueprint(**json.loads(s.blueprint_json))
        except Exception:
            continue
            
        results.append(
            SnapshotResponse(
                id=s.id,
                snapshot_id=s.snapshot_id,
                lineage_name=s.lineage_name,
                version=s.version,
                parent_preset_id=s.parent_preset_id,
                blueprint=blueprint,
                created_at=s.created_at,
                overall_score=score
            )
        )
    return results

@router.get("/snapshots/{snapshot_id}", response_model=SnapshotDetailResponse)
def get_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    snap = db.query(BlueprintSnapshot).filter(BlueprintSnapshot.snapshot_id == snapshot_id).first()
    if not snap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot with ID {snapshot_id} not found"
        )
        
    hist = db.query(GenerationHistory).filter(GenerationHistory.snapshot_id == snapshot_id).first()
    prompts = {}
    scores = {}
    if hist:
        try:
            prompts = json.loads(hist.prompts_json)
            scores = json.loads(hist.scores_json)
        except Exception:
            pass
            
    try:
        blueprint = CompositionBlueprint(**json.loads(snap.blueprint_json))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse snapshot blueprint: {str(e)}"
        )
        
    # Generate motif block and timeline on the fly to restore visual telemetry
    motif_block = MotifEngine.generate_block(
        blueprint.motif_type, 
        blueprint.motif_presence, 
        blueprint.motif_behavior, 
        blueprint.harmony_mode
    )
    
    timeline = ArrangementEngine.generate_timeline(
        blueprint.bpm,
        blueprint.energy,
        blueprint.genre,
        blueprint.glitch_density,
        blueprint.drum_intensity
    )
        
    return SnapshotDetailResponse(
        snapshot_id=snap.snapshot_id,
        lineage_name=snap.lineage_name,
        version=snap.version,
        parent_preset_id=snap.parent_preset_id,
        blueprint=blueprint,
        prompts=prompts,
        scores=scores,
        motif_block=motif_block,
        arrangement_timeline=timeline,
        created_at=snap.created_at
    )

@router.post("/snapshots/{snapshot_id}/restore", response_model=SnapshotDetailResponse)
def restore_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    # Restoring retrieves the snapshot and returns detail to set as client state.
    # It verifies the snapshot exists before returning.
    return get_snapshot(snapshot_id, db)
