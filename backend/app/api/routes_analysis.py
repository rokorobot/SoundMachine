from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List

from app.schemas import CompositionBlueprint
from app.composition_engine import CompositionEngine
from app.prompt_engine import PromptEngine
from app.scoring_engine import ScoringEngine

router = APIRouter(prefix="/api")

class CompareRequest(BaseModel):
    blueprint_a: CompositionBlueprint
    blueprint_b: CompositionBlueprint

@router.post("/analyze-prompt")
def analyze_prompt(blueprint: CompositionBlueprint):
    try:
        enriched = CompositionEngine.process(blueprint)
        prompts = PromptEngine.generate(enriched, target_model=blueprint.target_model)
        scores = ScoringEngine.evaluate(blueprint, prompts)
        return scores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/compare")
def compare_configurations(payload: CompareRequest):
    try:
        a = payload.blueprint_a
        b = payload.blueprint_b
        
        # Calculate scores
        enriched_a = CompositionEngine.process(a)
        prompts_a = PromptEngine.generate(enriched_a, target_model=a.target_model)
        scores_a = ScoringEngine.evaluate(a, prompts_a)
        
        enriched_b = CompositionEngine.process(b)
        prompts_b = PromptEngine.generate(enriched_b, target_model=b.target_model)
        scores_b = ScoringEngine.evaluate(b, prompts_b)
        
        # Build differences dict
        diff = {}
        for field in a.model_fields.keys():
            val_a = getattr(a, field)
            val_b = getattr(b, field)
            if val_a != val_b:
                if isinstance(val_a, int):
                    diff[field] = {
                        "value_a": val_a,
                        "value_b": val_b,
                        "delta": val_b - val_a
                    }
                else:
                    diff[field] = {
                        "value_a": val_a,
                        "value_b": val_b,
                        "delta": "changed"
                    }
                    
        return {
            "diff": diff,
            "scores_a": scores_a,
            "scores_b": scores_b,
            "overall_delta": scores_b["overall"] - scores_a["overall"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Comparison failed: {str(e)}"
        )
