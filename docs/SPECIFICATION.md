# Adaptive Sub-Edge Surface Reconstruction — Specification

## Goal
Extend OrcaSlicer's Z Anti-Aliasing (ZAA / Z Contouring) with a second, error-driven reconstruction stage.

The system first takes the low-cost quality improvement available from ZAA. It then measures the remaining difference between the predicted printable surface and the ideal model. Only regions that still exceed the requested tolerance receive additional outer-surface paths ("sub-edges").

The objective is not to replace ZAA or beat it on print time. It is to exceed the geometric quality ceiling of ZAA with the minimum necessary additional extrusion.

## Pipeline
Baseline slicing -> ZAA -> finite-bead surface prediction -> residual error -> adaptive sub-edge -> validation -> G-code

1. Orca produces baseline layer/perimeter geometry.
2. ZAA runs normally where eligible.
3. Build a finite-width predicted surface from post-ZAA paths.
4. Compare that surface with the source model.
5. If error is within tolerance, do nothing.
6. Otherwise generate candidate intermediate model contours.
7. Add the lowest-cost set of sub-edges satisfying the target.
8. Re-evaluate the surface and pass accepted paths downstream.

## Error-driven, not fixed-pitch
For a structural interval Z0..Z1, the optimizer may select:

Z0 < z1 < z2 < ... < zk < Z1

Each z_i is an independent optimization variable. Equal spacing and fixed 1/2 or 1/3 subdivisions are not required.

## Z constraints
Initial 0.4 mm nozzle target:
- configurable minimum adjacent printed-surface-path Z spacing: 0.08 mm
- monotonic accepted Z order
- no crossing between accepted sub-edge contours
- minimum spacing becomes a calibratable machine/material/nozzle profile value

0.08 mm is an initial engineering constraint, not a universal constant.

## Ordering and collision model
For non-crossing contours with z_A < z_B < z_C, print A -> B -> C. This intentionally mirrors ordinary bottom-to-top FDM layering.

Sub-edge/sub-edge collision is therefore not inherently expected for monotonic non-crossing geometry. Validation focuses on:
- real bead height exceeding the model
- inward/concave geometry reducing nozzle-body clearance
- insufficient support/contact
- travel across printed geometry
- seam blobs/local over-extrusion

Hard nozzle-body collisions are forbidden.

## Optimization objective
Minimize:

J = w_max E_max + w_rms E_rms + w_path C_path + w_time C_time + w_material C_material

where E_max/E_rms are surface-normal error metrics and the remaining terms penalize added complexity, time and material.

A quality mode may instead impose E_max <= user_tolerance and minimize added cost subject to that constraint.

## ZAA relationship
ZAA changes Z coordinates of existing eligible extrusion points and is highly time-efficient.

Adaptive Sub-Edge has a larger solution space because it may add new contours/material. It runs only after ZAA residual error justifies that cost.

Expected strengths over ZAA-only:
- lower attainable geometric error where moving existing paths is insufficient
- reconstruction of missing intermediate surface geometry
- explicit tolerance-driven quality control
- future outer-silhouette/side-wall treatment
- constant-Z deposition within each added contour

Expected cost:
- additional extrusion and print time

## Required behavior
1. Preserve Orca structural layer decisions.
2. Prefer post-ZAA geometry as the baseline.
3. Estimate post-ZAA printable-surface error.
4. Leave compliant regions untouched.
5. Generate true model cross-sections at candidate Z values where possible.
6. Permit multiple non-uniform sub-edges.
7. Optimize each Z independently.
8. Add only surface contributions, not full intermediate structural layers.
9. Validate support, topology, ordering and clearance.
10. Re-score the finite-bead surface.
11. Fail safely to unmodified Orca output on uncertainty/failure.

## First-version non-goals
- replacing ZAA
- full non-planar nozzle orientation
- downward-facing reconstruction without support modeling
- modifying infill/inner-wall scheduling
- G-code regex rewriting as the final architecture
- intentional nozzle collision as a smoothing mechanism
