"""T39 + C2 + T27: database path resolution, absolute-only env override,
CWD independence, and ambiguity detection. No live database is touched."""
import os

import pytest

from app.database import resolve_db_path, DEFAULT_DB_PATH, StartupError


# --- T39 / R43: default anchor is CWD-independent and points at backend/sound_machina.db ---

def test_default_anchor_points_at_backend_db():
    # database.py lives at backend/app/database.py; parents[1] == backend/
    assert DEFAULT_DB_PATH.name == "sound_machina.db"
    assert DEFAULT_DB_PATH.parent.name == "backend"
    assert DEFAULT_DB_PATH.parent.parent.name == "Sound Machine" or DEFAULT_DB_PATH.parent.name == "backend"


def test_default_resolution_is_cwd_independent(tmp_path):
    a = resolve_db_path(env={}, cwd=tmp_path / "cwd_a")
    b = resolve_db_path(env={}, cwd=tmp_path / "cwd_b")
    c = resolve_db_path(env={}, cwd=tmp_path / "another")
    # All three must resolve to the identical anchored default.
    assert a == b == c == DEFAULT_DB_PATH


# --- C2-a: absolute override honored ---

def test_absolute_env_override_honored(tmp_path):
    target = (tmp_path / "custom.db").resolve()
    got = resolve_db_path(env={"SOUND_MACHINA_DB": str(target)}, cwd=tmp_path)
    assert got == target


# --- C2-b: relative override rejected, never CWD-resolved ---

def test_relative_env_override_rejected(tmp_path):
    with pytest.raises(StartupError):
        resolve_db_path(env={"SOUND_MACHINA_DB": "relative/sound_machina.db"}, cwd=tmp_path)


def test_bare_relative_env_override_rejected(tmp_path):
    with pytest.raises(StartupError):
        resolve_db_path(env={"SOUND_MACHINA_DB": "sound_machina.db"}, cwd=tmp_path)


# --- T27 / R32 / C2-c: ambiguity detection, never a silent second empty DB ---

def test_ambiguity_both_default_and_cwd_exist(tmp_path):
    default = tmp_path / "anchored" / "sound_machina.db"
    default.parent.mkdir(parents=True)
    default.write_bytes(b"x")  # populated candidate
    foreign_cwd = tmp_path / "elsewhere"
    foreign_cwd.mkdir()
    (foreign_cwd / "sound_machina.db").write_bytes(b"y")  # second candidate
    with pytest.raises(StartupError):
        resolve_db_path(env={}, cwd=foreign_cwd, default_path=default)


def test_ambiguity_only_foreign_cwd_db_exists(tmp_path):
    default = tmp_path / "anchored" / "sound_machina.db"  # does not exist
    foreign_cwd = tmp_path / "elsewhere"
    foreign_cwd.mkdir()
    (foreign_cwd / "sound_machina.db").write_bytes(b"y")
    with pytest.raises(StartupError):
        resolve_db_path(env={}, cwd=foreign_cwd, default_path=default)


def test_fresh_install_when_neither_exists(tmp_path):
    default = tmp_path / "anchored" / "sound_machina.db"  # does not exist
    foreign_cwd = tmp_path / "elsewhere"
    foreign_cwd.mkdir()  # no db here
    got = resolve_db_path(env={}, cwd=foreign_cwd, default_path=default)
    assert got == default  # will be created fresh, not aborted


def test_no_ambiguity_when_cwd_equals_anchor(tmp_path):
    anchor_dir = tmp_path / "backend"
    anchor_dir.mkdir()
    default = anchor_dir / "sound_machina.db"
    default.write_bytes(b"x")
    # Running from the anchor dir: cwd path == default path, so no conflict.
    got = resolve_db_path(env={}, cwd=anchor_dir, default_path=default)
    assert got == default
