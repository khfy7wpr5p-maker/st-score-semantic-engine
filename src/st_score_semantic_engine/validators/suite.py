"""Deterministic aggregation of semantic validator results."""

from st_score_semantic_engine import REPORT_SCHEMA_VERSION
from st_score_semantic_engine.model import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    SemanticSnapshot,
    ValidationReport,
    ValidationStatus,
)

from .measure import validate_measure_membership
from .ties import validate_ties
from .timing import validate_timing
from .voice_staff import validate_voice_staff


def _diagnostic_sort_key(
    diagnostic: Diagnostic,
) -> tuple[str, str, str, str]:
    return (
        diagnostic.severity.value,
        diagnostic.code.value,
        diagnostic.source_id or "",
        diagnostic.message,
    )


def validate_snapshot(snapshot: SemanticSnapshot) -> ValidationReport:
    """Run the baseline validator suite and return a deterministic report."""

    diagnostics = list(snapshot.diagnostics)
    diagnostics.extend(validate_measure_membership(snapshot))
    diagnostics.extend(validate_timing(snapshot))
    diagnostics.extend(validate_voice_staff(snapshot))
    diagnostics.extend(validate_ties(snapshot))
    ordered = tuple(sorted(diagnostics, key=_diagnostic_sort_key))

    if any(
        diagnostic.code is DiagnosticCode.UNSUPPORTED_STRUCTURE
        for diagnostic in ordered
    ):
        status = ValidationStatus.UNSUPPORTED
    elif any(
        diagnostic.severity in (
            DiagnosticSeverity.WARNING,
            DiagnosticSeverity.ERROR,
        )
        for diagnostic in ordered
    ):
        status = ValidationStatus.DIAGNOSTIC
    else:
        status = ValidationStatus.PASS

    return ValidationReport(
        schema_version=REPORT_SCHEMA_VERSION,
        status=status,
        diagnostics=ordered,
    )
