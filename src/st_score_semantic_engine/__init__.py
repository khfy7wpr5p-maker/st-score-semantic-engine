"""ST Score Semantic Engine public package surface."""

from .model import (
    ClefContext,
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    KeySignatureContext,
    SemanticNote,
    SemanticSnapshot,
    TimeSignatureContext,
    ValidationReport,
    ValidationStatus,
)

SNAPSHOT_SCHEMA_VERSION = "st-semantic-snapshot-v1"
REPORT_SCHEMA_VERSION = "st-semantic-validation-report-v1"

__all__ = [
    "ClefContext",
    "Diagnostic",
    "DiagnosticCode",
    "DiagnosticSeverity",
    "KeySignatureContext",
    "REPORT_SCHEMA_VERSION",
    "SNAPSHOT_SCHEMA_VERSION",
    "SemanticNote",
    "SemanticSnapshot",
    "TimeSignatureContext",
    "ValidationReport",
    "ValidationStatus",
]
