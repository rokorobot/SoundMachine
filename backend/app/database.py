"""Database configuration, ORM models, and CWD-independent path resolution.

Importing this module has NO side effects: no connection is opened, no schema
is created, no database file is written. The engine/session are bound lazily
via ``configure()`` (called at app startup or explicitly by tests), so importing
the app can never touch the live database (the R32 footgun).
"""
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


class StartupError(RuntimeError):
    """Raised for unrecoverable startup misconfiguration (C2 / R32)."""


# R43: anchor is executable, not prose. This file is backend/app/database.py,
# so parents[1] is backend/ and the default DB is backend/sound_machina.db.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = _BACKEND_DIR / "sound_machina.db"


def resolve_db_path(env=None, cwd=None, default_path=None):
    """Resolve the active database path.

    C2: ``SOUND_MACHINA_DB`` must be absolute; a relative value is a blocking
    error and is never resolved relative to the process CWD.
    R32: when using the anchored default, refuse to silently pick between a
    populated CWD-relative database and the anchored path.
    """
    env = os.environ if env is None else env
    cwd = Path.cwd() if cwd is None else Path(cwd)
    default_path = DEFAULT_DB_PATH if default_path is None else Path(default_path)

    raw = env.get("SOUND_MACHINA_DB")
    if raw:
        p = Path(raw)
        if not p.is_absolute():
            raise StartupError(
                f"SOUND_MACHINA_DB must be an absolute path; got relative value {raw!r}. "
                "Provide an absolute path or unset the variable to use the anchored default."
            )
        return p.resolve()

    default_resolved = default_path.resolve()
    legacy_cwd_path = cwd / "sound_machina.db"
    legacy_cwd_resolved = legacy_cwd_path.resolve()

    if legacy_cwd_resolved != default_resolved:
        default_exists = default_path.exists()
        legacy_exists = legacy_cwd_path.exists()
        if default_exists and legacy_exists:
            raise StartupError(
                "DB_AMBIGUOUS: two candidate databases exist:\n"
                f"  anchored: {default_resolved}\n"
                f"  cwd:      {legacy_cwd_resolved}\n"
                "Set SOUND_MACHINA_DB to the absolute path of the intended database."
            )
        if legacy_exists and not default_exists:
            raise StartupError(
                "DB_AMBIGUOUS: a database exists at the CWD-relative path but not the anchored path:\n"
                f"  cwd:      {legacy_cwd_resolved}\n"
                f"  anchored: {default_resolved}\n"
                "Move it to the anchored path or set SOUND_MACHINA_DB to its absolute path."
            )
    return default_path


def db_url_for(path):
    return f"sqlite:///{Path(path).as_posix()}"


def make_engine(path):
    return create_engine(db_url_for(path), connect_args={"check_same_thread": False})


Base = declarative_base()


def _utcnow():
    return datetime.now(timezone.utc)


class Preset(Base):
    __tablename__ = "presets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    bank = Column(String, default="BANK_A", index=True)
    blueprint_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)


class BlueprintSnapshot(Base):
    __tablename__ = "blueprint_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String, unique=True, index=True)
    lineage_name = Column(String, index=True)
    version = Column(Integer, nullable=False)
    parent_preset_id = Column(Integer, nullable=True)
    blueprint_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    # WS1 additive columns (NULL on legacy rows).
    lineage_key = Column(String, nullable=True, index=True)
    parent_snapshot_id = Column(String, nullable=True)
    origin_type = Column(String, nullable=True)   # 'preset' | 'snapshot' | 'custom'
    origin_ref = Column(String, nullable=True)    # preset id (str) | snapshot_id | NULL


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String, index=True)
    prompts_json = Column(Text, nullable=False)
    scores_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    # WS1 additive columns (NULL on legacy rows).
    artifacts_json = Column(Text, nullable=True)   # {motif_block, arrangement_timeline, recommendations}
    engine_version = Column(String, nullable=True)


class Lineage(Base):
    __tablename__ = "lineages"

    key = Column(String, primary_key=True)          # uuid4 str, or 'legacy:<NAME>'
    display_name = Column(String, nullable=False)   # human-readable; NOT relational identity
    slug = Column(String, nullable=False, unique=True)
    preset_id = Column(Integer, nullable=True, unique=True)
    created_at = Column(DateTime, default=_utcnow)


class SchemaVersion(Base):
    __tablename__ = "schema_version"

    version = Column(Integer, primary_key=True)
    applied_at = Column(DateTime, default=_utcnow)


# Runtime-bound engine/session; bound lazily so import stays side-effect-free.
engine = None
SessionLocal = None
DB_PATH = None


def configure(path=None, *, env=None, cwd=None):
    """Bind the module-level engine/SessionLocal. Idempotent; safe to re-call."""
    global engine, SessionLocal, DB_PATH
    if path is None:
        path = resolve_db_path(env=env, cwd=cwd)
    DB_PATH = Path(path)
    engine = make_engine(path)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def get_db():
    if SessionLocal is None:
        configure()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
