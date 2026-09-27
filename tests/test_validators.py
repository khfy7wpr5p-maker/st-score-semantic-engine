from st_score_semantic_engine import SNAPSHOT_SCHEMA_VERSION
from st_score_semantic_engine.model import DiagnosticCode, SemanticNote, SemanticSnapshot
from st_score_semantic_engine.validators.measure import validate_measure_membership
from st_score_semantic_engine.validators.ties import validate_ties
from st_score_semantic_engine.validators.timing import validate_timing
from st_score_semantic_engine.validators.voice_staff import validate_voice_staff


def _note(
    *,
    source_id: str | None = "n1",
    measure_index: int = 0,
    pitch_midi: int = 60,
    onset_div: int = 0,
    duration_div: int = 4,
    voice: int | None = 1,
    staff: int | None = 1,
    tie_prev: str | None = None,
    tie_next: str | None = None,
    is_grace: bool = False,
) -> SemanticNote:
    return SemanticNote(
        source_id=source_id,
        part_id="P1",
        measure_index=measure_index,
        pitch_midi=pitch_midi,
        onset_div=onset_div,
        duration_div=duration_div,
        voice=voice,
        staff=staff,
        tie_prev=tie_prev,
        tie_next=tie_next,
        is_grace=is_grace,
    )


def _snapshot(*notes: SemanticNote, measure_count: int = 2) -> SemanticSnapshot:
    return SemanticSnapshot(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        source_kind="test",
        part_count=1,
        measure_count=measure_count,
        notes=notes,
        time_signatures=(),
        key_signatures=(),
        clefs=(),
    )


def _codes(diagnostics: tuple[object, ...]) -> list[DiagnosticCode]:
    return [diagnostic.code for diagnostic in diagnostics]  # type: ignore[attr-defined]


def test_measure_membership_accepts_valid_indices():
    assert validate_measure_membership(_snapshot(_note(measure_index=0))) == ()


def test_measure_membership_rejects_out_of_range_indices():
    diagnostics = validate_measure_membership(
        _snapshot(
            _note(source_id="negative", measure_index=-1),
            _note(source_id="too-high", measure_index=2),
        )
    )

    assert _codes(diagnostics) == [
        DiagnosticCode.INVALID_MEASURE_INDEX,
        DiagnosticCode.INVALID_MEASURE_INDEX,
    ]


def test_timing_accepts_positive_and_grace_zero_duration():
    snapshot = _snapshot(
        _note(source_id="normal", onset_div=0, duration_div=4),
        _note(source_id="grace", onset_div=4, duration_div=0, is_grace=True),
    )

    assert validate_timing(snapshot) == ()


def test_timing_rejects_negative_onset_and_invalid_durations():
    diagnostics = validate_timing(
        _snapshot(
            _note(source_id="bad-onset", onset_div=-1),
            _note(source_id="bad-duration", duration_div=-1),
            _note(source_id="zero", duration_div=0, is_grace=False),
        )
    )

    assert _codes(diagnostics) == [
        DiagnosticCode.INVALID_ONSET,
        DiagnosticCode.INVALID_DURATION,
        DiagnosticCode.INVALID_DURATION,
    ]


def test_voice_staff_reports_missing_and_invalid_values():
    diagnostics = validate_voice_staff(
        _snapshot(
            _note(source_id="missing-voice", voice=None),
            _note(source_id="invalid-voice", voice=0),
            _note(source_id="missing-staff", staff=None),
            _note(source_id="invalid-staff", staff=0),
        )
    )

    assert _codes(diagnostics) == [
        DiagnosticCode.MISSING_VOICE,
        DiagnosticCode.INVALID_VOICE,
        DiagnosticCode.MISSING_STAFF,
        DiagnosticCode.INVALID_STAFF,
    ]


def test_ties_accept_reciprocal_same_pitch_relation():
    snapshot = _snapshot(
        _note(source_id="a", pitch_midi=60, tie_next="b"),
        _note(source_id="b", pitch_midi=60, onset_div=4, tie_prev="a"),
    )

    assert validate_ties(snapshot) == ()


def test_ties_report_missing_target():
    diagnostics = validate_ties(_snapshot(_note(source_id="a", tie_next="missing")))

    assert _codes(diagnostics) == [DiagnosticCode.UNRESOLVED_TIE_REFERENCE]


def test_ties_report_non_reciprocal_relation():
    diagnostics = validate_ties(
        _snapshot(
            _note(source_id="a", tie_next="b"),
            _note(source_id="b", onset_div=4),
        )
    )

    assert _codes(diagnostics) == [DiagnosticCode.NON_RECIPROCAL_TIE]


def test_ties_report_pitch_mismatch():
    diagnostics = validate_ties(
        _snapshot(
            _note(source_id="a", pitch_midi=60, tie_next="b"),
            _note(source_id="b", pitch_midi=61, onset_div=4, tie_prev="a"),
        )
    )

    assert _codes(diagnostics) == [
        DiagnosticCode.TIE_PITCH_MISMATCH,
        DiagnosticCode.TIE_PITCH_MISMATCH,
    ]


def test_ties_fail_closed_for_duplicate_source_ids():
    diagnostics = validate_ties(
        _snapshot(
            _note(source_id="dup", tie_next="b"),
            _note(source_id="dup", onset_div=2),
            _note(source_id="b", onset_div=4, tie_prev="dup"),
        )
    )

    assert _codes(diagnostics) == [DiagnosticCode.UNSUPPORTED_STRUCTURE]
