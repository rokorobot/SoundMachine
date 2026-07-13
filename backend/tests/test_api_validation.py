"""C1, T35, T36, T10: origin/ancestry integrity, cross-lineage rejection,
malformed origins, and typed operator-safe errors. Every rejection is zero-write."""
from tests.helpers import row_counts, save_payload, a_blueprint


def _snapshot(client, **kw):
    return client.post("/api/snapshots", json=save_payload(a_blueprint(), **kw)).json()


def _assert_zero_write_rejection(client, payload, status, code):
    before = row_counts(client.db_path)
    r = client.post("/api/snapshots", json=payload)
    assert r.status_code == status, r.text
    assert r.json()["error"]["code"] == code
    assert row_counts(client.db_path) == before  # zero writes


# --- C1: snapshot-origin lineage integrity ---

def test_c1_missing_lineage_key_rejected(client):
    s1 = _snapshot(client, display_name="C1a")
    payload = save_payload(a_blueprint(bpm=133), origin_type="snapshot",
                           origin_ref=s1["snapshot_id"], parent_snapshot_id=s1["snapshot_id"],
                           lineage_key=None)
    _assert_zero_write_rejection(client, payload, 409, "LINEAGE_REQUIRED")


def test_c1_mismatched_lineage_key_rejected(client):
    s1 = _snapshot(client, display_name="C1b")
    payload = save_payload(a_blueprint(bpm=133), origin_type="snapshot",
                           origin_ref=s1["snapshot_id"], parent_snapshot_id=s1["snapshot_id"],
                           lineage_key="legacy:SOMETHING_ELSE")
    _assert_zero_write_rejection(client, payload, 409, "PARENT_LINEAGE_MISMATCH")


def test_c1_nonexistent_parent_rejected(client):
    payload = save_payload(a_blueprint(), origin_type="snapshot",
                           origin_ref="GHOST_9999", parent_snapshot_id="GHOST_9999",
                           lineage_key="legacy:GHOST")
    _assert_zero_write_rejection(client, payload, 409, "PARENT_NOT_FOUND")


def test_c1_valid_derived_lineage_succeeds(client):
    s1 = _snapshot(client, display_name="C1d")
    r = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=133), origin_type="snapshot", origin_ref=s1["snapshot_id"],
        parent_snapshot_id=s1["snapshot_id"], lineage_key=s1["lineage_key"]))
    assert r.status_code == 200
    assert r.json()["lineage_key"] == s1["lineage_key"]


# --- T35: cross-lineage parent rejected ---

def test_t35_cross_lineage_parent_rejected(client):
    l1 = _snapshot(client, display_name="LineageOne")
    l2 = _snapshot(client, display_name="LineageTwo")
    assert l1["lineage_key"] != l2["lineage_key"]
    # parent is l2's snapshot but we claim l1's lineage
    payload = save_payload(a_blueprint(bpm=133), origin_type="snapshot",
                           origin_ref=l2["snapshot_id"], parent_snapshot_id=l2["snapshot_id"],
                           lineage_key=l1["lineage_key"])
    _assert_zero_write_rejection(client, payload, 409, "PARENT_LINEAGE_MISMATCH")


# --- T36: malformed origin matrix ---

def test_t36_preset_origin_nonexistent(client):
    _assert_zero_write_rejection(
        client, save_payload(a_blueprint(), origin_type="preset", origin_ref="99999"),
        422, "ORIGIN_INVALID")


def test_t36_preset_origin_non_integer(client):
    _assert_zero_write_rejection(
        client, save_payload(a_blueprint(), origin_type="preset", origin_ref="abc"),
        422, "ORIGIN_INVALID")


def test_t36_snapshot_origin_missing_ref(client):
    _assert_zero_write_rejection(
        client, save_payload(a_blueprint(), origin_type="snapshot", origin_ref=None,
                             parent_snapshot_id=None),
        422, "ORIGIN_INVALID")


def test_t36_custom_origin_with_ref(client):
    _assert_zero_write_rejection(
        client, save_payload(a_blueprint(), origin_type="custom", origin_ref="12"),
        422, "ORIGIN_INVALID")


def test_t36_preset_origin_with_parent(client):
    s1 = _snapshot(client, display_name="X")
    preset = client.get("/api/presets").json()[0]
    _assert_zero_write_rejection(
        client, save_payload(a_blueprint(), origin_type="preset", origin_ref=str(preset["id"]),
                             parent_snapshot_id=s1["snapshot_id"]),
        422, "ORIGIN_PARENT_MISMATCH")


def test_t36_snapshot_origin_ref_ne_parent(client):
    s1 = _snapshot(client, display_name="Y")
    s2 = _snapshot(client, display_name="Z")
    _assert_zero_write_rejection(
        client, save_payload(a_blueprint(), origin_type="snapshot", origin_ref=s1["snapshot_id"],
                             parent_snapshot_id=s2["snapshot_id"], lineage_key=s1["lineage_key"]),
        422, "ORIGIN_PARENT_MISMATCH")


# --- T10: typed errors, no tracebacks ---

def test_t10_validation_error_typed(client):
    before = row_counts(client.db_path)
    bad = a_blueprint(genre="trance")  # unknown enum
    r = client.post("/api/snapshots", json=save_payload(bad))
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "VALIDATION_FAILED"
    assert "Traceback" not in body["error"]["message"]
    assert row_counts(client.db_path) == before


def test_t10_not_found_typed(client):
    r = client.get("/api/snapshots/DOES_NOT_EXIST_0001")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "SNAPSHOT_NOT_FOUND"
