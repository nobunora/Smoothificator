# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive outer-surface reconstruction for OrcaSlicer.

This fork investigates a **stock-Orca plugin** that reads Orca's final simplified outer-wall geometry (including ZAA where Orca applied it), measures remaining surface error, then adds only the extra surface-band paths needed to reduce that error.

> Status: 2026-10-01 full consistency + technical audit complete. Phase 0.5 implementation is gated only on repository revalidation against the new audited manifest; physical injection remains separately gated. Legacy Smoothificator scripts are preserved as upstream reference.

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
       validate both fingerprints
       match structural geometry uniquely
       derive machine translation + Orca quantization
       validate retraction / Zsafe / downstream clearance
       inject additive SubEdge paths
       restore exact parsed machine state
  -> file/printer
```

No custom Orca build is required for v1.

## Core ideas

- ZAA is used first where Orca applies it.
- Source mesh intersections are **material boundaries**, not nozzle centerlines.
- The planner derives one or more printable centerlines inside the residual surface band.
- Multiple paths may share one Z or use different Z values; each printable v1 SubEdgePath itself is constant-Z.
- The initial 0.08 mm constraint applies to **effective bead height above local support**, not pairwise path-Z spacing.
- Candidate geometry uses a finite-bead model; geometric bead volume and commanded/calibrated extrusion volume are separate.
- Final completed-surface scoring is separated from chronological support: no candidate may rely on material that has not been printed yet.
- Final physical clearance validates both plugin-generated motion and resumed original Orca motion against the same ToolClearanceProfile.
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
- one object / one total source instance / one ModelPart manifold volume;
- current validated Bambu 0.4 mm single-tool profile family;
- relative E and provable saved retraction state;
- firmware retract, arc fitting, adaptive PA, adaptive volumetric speed, fuzzy skin, line numbering, spiral, ironing, scarf, support/raft disabled where required;
- no first-layer refinement;
- no classic post-process script;
- no other slicing-pipeline capability besides this plugin;
- nested/self-supported target geometry;
- explicit hardware ToolClearanceProfile and downstream original-motion clearance validation;
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
- [Full consistency + technical audit](docs/FULL_CONSISTENCY_AUDIT_2026-10-01.md)
- [Audited revision manifest](docs/AUDIT_REVISION_2026-10-01.md)
- [Earlier dependency/feasibility audit](docs/DEPENDENCY_AUDIT.md)
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
