from app.schemas import CompositionBlueprint

def analyze_bpm(bpm: int) -> str:
    if bpm < 90:
        return "downtempo, slow-paced"
    elif bpm < 120:
        return "midtempo, steady groove"
    elif bpm < 140:
        return "uptempo, fast-paced, high-speed energy"
    else:
        return "hyper-tempo, frenetic speed, breakneck pace"

def analyze_energy(energy: int) -> str:
    if energy < 30:
        return "calm, relaxed, minimalist, subdued, low-energy"
    elif energy < 60:
        return "moderate energy, steady pulse, solid groove"
    elif energy < 85:
        return "high energy, driving rhythm, intense power"
    else:
        return "extreme energy, explosive impact, relentless power, maximum intensity"

def analyze_motif(motif_type: str, presence: int, behavior: str) -> str:
    if motif_type == "no motif" or presence == 0:
        return "no primary melodic theme, textured sound design focus"
    
    presence_word = "subtle"
    if presence > 75:
        presence_word = "dominant, front-and-center"
    elif presence > 40:
        presence_word = "clear, prominent"
        
    return f"{presence_word} {behavior} {motif_type} motif"

def analyze_harmony(mode: str, complexity: int) -> str:
    complexity_word = "simple minimalist"
    if complexity > 75:
        complexity_word = "highly complex, avant-garde, intricate"
    elif complexity > 40:
        complexity_word = "layered, rich"
        
    return f"{complexity_word} harmonies in a {mode} scale"

def analyze_bass(aggression: int) -> str:
    if aggression < 25:
        return "smooth, deep sub-bass, clean low-end"
    elif aggression < 60:
        return "warm analog bassline, solid low-end presence"
    elif aggression < 85:
        return "heavy driving bass, gritty saturated low-end"
    else:
        return "brutal, distorted, aggressive industrial synth bassline, punishing low-end"

def analyze_glitch(density: int) -> str:
    if density < 20:
        return "clean production, pristine digital signals"
    elif density < 50:
        return "subtle glitch textures, light click-and-pop details"
    elif density < 80:
        return "dense glitch aesthetics, frequent micro-stutters, stutter-edits, tape stops"
    else:
        return "chaotic digital fragmentation, severe glitching, granular audio degradation, stutter spray"

def analyze_drums(intensity: int) -> str:
    if intensity < 20:
        return "minimalist drums, sparse clicking hats, occasional kick"
    elif intensity < 50:
        return "standard electronic beats, clean kick-snare pattern, driving hi-hats"
    elif intensity < 80:
        return "heavy drums, aggressive syncopated percussion, pounding beats, metallic snares"
    else:
        return "punishing blast beats, hyper-compressed industrial kicks, overwhelming rhythmic chaos, dense complex breakbeats"

def analyze_atmosphere(depth: int) -> str:
    if depth < 20:
        return "dry production, upfront spatial treatment, intimate close-mic feel"
    elif depth < 50:
        return "moderate spatial depth, natural room reverb, warm acoustic spaces"
    elif depth < 80:
        return "vast atmospheric depths, lush synthesizer pads, sweeping echoes"
    else:
        return "cavernous cosmic reverbs, infinite decay tails, dark industrial drone backdrops, immense wall of sound"

class CompositionEngine:
    @staticmethod
    def process(blueprint: CompositionBlueprint) -> dict:
        """
        Creates an augmented, rich internal representation of the track
        from the flat user controls.
        """
        # Formulate descriptions deterministically
        bpm_desc = analyze_bpm(blueprint.bpm)
        energy_desc = analyze_energy(blueprint.energy)
        motif_desc = analyze_motif(blueprint.motif_type, blueprint.motif_presence, blueprint.motif_behavior)
        harmony_desc = analyze_harmony(blueprint.harmony_mode, blueprint.harmony_complexity)
        bass_desc = analyze_bass(blueprint.bass_aggression)
        glitch_desc = analyze_glitch(blueprint.glitch_density)
        drum_desc = analyze_drums(blueprint.drum_intensity)
        atmosphere_desc = analyze_atmosphere(blueprint.atmosphere_depth)

        # Structure mapping based on energy and genre
        structure_desc = "standard dynamic build-up and release"
        if blueprint.genre == "psycho_glitch_techno":
            structure_desc = "fragmented anti-drop structure, unexpected jump cuts, micro-breakdowns"
        elif blueprint.genre == "brutalist_techno":
            structure_desc = "relentless linear repetition, hypnotic loops, escalating noise walls"
        elif blueprint.genre == "ambient":
            structure_desc = "no drum drops, slow organic swell, formless soundscapes"
        elif blueprint.genre == "coldwave":
            structure_desc = "verse-chorus division, retro synth breakdowns, sudden cold endings"

        return {
            "bpm_label": f"{blueprint.bpm} BPM",
            "bpm_description": bpm_desc,
            "energy_description": energy_desc,
            "motif_description": motif_desc,
            "harmony_description": harmony_desc,
            "bass_description": bass_desc,
            "glitch_description": glitch_desc,
            "drum_description": drum_desc,
            "atmosphere_description": atmosphere_desc,
            "structure_description": structure_desc,
            "raw_blueprint": blueprint.model_dump()
        }
