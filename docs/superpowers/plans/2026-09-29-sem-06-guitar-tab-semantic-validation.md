# SEM-06 — Guitar TAB Read-Only Semantic Validation Implementation Plan

Date: 2026-09-29  
Status: REVIEW REQUIRED — NO PRODUCTION IMPLEMENTATION YET  
Architecture gate: SES-67  
Plan gate: SES-99  
Primary implementation repository: `khfy7wpr5p-maker/musicxml-to-guitar-tab-engine`  
Reference repository: `khfy7wpr5p-maker/st-score-semantic-engine`

## Goal

Add a bounded, artifact-based semantic validation sidecar to Guitar TAB Engine while preserving its exclusive authority over editable TAB generation, arrangement, and string/fret decisions.

## Global guardrails

Every task must preserve all of the following:

1. Guitar TAB Engine remains sole string/fret/fingering/arrangement authority.
2. Semantic Engine evidence is read-only and non-blocking for otherwise feasible editable TAB.
3. Partitura is not added as a Guitar TAB Engine runtime dependency.
4. No REST/network/Render service is introduced.
5. No MusicXML write-back or automatic correction is introduced.
6. Source bytes and existing canonical/arrangement models remain immutable.
7. RED → GREEN TDD is required before refactor.
8. Merge requires exact-head verification and whole-branch Guardrails review.

## Task 1 — Pin a semantic reference bundle

Target: `musicxml-to-guitar-tab-engine`

Create a repository-owned bounded fixture bundle containing:

- exact MusicXML source bytes;
- source SHA-256;
- Semantic Engine JSON snapshot generated from the same source;
- Semantic Engine commit;
- snapshot schema version;
- Partitura version;
- explicit supported-profile metadata.

Tests first:

- exact provenance admits the bundle;
- source SHA mismatch => semantic `UNSUPPORTED`;
- engine/schema/version mismatch => semantic `UNSUPPORTED`;
- malformed artifact => semantic `UNSUPPORTED`;
- no test may turn those cases into a Guitar TAB generation block.

Acceptance:
- no runtime Semantic Engine invocation;
- no network;
- no dependency change.

## Task 2 — Add immutable Guitar source semantic projection

Add the smallest pure projection from the already-admitted Guitar source model needed for comparison.

Projection fields:

- part/measure;
- pitch MIDI;
- exact local onset;
- exact duration;
- voice;
- staff;
- bounded tie role;
- meter;
- key context where deterministic;
- clef context where deterministic.

Do not include:
- string;
- fret;
- finger;
- barre;
- hand position;
- arrangement score or preference.

Tests first:

- stable deterministic ordering;
- source object fingerprint unchanged;
- unsupported/ambiguous structural mapping fails closed to semantic `UNSUPPORTED`;
- duplicate-unison ambiguity does not guess identity.

## Task 3 — Add deterministic semantic comparator

Implement a pure comparator between the Guitar source projection and admitted SemanticSnapshot.

Output:
- `PASS`;
- `DIAGNOSTIC`;
- `UNSUPPORTED`.

Requirements:

- deterministic diagnostic ordering;
- no raw cross-engine object-ID equality;
- exact timing normalization only;
- mismatch diagnostics for pitch/onset/duration/voice/staff/tie/context;
- ambiguity => `UNSUPPORTED`, not guessed alignment.

Tests first:

- unchanged fixture => `PASS`;
- one bounded semantic mismatch => `DIAGNOSTIC`;
- ambiguous mapping => `UNSUPPORTED`;
- provenance mismatch prevents `PASS`.

## Task 4 — Add SemanticTabValidationPacketV1 sidecar

Create an immutable packet that carries comparator result and provenance.

Required authority flags:

- `resolverEligible = false`;
- `selectorEligible = false`;
- `arrangementAuthority = false`;
- `automaticCorrectionAuthority = false`;
- `tabGenerationBlocking = false`.

Non-interference tests must prove the packet is not consumed by:
- source retention/reduction policy;
- string/fret selector;
- physical validator;
- canonical final selector;
- writer;
- teacher-edit mutation authority.

A semantic `DIAGNOSTIC` or `UNSUPPORTED` packet must leave the same Guitar TAB result as the baseline pipeline for the same feasible input.

## Task 5 — Qualify through the real editable-TAB path

Exercise the existing real conversion/workbench path with the pinned fixture.

Required cases:

1. Semantic PASS + feasible MusicXML => editable TAB produced.
2. Semantic DIAGNOSTIC + feasible MusicXML => same editable TAB produced, diagnostic attached separately.
3. Semantic UNSUPPORTED + feasible MusicXML => same editable TAB produced, unsupported evidence attached separately.
4. Semantic artifact absent => baseline behavior unchanged.
5. Existing Guitar engine capability/safety block => remains blocked for the same pre-existing reason; semantic packet does not override it.

Capture fingerprints of selected source events and string/fret output before and after semantic integration to prove non-interference.

## Task 6 — Documentation and quality gates

Update consumer architecture documentation to state:

- semantic evidence is sidecar-only;
- Guitar TAB Engine remains authority;
- unsupported evidence is non-blocking;
- no runtime network/Partitura dependency exists.

Run the repository's configured:
- focused tests;
- full test suite;
- lint/type/static checks;
- dependency checks;
- exact-head CI.

Finish with whole-branch Codex Engineering Guardrails review.

## Recommended issue split after plan approval

Create implementation issues only after SES-99 is explicitly approved:

- SEM-06A — pin semantic reference bundle;
- SEM-06B — Guitar source semantic projection;
- SEM-06C — deterministic comparator;
- SEM-06D — isolated validation packet + non-interference proof;
- SEM-06E — real editable-TAB path qualification and docs.

Each issue must be independently testable and must not grant merge/deploy authority.

## Stop conditions

Stop and return to architecture review if implementation requires any of the following:

- Semantic Engine choosing or ranking string/fret;
- semantic diagnostics suppressing feasible editable TAB;
- browser/runtime Partitura;
- network service;
- MusicXML mutation;
- new automatic correction authority;
- changing canonical/arrangement authority;
- weakening existing Guitar TAB safety gates.

## Approval requested

Explicit user approval of SES-99 is required before Task 1 production implementation starts.
