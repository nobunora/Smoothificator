# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive outer-surface reconstruction for OrcaSlicer.

This fork investigates a **stock-Orca plugin** that reads Orca's final simplified outer-wall geometry (including ZAA where Orca applied it), measures remaining surface error, then adds only the extra surface-band paths needed to reduce that error.

> Status: specification / pre-implementation consistency work. Project-template agent/workflow rules are integrated; production implementation remains gated on the final full-text audit and a validated repository-review handoff. Legacy Smoothificator scripts are preserved as upstream reference.

## Canonical architecture

```text
Stock Orca
  -> normal slicing / ZAA
  -> path simplification
  -> posSimplifyPath:
       copy final geometry
       normalize ZAA Z + local flow
       build immutable SubEdgePlan
       -> Plugin Preview uses same plan
  -> normal Orca G-code generation
  -> psGCodePostProcess:
       match exactly one plan
       inject additive SubEdge paths
       restore validated machine state
  -> file/printer
```

No custom Orca build is required for v1.

## Core ideas

- ZAA is used first where Orca applies it.
- Source mesh intersections are **material boundaries**, not nozzle centerlines.
- The planner derives one or more printable centerlines inside the residual surface band.
- Multiple paths may share one Z or use different Z values.
- The initial 0.08 mm constraint applies to **effective bead height above local support**, not pairwise path-Z spacing.
- Candidate flow is optimized with a finite-bead model.
- Original Orca structural/ZAA extrusion remains unchanged in v1.
- Final quality is predicted from structural beads + candidate SubEdge beads together.
- Preview and injection share one deterministic plan/hash.
- G-code injection is parser-based, streaming, validated, idempotent, atomic and all-or-nothing.

## Preview

Orca standard G-code viewer shows pre-post-process G-code.

The plugin provides a separate preview from the exact immutable plan:
- baseline/ZAA paths;
- target surface boundary;
- planned centerlines;
- bead height/flow;
- support/nesting diagnostics;
- residual-error map;
- predicted metrics;
- injection status.

## v1 safety scope

Physical injection is intentionally narrow:
- one object / one printable instance / one ModelPart volume;
- current validated Bambu 0.4 mm single-tool profile family;
- relative E;
- firmware retract, arc fitting, line numbering, spiral, ironing, scarf, support/raft disabled;
- no classic post-process script;
- no other slicing-pipeline plugin;
- nested/self-supported target geometry;
- fresh current-session slice.

Unsupported configurations may be analyzed but are not injected.

## Implementation workflow

Repository/AI work begins with [AGENTS.md](AGENTS.md).

The canonical system specification remains `docs/SPECIFICATION.md`. Versioned Codex/GitHub handoff contracts live under `docs/specs/`, and implementation/review evidence lives under `docs/implementation/`.

Production implementation starts only after the final consistency audit and a review-only repository validation returns `validated`.

## Documentation

- [Agent/repository rules](AGENTS.md)
- [Specification](docs/SPECIFICATION.md)
- [v1 handoff specification](docs/specs/adaptive-subedge-v1.md)
- [Implementation specification](docs/IMPLEMENTATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Dependency/feasibility audit](docs/DEPENDENCY_AUDIT.md)
- [Surface/flow model](docs/ERROR_MODEL.md)
- [ZAA integration](docs/ZAA_INTEGRATION.md)
- [Plugin requirements](docs/PLUGIN_REQUIREMENTS.md)
- [Orca API research](docs/ORCASLICER_PLUGIN_RESEARCH.md)
- [Upstream analysis](docs/SMOOTHIFICATOR_ANALYSIS.md)
- [Roadmap](docs/ROADMAP.md)
- [Test strategy](docs/TEST_STRATEGY.md)
- [Quality gates](docs/QUALITY_GATES.md)
- [Review/convergence process](docs/REVIEW_PROCESS.md)
- [Project-template rule adoption](docs/PROJECT_RULES_ADOPTION.md)
- [Documentation precedence](docs/DOCUMENT_CONTRACT.md)
- [ADR process](docs/ADR_PROCESS.md)

## License

GNU GPL terms and upstream copyright notices are retained.
