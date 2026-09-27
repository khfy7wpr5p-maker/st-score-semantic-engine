# Dependency Policy

## Partitura

- Package: `partitura`
- Initial qualified version: `1.9.0`
- Upstream: https://github.com/CPJKU/partitura
- Upstream license: Apache-2.0
- Integration model: dependency through the official public Python API
- Source policy: Partitura source code is not copied or forked into this repository.

The initial version is pinned exactly so repository-owned semantic fixtures can establish a
deterministic baseline. A future Partitura version change is a compatibility task: fixtures and
semantic outputs must be requalified before the supported version changes.

Using Partitura here does not change authority in any consumer repository. In particular, it does
not replace Editor Core canonical state, Student runtime models, ScoreGraph, or OMR correction
authority.
