import json
import sys
import argparse
from sqlalchemy.orm import Session
from app.database import Preset, SessionLocal, engine, Base

DEFAULT_PRESETS = [
    # BANK_A — Core Presets
    {
        "name": "Psych Tec",
        "bank": "BANK_A",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 132,
            "energy": 90,
            "motif_type": "cathedral organ",
            "motif_presence": 50,
            "motif_behavior": "fragmenting",
            "harmony_mode": "minor",
            "harmony_complexity": 60,
            "bass_aggression": 80,
            "glitch_density": 95,
            "drum_intensity": 85,
            "atmosphere_depth": 40,
            "target_model": "suno"
        }
    },
    {
        "name": "Cold Signal",
        "bank": "BANK_A",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 110,
            "energy": 65,
            "motif_type": "FM synth hook",
            "motif_presence": 75,
            "motif_behavior": "repeating",
            "harmony_mode": "phrygian",
            "harmony_complexity": 45,
            "bass_aggression": 55,
            "glitch_density": 15,
            "drum_intensity": 60,
            "atmosphere_depth": 70,
            "target_model": "udio"
        }
    },
    {
        "name": "Brutalist Warehouse",
        "bank": "BANK_A",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 135,
            "energy": 95,
            "motif_type": "bass motif",
            "motif_presence": 80,
            "motif_behavior": "repeating",
            "harmony_mode": "chromatic",
            "harmony_complexity": 30,
            "bass_aggression": 95,
            "glitch_density": 40,
            "drum_intensity": 95,
            "atmosphere_depth": 30,
            "target_model": "suno"
        }
    },
    {
        "name": "Ambient Machine",
        "bank": "BANK_A",
        "blueprint": {
            "genre": "ambient",
            "bpm": 75,
            "energy": 20,
            "motif_type": "choir pad",
            "motif_presence": 60,
            "motif_behavior": "soaring",
            "harmony_mode": "major",
            "harmony_complexity": 70,
            "bass_aggression": 10,
            "glitch_density": 10,
            "drum_intensity": 5,
            "atmosphere_depth": 95,
            "target_model": "udio"
        }
    },

    # BANK_B — RokoRobo Signature Collection
    {
        "name": "Velvet Dream",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "ambient",
            "bpm": 80,
            "energy": 35,
            "motif_type": "synth piano",
            "motif_presence": 65,
            "motif_behavior": "soaring",
            "harmony_mode": "minor",
            "harmony_complexity": 70,
            "bass_aggression": 15,
            "glitch_density": 10,
            "drum_intensity": 10,
            "atmosphere_depth": 85,
            "target_model": "suno"
        }
    },
    {
        "name": "Hi Def Love",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 115,
            "energy": 70,
            "motif_type": "FM synth hook",
            "motif_presence": 80,
            "motif_behavior": "repeating",
            "harmony_mode": "major",
            "harmony_complexity": 50,
            "bass_aggression": 45,
            "glitch_density": 20,
            "drum_intensity": 65,
            "atmosphere_depth": 55,
            "target_model": "udio"
        }
    },
    {
        "name": "Under Hypnosis",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 130,
            "energy": 85,
            "motif_type": "bell motif",
            "motif_presence": 60,
            "motif_behavior": "fragmenting",
            "harmony_mode": "phrygian",
            "harmony_complexity": 75,
            "bass_aggression": 70,
            "glitch_density": 80,
            "drum_intensity": 80,
            "atmosphere_depth": 50,
            "target_model": "suno"
        }
    },
    {
        "name": "Pink Lady",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 110,
            "energy": 60,
            "motif_type": "vocal phrase",
            "motif_presence": 70,
            "motif_behavior": "soaring",
            "harmony_mode": "minor",
            "harmony_complexity": 40,
            "bass_aggression": 50,
            "glitch_density": 15,
            "drum_intensity": 55,
            "atmosphere_depth": 60,
            "target_model": "suno"
        }
    },
    {
        "name": "Dark Disco",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 120,
            "energy": 75,
            "motif_type": "bass motif",
            "motif_presence": 75,
            "motif_behavior": "repeating",
            "harmony_mode": "dorian",
            "harmony_complexity": 55,
            "bass_aggression": 65,
            "glitch_density": 25,
            "drum_intensity": 75,
            "atmosphere_depth": 40,
            "target_model": "udio"
        }
    },
    {
        "name": "Skillbot Rap",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 125,
            "energy": 80,
            "motif_type": "vocal phrase",
            "motif_presence": 85,
            "motif_behavior": "staccato",
            "harmony_mode": "chromatic",
            "harmony_complexity": 50,
            "bass_aggression": 75,
            "glitch_density": 60,
            "drum_intensity": 80,
            "atmosphere_depth": 35,
            "target_model": "suno"
        }
    },
    {
        "name": "Sistema Acceso",
        "bank": "BANK_B",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 138,
            "energy": 95,
            "motif_type": "bass motif",
            "motif_presence": 85,
            "motif_behavior": "repeating",
            "harmony_mode": "chromatic",
            "harmony_complexity": 35,
            "bass_aggression": 90,
            "glitch_density": 35,
            "drum_intensity": 90,
            "atmosphere_depth": 45,
            "target_model": "udio"
        }
    },

    # BANK_C — Motif Laboratory
    {
        "name": "Organ Collapse",
        "bank": "BANK_C",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 135,
            "energy": 90,
            "motif_type": "cathedral organ",
            "motif_presence": 90,
            "motif_behavior": "fragmenting",
            "harmony_mode": "minor",
            "harmony_complexity": 85,
            "bass_aggression": 80,
            "glitch_density": 85,
            "drum_intensity": 85,
            "atmosphere_depth": 60,
            "target_model": "suno"
        }
    },
    {
        "name": "Piano Psychosis",
        "bank": "BANK_C",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 132,
            "energy": 85,
            "motif_type": "synth piano",
            "motif_presence": 80,
            "motif_behavior": "staccato",
            "harmony_mode": "chromatic",
            "harmony_complexity": 90,
            "bass_aggression": 70,
            "glitch_density": 75,
            "drum_intensity": 75,
            "atmosphere_depth": 40,
            "target_model": "udio"
        }
    },
    {
        "name": "FM Signal",
        "bank": "BANK_C",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 112,
            "energy": 65,
            "motif_type": "FM synth hook",
            "motif_presence": 75,
            "motif_behavior": "repeating",
            "harmony_mode": "phrygian",
            "harmony_complexity": 60,
            "bass_aggression": 55,
            "glitch_density": 30,
            "drum_intensity": 60,
            "atmosphere_depth": 70,
            "target_model": "suno"
        }
    },
    {
        "name": "Bell Machine",
        "bank": "BANK_C",
        "blueprint": {
            "genre": "ambient",
            "bpm": 72,
            "energy": 40,
            "motif_type": "bell motif",
            "motif_presence": 70,
            "motif_behavior": "ascending",
            "harmony_mode": "major",
            "harmony_complexity": 65,
            "bass_aggression": 20,
            "glitch_density": 15,
            "drum_intensity": 15,
            "atmosphere_depth": 90,
            "target_model": "udio"
        }
    },
    {
        "name": "Choir Protocol",
        "bank": "BANK_C",
        "blueprint": {
            "genre": "ambient",
            "bpm": 68,
            "energy": 30,
            "motif_type": "choir pad",
            "motif_presence": 85,
            "motif_behavior": "soaring",
            "harmony_mode": "minor",
            "harmony_complexity": 75,
            "bass_aggression": 25,
            "glitch_density": 10,
            "drum_intensity": 5,
            "atmosphere_depth": 95,
            "target_model": "suno"
        }
    },
    {
        "name": "Guitar Mutation",
        "bank": "BANK_C",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 130,
            "energy": 85,
            "motif_type": "electric guitar riff",
            "motif_presence": 75,
            "motif_behavior": "fragmenting",
            "harmony_mode": "phrygian",
            "harmony_complexity": 70,
            "bass_aggression": 80,
            "glitch_density": 70,
            "drum_intensity": 75,
            "atmosphere_depth": 50,
            "target_model": "udio"
        }
    },

    # BANK_D — Industrial Systems
    {
        "name": "Berghain Pressure",
        "bank": "BANK_D",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 135,
            "energy": 95,
            "motif_type": "bass motif",
            "motif_presence": 80,
            "motif_behavior": "repeating",
            "harmony_mode": "chromatic",
            "harmony_complexity": 40,
            "bass_aggression": 95,
            "glitch_density": 50,
            "drum_intensity": 95,
            "atmosphere_depth": 30,
            "target_model": "suno"
        }
    },
    {
        "name": "Concrete Hall",
        "bank": "BANK_D",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 132,
            "energy": 85,
            "motif_type": "bell motif",
            "motif_presence": 50,
            "motif_behavior": "repeating",
            "harmony_mode": "chromatic",
            "harmony_complexity": 30,
            "bass_aggression": 85,
            "glitch_density": 40,
            "drum_intensity": 90,
            "atmosphere_depth": 80,
            "target_model": "suno"
        }
    },
    {
        "name": "Steel Beam",
        "bank": "BANK_D",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 138,
            "energy": 90,
            "motif_type": "cathedral organ",
            "motif_presence": 60,
            "motif_behavior": "staccato",
            "harmony_mode": "minor",
            "harmony_complexity": 45,
            "bass_aggression": 90,
            "glitch_density": 45,
            "drum_intensity": 85,
            "atmosphere_depth": 35,
            "target_model": "udio"
        }
    },
    {
        "name": "Machine Ritual",
        "bank": "BANK_D",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 130,
            "energy": 80,
            "motif_type": "choir pad",
            "motif_presence": 70,
            "motif_behavior": "soaring",
            "harmony_mode": "phrygian",
            "harmony_complexity": 55,
            "bass_aggression": 80,
            "glitch_density": 30,
            "drum_intensity": 80,
            "atmosphere_depth": 75,
            "target_model": "suno"
        }
    },
    {
        "name": "Ultra Industrial",
        "bank": "BANK_D",
        "blueprint": {
            "genre": "brutalist_techno",
            "bpm": 140,
            "energy": 98,
            "motif_type": "bass motif",
            "motif_presence": 75,
            "motif_behavior": "repeating",
            "harmony_mode": "chromatic",
            "harmony_complexity": 35,
            "bass_aggression": 98,
            "glitch_density": 60,
            "drum_intensity": 98,
            "atmosphere_depth": 25,
            "target_model": "udio"
        }
    },
    {
        "name": "Factory Ghost",
        "bank": "BANK_D",
        "blueprint": {
            "genre": "ambient",
            "bpm": 85,
            "energy": 45,
            "motif_type": "FM synth hook",
            "motif_presence": 55,
            "motif_behavior": "fragmenting",
            "harmony_mode": "minor",
            "harmony_complexity": 65,
            "bass_aggression": 40,
            "glitch_density": 50,
            "drum_intensity": 25,
            "atmosphere_depth": 90,
            "target_model": "suno"
        }
    },

    # BANK_E — Coldwave / Minimal Wave
    {
        "name": "Static Heart",
        "bank": "BANK_E",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 108,
            "energy": 60,
            "motif_type": "vocal phrase",
            "motif_presence": 80,
            "motif_behavior": "repeating",
            "harmony_mode": "minor",
            "harmony_complexity": 40,
            "bass_aggression": 55,
            "glitch_density": 15,
            "drum_intensity": 60,
            "atmosphere_depth": 50,
            "target_model": "suno"
        }
    },
    {
        "name": "Cold Neon",
        "bank": "BANK_E",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 112,
            "energy": 68,
            "motif_type": "FM synth hook",
            "motif_presence": 70,
            "motif_behavior": "ascending",
            "harmony_mode": "phrygian",
            "harmony_complexity": 50,
            "bass_aggression": 60,
            "glitch_density": 10,
            "drum_intensity": 65,
            "atmosphere_depth": 65,
            "target_model": "udio"
        }
    },
    {
        "name": "Lucy Protocol",
        "bank": "BANK_E",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 115,
            "energy": 75,
            "motif_type": "synth piano",
            "motif_presence": 75,
            "motif_behavior": "repeating",
            "harmony_mode": "minor",
            "harmony_complexity": 45,
            "bass_aggression": 65,
            "glitch_density": 20,
            "drum_intensity": 70,
            "atmosphere_depth": 40,
            "target_model": "suno"
        }
    },
    {
        "name": "Ghost Signal",
        "bank": "BANK_E",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 105,
            "energy": 50,
            "motif_type": "bell motif",
            "motif_presence": 60,
            "motif_behavior": "fragmenting",
            "harmony_mode": "phrygian",
            "harmony_complexity": 60,
            "bass_aggression": 45,
            "glitch_density": 25,
            "drum_intensity": 50,
            "atmosphere_depth": 75,
            "target_model": "udio"
        }
    },
    {
        "name": "Velvet Delay",
        "bank": "BANK_E",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 100,
            "energy": 55,
            "motif_type": "electric guitar riff",
            "motif_presence": 65,
            "motif_behavior": "soaring",
            "harmony_mode": "minor",
            "harmony_complexity": 55,
            "bass_aggression": 40,
            "glitch_density": 15,
            "drum_intensity": 55,
            "atmosphere_depth": 80,
            "target_model": "suno"
        }
    },
    {
        "name": "No Return State",
        "bank": "BANK_E",
        "blueprint": {
            "genre": "coldwave",
            "bpm": 120,
            "energy": 80,
            "motif_type": "vocal phrase",
            "motif_presence": 85,
            "motif_behavior": "staccato",
            "harmony_mode": "chromatic",
            "harmony_complexity": 50,
            "bass_aggression": 70,
            "glitch_density": 35,
            "drum_intensity": 75,
            "atmosphere_depth": 45,
            "target_model": "udio"
        }
    },

    # BANK_F — Experimental AI
    {
        "name": "Neural Collapse",
        "bank": "BANK_F",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 140,
            "energy": 92,
            "motif_type": "synth piano",
            "motif_presence": 65,
            "motif_behavior": "fragmenting",
            "harmony_mode": "chromatic",
            "harmony_complexity": 95,
            "bass_aggression": 85,
            "glitch_density": 98,
            "drum_intensity": 90,
            "atmosphere_depth": 60,
            "target_model": "suno"
        }
    },
    {
        "name": "Fractal Object",
        "bank": "BANK_F",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 135,
            "energy": 85,
            "motif_type": "bell motif",
            "motif_presence": 75,
            "motif_behavior": "staccato",
            "harmony_mode": "phrygian",
            "harmony_complexity": 80,
            "bass_aggression": 75,
            "glitch_density": 90,
            "drum_intensity": 80,
            "atmosphere_depth": 55,
            "target_model": "udio"
        }
    },
    {
        "name": "Synthetic Memory",
        "bank": "BANK_F",
        "blueprint": {
            "genre": "ambient",
            "bpm": 60,
            "energy": 25,
            "motif_type": "choir pad",
            "motif_presence": 80,
            "motif_behavior": "soaring",
            "harmony_mode": "minor",
            "harmony_complexity": 85,
            "bass_aggression": 10,
            "glitch_density": 40,
            "drum_intensity": 10,
            "atmosphere_depth": 95,
            "target_model": "suno"
        }
    },
    {
        "name": "Digital Archaeology",
        "bank": "BANK_F",
        "blueprint": {
            "genre": "ambient",
            "bpm": 80,
            "energy": 50,
            "motif_type": "FM synth hook",
            "motif_presence": 65,
            "motif_behavior": "fragmenting",
            "harmony_mode": "dorian",
            "harmony_complexity": 70,
            "bass_aggression": 30,
            "glitch_density": 70,
            "drum_intensity": 20,
            "atmosphere_depth": 85,
            "target_model": "udio"
        }
    },
    {
        "name": "Electronica Ultima",
        "bank": "BANK_F",
        "blueprint": {
            "genre": "psycho_glitch_techno",
            "bpm": 128,
            "energy": 80,
            "motif_type": "vocal phrase",
            "motif_presence": 80,
            "motif_behavior": "repeating",
            "harmony_mode": "minor",
            "harmony_complexity": 65,
            "bass_aggression": 70,
            "glitch_density": 75,
            "drum_intensity": 75,
            "atmosphere_depth": 50,
            "target_model": "suno"
        }
    },
    {
        "name": "Machine Dream",
        "bank": "BANK_F",
        "blueprint": {
            "genre": "ambient",
            "bpm": 75,
            "energy": 30,
            "motif_type": "bell motif",
            "motif_presence": 70,
            "motif_behavior": "ascending",
            "harmony_mode": "phrygian",
            "harmony_complexity": 75,
            "bass_aggression": 20,
            "glitch_density": 30,
            "drum_intensity": 15,
            "atmosphere_depth": 92,
            "target_model": "udio"
        }
    }
]

def seed_database(db: Session = None, reset: bool = False):
    if reset:
        print("Reset flag active: dropping all tables and recreating schema...")
        Base.metadata.drop_all(bind=engine)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:

        existing_count = db.query(Preset).count()
        if existing_count == 0:
            print(f"Seeding {len(DEFAULT_PRESETS)} default presets into database...")
            for preset_data in DEFAULT_PRESETS:
                db_preset = Preset(
                    name=preset_data["name"],
                    bank=preset_data.get("bank", "BANK_A"),
                    blueprint_json=json.dumps(preset_data["blueprint"])
                )
                db.add(db_preset)
            db.commit()
            print("Seeding completed successfully.")
        else:
            print(f"Database already has {existing_count} presets. Skipping seed. (Use reset=True to force overwrite)")
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Sound Machina Presets")
    parser.add_argument("--reset", action="store_true", help="Reset/Wipe existing presets before seeding")
    args = parser.parse_args()
    seed_database(reset=args.reset)
