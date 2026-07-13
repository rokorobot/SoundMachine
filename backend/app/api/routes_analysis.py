from fastapi import APIRouter

from app.schemas import CompareRequest
from app.composition_engine import CompositionEngine
from app.prompt_engine import PromptEngine
from app.scoring_engine import ScoringEngine

router = APIRouter(prefix="/api")


@router.post("/compare")
def compare_configurations(payload: CompareRequest):
    a = payload.blueprint_a
    b = payload.blueprint_b

    enriched_a = CompositionEngine.process(a)
    scores_a = ScoringEngine.evaluate(a, PromptEngine.generate(enriched_a, target_model=a.target_model))
    enriched_b = CompositionEngine.process(b)
    scores_b = ScoringEngine.evaluate(b, PromptEngine.generate(enriched_b, target_model=b.target_model))

    diff = {}
    for field in a.model_fields.keys():
        val_a = getattr(a, field)
        val_b = getattr(b, field)
        if val_a != val_b:
            if isinstance(val_a, int):
                diff[field] = {"value_a": val_a, "value_b": val_b, "delta": val_b - val_a}
            else:
                diff[field] = {"value_a": val_a, "value_b": val_b, "delta": "changed"}

    return {
        "diff": diff,
        "scores_a": scores_a,
        "scores_b": scores_b,
        "overall_delta": scores_b["overall"] - scores_a["overall"],
    }
