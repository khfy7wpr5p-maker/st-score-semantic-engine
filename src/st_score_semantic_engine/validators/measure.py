"""Measure-membership validation."""

from st_score_semantic_engine.model import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    SemanticSnapshot,
)


def validate_measure_membership(
    snapshot: SemanticSnapshot,
) -> tuple[Diagnostic, ...]:
    """Report notes whose zero-based measure index is outside snapshot bounds."""

    diagnostics: list[Diagnostic] = []
    for note in snapshot.notes:
        if note.measure_index < 0 or note.measure_index >= snapshot.measure_count:
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.INVALID_MEASURE_INDEX,
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"Measure index {note.measure_index} is outside "
                        f"snapshot bounds [0, {snapshot.measure_count})."
                    ),
                    source_id=note.source_id,
                )
            )
    return tuple(diagnostics)
