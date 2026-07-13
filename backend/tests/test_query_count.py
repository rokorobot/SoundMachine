"""T8 (contract completion): the paginated snapshot list must not issue a
per-row query. Instruments actual executed SQL and asserts the SELECT count is
fixed and independent of the number of rows returned."""
from sqlalchemy import event

from app import database
from tests.helpers import save_payload, a_blueprint


def _count_selects_during_get(client, path):
    counter = {"n": 0}

    def before(conn, cursor, statement, params, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            counter["n"] += 1

    event.listen(database.engine, "before_cursor_execute", before)
    try:
        resp = client.get(path)
    finally:
        event.remove(database.engine, "before_cursor_execute", before)
    assert resp.status_code == 200
    return counter["n"], resp.json()


def _make_snapshots(client, n, tag):
    for i in range(n):
        r = client.post("/api/snapshots", json=save_payload(a_blueprint(bpm=120 + i), display_name=f"{tag}{i}"))
        assert r.status_code == 200, r.text


def test_snapshot_list_query_count_is_row_independent(client):
    _make_snapshots(client, 3, "Q")
    n_small, page_small = _count_selects_during_get(client, "/api/snapshots?limit=50")
    assert len(page_small["items"]) == 3

    _make_snapshots(client, 6, "R")  # now 9 total
    n_large, page_large = _count_selects_during_get(client, "/api/snapshots?limit=50")
    assert len(page_large["items"]) == 9

    # No N+1: returning 3x the rows must not change the query count.
    assert n_small == n_large, f"query count grew with rows: {n_small} -> {n_large}"
    # Fixed small bound: one list query + one count query (allow slack, never O(rows)).
    assert n_large <= 3, f"expected a fixed small query count, got {n_large}"


def test_snapshot_list_pagination_query_count_stable(client):
    _make_snapshots(client, 8, "P")
    n_page1, page1 = _count_selects_during_get(client, "/api/snapshots?limit=3")
    assert len(page1["items"]) == 3
    n_page2, _ = _count_selects_during_get(client, f"/api/snapshots?limit=3&before_id={page1['next_cursor']}")
    # Each page costs the same fixed number of queries regardless of page.
    assert n_page1 == n_page2
    assert n_page1 <= 3
