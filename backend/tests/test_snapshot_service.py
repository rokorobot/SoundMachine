"""T5, T37, T25, T38: version-collision retry, unrelated-IntegrityError no-retry,
slug-collision discrimination, and lineage-key (uuid) collision handling."""
import pytest
from sqlalchemy.exc import IntegrityError

from app import snapshot_service as svc
from app.schemas import CompositionBlueprint, LineageInput
from app.errors import APIError
from tests.helpers import a_blueprint


def _bp(**over):
    return CompositionBlueprint(**a_blueprint(**over))


def _custom(display_name):
    return LineageInput(origin_type="custom", display_name=display_name)


# --- T5: a recognized version collision is retried and resolved ---

def test_version_collision_retries_to_unique(session, monkeypatch):
    first = svc.save_snapshot(session, _bp(), _custom("Retry"))
    assert first["version"] == 1

    calls = {"n": 0}
    real_next = svc._next_version

    def stale_then_real(db, lineage_row):
        calls["n"] += 1
        if calls["n"] == 1:
            return 1  # collide with the existing v1 (snapshot_id already taken)
        return real_next(db, lineage_row)

    monkeypatch.setattr(svc, "_next_version", stale_then_real)
    second = svc.save_snapshot(session, _bp(bpm=133),
                               LineageInput(origin_type="snapshot",
                                            origin_ref=first["snapshot_id"],
                                            parent_snapshot_id=first["snapshot_id"],
                                            lineage_key=first["lineage_key"]))
    assert second["version"] == 2  # retried past the collision
    assert calls["n"] >= 2


# --- T37: an unrelated IntegrityError is NOT blindly retried ---

def test_unrelated_integrity_error_not_retried(session, monkeypatch):
    calls = {"n": 0}
    real_next = svc._next_version

    def counting_next(db, lineage_row):
        calls["n"] += 1
        return real_next(db, lineage_row)

    monkeypatch.setattr(svc, "_next_version", counting_next)

    def boom():
        raise IntegrityError("stmt", {}, Exception("NOT NULL constraint failed: other.col"))

    monkeypatch.setattr(session, "commit", boom)
    with pytest.raises(APIError) as ei:
        svc.save_snapshot(session, _bp(), _custom("Unrelated"))
    assert ei.value.code == "INTERNAL"
    assert calls["n"] == 1  # single attempt, no retry loop


# --- T25: slug collision -> distinct keys, deterministic discriminator, no id clash ---

def test_slug_collision_discriminated(session):
    a = svc.save_snapshot(session, _bp(), _custom("Same Name"))
    b = svc.save_snapshot(session, _bp(bpm=140), _custom("Same Name"))
    assert a["lineage_key"] != b["lineage_key"]           # distinct stable identity
    assert a["snapshot_id"] == "SAME_NAME_0001"
    assert b["snapshot_id"] == "SAME_NAME_2_0001"         # deterministic _2 discriminator
    assert a["snapshot_id"] != b["snapshot_id"]


# --- T38: lineage-key (uuid) collision is retried with a fresh key ---

def test_lineage_key_collision_retries(session, monkeypatch):
    # First custom lineage, capture its key.
    a = svc.save_snapshot(session, _bp(), _custom("Alpha"))
    existing_key = a["lineage_key"]

    keys = iter([existing_key, "fresh-uuid-key-1234"])
    monkeypatch.setattr(svc, "new_lineage_key", lambda: next(keys))
    b = svc.save_snapshot(session, _bp(bpm=140), _custom("Beta"))
    assert b["lineage_key"] == "fresh-uuid-key-1234"      # retried past the duplicate key
    assert b["lineage_key"] != existing_key
