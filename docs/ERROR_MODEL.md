# Surface Error Model

## Why Z error is insufficient
A staircase can have a small vertical difference while still deviating substantially from the intended surface. Evaluation therefore uses distance relative to the ideal surface.

## Reference geometry
Let M be the ideal model boundary and P be the printable surface envelope produced by the current path set.

For a sample q on P, define signed normal error approximately as:

e_n(q) = (q - p) · n(p)

where p is the corresponding/nearest point on M and n(p) is the outward model normal.

Initial implementations may use robust closest-point distance with sign derived from containment/normal direction, then improve correspondence for difficult topology.

## Metrics
For each perimeter segment/window:
- maximum absolute normal error E_max
- RMS normal error E_rms
- mean signed error (bias/overbuild)
- 95th percentile absolute error
- optional curvature-weighted error

Both underfill and overshoot matter.

## Printed-envelope approximation
The first geometry prototype should model an extrusion bead with finite width and height rather than treating paths as zero-width lines.

Inputs:
- extrusion width from slicer
- actual candidate layer/sub-edge height
- local path spacing
- optional empirical bead-shape model

The first model may use a rounded-rectangle or elliptical cap approximation. It must be replaceable by a calibrated empirical profile later.

## Adaptive search
For each base interval [Z0,Z1]:

1. Evaluate baseline error.
2. If acceptable: no sub-edge.
3. Otherwise generate candidate sets with k = 1..k_max intermediate contours.
4. Optimize z_1..z_k continuously.
5. Enforce:
   - z_1-Z0 >= z_min
   - z_(i+1)-z_i >= z_min
   - Z1-z_k >= z_min
6. Recompute the finite-bead surface envelope.
7. Choose the least-cost candidate satisfying the quality target.

k_max follows from the spacing constraint, not a fixed 1/2 or 1/3 scheme.

## Spatial adaptivity
Subdivision is local along perimeter arc length s. Different portions of one nominal layer may require different candidate counts/heights.

Conceptually:
k = k(s)
z_i = z_i(s)

The implementation must introduce transitions between regions safely rather than creating abrupt unsupported path starts.

## Validation model
Initial regression geometry:
- smooth surface whose tangent angle traverses approximately 1–30 degrees
- later extend toward horizontal and steep surfaces
- compare baseline against adaptive reconstruction
- report error, added path length, material and estimated time
