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

## Initial baseline

- Python: `>=3.10,<3.13`
- Partitura: `1.9.0`
- Snapshot schema: `st-semantic-snapshot-v1`
- Validation report schema: `st-semantic-validation-report-v1`

The first implementation sequence is tracked in
`docs/superpowers/plans/2026-09-27-st-score-semantic-engine-sem01-sem03.md`.

## Authority boundaries

Editor Core `ScoreDocumentV3 + NotationDocumentV4`,
`EditorSessionV4 / EditorHistoryV4`, and `SemanticAddressV3` remain authoritative in their
existing domains. Student runtime receives no Python/Partitura dependency in this phase. OMR
correction/apply authority is unchanged.

No Render service or public runtime deployment is part of the initial phase.
