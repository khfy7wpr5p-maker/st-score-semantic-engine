import json
from pathlib import Path

from st_score_semantic_engine.adapters.partitura_musicxml import load_musicxml_snapshot
from st_score_semantic_engine.serialization import snapshot_to_dict

FIXTURE = Path(__file__).parent / "fixtures" / "sem04_editor_parity.musicxml"
EXPECTED = Path(__file__).parent / "fixtures" / "sem04_editor_parity.expected.json"


def test_sem04_editor_compatible_musicxml_matches_pinned_snapshot():
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    snapshot = load_musicxml_snapshot(FIXTURE)
    assert snapshot_to_dict(snapshot) == expected
