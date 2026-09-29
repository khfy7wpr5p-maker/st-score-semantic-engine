# SEM-06 — Guitar TAB Read-Only Semantic Validation Architecture

Date: 2026-09-29  
Status: APPROVED ARCHITECTURE / IMPLEMENTATION PLAN PENDING APPROVAL  
Linear architecture gate: https://linear.app/seslitab/issue/SES-67/sem-06-guitar-tab-read-only-semantic-validation-architecture-gate  
Linear plan gate: https://linear.app/seslitab/issue/SES-99/sem-06p-guitar-tab-semantic-validation-implementation-plan-approval  
Notion handoff: https://app.notion.com/p/3ea2be2e5664813ca23ff78aa4c47fe7?pvs=204

## 1. Purpose

Add read-only musical-semantic validation between ST Score Semantic Engine and `musicxml-to-guitar-tab-engine` without transferring guitar arrangement authority.

The integration exists to detect source-semantic mismatch, ambiguity, or unsupported evidence. It must never become a string/fret selector, arrangement optimizer, automatic corrector, or reason to suppress an otherwise feasible editable TAB result.

## 2. Authority boundaries

### ST Score Semantic Engine

May:
- produce immutable `SemanticSnapshot` and `ValidationReport` evidence;
- provide deterministic source-semantic reference facts;
- emit explicit diagnostics for unsupported/ambiguous input.

May not:
- choose guitar string/fret/finger/barre/hand position;
- mutate MusicXML;
- alter Guitar TAB Engine canonical or arrangement policy;
- create runtime network authority.

### Guitar TAB Engine

Remains sole authority for:
- guitar configuration;
- string/fret assignment;
- fingering and physical-playability policy;
- arrangement/reduction decisions;
- provisional versus canonical TAB state;
- teacher-editable TAB generation;
- export eligibility.

Semantic evidence cannot override those decisions.

### Partitura

Partitura remains an offline/reference parser behind the Semantic Engine boundary. It must not be added to browser, Student App, or Guitar TAB Engine runtime dependencies.

## 3. Integration shape

The first implementation uses an artifact/sidecar model, not a service:

```text
MusicXML
   |
   +------------------------------+
   |                              |
   v                              v
Guitar TAB Engine             Semantic Engine
source admission              offline/reference run
   |                              |
   v                              v
Guitar source projection      SemanticSnapshot + provenance
   |                              |
   +-------------+----------------+
                 v
      Read-only semantic comparator
                 |
                 v
      SemanticTabValidationPacketV1
                 |
                 +----> diagnostics / review UI only
                 |
                 +----> NO selector / arranger / writer authority

Existing Guitar TAB pipeline continues independently:
source model -> arrangement/reduction -> string/fret -> editable TAB
```

No REST endpoint, Render service, browser Python, or background network dependency is added.

## 4. Semantic comparison scope

The comparator may inspect only source-level musical facts that both systems can represent deterministically:

- source fingerprint / provenance;
- part and measure identity;
- pitch MIDI;
- onset and duration;
- voice and staff;
- bounded tie roles;
- meter;
- key signature context;
- clef context where the Guitar source model exposes it deterministically.

The comparator must not compare or score:
- guitar string number;
- fret;
- finger;
- barre;
- hand position;
- voicing preference;
- arrangement quality;
- reduction quality;
- teacher preference.

## 5. Packet contract

A consumer-side immutable packet should expose, at minimum:

- `schemaVersion`;
- `sourceSha256`;
- `semanticEngineCommit`;
- `semanticSnapshotSchemaVersion`;
- `partituraVersion`;
- `status`: `PASS | DIAGNOSTIC | UNSUPPORTED`;
- deterministic diagnostics;
- `resolverEligible: false`;
- `selectorEligible: false`;
- `arrangementAuthority: false`;
- `automaticCorrectionAuthority: false`;
- `tabGenerationBlocking: false`.

The exact consumer-side type name may be refined during implementation, but these authority properties are fixed.

## 6. Generation invariant

For every MusicXML input that the existing Guitar TAB Engine considers feasible for editable TAB generation:

> Semantic evidence must not turn a feasible editable-TAB result into a file-level block.

Therefore:

- Semantic `PASS` may be shown as reference evidence.
- Semantic `DIAGNOSTIC` may request teacher review or annotate the result.
- Semantic `UNSUPPORTED` or low-confidence evidence must remain visible but non-blocking.
- Existing Guitar TAB Engine safety, capability, and physical-playability gates remain unchanged and may still block according to their own current rules.

This architecture does not redefine what the Guitar TAB Engine considers feasible.

## 7. Provenance and admission

Semantic comparison may produce `PASS` only when all required provenance pins match exactly, including:

- MusicXML source SHA-256;
- Semantic Engine commit;
- snapshot schema version;
- supported Partitura version;
- declared source-profile assumptions.

A provenance mismatch, ambiguous structural mapping, unsupported divisions/profile, or duplicate-unison ambiguity must fail closed to `UNSUPPORTED` semantic evidence, not to TAB suppression.

## 8. Non-interference requirements

Tests must prove that adding, removing, or changing the semantic packet cannot:

- alter selected string/fret positions;
- alter source-event retention;
- alter arrangement decisions;
- alter canonical/provisional classification;
- mutate source MusicXML;
- change export eligibility;
- change teacher-edit authority;
- create a new network request.

The semantic packet must not be imported into selector, arrangement, physical-validation, canonical-writer, or mutation-authority modules except where a pure assertion is needed to prove non-interference.

## 9. Failure policy

Unsupported or ambiguous semantic evidence must be explicit and deterministic.

No silent coercion is allowed. No missing semantic fact may be fabricated. No semantic diagnostic may be converted into an automatic source correction.

## 10. Implementation location

The Semantic Engine already provides the qualified `SemanticSnapshot`/validation capability. The first production changes should therefore be consumer-side in `musicxml-to-guitar-tab-engine`, using pinned artifacts and immutable comparison code.

The Semantic Engine repository owns this architecture and reference contract. It does not need a new runtime service.

## 11. Verification contract

Before merge, implementation must provide fresh evidence for:

- focused RED → GREEN unit tests;
- provenance admission;
- deterministic comparator output;
- PASS / DIAGNOSTIC / UNSUPPORTED cases;
- editable-TAB non-blocking behavior;
- selector/arranger/writer non-interference;
- source immutability;
- no new runtime/network dependency;
- repository quality checks;
- exact-head verification;
- whole-branch Codex Engineering Guardrails review.

## 12. Deployment boundary

No Render service, public endpoint, domain, worker, browser Python runtime, or new Student App dependency is authorized.

## 13. Approval boundary

This architecture was explicitly approved by the user on 2026-09-29.

Production implementation remains gated by the separate SEM-06 implementation plan review recorded in SES-99.
