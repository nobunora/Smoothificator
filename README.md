# Smoothificator — Adaptive Sub-Edge Research Fork

Error-driven adaptive sub-edge surface reconstruction for OrcaSlicer.

This repository is a fork of **TengerTechnologies/Smoothificator**. The upstream project refines outer walls by duplicating outer-wall G-code at smaller, equally spaced Z intervals. This fork is investigating a different architecture: evaluate the geometric error of the slicer's baseline surface **before final G-code generation**, then add only the intermediate surface paths required to reduce that error.

> **Status:** design/research branch. The original Smoothificator scripts are currently preserved. The adaptive geometry engine described below is not yet production-ready.

## Target concept

Instead of forcing a fixed outer-wall pitch such as 0.05 mm, the algorithm will:

1. keep OrcaSlicer's structural/base layer decisions;
2. compare the baseline printable surface with the ideal model;
3. locate outer-surface regions whose error exceeds a configured tolerance;
4. insert zero, one, or multiple intermediate **sub-edge** contours;
5. optimize each added contour's Z position independently;
6. enforce a configurable minimum adjacent Z spacing (initial target: **0.08 mm for a 0.4 mm nozzle**);
7. re-evaluate the finite-width printed surface and select the least-complex solution meeting the error target.

Intermediate Z positions therefore do **not** have to be 1/2 or 1/3 of the base layer height and do not have to be equally spaced.

## Intended architecture

```text
3D model
   ↓
OrcaSlicer slice geometry
   ↓
baseline outer-surface estimate
   ↓
model-vs-print surface error map
   ↓
adaptive candidate intermediate contours
   ↓
non-uniform multi-sub-edge Z optimization
   ↓
geometry / collision validation
   ↓
OrcaSlicer path generation
   ↓
G-code
```

The final implementation is intended to operate in OrcaSlicer's geometry/slicing pipeline rather than reconstructing geometry from completed G-code.

## Documentation

- [System specification](docs/SPECIFICATION.md)
- [Surface error model](docs/ERROR_MODEL.md)
- [Detailed implementation design](docs/IMPLEMENTATION.md)
- [Upstream Smoothificator analysis](docs/SMOOTHIFICATOR_ANALYSIS.md)
- [OrcaSlicer plugin research](docs/ORCASLICER_PLUGIN_RESEARCH.md)
- [Development roadmap](docs/ROADMAP.md)

## Upstream Smoothificator

The original scripts remain in this repository as the baseline/reference implementation. Upstream Smoothificator is a G-code post-processor that enables different effective layer heights for outer walls and the rest of a print.

Upstream project: TengerTechnologies/Smoothificator.

## License

This fork retains the upstream GNU GPL licensing terms and copyright notices. New contributions to this fork must remain compatible with the repository license.
