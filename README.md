# st-score-semantic-engine

A standalone Python semantic/reference engine for deterministic symbolic-score inspection and
validation across ST projects.

## Role

The engine uses Partitura through its official API and converts supported score information into
ST-owned immutable semantic contracts.

It is **not**:

- a score renderer or engraving engine;
- an editor state/history authority;
- a browser Python runtime;
- a MusicXML mutation/write-back service;
- a replacement for ScoreGraph or existing Editor Core canonical models;
- a deployed REST service.

## Qualified baseline

- Python: `>=3.10,<3.13`
- Partitura: `1.9.0`
- Snapshot schema: `st-semantic-snapshot-v1`
- Validation report schema: `st-semantic-validation-report-v1`

The first implementation sequence is tracked in
`docs/superpowers/plans/2026-09-27-st-score-semantic-engine-sem01-sem03.md`.

## Current public API

`load_musicxml_snapshot(path)` reads MusicXML with Partitura and returns an immutable,
JSON-serializable `SemanticSnapshot`. The current snapshot surface covers:

- source note ID and part ID;
- zero-based measure membership; `measure_count` is the score-wide measure span (maximum ordered measure count across parts);
- MIDI pitch;
- onset and duration in MusicXML/Partitura divisions;
- voice and staff;
- bounded tie relations;
- explicit time signature, key signature, and clef contexts;
- adapter diagnostics when source semantics are missing or unsupported; unpitched notes currently fail closed as `UNSUPPORTED_STRUCTURE`.

`validate_snapshot(snapshot)` runs the baseline read-only validators and returns a deterministic
`ValidationReport` with one of three statuses:

- `PASS` — no current baseline diagnostic;
- `DIAGNOSTIC` — at least one warning/error was found;
- `UNSUPPORTED` — the snapshot contains a structure the current validator cannot resolve safely.

A `PASS` result only covers the validators implemented by this package; it is not a general proof
that a score is musically correct.

## Minimal usage

```python
from st_score_semantic_engine.adapters.partitura_musicxml import load_musicxml_snapshot
from st_score_semantic_engine.serialization import snapshot_to_json
from st_score_semantic_engine.validators import validate_snapshot

snapshot = load_musicxml_snapshot("score.musicxml")
report = validate_snapshot(snapshot)

print(report.status.value)
print(snapshot_to_json(snapshot))
```

The adapter is read-only. It does not call `save_musicxml` and does not modify the source file.

## Authority boundaries

Editor Core `ScoreDocumentV3 + NotationDocumentV4`,
`EditorSessionV4 / EditorHistoryV4`, and `SemanticAddressV3` remain authoritative in their
existing domains. Student runtime receives no Python/Partitura dependency in this phase. OMR
correction/apply authority is unchanged.

No consumer repository integration, Render service, or public runtime deployment is part of this
initial phase.

## Dependency policy

See `docs/DEPENDENCIES.md`. Partitura is consumed as an external Apache-2.0 dependency and its
source is not copied into this repository. A Partitura version change requires semantic fixture
requalification.
