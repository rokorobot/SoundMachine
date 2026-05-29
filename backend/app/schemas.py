from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CompositionBlueprint(BaseModel):
    genre: str = Field(..., description="Genre of the track (e.g. psycho_glitch_techno, coldwave, brutalist_techno, ambient)")
    bpm: int = Field(..., ge=40, le=240, description="Beats per minute")
    energy: int = Field(..., ge=0, le=100, description="Overall energy of the composition")
    motif_type: str = Field(..., description="Primary melodic motif instrument/sound type")
    motif_presence: int = Field(..., ge=0, le=100, description="Melodic presence of the motif")
    motif_behavior: str = Field(..., description="Melodic behavior style of the motif (e.g. fragmenting, repeating, soaring)")
    harmony_mode: str = Field(..., description="Musical mode or scale mood (e.g. minor, major, phrygian, chromatic)")
    harmony_complexity: int = Field(..., ge=0, le=100, description="Complexity of the harmonic structure")
    bass_aggression: int = Field(..., ge=0, le=100, description="Aggressiveness and distortion level of basslines")
    glitch_density: int = Field(..., ge=0, le=100, description="Amount of micro-glitch, stutter, and cut elements")
    drum_intensity: int = Field(..., ge=0, le=100, description="Impact and complexity of the rhythmic section")
    atmosphere_depth: int = Field(..., ge=0, le=100, description="Presence of pads, ambient noise, and reverb tails")
    target_model: str = Field("suno", description="Target engine: 'suno' or 'udio'")

class PresetBase(BaseModel):
    name: str = Field(..., description="Preset name")
    bank: str = Field("BANK_A", description="Preset bank")
    blueprint: CompositionBlueprint

class PresetCreate(PresetBase):
    pass

class PresetResponse(PresetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GenerateRequest(CompositionBlueprint):
    parent_preset_name: Optional[str] = None
    parent_preset_id: Optional[int] = None

class GenerateResponse(BaseModel):
    blueprint: CompositionBlueprint
    prompts: dict = Field(..., description="Map of prompt types to prompt text outputs")
    motif_block: str
    arrangement_timeline: list
    scores: dict
    recommendations: list
    snapshot_id: Optional[str] = None

class SnapshotResponse(BaseModel):
    id: int
    snapshot_id: str
    lineage_name: str
    version: int
    parent_preset_id: Optional[int]
    blueprint: CompositionBlueprint
    created_at: datetime
    overall_score: int

    class Config:
        from_attributes = True

class SnapshotDetailResponse(BaseModel):
    snapshot_id: str
    lineage_name: str
    version: int
    parent_preset_id: Optional[int]
    blueprint: CompositionBlueprint
    prompts: dict
    scores: dict
    motif_block: str
    arrangement_timeline: list
    created_at: datetime

    class Config:
        from_attributes = True
