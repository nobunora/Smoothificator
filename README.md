# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive sub-edge surface reconstruction for OrcaSlicer.

This fork investigates a **stock-Orca plugin** that uses ZAA first, measures remaining surface error, then adds only the extra surface contours needed to reach a requested quality target.

> Status: specification / early implementation. Original Smoothificator scripts are preserved as upstream reference.

## Architecture
```text
Stock Orca
  -> normal slicing
  -> ZAA / Z Contouring
  -> posContouring: Analyzer creates immutable SubEdgePlan
       -> plugin Preview uses the same plan
  -> normal Orca G-code generation
  -> psGCodePostProcess: validate + inject the same plan
  -> file/printer
```

No custom Orca build is required for the v1 target.

## Core rules
- ZAA is the low-cost first stage.
- Sub-edges address only residual error.
- Added Z values are freely optimized, not fixed 1/2 or 1/3 subdivisions.
- Multiple non-crossing sub-edges are allowed and printed lower-Z first.
- Initial 0.4 mm-nozzle minimum adjacent Z spacing is 0.08 mm and configurable.
- Preview and injection share one deterministic plan/hash.
- G-code injection is parser-based, validated, idempotent, atomic and all-or-nothing.
- Any ambiguity leaves original Orca output unchanged.

## Preview
Orca's standard G-code viewer displays the pre-post-process file, so injected paths are not automatically shown there.

The plugin provides its own preview from the exact SubEdgePlan later used by the injector, including planned paths, Z values, residual-error visualization and injection status.

## Orca plugin constraints
SlicingPipeline hooks run on the slicing worker thread; they must not call host UI APIs. Live Orca graph references are copied into plugin-owned immutable data before the hook returns.

The preview is opened/refreshed through a UI-safe Script capability.

## Documentation
- [System specification](docs/SPECIFICATION.md)
- [Detailed implementation specification](docs/IMPLEMENTATION.md)
- [Surface error model](docs/ERROR_MODEL.md)
- [ZAA integration](docs/ZAA_INTEGRATION.md)
- [Plugin requirements](docs/PLUGIN_REQUIREMENTS.md)
- [Orca plugin/API research](docs/ORCASLICER_PLUGIN_RESEARCH.md)
- [Upstream Smoothificator analysis](docs/SMOOTHIFICATOR_ANALYSIS.md)
- [Roadmap](docs/ROADMAP.md)

## License
GNU GPL terms and upstream copyright notices are retained.
