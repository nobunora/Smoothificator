# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive surface reconstruction for OrcaSlicer.

Status: pre-implementation audit complete; implementation has not started.

## v1 architecture
Stock Orca only:

```text
fresh slice
 -> ZAA if applicable
 -> Orca path simplification
 -> posSimplifyPath Analyzer
 -> immutable SubEdgePlan
      -> Plugin Preview
 -> normal G-code generation
 -> psGCodePostProcess validated Injection
 -> output
```

## Key design rules
- ZAA first; Sub-edge addresses residual error.
- Orca ZAA path Z is normalized from layer-relative offset to absolute nozzle Z.
- ZAA local flow scaling is reproduced in the baseline model.
- 0.08 mm initially means minimum effective bead height above support, not minimum neighbor-path Z difference.
- Shallow slopes may therefore use several paths whose Z values differ by much less than 0.08 mm.
- Mesh intersection is a material boundary, not a nozzle centerline; path layout accounts for bead width.
- Printable v1 targets nested top-facing geometry only.
- Lower/upper structural beads and all added paths are included in final-surface scoring.
- G-code Injection uses safe-ceiling travel and exact state restoration.
- Preview and Injector consume one immutable plan hash.
- Any ambiguity leaves original Orca G-code unchanged.

## First printable scope
- stock supported Orca
- one object / one instance / one ModelPart
- current tested Bambu 0.4 single-tool profile family
- relative E
- no support/raft/ironing/scarf/spiral/arc fitting
- no other slicing-pipeline plugin or classic post-process script
- validated nozzle envelope

Scope expands only by tests + ADR.

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
