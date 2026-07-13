import sqlite3


def row_counts(db_path):
    con = sqlite3.connect(str(db_path))
    try:
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("presets", "blueprint_snapshots", "generation_history")}
    finally:
        con.close()


def first_preset(client):
    return client.get("/api/presets").json()[0]


def save_payload(blueprint, *, origin_type="custom", origin_ref=None,
                 lineage_key=None, display_name=None, parent_snapshot_id=None):
    return {
        "blueprint": blueprint,
        "lineage": {
            "lineage_key": lineage_key,
            "display_name": display_name,
            "origin_type": origin_type,
            "origin_ref": origin_ref,
            "parent_snapshot_id": parent_snapshot_id,
        },
    }


def a_blueprint(**over):
    base = dict(
        genre="psycho_glitch_techno", bpm=132, energy=90, motif_type="cathedral organ",
        motif_presence=50, motif_behavior="fragmenting", harmony_mode="minor",
        harmony_complexity=60, bass_aggression=80, glitch_density=95, drum_intensity=85,
        atmosphere_depth=40, target_model="suno",
    )
    base.update(over)
    return base
