"""H1 / T10 / R41: request-level typed-500 coverage.

Drives a real HTTP request through the app's actual routing and exception
handling, forces an *unexpected* internal exception in a read path via a
narrowly scoped monkeypatch, and asserts the catch-all handler converts it into
the standard typed error envelope with a safe public message and zero internal
leakage. The live database is never touched (isolated temp DB per test)."""
from fastapi.testclient import TestClient
import pytest

from tests.helpers import row_counts


@pytest.fixture
def client_raise_off(tmp_path, monkeypatch):
    """Like the shared ``client`` fixture, but with ``raise_server_exceptions``
    disabled so an unhandled exception is converted into the app's own HTTP 500
    response instead of being re-raised into the test process. Backed by an
    isolated temp database (SOUND_MACHINA_DB), never the live database."""
    dbfile = tmp_path / "internal_err.db"
    monkeypatch.setenv("SOUND_MACHINA_DB", str(dbfile))
    from app import database
    database.engine = None
    database.SessionLocal = None
    database.DB_PATH = None
    from app.main import create_app
    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as c:
        c.db_path = dbfile
        yield c


def test_unexpected_internal_error_returns_typed_500(client_raise_off, monkeypatch):
    before = row_counts(client_raise_off.db_path)

    # Narrowly scoped injection: replace the read service the route calls with
    # one that raises an *unexpected* error. The message is deliberately packed
    # with sensitive-looking tokens so we can prove none of them reach the client.
    import app.api.routes_history as routes_history
    sentinel = "boom SECRET_TOKEN=hunter2 path=/etc/passwd sql=SELECT * FROM presets"

    def _explode(*args, **kwargs):
        raise RuntimeError(sentinel)

    monkeypatch.setattr(routes_history, "list_snapshots", _explode)

    r = client_raise_off.get("/api/snapshots")

    # Real routing + real exception handling produced a typed 500 envelope.
    assert r.status_code == 500, r.text
    assert r.json() == {"error": {"code": "INTERNAL", "message": "Internal server error"}}

    body = r.json()
    assert body["error"]["code"] == "INTERNAL"          # expected INTERNAL code
    assert body["error"]["message"] == "Internal server error"  # safe public message

    # No traceback, exception class, filesystem path, SQL, secret, module/file
    # name, or the raw exception message may leak into the response body.
    raw = r.text
    for leak in (
        "Traceback", "RuntimeError", "boom", "SECRET_TOKEN", "hunter2",
        "/etc/passwd", "SELECT", "routes_history", ".py", sentinel,
    ):
        assert leak not in raw, f"leaked internal detail: {leak!r}"

    # The failed request performed no persistence write.
    assert row_counts(client_raise_off.db_path) == before
