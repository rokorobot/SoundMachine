"""T11, T33, T28: additive migration preserves legacy rows, never guesses
ambiguous associations, and aborts before DDL if the backup gate fails."""
import sqlite3

import pytest

from app.database import make_engine, StartupError
from app.migrations import run_migrations, CURRENT_SCHEMA_VERSION
from tests.fixtures import build_legacy_db, build_ambiguous_legacy_db


def _counts(path):
    con = sqlite3.connect(str(path))
    try:
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("presets", "blueprint_snapshots", "generation_history")}
    finally:
        con.close()


def _columns(path, table):
    con = sqlite3.connect(str(path))
    try:
        return {r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()}
    finally:
        con.close()


def _table_exists(path, table):
    con = sqlite3.connect(str(path))
    try:
        return con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone() is not None
    finally:
        con.close()


# --- T11: migration preserves rows, adds columns, seeds lineages, is idempotent ---

def test_migration_preserves_rows_and_is_additive(tmp_path):
    db = tmp_path / "legacy.db"
    expected = build_legacy_db(db)
    before = _counts(db)
    assert before == expected

    engine = make_engine(db)
    report = run_migrations(engine, db_path=db, backup=True)

    after = _counts(db)
    assert after == before  # R35: no row added or removed
    # additive columns present
    assert {"lineage_key", "parent_snapshot_id", "origin_type", "origin_ref"} <= _columns(db, "blueprint_snapshots")
    assert {"artifacts_json", "engine_version"} <= _columns(db, "generation_history")
    assert _table_exists(db, "lineages")
    assert _table_exists(db, "schema_version")
    # legacy rows keep NULL lineage_key
    con = sqlite3.connect(str(db))
    try:
        nulls = con.execute("SELECT COUNT(*) FROM blueprint_snapshots WHERE lineage_key IS NULL").fetchone()[0]
        assert nulls == before["blueprint_snapshots"]
    finally:
        con.close()

    # idempotent re-run: no changes, no error
    report2 = run_migrations(engine, db_path=db, backup=True)
    assert report2["applied"] == []
    assert _counts(db) == before


def test_migration_creates_verified_backup(tmp_path):
    db = tmp_path / "legacy.db"
    build_legacy_db(db)
    engine = make_engine(db)
    run_migrations(engine, db_path=db, backup=True)
    assert (tmp_path / "legacy.db.pre-ws1.bak").exists()


def test_deterministic_legacy_association(tmp_path):
    db = tmp_path / "legacy.db"
    build_legacy_db(db)
    engine = make_engine(db)
    report = run_migrations(engine, db_path=db, backup=False)
    assert report["ambiguities"] == []
    con = sqlite3.connect(str(db))
    try:
        rows = dict(con.execute("SELECT key, preset_id FROM lineages").fetchall())
    finally:
        con.close()
    # PSYCH_TEC and COLD_SIGNAL uniquely match a preset; CUSTOM matches none.
    assert rows["legacy:PSYCH_TEC"] is not None
    assert rows["legacy:COLD_SIGNAL"] is not None
    assert rows["legacy:CUSTOM"] is None


# --- T33: ambiguous association is never guessed ---

def test_ambiguous_association_not_guessed(tmp_path):
    db = tmp_path / "ambiguous.db"
    build_ambiguous_legacy_db(db)
    engine = make_engine(db)
    report = run_migrations(engine, db_path=db, backup=False)
    assert "PSYCH_TEC" in report["ambiguities"]
    con = sqlite3.connect(str(db))
    try:
        preset_id = con.execute("SELECT preset_id FROM lineages WHERE key=?", ("legacy:PSYCH_TEC",)).fetchone()[0]
    finally:
        con.close()
    assert preset_id is None  # not guessed


# --- T28: backup failure aborts before any DDL ---

def test_backup_failure_aborts_before_ddl(tmp_path):
    db = tmp_path / "legacy.db"
    build_legacy_db(db)
    engine = make_engine(db)

    def failing_backup(_):
        raise StartupError("BACKUP_FAILED: simulated")

    with pytest.raises(StartupError):
        run_migrations(engine, db_path=db, backup=True, backup_fn=failing_backup)

    # schema untouched: no new columns, no new tables
    assert "lineage_key" not in _columns(db, "blueprint_snapshots")
    assert "artifacts_json" not in _columns(db, "generation_history")
    assert not _table_exists(db, "lineages")
    assert not _table_exists(db, "schema_version")


def test_existing_backup_not_overwritten(tmp_path):
    db = tmp_path / "legacy.db"
    build_legacy_db(db)
    bak = tmp_path / "legacy.db.pre-ws1.bak"
    # Pre-existing valid backup (a copy) with a sentinel mtime marker file.
    import shutil
    shutil.copyfile(db, bak)
    sentinel = bak.stat().st_mtime_ns
    engine = make_engine(db)
    run_migrations(engine, db_path=db, backup=True)
    # Not overwritten: same file, same mtime.
    assert bak.stat().st_mtime_ns == sentinel
