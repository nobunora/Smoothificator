# Adaptive Sub-Edge Surface Reconstruction — Specification

## Goal
Reconstruct sloped/curved FDM outer surfaces more accurately without reducing the layer height of the complete part.

The slicer's ordinary layers remain the structural baseline. Additional outer-surface paths ("sub-edges") are inserted only where geometric error warrants them.

## Core principle
This project is **error-driven**, not fixed-pitch.

For a base interval from Z0 to Z1 with height h = Z1-Z0, the optimizer may select zero, one, or multiple intermediate paths:

Z0 < z1 < z2 < ... < zk < Z1

The intermediate heights do not need to be equally spaced.

### Hard Z-spacing constraint
For the initial 0.4 mm nozzle target:

- minimum adjacent printed surface-path Z spacing: 0.08 mm
- maximum spacing: the slicer-selected base interval
- the 0.08 mm value is a configurable safety constraint, not a mathematical constant

Therefore a 0.24 mm base interval may use, for example, 0.08/0.16 mm, but may also use non-uniform positions such as 0.09/0.17 mm if those positions reduce surface error and all spacing constraints are satisfied.

## Optimization objective
For each candidate surface region, minimize a cost such as:

J = w_max E_max + w_rms E_rms + w_path C_path + w_time C_time

where:
- E_max: maximum signed/absolute surface-normal error
- E_rms: RMS surface-normal error
- C_path: added extrusion/path complexity
- C_time: estimated print-time penalty

Primary quality metric is distance to the ideal model measured approximately along the local surface normal, not Z error alone.

## Required behavior
1. Analyze the ideal model surface and the baseline sliced geometry.
2. Estimate the error produced by the baseline layer geometry.
3. Leave regions below the error threshold unchanged.
4. For regions above threshold, generate candidate intermediate contours at free Z positions.
5. Allow multiple intermediate contours in one base-layer interval.
6. Optimize each intermediate Z independently subject to minimum spacing.
7. Extract only the surface material/path required for reconstruction; do not print a complete intermediate layer.
8. Re-evaluate geometric error after adding candidates.
9. Select the lowest-cost candidate satisfying configured error limits.
10. Pass the resulting geometry to normal OrcaSlicer path generation where practical.

## Non-goals for first implementation
- full non-planar nozzle orientation
- Z values below configured machine/nozzle minimum
- replacing OrcaSlicer's infill/inner-wall generation
- arbitrary post-G-code duplication as the final architecture

## Safety
Generated paths must be rejected if geometry or clearance validation cannot establish a safe printable route. Travel/Z-hop remains a slicer responsibility where supported, but extrusion-path collision must be validated before path generation.
