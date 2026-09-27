"""Canonical JSON-compatible serialization for semantic contracts."""

import json

from .model import (
    ClefContext,
    Diagnostic,
    KeySignatureContext,
    SemanticNote,
    SemanticSnapshot,
    TimeSignatureContext,
    ValidationReport,
)


def _diagnostic_to_dict(diagnostic: Diagnostic) -> dict[str, object]:
    return {
        "code": diagnostic.code.value,
        "severity": diagnostic.severity.value,
        "message": diagnostic.message,
        "source_id": diagnostic.source_id,
    }


def _time_signature_to_dict(context: TimeSignatureContext) -> dict[str, object]:
    return {
        "part_id": context.part_id,
        "onset_div": context.onset_div,
        "beats": context.beats,
        "beat_type": context.beat_type,
    }


def _key_signature_to_dict(context: KeySignatureContext) -> dict[str, object]:
    return {
        "part_id": context.part_id,
        "onset_div": context.onset_div,
        "fifths": context.fifths,
        "mode": context.mode,
    }


def _clef_to_dict(context: ClefContext) -> dict[str, object]:
    return {
        "part_id": context.part_id,
        "onset_div": context.onset_div,
        "staff": context.staff,
        "sign": context.sign,
        "line": context.line,
        "octave_change": context.octave_change,
    }


def _note_to_dict(note: SemanticNote) -> dict[str, object]:
    return {
        "source_id": note.source_id,
        "part_id": note.part_id,
        "measure_index": note.measure_index,
        "pitch_midi": note.pitch_midi,
        "onset_div": note.onset_div,
        "duration_div": note.duration_div,
        "voice": note.voice,
        "staff": note.staff,
        "tie_prev": note.tie_prev,
        "tie_next": note.tie_next,
        "is_grace": note.is_grace,
    }


def snapshot_to_dict(snapshot: SemanticSnapshot) -> dict[str, object]:
    return {
        "schema_version": snapshot.schema_version,
        "source_kind": snapshot.source_kind,
        "part_count": snapshot.part_count,
        "measure_count": snapshot.measure_count,
        "notes": [_note_to_dict(note) for note in snapshot.notes],
        "time_signatures": [
            _time_signature_to_dict(context) for context in snapshot.time_signatures
        ],
        "key_signatures": [
            _key_signature_to_dict(context) for context in snapshot.key_signatures
        ],
        "clefs": [_clef_to_dict(context) for context in snapshot.clefs],
        "diagnostics": [
            _diagnostic_to_dict(diagnostic) for diagnostic in snapshot.diagnostics
        ],
    }


def snapshot_to_json(snapshot: SemanticSnapshot) -> str:
    return json.dumps(
        snapshot_to_dict(snapshot),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def report_to_dict(report: ValidationReport) -> dict[str, object]:
    return {
        "schema_version": report.schema_version,
        "status": report.status.value,
        "diagnostics": [_diagnostic_to_dict(diagnostic) for diagnostic in report.diagnostics],
    }


def report_to_json(report: ValidationReport) -> str:
    return json.dumps(
        report_to_dict(report),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
