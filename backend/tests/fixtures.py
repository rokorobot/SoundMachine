"""Deterministic, sanitized legacy-schema fixtures (R33).

These build a PRE-WS1 schema SQLite database (old columns only, no lineages or
schema_version tables) populated with synthetic rows. The live database is never
used or copied here.
"""
import json
import sqlite3

# A valid blueprint within the known enum vocabulary.
LEGACY_BLUEPRINT = {
    "genre": "psycho_glitch_techno", "bpm": 132, "energy": 90,
    "motif_type": "cathedral organ", "motif_presence": 50, "motif_behavior": "fragmenting",
    "harmony_mode": "minor", "harmony_complexity": 60, "bass_aggression": 80,
    "glitch_density": 95, "drum_intensity": 85, "atmosphere_depth": 40, "target_model": "suno",
}
COLD_BLUEPRINT = {**LEGACY_BLUEPRINT, "genre": "coldwave", "bpm": 110, "glitch_density": 15,
                  "motif_type": "FM synth hook", "target_model": "udio"}

# Naive timestamps, exactly as the legacy code wrote them (datetime.utcnow, no tz).
_NAIVE_TS = "2026-05-28 23:00:30.000000"

_LEGACY_SCHEMA = """
CREATE TABLE presets (
    id INTEGER PRIMARY KEY, name TEXT UNIQUE, bank TEXT, blueprint_json TEXT NOT NULL,
    created_at DATETIME
);
CREATE TABLE blueprint_snapshots (
    id INTEGER PRIMARY KEY, snapshot_id TEXT UNIQUE, lineage_name TEXT, version INTEGER NOT NULL,
    parent_preset_id INTEGER, blueprint_json TEXT NOT NULL, created_at DATETIME
);
CREATE TABLE generation_history (
    id INTEGER PRIMARY KEY, snapshot_id TEXT, prompts_json TEXT NOT NULL, scores_json TEXT NOT NULL,
    created_at DATETIME
);
"""


def _history_payload():
    prompts = {
        "suno": {"style_tags": "psycho glitch techno, 132bpm, instrumental",
                 "prompt_body": "[Intro]\n[End]", "negative_prompt": "vocals, singing"},
        "udio": {"tags": "psycho glitch techno, electronic, 132 bpm",
                 "prompt_body": "[Instrumental Intro]", "negative_prompt": "vocals, voice, singing"},
        "active_target": "suno",
    }
    scores = {"overall": 90, "motif_clarity": 86, "genre_focus": 92,
              "prompt_density": 90, "model_compatibility": 94, "negative_prompt_quality": 92}
    return json.dumps(prompts), json.dumps(scores)


def _insert_snapshot(cur, snap_id, lineage, version, blueprint):
    cur.execute(
        "INSERT INTO blueprint_snapshots (snapshot_id, lineage_name, version, parent_preset_id, "
        "blueprint_json, created_at) VALUES (?,?,?,?,?,?)",
        (snap_id, lineage, version, None, json.dumps(blueprint), _NAIVE_TS),
    )
    prompts_json, scores_json = _history_payload()
    cur.execute(
        "INSERT INTO generation_history (snapshot_id, prompts_json, scores_json, created_at) "
        "VALUES (?,?,?,?)",
        (snap_id, prompts_json, scores_json, _NAIVE_TS),
    )


def build_legacy_db(path):
    """A clean legacy DB: PSYCH_TEC (uniquely matches a preset), COLD_SIGNAL
    (uniquely matches a preset), and CUSTOM (matches no preset)."""
    con = sqlite3.connect(str(path))
    try:
        con.executescript(_LEGACY_SCHEMA)
        cur = con.cursor()
        cur.execute("INSERT INTO presets (name, bank, blueprint_json, created_at) VALUES (?,?,?,?)",
                    ("Psych Tec", "BANK_A", json.dumps(LEGACY_BLUEPRINT), _NAIVE_TS))
        cur.execute("INSERT INTO presets (name, bank, blueprint_json, created_at) VALUES (?,?,?,?)",
                    ("Cold Signal", "BANK_A", json.dumps(COLD_BLUEPRINT), _NAIVE_TS))
        _insert_snapshot(cur, "PSYCH_TEC_0001", "PSYCH_TEC", 1, LEGACY_BLUEPRINT)
        _insert_snapshot(cur, "PSYCH_TEC_0002", "PSYCH_TEC", 2, LEGACY_BLUEPRINT)
        _insert_snapshot(cur, "COLD_SIGNAL_0001", "COLD_SIGNAL", 1, COLD_BLUEPRINT)
        _insert_snapshot(cur, "CUSTOM_0001", "CUSTOM", 1, LEGACY_BLUEPRINT)
        con.commit()
    finally:
        con.close()
    return {"presets": 2, "blueprint_snapshots": 4, "generation_history": 4}


def build_ambiguous_legacy_db(path):
    """Two presets sanitize to the same slug 'PSYCH_TEC' as a legacy lineage
    name -> association must NOT be guessed (T33)."""
    con = sqlite3.connect(str(path))
    try:
        con.executescript(_LEGACY_SCHEMA)
        cur = con.cursor()
        cur.execute("INSERT INTO presets (name, bank, blueprint_json, created_at) VALUES (?,?,?,?)",
                    ("Psych Tec", "BANK_A", json.dumps(LEGACY_BLUEPRINT), _NAIVE_TS))
        cur.execute("INSERT INTO presets (name, bank, blueprint_json, created_at) VALUES (?,?,?,?)",
                    ("Psych  Tec", "BANK_B", json.dumps(LEGACY_BLUEPRINT), _NAIVE_TS))
        _insert_snapshot(cur, "PSYCH_TEC_0001", "PSYCH_TEC", 1, LEGACY_BLUEPRINT)
        con.commit()
    finally:
        con.close()
    return {"presets": 2, "blueprint_snapshots": 1, "generation_history": 1}
