"""T1 + T26: engine determinism goldens coupled to PIPELINE_VERSION.

If any engine output changes, the committed golden must be regenerated AND
PIPELINE_VERSION bumped; this test fails otherwise.
"""
import json
from pathlib import Path

from app.pipeline_version import PIPELINE_VERSION
from tests.golden_data import build_goldens, build_case, MATRIX

GOLDEN_PATH = Path(__file__).parent / "goldens" / "engine_goldens.json"


def _load():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_determinism_two_runs_identical():
    for name, bp in MATRIX.items():
        assert build_case(bp) == build_case(bp), f"nondeterministic output for {name}"


def test_output_matches_committed_golden():
    committed = _load()
    live = build_goldens()
    assert live["cases"] == committed["cases"]


def test_golden_version_coupled_to_pipeline_version():
    committed = _load()
    # The committed golden must have been generated under the current pipeline
    # version; a bump without regeneration (or vice versa) fails here.
    assert committed["pipeline_version"] == PIPELINE_VERSION
