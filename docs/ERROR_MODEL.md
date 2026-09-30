# Surface Error, Bead and Support Model

## 1. Coordinate semantics
All engine coordinates are absolute print-space millimeters.

Orca ZAA path points are normalized by the adapter:
Z_abs = layer.print_z + unscale(path_point.z)

For Z-contoured non-ironing segments, Orca's emitted extrusion is also locally scaled:
effective_flow_ratio = (path.height + z_offset) / path.height

The baseline predictor MUST reproduce both Z and local flow effects.

## 2. Surface error
Let M be the ideal model boundary and P the predicted printed envelope.

Primary error:
e_n(q) = (q - p) dot n(p)

where p is nearest/corresponding point on M and n(p) is its outward normal.

Required metrics:
- E_max absolute normal error
- E_rms
- E_p95
- mean signed bias

Both underfill and overbuild matter.

## 3. Final combined surface
v1 does NOT replace or rewrite Orca structural beads.

Candidate quality is evaluated on the combined envelope of:
- lower structural/post-ZAA beads;
- all candidate SubEdge beads;
- upper structural/post-ZAA beads that Orca will print unchanged.

This is the authoritative overfill/overlap model.

## 4. Flow model
For a normal non-bridge candidate bead with width w and effective bead height h:

A = h * (w - h * (1 - pi/4))

mm3_per_mm = A

This matches Orca Flow::mm3_per_mm() rounded-rectangle model.

A candidate is invalid if required width/height/flow is outside calibrated printable bounds.

ZAA structural beads use Orca's local extrusion scaling described in section 1.

## 5. Meaning of the 0.08 mm constraint
Initial h_min = 0.08 mm for the 0.4 mm nozzle target.

It applies to **effective deposited bead height above local supporting material**, not to pairwise Z distance between candidate paths.

For candidate j:
h_eff,j = z_nozzle,j - z_support,j

Require:
h_min <= h_eff,j <= configured maximum.

Two non-crossing candidate paths may have |z_i-z_j| < 0.08 mm if each has sufficient local support height and passes all clearance/overlap checks.

## 6. Local support model
For each candidate centerline, determine support height from the predicted lower material envelope at/under that path footprint.

v1 supports only nested/self-supported top-facing geometry.

Required local nesting:
higher material sections must not expand outward beyond lower support beyond tolerance.

Reject unsupported outward-expanding/overhang regions in printable v1.

## 7. Surface boundary vs nozzle centerline
A mesh-plane intersection C(z) is the target **material boundary**, not the extrusion centerline.

The planner must derive centerlines inside the material side based on:
- bead width/shape
- available surface band
- lower support envelope
- target final boundary

No fixed half-width offset is assumed exact.

## 8. Surface-band coverage
A wide shallow terrace may require multiple centerlines.

The optimizer may generate:
- several paths at one Z;
- several paths at different Z;
- combinations of both.

Coverage is scored by the final finite-bead envelope.

The old assumption "one Z schedule for one whole wall loop" is not a v1 requirement.

## 9. Candidate optimization
For each eligible error region:
1. predict baseline structural/ZAA bead envelope;
2. identify residual surface band;
3. generate candidate centerlines and nozzle Z values;
4. derive local support height and bead height;
5. assign candidate width/flow;
6. combine candidate beads with unchanged structural beads;
7. reject support/crossing/nozzle-clearance invalid candidates;
8. recompute error;
9. select minimum-cost feasible candidate set meeting tolerance.

No fixed 1/2 or 1/3 pitch assumption.

## 10. Collision model
Candidate paths are non-crossing and ordered so lower required nozzle Z paths are printed before higher ones where order matters.

Pairwise Z alone does not establish safety.

Validate:
- support footprint
- finite bead envelope
- nozzle-body clearance
- safe travel path
- path crossings
- structural-layer ceiling

G-code execution additionally uses the safe-ceiling travel invariant defined by ADR-0007.

## 11. Validation geometry
Initial:
- fixed 1, 5, 10, 15, 20, 25, 30 degree coupons
- continuous 1-30 degree smooth curve

Report:
- E_max/E_rms/E_p95/bias
- candidate path length
- material delta
- estimated time
- candidate bead heights
- measured roughness where available
