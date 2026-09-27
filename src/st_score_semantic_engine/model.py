"""ST-owned immutable semantic contracts."""

from dataclasses import dataclass
from enum import Enum


class DiagnosticSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class DiagnosticCode(str, Enum):
    MISSING_SOURCE_ID = "MISSING_SOURCE_ID"
    MISSING_VOICE = "MISSING_VOICE"
    INVALID_VOICE = "INVALID_VOICE"
    MISSING_STAFF = "MISSING_STAFF"
    INVALID_STAFF = "INVALID_STAFF"
    INVALID_MEASURE_INDEX = "INVALID_MEASURE_INDEX"
    INVALID_ONSET = "INVALID_ONSET"
    INVALID_DURATION = "INVALID_DURATION"
    UNRESOLVED_TIE_REFERENCE = "UNRESOLVED_TIE_REFERENCE"
    NON_RECIPROCAL_TIE = "NON_RECIPROCAL_TIE"
    TIE_PITCH_MISMATCH = "TIE_PITCH_MISMATCH"
    UNSUPPORTED_STRUCTURE = "UNSUPPORTED_STRUCTURE"


@dataclass(frozen=True)
class Diagnostic:
    code: DiagnosticCode
    severity: DiagnosticSeverity
    message: str
    source_id: str | None = None


@dataclass(frozen=True)
class TimeSignatureContext:
    part_id: str
    onset_div: int
    beats: int
    beat_type: int


@dataclass(frozen=True)
class KeySignatureContext:
    part_id: str
    onset_div: int
    fifths: int
    mode: str | None


@dataclass(frozen=True)
class ClefContext:
    part_id: str
    onset_div: int
    staff: int
    sign: str
    line: int | None
    octave_change: int


@dataclass(frozen=True)
class SemanticNote:
    source_id: str | None
    part_id: str
    measure_index: int
    pitch_midi: int
    onset_div: int
    duration_div: int
    voice: int | None
    staff: int | None
    tie_prev: str | None
    tie_next: str | None
    is_grace: bool


@dataclass(frozen=True)
class SemanticSnapshot:
    schema_version: str
    source_kind: str
    part_count: int
    measure_count: int
    notes: tuple[SemanticNote, ...]
    time_signatures: tuple[TimeSignatureContext, ...]
    key_signatures: tuple[KeySignatureContext, ...]
    clefs: tuple[ClefContext, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


class ValidationStatus(str, Enum):
    PASS = "PASS"
    DIAGNOSTIC = "DIAGNOSTIC"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    status: ValidationStatus
    diagnostics: tuple[Diagnostic, ...]
