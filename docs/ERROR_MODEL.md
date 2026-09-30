# Surface Error and Flow Model

## 1. Coordinate semantics
All values in this document use absolute print-space millimeters.

For a structural layer interval:

Z0 = previous structural-layer command Z
Z1 = current structural-layer command Z

If intermediate passes exist:

Z0 < z1 < ... < zk < Z1

Each z_i is the **nozzle/path command Z**, i.e. the nominal top height of that deposited pass.

## 2. Why Z error is insufficient
Quality is evaluated relative to the ideal model surface, not only in vertical Z.

Let M be the ideal boundary and P the predicted printable surface envelope.

For a sample q on P:
e_n(q) = (q - p) dot n(p)

where p is the corresponding/nearest point on M and n(p) is the outward model normal.

Initial implementation may use closest-point distance plus sign derived from normal/containment.

Required metrics:
- maximum absolute normal error E_max
- RMS normal error E_rms
- 95th percentile absolute error E_p95
- mean signed error / bias

Both underfill and overbuild matter.

## 3. Refined outer-wall pass schedule

Adaptive Sub-Edge does NOT simply add material.

For [Z0,Z1] with intermediate command heights z1..zk:

h1 = z1 - Z0
hi = zi - z(i-1)
h_top = Z1 - zk

All values must be positive and satisfy configured minimum-height/spacing constraints.

The existing Orca outer-wall path becomes the final **top pass**. If ZAA made that path non-planar, its local absolute command Z varies by segment, so its remaining height and flow must be evaluated segment-by-segment.

With no intermediate pass:
h_top = Z1-Z0 and original G-code remains untouched.

## 4. Flow model
For a non-bridge pass of nominal width w and effective height h, v1 SHOULD reproduce Orca's rounded-rectangle area model:

A = h * (w - h * (1 - pi/4))

mm3_per_mm = A

Requirements:
- w > 0
- h > 0
- w >= h for the v1 non-bridge model
- invalid/non-positive flow rejects the candidate

The original upper-wall extrusion is rescaled/re-emitted according to its reduced local top-pass area, not merely multiplied by an arbitrary pass fraction. For ZAA upper walls, segment j uses h_top_j = Z_top_j - z_k.

The intermediate contour length may differ from the original wall length, so total material is not forced to equal the old loop volume exactly. It is determined by each pass's contour length and cross-section.

## 5. Printed-envelope approximation
Each pass is modeled with finite width/height.

Initial bead profile:
- rounded rectangle preferred for consistency with Orca flow area;
- elliptical profile may be retained only as an experimental comparison model.

Inputs:
- command Z
- effective pass height
- width
- XY path
- local support relationship

The bead's nominal top is command Z and nominal bottom is command Z - effective_height.

## 6. Adaptive search
For each eligible full outer-wall loop interval:

1. Build post-ZAA/post-simplification baseline.
2. Evaluate baseline error.
3. If compliant: no refinement.
4. Generate candidate k and command heights z1..zk.
5. Construct corresponding model cross-sections/outer contours.
6. Compute effective heights from adjacent Z values.
7. Compute pass flows.
8. Reconstruct the actual upper-wall absolute Z profile from ZAA path offsets.
9. Compute h_top_j and target flow per upper-wall segment.
10. Reject any schedule with insufficient remaining top height.
11. Recompute finite-bead surface.
12. Reject support/crossing/clearance-invalid schedules.
13. Choose lowest-cost schedule meeting tolerance.

k_max follows from physical height constraints and configured guardrail.

## 7. v1 spatial scope
v1 uses one common Z schedule for one entire matched external-perimeter loop.

The previous concept:
k = k(s), z_i = z_i(s)

is deferred because it requires partial-loop segmentation and local rewriting of original E values.

Future segment-level adaptivity requires a separate ADR and test suite.

## 8. Support and collision assumptions
For a non-crossing outward sequence printed lower-Z first:
- each pass must have sufficient overlap/contact with lower accepted material;
- next pass command Z must exceed lower pass nominal top by the required height;
- top structural outer wall uses remaining local h_top_j, avoiding the previous additive-only over-extrusion problem.

Concave/inward/nozzle-body uncertain cases are unsupported in v1.

## 9. Validation geometry
Initial analytic/physical set:
- smooth tangent-angle sweep approximately 1-30 degrees
- fixed 1, 5, 10, 15, 20, 25, 30 degree coupons

Report:
- E_max / E_rms / E_p95 / bias
- added path length
- rewritten original-wall material
- total material delta
- estimated time
- measured roughness where available
