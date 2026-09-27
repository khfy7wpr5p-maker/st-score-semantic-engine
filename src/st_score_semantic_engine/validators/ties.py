"""Bounded tie-relation validation."""

from collections import Counter

from st_score_semantic_engine.model import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    SemanticNote,
    SemanticSnapshot,
)


def _tie_diagnostic(
    *,
    code: DiagnosticCode,
    message: str,
    note: SemanticNote,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        source_id=note.source_id,
    )


def validate_ties(snapshot: SemanticSnapshot) -> tuple[Diagnostic, ...]:
    """Validate source-ID-addressable tie endpoints without guessing."""

    id_counts = Counter(
        note.source_id for note in snapshot.notes if note.source_id is not None
    )
    duplicate_ids = sorted(
        source_id for source_id, count in id_counts.items() if count > 1
    )
    if duplicate_ids:
        return tuple(
            Diagnostic(
                code=DiagnosticCode.UNSUPPORTED_STRUCTURE,
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Duplicate source ID {source_id!r} makes tie resolution ambiguous."
                ),
                source_id=source_id,
            )
            for source_id in duplicate_ids
        )

    notes_by_id = {
        note.source_id: note
        for note in snapshot.notes
        if note.source_id is not None
    }
    diagnostics: list[Diagnostic] = []

    for note in snapshot.notes:
        for direction, target_id, reciprocal_field in (
            ("previous", note.tie_prev, "tie_next"),
            ("next", note.tie_next, "tie_prev"),
        ):
            if target_id is None:
                continue

            target = notes_by_id.get(target_id)
            if target is None:
                diagnostics.append(
                    _tie_diagnostic(
                        code=DiagnosticCode.UNRESOLVED_TIE_REFERENCE,
                        message=(
                            f"Tie {direction} target {target_id!r} cannot be resolved."
                        ),
                        note=note,
                    )
                )
                continue

            if note.source_id is None or getattr(target, reciprocal_field) != note.source_id:
                diagnostics.append(
                    _tie_diagnostic(
                        code=DiagnosticCode.NON_RECIPROCAL_TIE,
                        message=(
                            f"Tie relation to {target_id!r} is not reciprocal."
                        ),
                        note=note,
                    )
                )

            if target.pitch_midi != note.pitch_midi:
                diagnostics.append(
                    _tie_diagnostic(
                        code=DiagnosticCode.TIE_PITCH_MISMATCH,
                        message=(
                            f"Tied notes differ in pitch: "
                            f"{note.pitch_midi} != {target.pitch_midi}."
                        ),
                        note=note,
                    )
                )

    return tuple(diagnostics)
