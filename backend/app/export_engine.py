import json
from typing import Dict

class ExportEngine:
    @staticmethod
    def format_text_prompt(preset_name: str, target: str, prompts: dict) -> str:
        """
        Formats a generated prompt into a clean copy-pasteable txt layout.
        """
        if target == "suno":
            suno = prompts["suno"]
            return (
                f"=== SOUND MACHINA v0.1 PROMPT EXPORT ===\n"
                f"Preset: {preset_name}\n"
                f"Target: Suno AI\n"
                f"----------------------------------------\n"
                f"STYLE TAGS:\n"
                f"{suno['style_tags']}\n\n"
                f"NEGATIVE PROMPT:\n"
                f"{suno['negative_prompt']}\n\n"
                f"PROMPT BODY / LYRICS BOX:\n"
                f"{suno['prompt_body']}\n"
                f"========================================"
            )
        else:
            udio = prompts["udio"]
            return (
                f"=== SOUND MACHINA v0.1 PROMPT EXPORT ===\n"
                f"Preset: {preset_name}\n"
                f"Target: Udio AI\n"
                f"----------------------------------------\n"
                f"TAGS / DESCRIPTORS:\n"
                f"{udio['tags']}\n\n"
                f"NEGATIVE PROMPT:\n"
                f"{udio['negative_prompt']}\n\n"
                f"STRUCTURE / LYRICS BOX:\n"
                f"{udio['prompt_body']}\n"
                f"========================================"
            )

    @staticmethod
    def format_project_json(preset_name: str, blueprint: dict, prompts: dict) -> str:
        """
        Creates a JSON dump containing all parameters and generated prompt variations.
        """
        project_data = {
            "application": "Sound Machina",
            "version": "0.1",
            "preset_name": preset_name,
            "blueprint": blueprint,
            "generated_prompts": prompts
        }
        return json.dumps(project_data, indent=2)
