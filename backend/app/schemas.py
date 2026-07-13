from datetime import datetime, timezone
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, ConfigDict, field_serializer

# --- Enumerated vocabularies (proven safe against all 186 stored blueprints) ---
Genre = Literal["psycho_glitch_techno", "coldwave", "brutalist_techno", "ambient"]
MotifType = Literal[
    "cathedral organ", "synth piano", "FM synth hook", "electric guitar riff",
    "vocal phrase", "bass motif", "bell motif", "choir pad", "no motif",
]
MotifBehavior = Literal["fragmenting", "repeating", "soaring", "staccato", "ascending"]
HarmonyMode = Literal["minor", "major", "phrygian", "chromatic", "dorian"]
TargetModel = Literal["suno", "udio"]
OriginType = Literal["preset", "snapshot", "custom"]


def iso_z(dt: Optional[datetime]) -> Optional[str]:
    """Serialize a datetime as UTC ISO-8601 with a trailing Z. Naive datetimes
    (legacy rows) are defined as UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


class CompositionBlueprint(BaseModel):
    genre: Genre
    bpm: int = Field(..., ge=40, le=240)
    energy: int = Field(..., ge=0, le=100)
    motif_type: MotifType
    motif_presence: int = Field(..., ge=0, le=100)
    motif_behavior: MotifBehavior
    harmony_mode: HarmonyMode
    harmony_complexity: int = Field(..., ge=0, le=100)
    bass_aggression: int = Field(..., ge=0, le=100)
    glitch_density: int = Field(..., ge=0, le=100)
    drum_intensity: int = Field(..., ge=0, le=100)
    atmosphere_depth: int = Field(..., ge=0, le=100)
    target_model: TargetModel = "suno"


class PresetBase(BaseModel):
    name: str
    bank: str = "BANK_A"
    blueprint: CompositionBlueprint


class PresetCreate(PresetBase):
    pass


class PresetResponse(PresetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

    @field_serializer("created_at")
    def _ser_created_at(self, dt: datetime, _info):
        return iso_z(dt)


# --- Lifecycle: preview (non-persistent) ---
class PreviewRequest(CompositionBlueprint):
    client_revision: Optional[int] = None


class PreviewResponse(BaseModel):
    prompts: dict
    motif_block: str
    arrangement_timeline: list
    scores: dict
    recommendations: list
    client_revision: Optional[int] = None


# --- Lifecycle: save snapshot (server-authoritative, immutable) ---
class LineageInput(BaseModel):
    lineage_key: Optional[str] = None
    display_name: Optional[str] = None
    origin_type: OriginType = "custom"
    origin_ref: Optional[str] = None
    parent_snapshot_id: Optional[str] = None


class SnapshotSaveRequest(BaseModel):
    blueprint: CompositionBlueprint
    lineage: LineageInput


class SnapshotRecord(BaseModel):
    """Complete artifact contract (R40): identical for save response and detail."""
    snapshot_id: str
    lineage_key: str
    lineage_display: str
    version: int
    parent_snapshot_id: Optional[str] = None
    origin_type: Optional[str] = None
    origin_ref: Optional[str] = None
    blueprint: CompositionBlueprint
    prompts: dict
    scores: dict
    recommendations: list
    motif_block: str
    arrangement_timeline: list
    engine_version: Optional[str] = None
    artifacts_provenance: str
    created_at: datetime

    @field_serializer("created_at")
    def _ser_created_at(self, dt: datetime, _info):
        return iso_z(dt)


class SnapshotListItem(BaseModel):
    id: int
    snapshot_id: str
    lineage_key: Optional[str] = None
    lineage_name: str
    version: int
    parent_snapshot_id: Optional[str] = None
    blueprint: CompositionBlueprint
    overall_score: int
    engine_version: Optional[str] = None
    created_at: datetime

    @field_serializer("created_at")
    def _ser_created_at(self, dt: datetime, _info):
        return iso_z(dt)


class SnapshotPage(BaseModel):
    items: List[SnapshotListItem]
    total: int
    next_cursor: Optional[int] = None


# --- Comparison (unchanged behavior; retained for /api/compare) ---
class CompareRequest(BaseModel):
    blueprint_a: CompositionBlueprint
    blueprint_b: CompositionBlueprint
