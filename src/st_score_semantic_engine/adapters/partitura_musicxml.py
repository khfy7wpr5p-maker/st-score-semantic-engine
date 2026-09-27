"""Partitura-backed MusicXML adapter for ST semantic snapshots."""

from pathlib import Path
from typing import Any

import partitura  # type: ignore[import-untyped]
import partitura.score as pt_score  # type: ignore[import-untyped]

from st_score_semantic_engine import SNAPSHOT_SCHEMA_VERSION
from st_score_semantic_engine.model import (
    ClefContext,
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    KeySignatureContext,
    SemanticNote,
    SemanticSnapshot,
    TimeSignatureContext,
)


def _measure_index_for_onset(measures: list[Any], onset_div: int) -> int:
    for index, measure in enumerate(measures):
        start = getattr(measure, "start", None)
        end = getattr(measure, "end", None)
        if start is None or end is None:
            continue
        if int(start.t) <= onset_div < int(end.t):
            return index
    return -1


def _linked_id(
    linked_note: Any,
    *,
    source_id: str | None,
    diagnostics: list[Diagnostic],
) -> str | None:
    if linked_note is None:
        return None

    linked_id = getattr(linked_note, "id", None)
    if linked_id is None:
        diagnostics.append(
            Diagnostic(
                code=DiagnosticCode.UNRESOLVED_TIE_REFERENCE,
                severity=DiagnosticSeverity.WARNING,
                message="Tie endpoint exists but has no source note ID.",
                source_id=source_id,
            )
        )
        return None

    return str(linked_id)


def _part_id(part: Any, diagnostics: list[Diagnostic]) -> str:
    value = getattr(part, "id", None)
    if value is not None:
        return str(value)

    diagnostics.append(
        Diagnostic(
            code=DiagnosticCode.UNSUPPORTED_STRUCTURE,
            severity=DiagnosticSeverity.ERROR,
            message="MusicXML part has no stable part ID.",
        )
    )
    return ""


def load_musicxml_snapshot(path: str | Path) -> SemanticSnapshot:
    """Load MusicXML and return a deterministic ST semantic snapshot."""

    score = partitura.load_musicxml(path, force_note_ids=None)
    diagnostics: list[Diagnostic] = []
    note_rows: list[tuple[tuple[object, ...], SemanticNote]] = []
    time_signatures: list[tuple[int, TimeSignatureContext]] = []
    key_signatures: list[tuple[int, KeySignatureContext]] = []
    clefs: list[tuple[int, ClefContext]] = []
    measure_count = 0

    for part_index, part in enumerate(score.parts):
        part_id = _part_id(part, diagnostics)
        measures = list(part.measures)
        measure_count += len(measures)

        for source_ordinal, note in enumerate(
            part.iter_all(pt_score.Note, include_subclasses=True)
        ):
            source_id_raw = getattr(note, "id", None)
            source_id = str(source_id_raw) if source_id_raw is not None else None
            if source_id is None:
                diagnostics.append(
                    Diagnostic(
                        code=DiagnosticCode.MISSING_SOURCE_ID,
                        severity=DiagnosticSeverity.WARNING,
                        message="Source note has no MusicXML note ID.",
                    )
                )

            start = getattr(note, "start", None)
            end = getattr(note, "end", None)
            if start is None or end is None:
                diagnostics.append(
                    Diagnostic(
                        code=DiagnosticCode.UNSUPPORTED_STRUCTURE,
                        severity=DiagnosticSeverity.ERROR,
                        message="Pitched note is missing timeline boundaries.",
                        source_id=source_id,
                    )
                )
                continue

            onset_div = int(start.t)
            duration_div = int(end.t) - onset_div
            measure_index = _measure_index_for_onset(measures, onset_div)
            if measure_index < 0:
                diagnostics.append(
                    Diagnostic(
                        code=DiagnosticCode.INVALID_MEASURE_INDEX,
                        severity=DiagnosticSeverity.ERROR,
                        message="Note onset does not belong to a known measure.",
                        source_id=source_id,
                    )
                )

            voice_raw = getattr(note, "voice", None)
            staff_raw = getattr(note, "staff", None)
            voice = int(voice_raw) if voice_raw is not None else None
            staff = int(staff_raw) if staff_raw is not None else None
            pitch_midi = int(note.midi_pitch)

            semantic_note = SemanticNote(
                source_id=source_id,
                part_id=part_id,
                measure_index=measure_index,
                pitch_midi=pitch_midi,
                onset_div=onset_div,
                duration_div=duration_div,
                voice=voice,
                staff=staff,
                tie_prev=_linked_id(
                    getattr(note, "tie_prev", None),
                    source_id=source_id,
                    diagnostics=diagnostics,
                ),
                tie_next=_linked_id(
                    getattr(note, "tie_next", None),
                    source_id=source_id,
                    diagnostics=diagnostics,
                ),
                is_grace=isinstance(note, pt_score.GraceNote),
            )

            staff_key = staff if staff is not None else 2**31 - 1
            voice_key = voice if voice is not None else 2**31 - 1
            note_rows.append(
                (
                    (
                        part_index,
                        onset_div,
                        measure_index,
                        staff_key,
                        voice_key,
                        pitch_midi,
                        source_id or "",
                        source_ordinal,
                    ),
                    semantic_note,
                )
            )

        for context in part.iter_all(pt_score.TimeSignature):
            time_signatures.append(
                (
                    part_index,
                    TimeSignatureContext(
                        part_id=part_id,
                        onset_div=int(context.start.t),
                        beats=int(context.beats),
                        beat_type=int(context.beat_type),
                    ),
                )
            )

        for context in part.iter_all(pt_score.KeySignature):
            mode_raw = getattr(context, "mode", None)
            key_signatures.append(
                (
                    part_index,
                    KeySignatureContext(
                        part_id=part_id,
                        onset_div=int(context.start.t),
                        fifths=int(context.fifths),
                        mode=str(mode_raw) if mode_raw is not None else None,
                    ),
                )
            )

        for context in part.iter_all(pt_score.Clef):
            octave_change_raw = getattr(context, "octave_change", None)
            line_raw = getattr(context, "line", None)
            clefs.append(
                (
                    part_index,
                    ClefContext(
                        part_id=part_id,
                        onset_div=int(context.start.t),
                        staff=int(context.staff),
                        sign=str(context.sign),
                        line=int(line_raw) if line_raw is not None else None,
                        octave_change=(
                            int(octave_change_raw) if octave_change_raw is not None else 0
                        ),
                    ),
                )
            )

    note_rows.sort(key=lambda row: row[0])
    time_signatures.sort(
        key=lambda row: (
            row[0],
            row[1].onset_div,
            row[1].beats,
            row[1].beat_type,
        )
    )
    key_signatures.sort(
        key=lambda row: (
            row[0],
            row[1].onset_div,
            row[1].fifths,
            row[1].mode or "",
        )
    )
    clefs.sort(
        key=lambda row: (
            row[0],
            row[1].onset_div,
            row[1].staff,
            row[1].sign,
            row[1].line if row[1].line is not None else -1,
            row[1].octave_change,
        )
    )

    return SemanticSnapshot(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        source_kind="musicxml",
        part_count=len(score.parts),
        measure_count=measure_count,
        notes=tuple(note for _, note in note_rows),
        time_signatures=tuple(context for _, context in time_signatures),
        key_signatures=tuple(context for _, context in key_signatures),
        clefs=tuple(context for _, context in clefs),
        diagnostics=tuple(diagnostics),
    )
