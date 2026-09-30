# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive outer-surface reconstruction for OrcaSlicer.

This fork investigates a **stock-Orca plugin** that uses Orca's final simplified outer-wall geometry (including ZAA where Orca applies it), measures remaining surface error, then refines only the outer wall where the requested tolerance is not met.

> Status: specification / pre-implementation audit complete. Legacy Smoothificator scripts are preserved as upstream reference.

## Canonical architecture
```text
Stock Orca
  -> normal slicing / ZAA
  -> path simplification
  -> posSimplifyPath: copy final geometry
  -> Analyzer creates immutable SubEdgePlan
       -> Plugin Preview uses same plan
  -> normal Orca G-code generation
  -> psGCodePostProcess:
       match plan
       rewrite upper outer-wall flow
       inject intermediate passes
  -> file/printer
```

No custom Orca build is required for v1.

## Important design correction
Sub-edges are **not simply extra material**.

For a refined structural-layer interval, outer-wall extrusion is redistributed across:
- optimized intermediate passes; and
- the original upper outer-wall path with reduced remaining effective height.

This avoids over-extruding the original upper wall.

## Core rules
- final post-simplification geometry is the baseline;
- ZAA is automatically included when Orca applied it;
- Z values are freely optimized;
- v1 uses one common Z schedule for an entire matched external-wall loop;
- non-crossing intermediate passes print lower-Z first;
- initial 0.4 mm-nozzle minimum pass height is 0.08 mm;
- all domain coordinates are absolute print-space mm;
- Preview and Injection share one deterministic plan/hash;
- G-code execution is parser-based, stateful, atomic, idempotent and all-or-nothing.

## Preview
Orca standard G-code viewer shows pre-post-process G-code.

The plugin provides a separate preview of the exact immutable plan, including:
- intermediate contours;
- rewritten upper wall;
- pass Z/heights;
- residual error;
- predicted metrics;
- injection status.

## v1 safety scope
Physical injection starts intentionally narrow: one object, one instance, one positive model volume, one tool, By-Layer printing, absolute XYZ, relative E, arc fitting/scarf/fuzzy/vase disabled, and no other mutating postprocessor.

Unsupported configurations may be analyzed but are not injected.

## Documentation
- [Specification](docs/SPECIFICATION.md)
- [Implementation specification](docs/IMPLEMENTATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Pre-implementation audit](docs/PRE_IMPLEMENTATION_AUDIT.md)
- [Surface/flow model](docs/ERROR_MODEL.md)
- [ZAA integration](docs/ZAA_INTEGRATION.md)
- [Plugin requirements](docs/PLUGIN_REQUIREMENTS.md)
- [Orca API research](docs/ORCASLICER_PLUGIN_RESEARCH.md)
- [Upstream analysis](docs/SMOOTHIFICATOR_ANALYSIS.md)
- [Roadmap](docs/ROADMAP.md)
- [ADR process](docs/ADR_PROCESS.md)

## License
GNU GPL terms and upstream copyright notices are retained.
