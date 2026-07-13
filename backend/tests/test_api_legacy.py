"""T24 + T6 + R18/R39 at the API layer, over a migrated legacy database.

Legacy snapshots lack stored motif/timeline/recommendations, so those are
reconstructed and disclosed; blueprint/prompts/scores remain exact. Saving from
a legacy-associated preset continues the same legacy lineage."""
from tests.helpers import row_counts, save_payload, a_blueprint


def test_legacy_detail_discloses_reconstruction(legacy_client):
    before = row_counts(legacy_client.db_path)
    r = legacy_client.get("/api/snapshots/CUSTOM_0001")
    assert r.status_code == 200
    rec = r.json()
    assert rec["artifacts_provenance"] == "LEGACY_RECONSTRUCTED"
    assert rec["engine_version"] is None
    # reconstructed fields are present but explicitly non-historical
    assert rec["motif_block"]
    assert rec["arrangement_timeline"]
    # stored fields remain exact
    assert rec["prompts"]["suno"]["style_tags"]
    assert rec["scores"]["overall"] == 90
    # read is zero-write
    assert row_counts(legacy_client.db_path) == before


def test_legacy_list_includes_legacy_rows(legacy_client):
    page = legacy_client.get("/api/snapshots?limit=50").json()
    ids = {it["snapshot_id"] for it in page["items"]}
    assert {"PSYCH_TEC_0001", "PSYCH_TEC_0002", "COLD_SIGNAL_0001", "CUSTOM_0001"} <= ids
    assert page["total"] == 4


def test_saving_from_legacy_associated_preset_continues_lineage(legacy_client):
    presets = legacy_client.get("/api/presets").json()
    psych = next(p for p in presets if p["name"] == "Psych Tec")
    r = legacy_client.post("/api/snapshots", json=save_payload(
        psych["blueprint"], origin_type="preset", origin_ref=str(psych["id"])))
    assert r.status_code == 200, r.text
    rec = r.json()
    # continues legacy:PSYCH_TEC (max legacy version was 2) -> version 3
    assert rec["lineage_key"] == "legacy:PSYCH_TEC"
    assert rec["version"] == 3
    assert rec["snapshot_id"] == "PSYCH_TEC_0003"
    assert rec["engine_version"] == "1.0.0-ws1"
    assert rec["artifacts_provenance"] == "STORED"


def test_new_save_is_exact_stored(legacy_client):
    saved = legacy_client.post("/api/snapshots", json=save_payload(
        a_blueprint(), display_name="Fresh")).json()
    detail = legacy_client.get(f"/api/snapshots/{saved['snapshot_id']}").json()
    # new snapshot round-trips byte-identical incl. recommendations
    assert detail["recommendations"] == saved["recommendations"]
    assert detail["motif_block"] == saved["motif_block"]
    assert detail["arrangement_timeline"] == saved["arrangement_timeline"]
    assert detail["artifacts_provenance"] == "STORED"
