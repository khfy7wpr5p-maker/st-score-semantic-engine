from st_score_semantic_engine import REPORT_SCHEMA_VERSION, SNAPSHOT_SCHEMA_VERSION
from st_score_semantic_engine.model import (
    SemanticNote,
    SemanticSnapshot,
    ValidationReport,
    ValidationStatus,
)
from st_score_semantic_engine.serialization import (
    report_to_dict,
    report_to_json,
    snapshot_to_dict,
    snapshot_to_json,
)


def _snapshot() -> SemanticSnapshot:
    note = SemanticNote(
        source_id="n1",
        part_id="P1",
        measure_index=0,
        pitch_midi=60,
        onset_div=0,
        duration_div=4,
        voice=1,
        staff=1,
        tie_prev=None,
        tie_next=None,
        is_grace=False,
    )
    return SemanticSnapshot(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        source_kind="musicxml",
        part_count=1,
        measure_count=1,
        notes=(note,),
        time_signatures=(),
        key_signatures=(),
        clefs=(),
    )


def test_snapshot_serializes_with_explicit_schema_and_arrays():
    payload = snapshot_to_dict(_snapshot())

    assert payload["schema_version"] == "st-semantic-snapshot-v1"
    assert isinstance(payload["notes"], list)
    assert payload["notes"][0]["source_id"] == "n1"


def test_snapshot_json_is_byte_stable():
    first = snapshot_to_json(_snapshot())
    second = snapshot_to_json(_snapshot())

    assert first == second
    assert " " not in first


def test_validation_report_serialization_uses_string_enum_values():
    report = ValidationReport(
        schema_version=REPORT_SCHEMA_VERSION,
        status=ValidationStatus.PASS,
        diagnostics=(),
    )

    assert report_to_dict(report)["status"] == "PASS"
    assert report_to_json(report) == (
        '{"diagnostics":[],"schema_version":"st-semantic-validation-report-v1","status":"PASS"}'
    )
