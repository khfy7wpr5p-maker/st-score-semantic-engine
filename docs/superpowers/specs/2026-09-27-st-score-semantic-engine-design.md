# ST Score Semantic Engine — Architecture Design

Date: 2026-09-27  
Status: APPROVED  
Linear gate: SES-39  
Notion source: https://app.notion.com/p/3e82be2e5664818f9f9ed0a9a86ea0ba?pvs=204

## 1. Problem

ST projects need a shared, deterministic way to inspect and validate musical semantics across MusicXML, OMR output, editor state, restoration, TAB conversion, and score-following research.

This repository is not a new editor or renderer. It is a standalone semantic/reference layer.

## 2. Scope

The engine will:

1. read controlled MusicXML input, with future ST snapshot adapters added only after separate approval;
2. use Partitura through its official public API;
3. normalize symbolic score semantics into ST-owned immutable snapshots;
4. run read-only semantic validators;
5. emit deterministic validation reports and JSON-compatible fixtures.

## 3. Non-goals

Phase 1 does not include:

- score engraving or visual rendering;
- SVG/DOM hit-testing;
- editor selection or undo/redo;
- browser-side Python;
- Student App runtime dependency on Partitura;
- REST or microservice deployment;
- automatic MusicXML mutation/write-back;
- guitar string/fret optimization;
- OMR recognition;
- replacement of Editor Core canonical models;
- replacement of ScoreGraph.

## 4. Authority boundaries

### Editor Core

The following remain authoritative:

- `ScoreDocumentV3 + NotationDocumentV4` — canonical score state;
- `EditorSessionV4 / EditorHistoryV4` — history authority;
- `SemanticAddressV3` — exact current-revision semantic identity.

The semantic engine may compare or validate these models later through separately approved read-only adapters. It does not become the editor's source of truth.

### Rendering Layer

Renderer output, DOM structure, SVG geometry, and hit-test coordinates remain projection concerns. They are not semantic authoring authority.

### Student App

Partitura may be used only as an offline/reference oracle unless a future architecture decision explicitly changes this boundary.

Phase 1 adds:

- no Python runtime in the browser;
- no Partitura package to Student runtime dependencies;
- no network call to a Partitura service.

### OMR Correction Engine

This engine may later provide semantic evidence. It does not widen correction proposal authority, apply authority, confidence thresholds, or abstention rules.

## 5. Architecture

```text
MusicXML / future approved ST snapshot
                |
                v
          Input Adapter
                |
                v
        Partitura Adapter
                |
                v
        SemanticSnapshot
                |
      +---------+---------+
      |         |         |
      v         v         v
   Measure    Timing    Relation
  Validator  Validator  Validator
      +---------+---------+
                |
                v
        ValidationReport
```

## 6. Initial public contract

The initial public output is a deterministic, JSON-serializable `SemanticSnapshot`.

Initial note semantics:

- `source_id`
- `part_id`
- `measure_index`
- `pitch_midi`
- `onset_div`
- `duration_div`
- `voice`
- `staff`
- `tie_prev`
- `tie_next`

Initial score/context semantics:

- part count;
- measure count;
- time-signature context;
- key-signature context;
- clef context.

The exact Python field names may be refined in the implementation plan, but the semantic meaning above is fixed by this design.

## 7. Determinism rules

For the same repository-owned fixture and the same supported dependency set, repeated execution must yield:

- identical note ordering;
- identical measure membership;
- identical onset/duration values;
- identical voice/staff values;
- identical tie relations;
- byte-stable normalized JSON after canonical serialization.

Output ordering must not depend on renderer order, DOM order, object identity, hash iteration order, or filesystem ordering.

## 8. Failure policy

- Unsupported or ambiguous structures must not be silently coerced.
- Missing information must not be fabricated.
- Parser or semantic uncertainty must produce an explicit diagnostic.
- Consumer authority must not be widened by inference.
- When a safe interpretation is unavailable, return an explicit `UNKNOWN` or `UNSUPPORTED` diagnostic and fail closed for validation decisions.

## 9. Dependency policy

- Package language: Python.
- Minimum Python baseline: 3.10, matching Partitura 1.9.0's declared minimum.
- Initial Partitura version: exactly `1.9.0` for deterministic baseline qualification.
- Partitura source is not forked or copied into this repository.
- Apache-2.0 dependency attribution is documented; ST-owned code remains independently maintained.
- Browser bundles do not include Python/Partitura.

A future Partitura upgrade is treated as a compatibility task requiring fixture requalification before the supported version changes.

## 10. First vertical slice

### SEM-01 — package/contracts foundation

Create the Python package, immutable semantic contract types, diagnostics model, serialization policy, and test harness.

### SEM-02 — MusicXML to deterministic SemanticSnapshot

Use a repository-owned MusicXML fixture with:

- at least two measures;
- at least two voices or explicit voice/staff information;
- at least one tie relation;
- stable note IDs.

Required extracted semantics:

- source/note reference;
- part;
- measure;
- pitch;
- onset;
- duration;
- voice;
- staff;
- tie relation.

### SEM-03 — baseline read-only validators

Add deterministic validation for:

- measure membership/coverage;
- onset/duration sanity;
- voice/staff presence and normalization;
- bounded tie relation consistency.

No mutation or correction is authorized.

## 11. Verification contract

A tranche may be called complete only with fresh evidence for the changed behavior.

Minimum evidence:

- focused unit tests;
- deterministic snapshot regression;
- canonical JSON serialization regression;
- package import/build check;
- configured lint/type checks;
- dependency/license review record;
- exact-head verification.

## 12. Consumer integration order

After SEM-01 through SEM-03 are qualified, consumer integrations remain separate approval gates:

1. Editor Core read-only semantic comparison;
2. OMR Correction read-only evidence adapter;
3. Score Restore validation fixture;
4. TAB Engine pre/post semantic comparison;
5. Student offline/reference fixtures;
6. Score Following research adapter.

This is an ordering preference, not implementation authority.

## 13. Deployment boundary

Phase 1 has no Render service and no public runtime deployment.

No new Render service, preview URL, domain, web service, or background service may be created under this architecture.

## 14. Acceptance criteria

This architecture is accepted when:

- Partitura is clearly a semantic/reference dependency, not a canonical editor model;
- existing ST authority boundaries remain intact;
- Student runtime has no Python/Partitura coupling;
- write-back/mutation remains out of scope;
- the first vertical slice is small and independently testable;
- every consumer integration remains a separate approval gate.

## 15. Next gate

The approved design authorizes an implementation plan only.

Production code begins only after the implementation plan is reviewed and explicitly approved.
