"""Lifecycle API invariants: preview zero-writes, atomic save, parent chains,
pagination, immutability, recommendations round-trip."""
from tests.helpers import row_counts, first_preset, save_payload, a_blueprint


def test_root_online(client):
    assert client.get("/").json()["status"] == "online"


# --- T3: preview performs zero DB writes ---

def test_preview_zero_writes(client):
    before = row_counts(client.db_path)
    r = client.post("/api/preview", json={**a_blueprint(), "client_revision": 7})
    assert r.status_code == 200
    body = r.json()
    assert body["client_revision"] == 7
    assert set(body) >= {"prompts", "motif_block", "arrangement_timeline", "scores", "recommendations"}
    assert row_counts(client.db_path) == before  # nothing persisted


# --- T4: save creates exactly 1+1 rows with artifacts + engine_version ---

def test_save_creates_one_snapshot_one_history(client):
    before = row_counts(client.db_path)
    r = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="My Project"))
    assert r.status_code == 200, r.text
    rec = r.json()
    after = row_counts(client.db_path)
    assert after["blueprint_snapshots"] == before["blueprint_snapshots"] + 1
    assert after["generation_history"] == before["generation_history"] + 1
    assert rec["version"] == 1
    assert rec["parent_snapshot_id"] is None
    assert rec["engine_version"] == "1.0.0-ws1"
    assert rec["artifacts_provenance"] == "STORED"
    assert rec["recommendations"] is not None
    assert rec["created_at"].endswith("Z")


# --- T21: sequential saves form a linear parent chain ---

def test_sequential_parent_chain(client):
    # s1: custom root
    s1 = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="Chain")).json()
    assert s1["parent_snapshot_id"] is None
    # s2: descends from s1 (snapshot origin)
    s2 = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=133), origin_type="snapshot", origin_ref=s1["snapshot_id"],
        lineage_key=s1["lineage_key"], parent_snapshot_id=s1["snapshot_id"])).json()
    # s3: descends from s2
    s3 = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=134), origin_type="snapshot", origin_ref=s2["snapshot_id"],
        lineage_key=s2["lineage_key"], parent_snapshot_id=s2["snapshot_id"])).json()

    assert s1["lineage_key"] == s2["lineage_key"] == s3["lineage_key"]
    assert [s1["version"], s2["version"], s3["version"]] == [1, 2, 3]
    assert s3["parent_snapshot_id"] == s2["snapshot_id"]
    assert s2["parent_snapshot_id"] == s1["snapshot_id"]
    assert s1["parent_snapshot_id"] is None


# --- restore-then-branch (sequence B): child of an older snapshot ---

def test_restore_branch_from_older_snapshot(client):
    s1 = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="Branchy")).json()
    s2 = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=133), origin_type="snapshot", origin_ref=s1["snapshot_id"],
        lineage_key=s1["lineage_key"], parent_snapshot_id=s1["snapshot_id"])).json()
    # Branch off s1 (not the newest s2)
    s3 = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=140), origin_type="snapshot", origin_ref=s1["snapshot_id"],
        lineage_key=s1["lineage_key"], parent_snapshot_id=s1["snapshot_id"])).json()
    assert s3["parent_snapshot_id"] == s1["snapshot_id"]  # branch from s1
    assert s3["version"] == 3  # dense version, independent of ancestry
    assert s3["lineage_key"] == s1["lineage_key"]


# --- T32: repeated saves from one preset reuse one stable lineage ---

def test_preset_lineage_is_stable(client):
    preset = first_preset(client)
    a = client.post("/api/snapshots", json=save_payload(
        preset["blueprint"], origin_type="preset", origin_ref=str(preset["id"]))).json()
    b = client.post("/api/snapshots", json=save_payload(
        preset["blueprint"], origin_type="preset", origin_ref=str(preset["id"]))).json()
    assert a["lineage_key"] == b["lineage_key"]         # same lineage across sessions
    assert [a["version"], b["version"]] == [1, 2]        # continuous versioning
    assert not b["snapshot_id"].endswith("_2_0001")      # no NAME_2 lineage proliferation


def test_custom_projects_are_independent(client):
    a = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="Alpha")).json()
    b = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="Beta")).json()
    assert a["lineage_key"] != b["lineage_key"]


# --- T34: recommendations survive save -> detail exactly ---

def test_recommendations_round_trip(client):
    saved = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="RT")).json()
    detail = client.get(f"/api/snapshots/{saved['snapshot_id']}").json()
    assert detail["recommendations"] == saved["recommendations"]
    assert detail["prompts"] == saved["prompts"]
    assert detail["artifacts_provenance"] == "STORED"


# --- T8: pagination, id desc, cursor, total ---

def test_pagination(client):
    for i in range(5):
        client.post("/api/snapshots", json=save_payload(a_blueprint(bpm=120 + i), display_name=f"P{i}"))
    page1 = client.get("/api/snapshots?limit=2").json()
    assert len(page1["items"]) == 2
    assert page1["total"] == 5
    ids = [it["id"] for it in page1["items"]]
    assert ids == sorted(ids, reverse=True)  # id desc
    page2 = client.get(f"/api/snapshots?limit=2&before_id={page1['next_cursor']}").json()
    assert all(it["id"] < page1["next_cursor"] for it in page2["items"])


# --- T9: snapshots are immutable (no mutation surface) ---

def test_no_mutation_surface(client):
    s = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="Immutable")).json()
    sid = s["snapshot_id"]
    assert client.put(f"/api/snapshots/{sid}", json={}).status_code in (404, 405)
    assert client.patch(f"/api/snapshots/{sid}", json={}).status_code in (404, 405)
    assert client.delete(f"/api/snapshots/{sid}").status_code in (404, 405)


# --- removed endpoints are gone (breaking API change) ---

def test_removed_endpoints_absent(client):
    assert client.post("/api/generate", json=a_blueprint()).status_code == 404
    assert client.post("/api/analyze-prompt", json=a_blueprint()).status_code == 404
    s = client.post("/api/snapshots", json=save_payload(a_blueprint())).json()
    assert client.post(f"/api/snapshots/{s['snapshot_id']}/restore").status_code == 404
