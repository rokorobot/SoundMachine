class MotifEngine:
    @staticmethod
    def generate_block(motif_type: str, presence: int, behavior: str, harmony_mode: str) -> str:
        """
        Creates a structured "Core Musical Identity Block" separate from style tags.
        """
        if motif_type == "no motif" or presence == 0:
            return (
                "[Core Musical Identity:\n"
                "no primary melodic motif,\n"
                "focus strictly on micro-rhythm and texture,\n"
                "drones and atmospheric tension serve as structural glue]"
            )

        # 1. Base instrument adjective
        instrument_descriptors = {
            "cathedral organ": "cold cathedral organ motif",
            "synth piano": "glassy synth piano motif",
            "FM synth hook": "metallic FM synth hook motif",
            "electric guitar riff": "gritty electric guitar riff",
            "vocal phrase": "processed vocal phrase motif",
            "bass motif": "distorted analog bass motif",
            "bell motif": "crystalline chime bell motif",
            "choir pad": "ethereal choir pad motif"
        }
        instrument = instrument_descriptors.get(motif_type, f"custom {motif_type} motif")

        # 2. Harmony key phrase
        harmony_descriptors = {
            "minor": "minor-key obsessive 4-bar phrase",
            "major": "major-key bright diatonic 4-bar phrase",
            "phrygian": "phrygian-mode tense eastern-flavored 4-bar phrase",
            "chromatic": "chromatic-mode dissonant complex 2-bar phrase",
            "dorian": "dorian-mode retro-melancholic 4-bar phrase"
        }
        harmony_phrase = harmony_descriptors.get(harmony_mode, f"{harmony_mode}-mode melodic phrase")

        # 3. Behavior translation
        behavior_descriptors = {
            "fragmenting": "gradually fragmented by glitch processing",
            "repeating": "hypnotically repeating in tight loops",
            "soaring": "soaring dynamically over the rhythm track",
            "staccato": "broken into sharp staccato stabs",
            "ascending": "escalating in pitch and pressure"
        }
        behavior_phrase = behavior_descriptors.get(behavior, f"characterized by {behavior} motions")

        # 4. Presence modifiers
        if presence > 80:
            presence_phrase = "highly dominant, front-and-center in the mix, overriding background signals"
            role_phrase = "serves as the absolute structural anchor of the entire composition"
        elif presence > 40:
            presence_phrase = "reintroduced after each structural breakdown or hard reset"
            role_phrase = "serves as the emotional anchor inside the industrial chaos"
        else:
            presence_phrase = "ghostly sub-level presence drifting behind main mix elements"
            role_phrase = "serves as a faint memory cell popping up occasionally"

        return (
            f"[Core Musical Identity:\n"
            f"{instrument},\n"
            f"{harmony_phrase},\n"
            f"{behavior_phrase},\n"
            f"{presence_phrase},\n"
            f"{role_phrase}]"
        )
