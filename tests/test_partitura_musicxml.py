import json
from pathlib import Path

from st_score_semantic_engine import serialization
from st_score_semantic_engine.adapters import partitura_musicxml
from st_score_semantic_engine.model import DiagnosticCode, ValidationStatus
from st_score_semantic_engine.validators.suite import validate_snapshot

FIXTURE_DIR = Path(__file__).parent / "fixtures"
MUSICXML_FIXTURE = FIXTURE_DIR / "semantic_baseline.musicxml"
EXPECTED_FIXTURE = FIXTURE_DIR / "semantic_baseline.expected.json"


def _expected() -> dict[str, object]:
    return json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))


def test_musicxml_fixture_matches_independent_expected_snapshot():
    snapshot = partitura_musicxml.load_musicxml_snapshot(MUSICXML_FIXTURE)

    assert serialization.snapshot_to_dict(snapshot) == _expected()


def test_musicxml_snapshot_is_deterministic():
    first = serialization.snapshot_to_json(
        partitura_musicxml.load_musicxml_snapshot(MUSICXML_FIXTURE)
    )
    second = serialization.snapshot_to_json(
        partitura_musicxml.load_musicxml_snapshot(MUSICXML_FIXTURE)
    )

    assert first == second


def test_musicxml_fixture_passes_baseline_validation():
    snapshot = partitura_musicxml.load_musicxml_snapshot(MUSICXML_FIXTURE)
    report = validate_snapshot(snapshot)

    assert report.status is ValidationStatus.PASS
    assert report.diagnostics == ()


def test_multi_part_measure_count_tracks_score_measure_span(tmp_path: Path):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>One</part-name></score-part>
    <score-part id="P2"><part-name>Two</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <note id="p1n1">
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration><voice>1</voice><type>whole</type><staff>1</staff>
      </note>
    </measure>
  </part>
  <part id="P2">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <note id="p2n1">
        <pitch><step>E</step><octave>4</octave></pitch>
        <duration>4</duration><voice>1</voice><type>whole</type><staff>1</staff>
      </note>
    </measure>
  </part>
</score-partwise>
"""
    path = tmp_path / "two-parts.musicxml"
    path.write_text(xml, encoding="utf-8")

    snapshot = partitura_musicxml.load_musicxml_snapshot(path)

    assert snapshot.part_count == 2
    assert snapshot.measure_count == 1


def test_unpitched_note_is_reported_as_unsupported(tmp_path: Path):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Percussion</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <note id="u1">
        <unpitched><display-step>C</display-step><display-octave>5</display-octave></unpitched>
        <duration>1</duration><voice>1</voice><type>quarter</type><staff>1</staff>
      </note>
    </measure>
  </part>
</score-partwise>
"""
    path = tmp_path / "unpitched.musicxml"
    path.write_text(xml, encoding="utf-8")

    snapshot = partitura_musicxml.load_musicxml_snapshot(path)

    assert [
        (diagnostic.code, diagnostic.source_id)
        for diagnostic in snapshot.diagnostics
    ] == [(DiagnosticCode.UNSUPPORTED_STRUCTURE, "u1")]
