"""Division-domain timing validation."""

from st_score_semantic_engine.model import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    SemanticSnapshot,
)


def validate_timing(snapshot: SemanticSnapshot) -> tuple[Diagnostic, ...]:
    """Validate canonical integer onset and duration invariants."""

    diagnostics: list[Diagnostic] = []
    for note in snapshot.notes:
        if note.onset_div < 0:
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.INVALID_ONSET,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Negative onset_div {note.onset_div} is invalid.",
                    source_id=note.source_id,
                )
            )

        if note.duration_div < 0 or (
            note.duration_div == 0 and not note.is_grace
        ):
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.INVALID_DURATION,
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"duration_div {note.duration_div} is invalid "
                        f"for is_grace={note.is_grace}."
                    ),
                    source_id=note.source_id,
                )
            )

    return tuple(diagnostics)
