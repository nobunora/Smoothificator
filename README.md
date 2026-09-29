# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive sub-edge surface reconstruction for OrcaSlicer.

This fork of **TengerTechnologies/Smoothificator** is researching a geometry-stage surface reconstruction method that works **after OrcaSlicer's Z Anti-Aliasing (ZAA)**.

> Status: design/research. Original Smoothificator scripts are preserved. No production sub-edge printing implementation exists yet.

## Core idea
Use ZAA first because it improves surface geometry with very little added path cost. Then measure the **remaining surface error** against the original model.

Only where ZAA still misses the requested tolerance:
- add zero, one, or multiple intermediate surface contours;
- choose each contour's Z independently;
- use true model geometry rather than fixed 1/2 or 1/3 subdivision;
- print non-crossing contours from lower Z to higher Z;
- stop adding paths as soon as the quality target is met.

Initial 0.4 mm-nozzle research uses 0.08 mm as the configurable minimum adjacent Z spacing.

```text
Orca baseline
    ↓
ZAA / Z Contouring
    ↓
post-ZAA surface-error estimator
    ↓
within tolerance? ── yes → unchanged
    ↓ no
Adaptive Sub-Edge optimizer
    ↓
validated path injection
    ↓
normal Orca downstream pipeline
```

## Orca plugin status
Current Orca Python SlicingPipeline bindings are sufficient for **analysis**: they expose the source model, layers and 3D extrusion paths.

They are **not yet sufficient for final printing** because perimeter paths, path points and layer Z structure are read-only from Python. Arbitrary-Z new extrusion paths cannot currently be inserted through the public binding.

The target architecture is therefore:
- a small Orca C++/pybind path-insertion extension;
- a pure-Python Adaptive Sub-Edge wheel using that extension.

If the insertion API is upstreamed into OrcaSlicer, the feature can become an ordinary installable plugin.

## Documentation
- [System specification](docs/SPECIFICATION.md)
- [Surface error model](docs/ERROR_MODEL.md)
- [Detailed implementation specification](docs/IMPLEMENTATION.md)
- [ZAA integration strategy](docs/ZAA_INTEGRATION.md)
- [Plugin requirements](docs/PLUGIN_REQUIREMENTS.md)
- [OrcaSlicer plugin/API research](docs/ORCASLICER_PLUGIN_RESEARCH.md)
- [Upstream Smoothificator analysis](docs/SMOOTHIFICATOR_ANALYSIS.md)
- [Development roadmap](docs/ROADMAP.md)

## License
This fork retains the upstream GNU GPL licensing terms and copyright notices.
