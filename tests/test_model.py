from dataclasses import FrozenInstanceError

import pytest

from st_score_semantic_engine import SNAPSHOT_SCHEMA_VERSION
from st_score_semantic_engine.model import SemanticNote, SemanticSnapshot


def _note() -> SemanticNote:
    return SemanticNote(
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


def test_package_exposes_schema_versions():
    import st_score_semantic_engine as semantic

    assert semantic.SNAPSHOT_SCHEMA_VERSION == "st-semantic-snapshot-v1"
    assert semantic.REPORT_SCHEMA_VERSION == "st-semantic-validation-report-v1"


def test_semantic_note_is_immutable():
    note = _note()

    with pytest.raises(FrozenInstanceError):
        note.pitch_midi = 61  # type: ignore[misc]


def test_semantic_snapshot_uses_tuple_notes():
    snapshot = SemanticSnapshot(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        source_kind="musicxml",
        part_count=1,
        measure_count=1,
        notes=(_note(),),
        time_signatures=(),
        key_signatures=(),
        clefs=(),
    )

    assert isinstance(snapshot.notes, tuple)
    assert snapshot.notes == (_note(),)
