"""T2 + T10 + T12: enum validation, legacy-fixture parse compatibility, and
Z-suffixed UTC timestamp serialization."""
import json
import sqlite3
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import CompositionBlueprint, iso_z
from tests.fixtures import build_legacy_db


def test_valid_blueprint_accepts_known_vocabulary():
    bp = CompositionBlueprint(
        genre="ambient", bpm=75, energy=20, motif_type="choir pad", motif_presence=60,
        motif_behavior="soaring", harmony_mode="major", harmony_complexity=70,
        bass_aggression=10, glitch_density=10, drum_intensity=5, atmosphere_depth=95,
        target_model="udio",
    )
    assert bp.genre == "ambient"


@pytest.mark.parametrize("field,bad", [
    ("genre", "trance"),
    ("motif_type", "kazoo"),
    ("motif_behavior", "wobbling"),
    ("harmony_mode", "lydian"),
    ("target_model", "riffusion"),
])
def test_unknown_enum_rejected(field, bad):
    good = dict(
        genre="ambient", bpm=75, energy=20, motif_type="choir pad", motif_presence=60,
        motif_behavior="soaring", harmony_mode="major", harmony_complexity=70,
        bass_aggression=10, glitch_density=10, drum_intensity=5, atmosphere_depth=95,
        target_model="udio",
    )
    good[field] = bad
    with pytest.raises(ValidationError):
        CompositionBlueprint(**good)


def test_all_legacy_fixture_blueprints_parse(tmp_path):
    db = tmp_path / "legacy.db"
    build_legacy_db(db)
    con = sqlite3.connect(str(db))
    try:
        blobs = [r[0] for r in con.execute("SELECT blueprint_json FROM presets").fetchall()]
        blobs += [r[0] for r in con.execute("SELECT blueprint_json FROM blueprint_snapshots").fetchall()]
    finally:
        con.close()
    for blob in blobs:
        CompositionBlueprint(**json.loads(blob))  # must not raise


def test_iso_z_serializes_utc_with_z():
    aware = datetime(2026, 7, 13, 10, 8, 2, tzinfo=timezone.utc)
    naive = datetime(2026, 7, 13, 10, 8, 2)  # legacy naive, defined as UTC
    assert iso_z(aware).endswith("Z")
    assert iso_z(naive).endswith("Z")
    assert iso_z(aware) == iso_z(naive)
