# ZAA Integration Strategy

## Role of ZAA
OrcaSlicer Z Contouring/ZAA is the first-line optimizer. It modifies Z coordinates of existing eligible extrusion points so top-facing curved/sloped surfaces follow the source mesh more closely while retaining the nominal structural layer height.

Adaptive Sub-Edge does not duplicate this work.

## Hybrid strategy
1. Baseline slicing
2. ZAA
3. Predict the finite-bead surface actually implied by the post-ZAA paths
4. Measure residual normal error
5. If within tolerance: stop
6. If outside tolerance: add optimized sub-edge contours
7. Re-score

## Why ZAA first
ZAA generally changes existing paths rather than adding complete new extrusion paths. Its quality improvement therefore has a much lower time/material cost than sub-edge reconstruction.

The optimizer should spend added material only after ZAA has exhausted the low-cost correction available to the existing path topology.

## Different solution spaces

ZAA:
- modifies existing path Z
- path topology largely fixed
- excellent time efficiency
- current official scope focuses on top-facing curved/sloped surfaces

Adaptive Sub-Edge:
- creates new surface contours
- can add missing intermediate material
- each added contour can have independent Z
- explicit residual-error/tolerance objective
- incurs additional path/time/material cost

## Quality target
The project should be judged against:
- normal 0.20 mm
- fine conventional layers
- ZAA-only
- ZAA + Adaptive Sub-Edge

Primary success criterion is not "beats ZAA everywhere." It is:

**For geometries where ZAA-only remains above the requested surface-error tolerance, achieve a materially lower error with a smaller time penalty than globally reducing layer height.**

## Collision distinction
ZAA may produce high-to-low neighboring extrusion ordering inside one contoured layer, creating nozzle-interference concerns.

For Adaptive Sub-Edge, accepted non-crossing contours are explicitly sorted from lower Z to higher Z. This makes the common case closer to ordinary FDM layering.

## Benchmark targets
Initial angles:
1°, 5°, 10°, 15°, 20°, 25°, 30°

Compare:
- error metrics
- roughness proxy / measured Ra where equipment permits
- print time
- material
- failures/artifacts
- dimensional bias

Also include domes/chamfers and a model with side-silhouette curvature once the top-facing PoC is stable.
