"""Versioned additive migration runner with a verified pre-migration backup gate.

Guarantees (R31/R32/R35):
- No schema change occurs until a verified backup exists (for existing data DBs).
- Every step is additive and idempotent; legacy rows are never rewritten.
- Legacy lineage association is deterministic-or-nothing (R39): a legacy lineage
  is linked to a preset only on a unique, unambiguous match; ambiguities are
  reported, never guessed.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.database import Base, StartupError
from app.lineage import sanitize_slug


def _dt_str():
    # Matches SQLAlchemy's SQLite DateTime storage format so ORM reads parse it.
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")


def _table_exists(conn, table):
    row = conn.exec_driver_sql(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def _columns(conn, table):
    return {r[1] for r in conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()}


def _index_exists(conn, name):
    row = conn.exec_driver_sql(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?", (name,)
    ).fetchone()
    return row is not None


# --- individual additive steps (each idempotent) ---

def _step_snapshot_columns(conn):
    cols = _columns(conn, "blueprint_snapshots")
    for name in ("lineage_key", "parent_snapshot_id", "origin_type", "origin_ref"):
        if name not in cols:
            conn.exec_driver_sql(f"ALTER TABLE blueprint_snapshots ADD COLUMN {name} TEXT")


def _step_history_columns(conn):
    cols = _columns(conn, "generation_history")
    for name in ("artifacts_json", "engine_version"):
        if name not in cols:
            conn.exec_driver_sql(f"ALTER TABLE generation_history ADD COLUMN {name} TEXT")


def _step_unique_index(conn):
    if not _index_exists(conn, "ux_snapshots_lineagekey_version"):
        conn.exec_driver_sql(
            "CREATE UNIQUE INDEX ux_snapshots_lineagekey_version "
            "ON blueprint_snapshots(lineage_key, version)"
        )


def _step_associate_legacy_lineages(conn):
    """Return the list of legacy lineage names that could not be uniquely
    associated (ambiguous). Never guesses."""
    ambiguities = []
    names = [
        r[0] for r in conn.exec_driver_sql(
            "SELECT DISTINCT lineage_name FROM blueprint_snapshots WHERE lineage_key IS NULL"
        ).fetchall()
    ]
    presets = conn.exec_driver_sql("SELECT id, name FROM presets").fetchall()
    slug_to_presets = {}
    for pid, pname in presets:
        slug_to_presets.setdefault(sanitize_slug(pname), []).append(pid)

    for name in names:
        if name is None:
            continue
        key = "legacy:" + name
        if conn.exec_driver_sql("SELECT 1 FROM lineages WHERE key=?", (key,)).fetchone():
            continue  # idempotent
        matches = slug_to_presets.get(name, [])
        preset_id = None
        if len(matches) == 1:
            claimed = conn.exec_driver_sql(
                "SELECT 1 FROM lineages WHERE preset_id=?", (matches[0],)
            ).fetchone()
            if claimed:
                ambiguities.append(name)
            else:
                preset_id = matches[0]
        elif len(matches) > 1:
            ambiguities.append(name)
        conn.exec_driver_sql(
            "INSERT INTO lineages (key, display_name, slug, preset_id, created_at) "
            "VALUES (?,?,?,?,?)",
            (key, name, name, preset_id, _dt_str()),
        )
    return ambiguities


# version -> (name, fn)
STEPS = [
    (1, "snapshot_columns", _step_snapshot_columns),
    (2, "history_columns", _step_history_columns),
    (3, "unique_index", _step_unique_index),
    (4, "associate_legacy_lineages", _step_associate_legacy_lineages),
]
CURRENT_SCHEMA_VERSION = max(v for v, _, _ in STEPS)


def _current_version(conn):
    if not _table_exists(conn, "schema_version"):
        return 0
    row = conn.exec_driver_sql("SELECT MAX(version) FROM schema_version").fetchone()
    return (row[0] or 0) if row else 0


def _stamp(conn, version):
    conn.exec_driver_sql(
        "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
        (version, _dt_str()),
    )


def verify_backup(src_path, bak_path):
    """Backup is valid iff it passes integrity_check and row counts match src."""
    con = sqlite3.connect(str(bak_path))
    try:
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            return False
        srccon = sqlite3.connect(f"file:{Path(src_path).as_posix()}?mode=ro", uri=True)
        try:
            for t in ("presets", "blueprint_snapshots", "generation_history"):
                bak_n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                src_n = srccon.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                if bak_n != src_n:
                    return False
        finally:
            srccon.close()
        return True
    finally:
        con.close()


def create_verified_backup(db_path):
    """Create (if absent) and verify a one-time pre-migration backup.
    Never overwrites an existing backup. Raises StartupError on failure."""
    src = Path(db_path)
    bak = src.with_name(src.name + ".pre-ws1.bak")
    if not bak.exists():
        srccon = sqlite3.connect(str(src))
        dstcon = sqlite3.connect(str(bak))
        try:
            with dstcon:
                srccon.backup(dstcon)
        finally:
            dstcon.close()
            srccon.close()
    if not verify_backup(src, bak):
        raise StartupError(f"BACKUP_FAILED: verification of backup {bak} failed; schema unchanged.")
    return bak


def run_migrations(engine, *, db_path=None, backup=True, backup_fn=None):
    """Apply pending additive migrations. For an existing data database, a
    verified backup is created before ANY DDL; if it fails, the schema is left
    untouched. Returns a report dict."""
    report = {"applied": [], "ambiguities": [], "backed_up": False, "fresh": False}

    with engine.connect() as conn:
        has_schema_version = _table_exists(conn, "schema_version")
        has_data_tables = _table_exists(conn, "blueprint_snapshots")

    # Brand-new database: build current schema and stamp; nothing to back up.
    if not has_schema_version and not has_data_tables:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            for v, _, _ in STEPS:
                _stamp(conn, v)
        report["fresh"] = True
        return report

    applied = 0
    if has_schema_version:
        with engine.connect() as conn:
            applied = _current_version(conn)

    pending = [s for s in STEPS if s[0] > applied]
    if not pending:
        return report

    # Backup gate BEFORE any DDL (R31).
    if backup and db_path is not None:
        (backup_fn or create_verified_backup)(db_path)
        report["backed_up"] = True

    # Safe to change schema now: create the new tables, then apply steps.
    Base.metadata.create_all(bind=engine)
    for version, name, fn in pending:
        with engine.begin() as conn:
            result = fn(conn)
            _stamp(conn, version)
        report["applied"].append(name)
        if name == "associate_legacy_lineages" and result:
            report["ambiguities"] = result
    return report
