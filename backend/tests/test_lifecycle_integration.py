"""T20 (contract completion): one connected end-to-end WS1 lifecycle loop,
exercising the ratified sequence as a workflow (not isolated fragments):

  preview (no write) -> save custom root s1 -> save descendant s2 ->
  restore s1 -> branch save s3 (child of s1, not the newer s2)

Verifies persistence boundaries, lineage/version/parent behavior, and that
returned representations round-trip. Uses only the disposable test database.
"""
from tests.helpers import row_counts, save_payload, a_blueprint


def test_full_lifecycle_loop(client):
    base = row_counts(client.db_path)

    # 1. Preview is non-persistent.
    pv = client.post("/api/preview", json={**a_blueprint(), "client_revision": 1})
    assert pv.status_code == 200
    assert row_counts(client.db_path) == base, "preview must not write"

    # 2. Save a custom root -> s1.
    s1 = client.post("/api/snapshots", json=save_payload(a_blueprint(), display_name="Loop")).json()
    after_s1 = row_counts(client.db_path)
    assert after_s1["blueprint_snapshots"] == base["blueprint_snapshots"] + 1
    assert after_s1["generation_history"] == base["generation_history"] + 1
    assert s1["version"] == 1 and s1["parent_snapshot_id"] is None
    assert s1["origin_type"] == "custom"

    # 3. Edit and save a descendant -> s2 (snapshot origin, parent s1).
    s2 = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=140), origin_type="snapshot", origin_ref=s1["snapshot_id"],
        parent_snapshot_id=s1["snapshot_id"], lineage_key=s1["lineage_key"])).json()
    assert s2["version"] == 2
    assert s2["parent_snapshot_id"] == s1["snapshot_id"]
    assert s2["lineage_key"] == s1["lineage_key"]

    # 4. Restore s1 -> exact stored record, zero writes.
    before_restore = row_counts(client.db_path)
    restored = client.get(f"/api/snapshots/{s1['snapshot_id']}").json()
    assert row_counts(client.db_path) == before_restore, "restore is read-only"
    assert restored["snapshot_id"] == s1["snapshot_id"]
    assert restored["blueprint"] == s1["blueprint"]
    assert restored["recommendations"] == s1["recommendations"]
    assert restored["artifacts_provenance"] == "STORED"

    # 5. Branch off the RESTORED s1 (not the newer s2) -> s3.
    s3 = client.post("/api/snapshots", json=save_payload(
        a_blueprint(bpm=90, energy=30), origin_type="snapshot", origin_ref=s1["snapshot_id"],
        parent_snapshot_id=s1["snapshot_id"], lineage_key=s1["lineage_key"])).json()
    assert s3["parent_snapshot_id"] == s1["snapshot_id"]  # branch from s1, regardless of s2
    assert s3["version"] == 3                             # dense per-lineage counter
    assert s3["lineage_key"] == s1["lineage_key"]

    # 6. Final persisted state: exactly three snapshots + three history rows.
    final = row_counts(client.db_path)
    assert final["blueprint_snapshots"] == base["blueprint_snapshots"] + 3
    assert final["generation_history"] == base["generation_history"] + 3

    # Lineage chain: s1 root; s2 and s3 both children of s1.
    page = client.get("/api/snapshots?limit=50").json()
    by_id = {it["snapshot_id"]: it for it in page["items"]}
    assert {s1["snapshot_id"], s2["snapshot_id"], s3["snapshot_id"]} <= set(by_id)
    assert by_id[s1["snapshot_id"]]["parent_snapshot_id"] is None
    assert by_id[s2["snapshot_id"]]["parent_snapshot_id"] == s1["snapshot_id"]
    assert by_id[s3["snapshot_id"]]["parent_snapshot_id"] == s1["snapshot_id"]
    # All three share one stable lineage identity.
    assert len({by_id[s["snapshot_id"]]["lineage_key"] for s in (s1, s2, s3)}) == 1
