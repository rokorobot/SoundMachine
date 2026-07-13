import re

class PromptEngine:
    @staticmethod
    def generate_suno(enriched_composition: dict) -> dict:
        """
        Formats composition details into Suno's prompt structure:
        - Style Tags (max ~120 chars)
        - Structured Prompt / Lyrics Box containing composition directions
        - Negative Prompt
        """
        blueprint = enriched_composition["raw_blueprint"]
        
        # Style Tags formulation (comma-separated, clean, concise)
        genre_tag = blueprint["genre"].replace("_", " ")
        style_list = [
            genre_tag,
            f"{blueprint['bpm']}bpm",
            "instrumental" if blueprint["motif_type"] != "vocal phrase" else "vocals",
        ]
        
        # Add a couple of highly relevant descriptors based on sliders
        if blueprint["glitch_density"] > 60:
            style_list.append("glitch")
        if blueprint["bass_aggression"] > 60:
            style_list.append("heavy bass")
        if blueprint["atmosphere_depth"] > 60:
            style_list.append("atmospheric")
            
        style_tags = ", ".join(style_list)  # R13: no hidden 120-char truncation
        
        # Section Prompt Formulation (incorporates structures and motifs)
        lyrics_prompt = (
            f"[Intro]\n"
            f"[Atmosphere: {enriched_composition['atmosphere_description']}]\n"
            f"[Tempo: {enriched_composition['bpm_description']}]\n\n"
            f"[Verse 1]\n"
            f"[Rhythm: {enriched_composition['drum_description']}]\n"
            f"[Bass: {enriched_composition['bass_description']}]\n\n"
            f"[Motif Showcase]\n"
            f"[{enriched_composition['motif_description']}]\n"
            f"[Harmony: {enriched_composition['harmony_description']}]\n\n"
            f"[Glitch Break]\n"
            f"[Texture: {enriched_composition['glitch_description']}]\n\n"
            f"[Outro]\n"
            f"[Structure: {enriched_composition['structure_description']}]\n"
            f"[End]"
        )
        
        # Negative Prompt setup
        negative_tags = []
        if blueprint["motif_type"] != "vocal phrase":
            negative_tags.append("vocals")
            negative_tags.append("singing")
            
        if blueprint["glitch_density"] < 20:
            negative_tags.append("glitch")
            negative_tags.append("noise")
            
        negative_prompt = ", ".join(negative_tags)
        
        return {
            "style_tags": style_tags,
            "prompt_body": lyrics_prompt,
            "negative_prompt": negative_prompt or "none"
        }

    @staticmethod
    def generate_udio(enriched_composition: dict) -> dict:
        """
        Formats composition details into Udio's prompt structure:
        - Tags prompt (comma-separated tags)
        - Structure markers for lyrics field
        """
        blueprint = enriched_composition["raw_blueprint"]
        genre_tag = blueprint["genre"].replace("_", " ")
        
        # Udio uses descriptive lists of tags
        tags = [
            genre_tag,
            "electronic",
            f"{blueprint['bpm']} bpm",
            f"energy level {blueprint['energy']}",
            f"{blueprint['motif_type']}",
            enriched_composition['bass_description'].split(",")[0], # first phrase of bass description
        ]
        
        if blueprint["glitch_density"] > 50:
            tags.append("idm")
            tags.append("glitch")
        if blueprint["atmosphere_depth"] > 50:
            tags.append("ambient")
            tags.append("reverb")
            
        udio_tags = ", ".join(tags)
        
        # Structure markers
        structure_prompt = (
            f"[Instrumental Intro - {enriched_composition['atmosphere_description']}]\n"
            f"[Verse - {enriched_composition['drum_description']}]\n"
            f"[Bass Drop - {enriched_composition['bass_description']}]\n"
            f"[Primary Motif Hook - {enriched_composition['motif_description']}]\n"
            f"[Bridge - {enriched_composition['glitch_description']}]\n"
            f"[Outro - {enriched_composition['structure_description']}]"
        )
        
        return {
            "tags": udio_tags,
            "prompt_body": structure_prompt,
            "negative_prompt": "vocals, voice, singing" if blueprint["motif_type"] != "vocal phrase" else "instrumental solo"
        }

    @classmethod
    def generate(cls, enriched_composition: dict, target_model: str = "suno") -> dict:
        """
        Generate prompts based on target model preference.
        """
        suno_outputs = cls.generate_suno(enriched_composition)
        udio_outputs = cls.generate_udio(enriched_composition)
        
        return {
            "suno": suno_outputs,
            "udio": udio_outputs,
            "active_target": target_model
        }
