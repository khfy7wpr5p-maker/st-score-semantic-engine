import json
from pathlib import Path

from st_score_semantic_engine.adapters.partitura_musicxml import (
    load_musicxml_snapshot,
)
from st_score_semantic_engine.serialization import snapshot_to_dict, snapshot_to_json


FIXTURE_DIR = Path(__file__).parent / "fixtures"
MUSICXML_FIXTURE = FIXTURE_DIR / "semantic_baseline.musicxml"
EXPECTED_FIXTURE = FIXTURE_DIR / "semantic_baseline.expected.json"


def _expected() -> dict[str, object]:
    return json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))


def test_musicxml_fixture_matches_independent_expected_snapshot():
    snapshot = load_musicxml_snapshot(MUSICXML_FIXTURE)

    assert snapshot_to_dict(snapshot) == _expected()


def test_musicxml_snapshot_is_deterministic():
    first = snapshot_to_json(load_musicxml_snapshot(MUSICXML_FIXTURE))
    second = snapshot_to_json(load_musicxml_snapshot(MUSICXML_FIXTURE))

    assert first == second
