# ST Score Semantic Engine — SEM-01 to SEM-03 Implementation Plan

Date: 2026-09-27  
Design: `docs/superpowers/specs/2026-09-27-st-score-semantic-engine-design.md`  
Linear: SES-40 → SES-41 → SES-42  
Execution mode after approval: isolated branch/worktree, inline TDD  
Production code status: NOT AUTHORIZED UNTIL THIS PLAN IS APPROVED

## Objective

Deliver the smallest useful standalone semantic engine that:

1. defines ST-owned immutable semantic contracts;
2. reads one repository-owned MusicXML fixture through Partitura 1.9.0;
3. produces a deterministic `SemanticSnapshot`;
4. validates baseline measure/timing/voice/staff/tie invariants;
5. produces deterministic `ValidationReport` data;
6. does not modify MusicXML, any consumer repository, or any runtime deployment.

## Fixed technical decisions

### Runtime

- Python: `>=3.10,<3.13` for the first qualification matrix.
- Partitura: exactly `1.9.0`.
- Package layout: `src/`.
- Build backend: setuptools.
- Unit test runner: pytest.
- Static checks: Ruff + mypy.
- Build verification: `python -m build`.
- Data model: stdlib frozen dataclasses; no Pydantic dependency.
- Serialization: stdlib `json` with canonical ordering.
- No CLI in this tranche.
- No web server, REST API, Render service, database, or browser runtime.

### Partitura API boundary

Only public/stable-facing Partitura surfaces required by this tranche should be consumed:

- `partitura.load_musicxml(..., force_note_ids="keep")`;
- `Score.parts`;
- `Part.measures`;
- `Part.iter_all(...)`;
- `Part.note_array(...)` only where it reduces duplication without losing relation semantics;
- score objects such as `Note`, `TimeSignature`, `KeySignature`, and `Clef`;
- note `tie_prev` / `tie_next` relations.

Do not import private helpers whose names begin with `_`.

### Identity rule

- Preserve MusicXML/Partitura note IDs when present.
- `source_id` is `str | None`.
- Do not fabricate a source ID when the input has none.
- Missing IDs produce explicit diagnostics.
- ST editor identities such as `SemanticAddressV3` are not generated here.

### Ordering rule

Canonical note ordering is:

`(part_index, onset_div, measure_index, staff_or_max, voice_or_max, pitch_midi, source_id_or_empty, source_ordinal)`

`source_ordinal` is an adapter-local deterministic ordinal from the Partitura traversal and is used only as a final stable tie-breaker. It is not exposed as semantic identity.

### Measure-index rule

`measure_index` is zero-based within each Part and is derived from the ordered `Part.measures` timeline, not from MusicXML measure labels/numbers.

### Timing rule

- `onset_div` and `duration_div` preserve Partitura division-domain integer timing.
- Grace notes may have `duration_div == 0`.
- Negative onset or duration is invalid.
- No float conversion is used for the canonical division fields.

## Target file map

```text
.
├── pyproject.toml
├── README.md
├── docs/
│   ├── DEPENDENCIES.md
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-09-27-st-score-semantic-engine-design.md
│       └── plans/
│           └── 2026-09-27-st-score-semantic-engine-sem01-sem03.md
├── src/
│   └── st_score_semantic_engine/
│       ├── __init__.py
│       ├── model.py
│       ├── serialization.py
│       ├── adapters/
│       │   ├── __init__.py
│       │   └── partitura_musicxml.py
│       └── validators/
│           ├── __init__.py
│           ├── measure.py
│           ├── timing.py
│           ├── voice_staff.py
│           ├── ties.py
│           └── suite.py
├── tests/
│   ├── fixtures/
│   │   ├── semantic_baseline.musicxml
│   │   └── semantic_baseline.expected.json
│   ├── test_model.py
│   ├── test_serialization.py
│   ├── test_partitura_musicxml.py
│   └── test_validators.py
└── .github/
    └── workflows/
        └── ci.yml
```

## Public contract to implement

### `src/st_score_semantic_engine/model.py`

Use frozen dataclasses and tuples.

```python
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
```

`schema_version` constants:

- snapshot: `st-semantic-snapshot-v1`
- report: `st-semantic-validation-report-v1`

No additional public contract should be added during SEM-01 to SEM-03 unless required by a failing test or the approved design.

---

# Task 1 — SES-40 / SEM-01A: Bootstrap package and test harness

## Files

Create:

- `pyproject.toml`
- `src/st_score_semantic_engine/__init__.py`
- `tests/test_model.py`
- `docs/DEPENDENCIES.md`
- `.github/workflows/ci.yml`

Update:

- `README.md`

## Step 1 — RED: package import test

Write `tests/test_model.py` first:

```python
def test_package_exposes_schema_versions():
    import st_score_semantic_engine as semantic

    assert semantic.SNAPSHOT_SCHEMA_VERSION == "st-semantic-snapshot-v1"
    assert semantic.REPORT_SCHEMA_VERSION == "st-semantic-validation-report-v1"
```

Run:

```bash
python -m pytest tests/test_model.py -q
```

Expected: FAIL because the package does not exist.

## Step 2 — GREEN: minimal package scaffold

Create `pyproject.toml` with:

- `requires-python = ">=3.10,<3.13"`
- dependency `partitura==1.9.0`
- dev extras for `pytest`, `ruff`, `mypy`, `build`
- setuptools `src` package discovery.

Create `__init__.py` with only the two schema constants.

Run:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_model.py -q
```

Expected: PASS.

## Step 3 — Add dependency boundary documentation

`docs/DEPENDENCIES.md` must record:

- Partitura 1.9.0;
- upstream repository;
- Apache-2.0 license;
- no Partitura source copied;
- version upgrades require fixture requalification;
- no runtime consumer coupling implied.

## Step 4 — CI baseline

Add `.github/workflows/ci.yml` matrix:

- Python 3.10
- Python 3.11
- Python 3.12

For each:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
ruff check .
mypy src
python -m build
```

Do not add deployment jobs.

## Step 5 — Verify

Run locally/current execution environment where available:

```bash
python -m pytest -q
ruff check .
mypy src
python -m build
```

## Commit

```text
chore: bootstrap semantic engine package and CI
```

Completion mapping: first half of SES-40.

---

# Task 2 — SES-40 / SEM-01B: Lock immutable contracts and canonical serialization

## Files

Create:

- `src/st_score_semantic_engine/model.py`
- `src/st_score_semantic_engine/serialization.py`
- `tests/test_serialization.py`

Update:

- `src/st_score_semantic_engine/__init__.py`

## Step 1 — RED: immutable contract tests

Add tests proving:

1. `SemanticNote` cannot be mutated.
2. `SemanticSnapshot.notes` is a tuple.
3. empty snapshot serializes with explicit schema version.
4. canonical serialization is byte-stable across repeated calls.

Example:

```python
def test_semantic_note_is_immutable():
    note = SemanticNote(...)
    with pytest.raises(FrozenInstanceError):
        note.pitch_midi = 61
```

Run:

```bash
python -m pytest tests/test_model.py tests/test_serialization.py -q
```

Expected: FAIL before model/serializer implementation.

## Step 2 — GREEN: implement contracts

Implement exactly the public contract listed above.

Do not add Partitura imports to `model.py`.

This guarantees the ST-owned contract is independent from the upstream object model.

## Step 3 — GREEN: canonical serializer

Expose:

```python
def snapshot_to_dict(snapshot: SemanticSnapshot) -> dict[str, object]: ...
def snapshot_to_json(snapshot: SemanticSnapshot) -> str: ...
def report_to_dict(report: ValidationReport) -> dict[str, object]: ...
def report_to_json(report: ValidationReport) -> str: ...
```

Canonical JSON requirements:

```python
json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
)
```

Enums serialize to their string values. Tuples serialize as arrays.

## Step 4 — Verify

```bash
python -m pytest tests/test_model.py tests/test_serialization.py -q
ruff check src tests
mypy src
```

## Commit

```text
feat: define immutable semantic contracts and serialization
```

Completion mapping: SES-40 complete only after the broad package checks also pass.

After fresh verification, update Linear SES-40 to Done and set SES-41 In Progress.

---

# Task 3 — SES-41 / SEM-02A: Add controlled MusicXML fixture and prove the adapter gap

## Files

Create:

- `tests/fixtures/semantic_baseline.musicxml`
- `tests/fixtures/semantic_baseline.expected.json`
- `tests/test_partitura_musicxml.py`
- `src/st_score_semantic_engine/adapters/__init__.py`

## Fixture requirements

Create a minimal repository-owned MusicXML fixture containing:

- one Part with explicit part ID;
- two measures;
- 4/4 time signature;
- explicit clef;
- explicit key signature;
- voice 1 and voice 2;
- staff values;
- at least one tied note spanning a measure boundary;
- explicit stable MusicXML note IDs.

Do not copy a copyrighted musical work. Use an original synthetic test sequence.

## Step 1 — Establish expected JSON independently

Write `semantic_baseline.expected.json` by inspection of the fixture, not by dumping adapter output.

It must encode expected:

- part count;
- measure count;
- notes;
- division timing;
- voices;
- staves;
- ties;
- time signature;
- key signature;
- clef.

## Step 2 — RED: adapter contract test

Test intended public API:

```python
from st_score_semantic_engine.adapters.partitura_musicxml import (
    load_musicxml_snapshot,
)

snapshot = load_musicxml_snapshot(FIXTURE)
assert snapshot_to_dict(snapshot) == EXPECTED
```

Run:

```bash
python -m pytest tests/test_partitura_musicxml.py -q
```

Expected: FAIL because adapter does not exist.

## Commit after RED test/fixture

```text
test: define deterministic MusicXML semantic baseline
```

Do not change production implementation in this commit.

---

# Task 4 — SES-41 / SEM-02B: Implement Partitura MusicXML adapter

## Files

Create:

- `src/st_score_semantic_engine/adapters/partitura_musicxml.py`

Update if necessary:

- `tests/test_partitura_musicxml.py`

## Public API

```python
def load_musicxml_snapshot(path: str | Path) -> SemanticSnapshot:
    ...
```

No alternate public adapter API in this tranche.

## Step 1 — Load without rewriting identity

Use:

```python
score = partitura.load_musicxml(
    path,
    force_note_ids="keep",
)
```

Do not call `save_musicxml`.

## Step 2 — Extract parts and measures

For each part in `score.parts`:

- preserve `part.id`;
- enumerate `part.measures` in timeline order;
- build an internal mapping from measure timeline interval to zero-based `measure_index`.

If a note cannot be assigned to a measure, store `measure_index = -1` and emit `INVALID_MEASURE_INDEX`; do not guess a measure.

## Step 3 — Extract notes

Iterate Partitura notes through public score traversal.

For each note:

- `source_id = note.id`;
- `pitch_midi = note.midi_pitch`;
- `onset_div = note.start.t`;
- `duration_div = note.end.t - note.start.t`;
- `voice = note.voice`;
- `staff = note.staff`;
- `tie_prev = note.tie_prev.id if linked and ID exists else None`;
- `tie_next = note.tie_next.id if linked and ID exists else None`;
- `is_grace` from Partitura note/grace semantics.

If a linked tie object exists but lacks an ID, emit `UNRESOLVED_TIE_REFERENCE`.

If a note ID is missing, preserve `None` and emit `MISSING_SOURCE_ID`.

Do not create synthetic IDs.

## Step 4 — Extract contexts

Using public score objects:

- `TimeSignature`: `part_id`, `onset_div`, `beats`, `beat_type`;
- `KeySignature`: `part_id`, `onset_div`, `fifths`, `mode`;
- `Clef`: `part_id`, `onset_div`, `staff`, `sign`, `line`, `octave_change`.

If the input omits a context and Partitura only supplies an inferred default through a map, do not invent a source event in the snapshot. Snapshot context arrays represent explicit imported context objects only.

## Step 5 — Sort canonically

Sort semantic notes using the fixed ordering rule in this plan.

Sort contexts by:

`(part_index, onset_div, staff when applicable, remaining semantic fields)`.

## Step 6 — GREEN

Run:

```bash
python -m pytest tests/test_partitura_musicxml.py -q
```

Expected: fixture equality PASS.

## Step 7 — Add determinism and identity regression tests

Add:

- repeated calls produce identical `snapshot_to_json`;
- note IDs equal fixture IDs;
- tie endpoints are reciprocal;
- measure indices match expected zero-based indices;
- no unexpected adapter diagnostics for the valid fixture.

Run the file again.

## Step 8 — Broad verification

```bash
python -m pytest -q
ruff check .
mypy src
python -m build
```

## Commit

```text
feat: add deterministic Partitura MusicXML adapter
```

After fresh verification, update Linear SES-41 to Done and set SES-42 In Progress.

---

# Task 5 — SES-42 / SEM-03A: Add baseline validators using model-only tests

## Files

Create:

- `src/st_score_semantic_engine/validators/__init__.py`
- `src/st_score_semantic_engine/validators/measure.py`
- `src/st_score_semantic_engine/validators/timing.py`
- `src/st_score_semantic_engine/validators/voice_staff.py`
- `src/st_score_semantic_engine/validators/ties.py`
- `src/st_score_semantic_engine/validators/suite.py`
- `tests/test_validators.py`

## Design rule

Validator unit tests must construct `SemanticSnapshot` values directly.

They must not require Partitura or parse MusicXML. This keeps validation behavior independent from the adapter implementation.

## Step 1 — RED: measure validator tests

Public function:

```python
def validate_measure_membership(
    snapshot: SemanticSnapshot,
) -> tuple[Diagnostic, ...]:
    ...
```

Cases:

- valid indices → no diagnostic;
- negative index → `INVALID_MEASURE_INDEX`;
- index >= `measure_count` → `INVALID_MEASURE_INDEX`.

Run focused test. Expected RED.

Implement smallest code. Run GREEN.

## Step 2 — RED/GREEN: timing validator

Public function:

```python
def validate_timing(
    snapshot: SemanticSnapshot,
) -> tuple[Diagnostic, ...]:
    ...
```

Rules:

- `onset_div < 0` → `INVALID_ONSET`;
- `duration_div < 0` → `INVALID_DURATION`;
- `duration_div == 0` is allowed only for `is_grace=True`;
- non-grace zero duration → `INVALID_DURATION`.

RED → GREEN.

## Step 3 — RED/GREEN: voice/staff validator

Public function:

```python
def validate_voice_staff(
    snapshot: SemanticSnapshot,
) -> tuple[Diagnostic, ...]:
    ...
```

Rules:

- `voice is None` → `MISSING_VOICE`;
- `voice <= 0` → `INVALID_VOICE`;
- `staff is None` → `MISSING_STAFF`;
- `staff <= 0` → `INVALID_STAFF`.

Do not auto-assign voice or staff.

RED → GREEN.

## Step 4 — RED/GREEN: tie validator

Public function:

```python
def validate_ties(
    snapshot: SemanticSnapshot,
) -> tuple[Diagnostic, ...]:
    ...
```

Rules for non-null endpoints:

1. referenced ID must exist;
2. `A.tie_next == B.id` requires `B.tie_prev == A.id`;
3. tied notes must have identical `pitch_midi`.

Diagnostics:

- missing target → `UNRESOLVED_TIE_REFERENCE`;
- missing reciprocal relation → `NON_RECIPROCAL_TIE`;
- pitch mismatch → `TIE_PITCH_MISMATCH`.

If duplicate non-null source IDs exist, treat tie resolution as unsupported for those IDs and emit `UNSUPPORTED_STRUCTURE`; do not choose one arbitrarily.

RED → GREEN.

## Commit

```text
feat: add baseline semantic validators
```

---

# Task 6 — SES-42 / SEM-03B: Aggregate ValidationReport and end-to-end fixture proof

## Files

Update:

- `src/st_score_semantic_engine/validators/suite.py`
- `src/st_score_semantic_engine/validators/__init__.py`
- `tests/test_validators.py`
- `tests/test_partitura_musicxml.py`
- `README.md`

## Public API

```python
def validate_snapshot(snapshot: SemanticSnapshot) -> ValidationReport:
    ...
```

Aggregation order must be fixed:

1. adapter-origin diagnostics already on snapshot;
2. measure diagnostics;
3. timing diagnostics;
4. voice/staff diagnostics;
5. tie diagnostics.

Then canonical-sort diagnostics by:

`(severity, code, source_id_or_empty, message)`

Status rule:

- any `UNSUPPORTED_STRUCTURE` diagnostic → `UNSUPPORTED`;
- otherwise any WARNING or ERROR diagnostic → `DIAGNOSTIC`;
- otherwise → `PASS`.

Do not interpret `PASS` as correctness beyond the implemented validators.

## RED: end-to-end baseline report

For the valid fixture:

```python
snapshot = load_musicxml_snapshot(FIXTURE)
report = validate_snapshot(snapshot)
assert report.status is ValidationStatus.PASS
assert report.diagnostics == ()
```

Expected RED before suite implementation.

## GREEN

Implement the aggregator and rerun.

## Negative end-to-end tests

Create model-only snapshots proving:

- missing voice produces DIAGNOSTIC;
- broken tie produces DIAGNOSTIC;
- duplicate tie identity produces UNSUPPORTED.

Do not add malformed MusicXML unless a Partitura parsing behavior itself needs regression coverage.

## README

Document only:

- what the engine is;
- what it is not;
- supported first-phase API;
- Python/Partitura baseline;
- minimal Python usage example;
- authority boundaries;
- no deployment.

Do not advertise integration with consumer repos as completed.

## Commit

```text
feat: aggregate semantic validation reports
```

---

# Task 7 — Final qualification for SES-40/41/42 branch

## Fresh verification commands

Run all:

```bash
python -m pytest -q
ruff check .
mypy src
python -m build
```

If GitHub Actions is available on the exact head, require CI PASS for Python 3.10, 3.11, and 3.12 before claiming branch qualification.

## Manual contract checks

Confirm:

- no `save_musicxml` call;
- no network/server framework dependency;
- no Render config/service creation;
- no consumer repository edits;
- no Student runtime dependency;
- no ScoreGraph or Editor Core canonical contract copied/replaced;
- no Partitura source copied into repository;
- only public Partitura APIs are used;
- no secrets/tokens committed.

## Final review

Run an independent whole-branch review against:

- approved design;
- SES-40;
- SES-41;
- SES-42;
- Codex Engineering Guardrails.

Important/Critical findings require a test-first fix before closeout.

Minor findings are reported rather than silently expanding scope.

## Completion reporting

For each Linear task, use:

```text
COMPLETED: <SES-ID — title>
RESULT: <observable result>
VERIFICATION: <fresh commands / CI evidence>
NOTION: <updated page>
LINEAR: <updated issue>
RENDER: UNCHANGED
BLOCKERS: <none or exact blocker>
NEXT: <next SES-ID — exact title>
NEXT START CONDITION: <exact gate>
```

Final SEM-03 report must set NEXT to:

`Consumer integration architecture gate — Editor Core read-only semantic comparison`

but must not start that integration without separate user approval.

---

# Stop conditions

Stop and request a new design/spec decision if implementation would require any of the following:

- changing the canonical snapshot semantics defined here;
- adding MusicXML mutation/write-back;
- adding a server or deployment;
- adding browser/runtime Partitura;
- editing a consumer repository;
- generating or replacing Editor Core identity;
- adding guitar string/fret optimization;
- widening OMR correction/apply authority;
- depending on private Partitura internals;
- accepting nondeterministic output as normal.

# Approval gate

This plan is ready for human review.

Approval authorizes execution of SES-40 → SES-41 → SES-42 in this repository under TDD and the stated stop conditions. It does not authorize merge to `main`, deployment, or consumer integration.
