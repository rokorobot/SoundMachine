import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A TestClient backed by an isolated temporary database. The live database
    is never touched (SOUND_MACHINA_DB points at a temp file)."""
    dbfile = tmp_path / "test.db"
    monkeypatch.setenv("SOUND_MACHINA_DB", str(dbfile))
    from app import database
    database.engine = None
    database.SessionLocal = None
    database.DB_PATH = None
    from app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        c.db_path = dbfile
        yield c


@pytest.fixture
def session(tmp_path, monkeypatch):
    """A DB session over a fresh temp database (service-level tests)."""
    dbfile = tmp_path / "svc.db"
    monkeypatch.setenv("SOUND_MACHINA_DB", str(dbfile))
    from app import database
    database.engine = None
    database.SessionLocal = None
    database.DB_PATH = None
    engine = database.configure(dbfile)
    from app.migrations import run_migrations
    run_migrations(engine, db_path=dbfile, backup=False)
    from app.seed import seed_if_empty
    seed_if_empty(database.SessionLocal)
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def legacy_client(tmp_path, monkeypatch):
    """A TestClient over a MIGRATED legacy database (legacy rows lack stored
    motif/timeline artifacts). Built from a sanitized fixture, never the live DB."""
    from tests.fixtures import build_legacy_db
    dbfile = tmp_path / "legacy.db"
    build_legacy_db(dbfile)
    monkeypatch.setenv("SOUND_MACHINA_DB", str(dbfile))
    from app import database
    database.engine = None
    database.SessionLocal = None
    database.DB_PATH = None
    from app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        c.db_path = dbfile
        yield c
