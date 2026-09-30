# ZAA Integration Strategy

## Role of ZAA
Orca Z Contouring/ZAA is the first-line low-cost surface improvement.

Adaptive Sub-Edge does not attempt to detect or reproduce ZAA internally. It analyzes the final simplified extrusion paths that already contain any ZAA adjustments Orca chose to apply.

## Canonical analysis point
Use **posSimplifyPath**, not posContouring.

Reason:
posContouring hook is conditional on need_z_contouring(); posSimplifyPath occurs later and remains usable when ZAA is disabled/ineligible.

## Path Z semantics
ZAA ContourZ stores point.z as a layer-relative offset d.

Adapter reconstructs:
Z_abs = layer.print_z + unscale(point.z)

The engine only sees absolute print-space Z.

## Hybrid strategy
1. normal Orca slice/perimeters;
2. ZAA if Orca applies it;
3. path simplification;
4. posSimplifyPath snapshot;
5. finite-bead prediction;
6. residual normal-error evaluation;
7. if needed, optimize a complete refined outer-wall pass schedule;
8. export normal Orca G-code;
9. rewrite top external-wall flow and inject intermediate passes.

## Why ZAA remains first
ZAA improves geometry by moving existing path vertices with little added extrusion/time.

Sub-edge refinement is more expensive and should only be used where the final baseline still misses tolerance.

## Solution-space difference
ZAA:
- existing path topology;
- varying Z offsets along path;
- excellent time efficiency.

Adaptive Sub-Edge v1:
- creates additional constant-command-Z external contours;
- redistributes vertical outer-wall extrusion across those passes;
- preserves inner/infill structural layer schedule;
- explicit error tolerance.

## Flow interaction
Sub-edge is NOT "ZAA path + extra material".

For structural interval [Z0,Z1] with intermediate z_i, the original external wall at Z1 is rewritten to its remaining effective height.

This is required to avoid over-extrusion where intermediate passes raise the support surface.

## Success criterion
Compare:
- normal;
- fine conventional layers;
- ZAA-only;
- ZAA + Adaptive Sub-Edge.

Primary claim to test:

Where ZAA-only remains above target surface-error tolerance, ZAA + Adaptive Sub-Edge should lower geometric error with less time cost than globally reducing layer height.

## Collision distinction
Intermediate contours are non-crossing and printed lower command Z to higher command Z.

This avoids ZAA's high-to-low ordering issue in the supported v1 geometry class.

## Benchmark targets
Fixed angles:
1, 5, 10, 15, 20, 25, 30 degrees.

Also:
- continuous smooth slope coupon;
- dome/chamfer later.

Measure:
- E_max/E_rms/E_p95;
- roughness where available;
- print time;
- material delta;
- wall artifacts;
- failures.
