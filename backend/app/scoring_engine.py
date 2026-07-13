from typing import Dict, Any, List
from app.schemas import CompositionBlueprint

class ScoringEngine:
    @staticmethod
    def evaluate(blueprint: CompositionBlueprint, prompts: dict) -> dict:
        """
        Calibrated, deterministic, rule-based diagnostic analysis of prompt composition.
        Scores 5 components from 0 to 100 with strict standards and yields alerts/recommendations.
        """
        # Read parameters
        genre = blueprint.genre
        bpm = blueprint.bpm
        energy = blueprint.energy
        motif_type = blueprint.motif_type
        motif_presence = blueprint.motif_presence
        motif_behavior = blueprint.motif_behavior
        bass_aggression = blueprint.bass_aggression
        glitch_density = blueprint.glitch_density
        drum_intensity = blueprint.drum_intensity
        target_model = blueprint.target_model
        
        # Style tag length for prompt density checks
        suno_style = prompts.get("suno", {}).get("style_tags", "")
        udio_tags = prompts.get("udio", {}).get("tags", "")
        active_tags = suno_style if target_model == "suno" else udio_tags
        tags_len = len(active_tags)
        
        # Calibration Base Settings (starting below 100 to represent realistic tolerances)
        motif_clarity = 94
        genre_focus = 92
        prompt_density = 90
        model_compatibility = 94
        negative_prompt_quality = 92
        
        recommendations = []

        # 1. MOTIF CLARITY RULES
        if motif_type == "no motif" or motif_presence == 0:
            motif_clarity = 45
            recommendations.append({
                "level": "error",
                "code": "NO_THEMATIC_ANCHOR",
                "message": "NO THEMATIC ANCHOR: The track lacks a melodic motif, which may lead to generic sound design.",
                "target": "motif_type"
            })
        else:
            if motif_presence < 25:
                motif_clarity -= 35
                recommendations.append({
                    "level": "error",
                    "code": "WEAK_MOTIF_SIGNATURE",
                    "message": "WEAK MOTIF SIGNATURE: Motif presence is extremely low; prompt might fail to establish recurring identity.",
                    "target": "motif_presence"
                })
            elif motif_presence < 55:
                motif_clarity -= 8
                recommendations.append({
                    "level": "info",
                    "code": "LOW_MOTIF_PRESENCE",
                    "message": "LOW MOTIF PRESENCE: Motif has a moderate presence. Increase slider to make it stand out.",
                    "target": "motif_presence"
                })
            
            if glitch_density > 85 and motif_presence < 45:
                motif_clarity -= 25
                recommendations.append({
                    "level": "warning",
                    "code": "IDENTITY_DEGRADATION_RISK",
                    "message": "IDENTITY DEGRADATION RISK: Severe glitch levels are likely to disrupt the weak motif. Boost motif presence.",
                    "target": "glitch_density"
                })
                
            if motif_presence > 85 and energy < 45:
                motif_clarity -= 15
                recommendations.append({
                    "level": "warning",
                    "code": "MOTIF_ENERGY_MISMATCH",
                    "message": "MOTIF ENERGY MISMATCH: Melodic presence is highly dominant, but overall energy is low, creating a structural mismatch.",
                    "target": "motif_presence"
                })

            if len(recommendations) == 0 or not any(r["target"] == "motif_presence" or r["target"] == "motif_type" for r in recommendations):
                recommendations.append({
                    "level": "info",
                    "code": "MOTIF_STABLE",
                    "message": "MOTIF STABLE: Primary musical motif is well-anchored and clearly defined.",
                    "target": "motif_type"
                })

        # 2. GENRE FOCUS RULES
        if genre == "psycho_glitch_techno":
            # BPM techno check (125-140)
            if bpm < 125 or bpm > 140:
                diff = min(30, abs(132 - bpm) * 2)
                genre_focus -= diff
                recommendations.append({
                    "level": "warning",
                    "code": "TEMPO_MISMATCH_TECHNO",
                    "message": f"TEMPO MISMATCH: Psycho Glitch Techno is typically optimal at 125-140 BPM (currently {bpm}).",
                    "target": "bpm"
                })
            elif bpm != 132:
                genre_focus -= 4  # Small precision deduction
            
            # Glitch check
            if glitch_density < 50:
                genre_focus -= 25
                recommendations.append({
                    "level": "error",
                    "code": "GLITCH_DEFICIT",
                    "message": "GLITCH DEFICIT: Psycho Glitch Techno requires higher glitch density. Push past 50%.",
                    "target": "glitch_density"
                })
                
        elif genre == "coldwave":
            # BPM coldwave check (100-120)
            if bpm < 100 or bpm > 120:
                diff = min(30, abs(110 - bpm) * 2)
                genre_focus -= diff
                recommendations.append({
                    "level": "warning",
                    "code": "TEMPO_MISMATCH_COLDWAVE",
                    "message": f"TEMPO MISMATCH: Coldwave beats are typically optimal at 100-120 BPM (currently {bpm}).",
                    "target": "bpm"
                })
            elif bpm != 110:
                genre_focus -= 4
                
            # Glitch should be minimal
            if glitch_density > 40:
                genre_focus -= 20
                recommendations.append({
                    "level": "warning",
                    "code": "GLITCH_INTRUSION",
                    "message": "GLITCH INTRUSION: Coldwave requires clean rhythms. Lower glitch density below 40%.",
                    "target": "glitch_density"
                })
                
        elif genre == "brutalist_techno":
            # BPM brutalist check (130-145)
            if bpm < 130 or bpm > 145:
                diff = min(30, abs(135 - bpm) * 2)
                genre_focus -= diff
                recommendations.append({
                    "level": "warning",
                    "code": "TEMPO_MISMATCH_BRUTALIST",
                    "message": f"TEMPO MISMATCH: Brutalist Warehouse techno is optimal at 130-145 BPM.",
                    "target": "bpm"
                })
            elif bpm != 135:
                genre_focus -= 4
                
            if bass_aggression < 70 or drum_intensity < 70:
                genre_focus -= 25
                recommendations.append({
                    "level": "error",
                    "code": "INSUFFICIENT_ATTACK",
                    "message": "INSUFFICIENT ATTACK: Brutalist Techno requires aggressive bass and drums. Boost both past 70%.",
                    "target": "bass_aggression"
                })
                
        elif genre == "ambient":
            # BPM ambient check (50-90)
            if bpm < 50 or bpm > 90:
                diff = min(30, abs(75 - bpm) * 2)
                genre_focus -= diff
                recommendations.append({
                    "level": "warning",
                    "code": "TEMPO_MISMATCH_AMBIENT",
                    "message": f"TEMPO MISMATCH: Ambient tracks are typically optimal at 50-90 BPM.",
                    "target": "bpm"
                })
            elif bpm != 75:
                genre_focus -= 4
                
            if drum_intensity > 30:
                genre_focus -= 25
                recommendations.append({
                    "level": "error",
                    "code": "RHYTHMIC_INTERFERENCE",
                    "message": "RHYTHMIC INTERFERENCE: Ambient tracks require sparse drums. Reduce drum intensity below 30%.",
                    "target": "drum_intensity"
                })

        if genre_focus >= 85 and len([r for r in recommendations if r["target"] == "bpm" or r["target"] == "genre"]) == 0:
            recommendations.append({
                "level": "info",
                "code": "GENRE_STABLE",
                "message": "GENRE STABLE: Temporal and rhythmic properties align perfectly with selected style footprint.",
                "target": "genre"
            })

        # 3. PROMPT DENSITY RULES (Tag Overload / Under-described checks)
        pressure = (glitch_density + drum_intensity + bass_aggression) / 3.0
        if energy > 90 and pressure > 85:
            prompt_density -= 20
            recommendations.append({
                "level": "warning",
                "code": "PROMPT_DENSITY_OVERLOAD",
                "message": "PROMPT DENSITY OVERLOAD: High energy combined with maximum sound pressure risks muddying the generated track.",
                "target": "energy"
            })
            
        if tags_len < 30:
            prompt_density -= 25
            recommendations.append({
                "level": "warning",
                "code": "UNDER_DESCRIBED",
                "message": "UNDER-DESCRIBED: Prompt tag set is very brief. Consider tweaking controls to add sound descriptors.",
                "target": "glitch_density"
            })
        elif tags_len > 110:
            prompt_density -= 12
            recommendations.append({
                "level": "info",
                "code": "PROMPT_APPROACHING_LIMIT",
                "message": "PROMPT APPROACHING LIMIT: Style description is dense. Consider lowering a slider to keep tags clear.",
                "target": "glitch_density"
            })

        if prompt_density >= 85 and len([r for r in recommendations if r["code"] in ["PROMPT_DENSITY_OVERLOAD", "UNDER_DESCRIBED"]]) == 0:
            recommendations.append({
                "level": "info",
                "code": "DENSITY_STABLE",
                "message": "DENSITY STABLE: Tag density is balanced and fits model input constraints.",
                "target": "glitch_density"
            })

        # 4. MODEL COMPATIBILITY RULES
        # R13: the Suno 120-character assumption is removed pending separate
        # platform research; no tag-length threshold penalty is applied. The
        # actual tag length remains visible in the prompt terminal.
        if target_model == "udio":
            if bpm > 160:
                model_compatibility -= 20
                recommendations.append({
                    "level": "warning",
                    "code": "UDIO_TEMPO_STRETCH",
                    "message": "UDIO TEMPO STRETCH: Hyper-tempo prompts (>160 BPM) can lead to glitchy vocal outputs in Udio.",
                    "target": "bpm"
                })
            if glitch_density > 90:
                model_compatibility -= 10
                recommendations.append({
                    "level": "info",
                    "code": "UDIO_GLITCH_CRITICAL",
                    "message": "UDIO GLITCH CRITICAL: High glitch density (>90%) may cause synthesis errors in Udio.",
                    "target": "glitch_density"
                })

        if model_compatibility >= 90:
            recommendations.append({
                "level": "info",
                "code": "MODEL_COMPATIBILITY_OK",
                "message": "COMPATIBILITY OK: System calibration conforms to model parser constraints.",
                "target": "target_model"
            })

        # 5. NEGATIVE PROMPT QUALITY RULES
        active_neg = prompts.get(target_model, {}).get("negative_prompt", "")
        machine_empty = active_neg == "none" or not active_neg.strip()
        if machine_empty and motif_type == "vocal phrase":
            # R27: a vocal blueprint legitimately omits vocal exclusions. This is
            # a machine-owned value, not an operator error, so it is not a deficit.
            recommendations.append({
                "level": "info",
                "code": "VOCAL_NEGATIVE_MACHINE_MANAGED",
                "message": "VOCAL EXCLUSIONS MACHINE-MANAGED: Vocal blueprints intentionally omit vocal exclusions; the negative prompt is machine-owned.",
                "target": "target_model"
            })
        elif machine_empty:
            negative_prompt_quality = 40
            recommendations.append({
                "level": "error",
                "code": "EXCLUSION_DEFICIT",
                "message": "EXCLUSION DEFICIT: Negative prompt is empty. AI models might leak unwanted vocal or percussion noise.",
                "target": "target_model"
            })
        else:
            if motif_type != "vocal phrase" and "vocals" not in active_neg.lower():
                negative_prompt_quality -= 20
                recommendations.append({
                    "level": "warning",
                    "code": "VOCAL_LEAKAGE_RISK",
                    "message": "VOCAL LEAKAGE RISK: Instrumental tracks should include 'vocals' in the negative prompt.",
                    "target": "target_model"
                })
            
            if "drums" in active_neg.lower() and drum_intensity > 50:
                negative_prompt_quality -= 25
                recommendations.append({
                    "level": "warning",
                    "code": "CONSTRAINT_CONFLICT",
                    "message": "CONSTRAINT CONFLICT: Excluded drums in negative prompt but drum intensity is high.",
                    "target": "drum_intensity"
                })

        if negative_prompt_quality >= 85 and len([r for r in recommendations if r["code"] in ["EXCLUSION_DEFICIT", "VOCAL_LEAKAGE_RISK", "CONSTRAINT_CONFLICT"]]) == 0:
            recommendations.append({
                "level": "info",
                "code": "CONSTRAINTS_OK",
                "message": "CONSTRAINTS OK: Negative exclusions are well-calibrated and free of logical conflicts.",
                "target": "target_model"
            })

        # Cap subscores at 0 and 100
        motif_clarity = max(0, min(100, motif_clarity))
        genre_focus = max(0, min(100, genre_focus))
        prompt_density = max(0, min(100, prompt_density))
        model_compatibility = max(0, min(100, model_compatibility))
        negative_prompt_quality = max(0, min(100, negative_prompt_quality))
        
        # Calculate overall score
        overall = int(
            (motif_clarity + genre_focus + prompt_density + model_compatibility + negative_prompt_quality) / 5.0
        )
        
        # Apply standard calibration offsets (so even optimal setups rarely exceed 95)
        # Apply a flat -3% tolerance check limit to model overall complexity
        overall = min(95, overall)

        return {
            "overall": overall,
            "motif_clarity": motif_clarity,
            "genre_focus": genre_focus,
            "prompt_density": prompt_density,
            "model_compatibility": model_compatibility,
            "negative_prompt_quality": negative_prompt_quality,
            "recommendations": recommendations
        }
