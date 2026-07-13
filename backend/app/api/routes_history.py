from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SnapshotPage, SnapshotRecord
from app.snapshot_service import list_snapshots, get_snapshot_record

router = APIRouter(prefix="/api")


@router.get("/snapshots", response_model=SnapshotPage)
def get_snapshots(
    limit: int = Query(50, ge=1, le=200),
    before_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """Paginated registry read (R10): id-desc cursor, single query, no N+1."""
    return list_snapshots(db, limit=limit, before_id=before_id)


@router.get("/snapshots/{snapshot_id}", response_model=SnapshotRecord)
def get_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    """Read-only detail. New rows return STORED artifacts; legacy rows return
    reconstructed motif/timeline/recommendations flagged LEGACY_RECONSTRUCTED."""
    return get_snapshot_record(db, snapshot_id)
