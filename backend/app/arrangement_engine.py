from typing import List, Dict, Any

class ArrangementEngine:
    @staticmethod
    def generate_timeline(bpm: int, energy: int, genre: str, glitch_density: int, drum_intensity: int) -> List[Dict[str, Any]]:
        """
        Creates a 5-phase deterministic track arrangement layout.
        Calculates time codes and modulated energy states based on composition blueprint.
        """
        # Formulate approximate phase durations based on BPM (faster BPM = shorter phases in time)
        # Standard base: 120 BPM = 30 second sections.
        factor = 120.0 / float(bpm)
        
        durations = [
            int(30 * factor),  # Intro
            int(45 * factor),  # Establish Motif
            int(40 * factor),  # Pressure Build
            int(60 * factor),  # Mutation / Peak
            int(30 * factor)   # Outro
        ]
        
        phases = [
            "Intro",
            "Establish Motif",
            "Pressure Build",
            "Mutation / Peak",
            "Outro / Residual Signal"
        ]
        
        descriptions = [
            "Ambient soundscape layers initialized. Drum pulse bypassed, slow atmospheric swell.",
            "Melodic cells fade in. Base frequency lines introduced, establishing harmonic field.",
            "Rhythmic density increased. Glitch elements activate, filters sweeps rising in cutoff.",
            "Saturated peak performance. Maximum glitch triggers, drum impact maxed, motif fully modded.",
            "Signal decay. Reverb tails decay to silence, rhythm elements mute, residual synth noise."
        ]
        
        # Energy modulations per phase
        energy_factors = [0.4, 0.7, 0.9, 1.1, 0.3]
        
        timeline = []
        current_seconds = 0
        
        for i in range(5):
            duration = durations[i]
            phase_energy = min(100, int(energy * energy_factors[i]))
            
            # Format time codes MM:SS
            start_m, start_s = divmod(current_seconds, 60)
            end_m, end_s = divmod(current_seconds + duration, 60)
            
            time_start = f"{start_m:02d}:{start_s:02d}"
            time_end = f"{end_m:02d}:{end_s:02d}"
            
            timeline.append({
                "phase": phases[i],
                "time_start": time_start,
                "time_end": time_end,
                "duration_seconds": duration,
                "energy_level": phase_energy,
                "description": descriptions[i]
            })
            
            current_seconds += duration
            
        return timeline
