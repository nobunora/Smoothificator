# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive surface reconstruction for OrcaSlicer.

Status: specification / pre-implementation audit complete.

## v1 architecture
Stock Orca only:

```text
fresh slice
  -> ZAA (if applicable)
  -> Orca path simplification
  -> posSimplifyPath Analyzer
  -> immutable SubEdgePlan
       -> plugin Preview
  -> normal G-code generation
  -> psGCodePostProcess: exact-plan validation/injection
  -> output
```

No custom Orca build is required.

## Key rules
- ZAA first; Sub-edge only addresses residual error.
- Added paths may use multiple non-uniform Z values.
- Flow/material overlap is optimized with a finite-bead model.
- Lower/upper structural beads remain part of the final-surface simulation.
- Non-crossing Sub-edges print lower-Z first.
- Preview and Injector consume the same plan hash.
- Injection is parser/state-machine based, streaming, atomic, idempotent and all-or-nothing.
- Missing fresh plan or any ambiguity leaves original Orca output unchanged.

## First printable scope
Intentionally narrow:
- one printable object
- one printable instance
- one ModelPart volume
- one tool
- no modifier/negative volume
- no other slicing-pipeline plugin
- no classic post-process script
- outward/top-facing non-crossing surface

Scope expands only after tests/ADR.

## Documents
- [Specification](docs/SPECIFICATION.md)
- [Implementation](docs/IMPLEMENTATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Error/material model](docs/ERROR_MODEL.md)
- [Plugin/API research](docs/ORCASLICER_PLUGIN_RESEARCH.md)
- [Plugin requirements](docs/PLUGIN_REQUIREMENTS.md)
- [ZAA integration](docs/ZAA_INTEGRATION.md)
- [Dependency audit](docs/DEPENDENCY_AUDIT.md)
- [ADRs](docs/adr/)
- [Roadmap](docs/ROADMAP.md)

Original Smoothificator scripts remain as upstream reference.

## License
GNU GPL terms and upstream notices are retained.
