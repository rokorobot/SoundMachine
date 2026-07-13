"""Deterministic engine golden matrix (T1/T26).

Covers all four genres, the vocal-phrase and no-motif special cases, and slider
boundaries. The committed golden JSON is regenerated with build_goldens() and
must be re-committed (with a PIPELINE_VERSION bump) whenever engine output changes.
"""
from app.schemas import CompositionBlueprint
from app.composition_engine import CompositionEngine
from app.prompt_engine import PromptEngine
from app.scoring_engine import ScoringEngine
from app.motif_engine import MotifEngine
from app.arrangement_engine import ArrangementEngine
from app.pipeline_version import PIPELINE_VERSION


def _bp(**over):
    base = dict(
        genre="psycho_glitch_techno", bpm=132, energy=90, motif_type="cathedral organ",
        motif_presence=50, motif_behavior="fragmenting", harmony_mode="minor",
        harmony_complexity=60, bass_aggression=80, glitch_density=95, drum_intensity=85,
        atmosphere_depth=40, target_model="suno",
    )
    base.update(over)
    return base


MATRIX = {
    "psycho_default": _bp(),
    "coldwave": _bp(genre="coldwave", bpm=110, glitch_density=15, motif_type="FM synth hook",
                    harmony_mode="phrygian", target_model="udio"),
    "brutalist": _bp(genre="brutalist_techno", bpm=135, bass_aggression=95, drum_intensity=95,
                     motif_type="bass motif", harmony_mode="chromatic"),
    "ambient": _bp(genre="ambient", bpm=75, energy=20, drum_intensity=5, glitch_density=10,
                   motif_type="choir pad", motif_behavior="soaring", atmosphere_depth=95, target_model="udio"),
    "vocal_phrase": _bp(genre="coldwave", bpm=110, glitch_density=50, motif_type="vocal phrase",
                        motif_behavior="soaring"),
    "no_motif": _bp(motif_type="no motif", motif_presence=0),
    "min_boundary": _bp(genre="ambient", bpm=40, energy=0, motif_presence=0, harmony_complexity=0,
                        bass_aggression=0, glitch_density=0, drum_intensity=0, atmosphere_depth=0,
                        motif_type="no motif"),
    "max_boundary": _bp(bpm=240, energy=100, motif_presence=100, harmony_complexity=100,
                        bass_aggression=100, glitch_density=100, drum_intensity=100, atmosphere_depth=100),
}


def build_case(blueprint_dict):
    bp = CompositionBlueprint(**blueprint_dict)
    enriched = CompositionEngine.process(bp)
    prompts = PromptEngine.generate(enriched, target_model=bp.target_model)
    scores = ScoringEngine.evaluate(bp, prompts)
    motif = MotifEngine.generate_block(bp.motif_type, bp.motif_presence, bp.motif_behavior, bp.harmony_mode)
    timeline = ArrangementEngine.generate_timeline(bp.bpm, bp.energy, bp.genre, bp.glitch_density, bp.drum_intensity)
    return {"prompts": prompts, "scores": scores, "motif_block": motif, "arrangement_timeline": timeline}


def build_goldens():
    return {
        "pipeline_version": PIPELINE_VERSION,
        "cases": {name: build_case(bp) for name, bp in MATRIX.items()},
    }
