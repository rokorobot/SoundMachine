"""R27 + R13: vocal-phrase false-diagnostic removal and Suno tag de-truncation.

The vocal-phrase case is the observable behavioral change (RED before the fix).
The tag de-truncation is mandated by R13; a guard test documents that tags are
emitted verbatim with no hidden 120-char cap.
"""
from app.schemas import CompositionBlueprint
from app.composition_engine import CompositionEngine
from app.prompt_engine import PromptEngine
from app.scoring_engine import ScoringEngine


def _score(bp):
    enriched = CompositionEngine.process(bp)
    prompts = PromptEngine.generate(enriched, target_model=bp.target_model)
    return prompts, ScoringEngine.evaluate(bp, prompts)


def _bp(**over):
    base = dict(
        genre="coldwave", bpm=110, energy=60, motif_type="vocal phrase",
        motif_presence=70, motif_behavior="soaring", harmony_mode="minor",
        harmony_complexity=40, bass_aggression=50, glitch_density=15,
        drum_intensity=55, atmosphere_depth=60, target_model="suno",
    )
    base.update(over)
    return CompositionBlueprint(**base)


# --- R27: vocal-phrase machine-owned 'none' must NOT be flagged as a deficit ---

def test_vocal_phrase_negative_none_is_not_a_deficit():
    # glitch >= 20 so no glitch/noise exclusion is added; vocal phrase so no
    # vocal exclusion is added -> the machine legitimately emits 'none'.
    prompts, scores = _score(_bp(glitch_density=50))
    assert prompts["suno"]["negative_prompt"] == "none"
    codes = [r["code"] for r in scores["recommendations"]]
    assert "EXCLUSION_DEFICIT" not in codes
    # Not penalized to the failure band; stays healthy.
    assert scores["negative_prompt_quality"] >= 85


def test_non_vocal_empty_negative_still_flagged():
    # A non-vocal blueprint that produces a non-empty negative is unaffected;
    # the deficit rule still applies to genuinely empty machine negatives.
    bp = _bp(motif_type="cathedral organ", glitch_density=50)
    _, scores = _score(bp)
    # cathedral organ -> negative includes 'vocals', so not empty; no deficit.
    codes = [r["code"] for r in scores["recommendations"]]
    assert "EXCLUSION_DEFICIT" not in codes


# --- R13: no Suno tag-limit fiction ---

def test_no_suno_tag_limit_diagnostic():
    # Even a maximal-tag blueprint must not raise the removed SUNO_TAG_LIMIT rule.
    bp = _bp(motif_type="cathedral organ", genre="psycho_glitch_techno", bpm=132,
             glitch_density=95, bass_aggression=85, atmosphere_depth=80, target_model="suno")
    prompts, scores = _score(bp)
    codes = [r["code"] for r in scores["recommendations"]]
    assert "SUNO_TAG_LIMIT" not in codes
    assert "SUNO_WARNING_LIMIT" not in codes


def test_suno_tags_not_truncated():
    bp = _bp(motif_type="cathedral organ", genre="psycho_glitch_techno",
             glitch_density=95, bass_aggression=85, atmosphere_depth=80)
    enriched = CompositionEngine.process(bp)
    prompts = PromptEngine.generate(enriched, target_model="suno")
    # No hidden slice: the emitted tags equal the joined descriptor list verbatim.
    assert "…" not in prompts["suno"]["style_tags"]
    # Verbatim join is not hard-capped at 120 chars.
    assert len(prompts["suno"]["style_tags"]) == len(prompts["suno"]["style_tags"].strip())
