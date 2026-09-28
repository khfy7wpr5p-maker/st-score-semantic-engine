"""Voice and staff presence/range validation."""

from st_score_semantic_engine.model import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    SemanticSnapshot,
)


def validate_voice_staff(snapshot: SemanticSnapshot) -> tuple[Diagnostic, ...]:
    """Validate explicit positive voice and staff numbers without coercion."""

    diagnostics: list[Diagnostic] = []
    for note in snapshot.notes:
        if note.voice is None:
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.MISSING_VOICE,
                    severity=DiagnosticSeverity.WARNING,
                    message="Source note has no explicit voice.",
                    source_id=note.source_id,
                )
            )
        elif note.voice <= 0:
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.INVALID_VOICE,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Voice {note.voice} must be positive.",
                    source_id=note.source_id,
                )
            )

        if note.staff is None:
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.MISSING_STAFF,
                    severity=DiagnosticSeverity.WARNING,
                    message="Source note has no explicit staff.",
                    source_id=note.source_id,
                )
            )
        elif note.staff <= 0:
            diagnostics.append(
                Diagnostic(
                    code=DiagnosticCode.INVALID_STAFF,
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Staff {note.staff} must be positive.",
                    source_id=note.source_id,
                )
            )

    return tuple(diagnostics)
