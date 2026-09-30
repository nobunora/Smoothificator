# Surface Error, Bead, Support, and Flow Model

This document defines the v1 ideal geometry model. It does not claim to be a complete empirical extrusion model.

## 1. Coordinate frame

All engine geometry uses Orca's centered PrintObject slice-space in millimeters.

The Orca adapter owns:
- scaled XY -> mm;
- centered source-mesh reconstruction per ADR-0012;
- ZAA relative-Z -> absolute centered-slice Z.

No engine code performs Orca transform reconstruction.

## 2. Surface error

Let:
- (M) = ideal source-model material boundary;
- (P) = predicted nominal printed bead envelope.

For a sampled point (q) on/near the predicted envelope, define signed normal-oriented error against corresponding/closest source point (p) with outward normal (n(p)):

[
e_n(q)=(q-p)cdot n(p).
]

Initial implementation may use a robust closest-point approximation plus sign from source normal/inside-outside evidence.

Required metrics:
- (E_{max}): maximum absolute error;
- (E_{rms});
- (E_{p95});
- signed mean/bias.

Underfill and overbuild are both errors.

## 3. Structural baseline

The baseline includes the final simplified Orca structural paths visible at `posSimplifyPath`.

### Normal planar segment

Use:
- path width;
- path nominal height;
- path nominal geometric `mm3_per_mm`;
- absolute layer/path Z.

### ZAA segment

For local ZAA offset (d):

[
h_{local}=h_{path}+d
]

and Orca's local ZAA volume ratio is:

[
r_{zaa}=rac{h_{path}+d}{h_{path}}.
]

Define the v1 local **geometric** volumetric target as:

[
q_{geom,zaa}=q_{path}cdot r_{zaa}.
]

This is paired with (h_{local}) to reconstruct an effective finite bead for nominal geometry prediction.

Global print/filament/outer-wall flow calibration ratios are NOT multiplied into the ideal geometric envelope; they are execution calibration values handled separately.

## 4. Candidate geometric bead model

For a normal non-bridge candidate with effective bead height (h) and nominal width (w), initial rounded-rectangle cross-section:

[
q_{geom}
=
hleft(w-h(1-pi/4)ight).
]

Constraints:
- (h>0);
- (w>0);
- printable calibration bounds apply;
- any invalid/non-positive cross-section is infeasible.

Given a fixed (h) and geometric volume (q), an effective width may be reconstructed as:

[
w=rac{q}{h}+h(1-pi/4).
]

This is useful for ZAA structural envelope reconstruction.

## 5. Geometric versus commanded volume

Following ADR-0022:

### Geometric volume
Used for surface prediction/optimization.

Represents the nominal bead geometry the slicer/plugin is trying to create.

### Commanded volume
Used for E generation and max-volumetric-speed checks.

For v1 external-surface candidate segment:

[
q_{cmd}
=
q_{geom}
cdot r_{print}
cdot r_{filament}
cdot r_{outer}.
]

Where (r_{outer}=1) unless Orca `set_other_flow_ratios` enables `outer_wall_flow_ratio`.

### Physical empirical volume
Not yet modeled.

No assumption is made that a calibration multiplier such as `filament_flow_ratio=0.98` means the real bead becomes exactly 2% smaller. Physical calibration is a later phase.

## 6. Effective bead height and 0.08 mm rule

The initial 0.4 mm nozzle research value:

[
h_{min}=0.08	ext{ mm}
]

applies to the candidate's **effective bead height above its local supporting material**:

[
h_{eff,j}=Z_{nozzle,j}-Z_{support,j}.
]

It is NOT a minimum pairwise Z difference between two candidate paths.

Two nearby candidate centerlines may differ by less than 0.08 mm in absolute Z if each has valid local support and all overlap/clearance/collision checks pass.

## 7. Local support envelope

For each candidate segment:
1. query the predicted material already present below/at the segment footprint;
2. determine local support height/overlap;
3. derive (h_{eff});
4. reject unsupported/excessively weak contact;
5. evaluate candidate bead overlap with existing/candidate material.

Printable v1 requires nested/self-supported top-facing surface bands.

Higher target material sections must remain contained/supported by lower predicted material within tolerance.

## 8. Material boundary versus nozzle centerline

A mesh-plane intersection (C(z)) is a target material boundary.

It MUST NOT be emitted directly as nozzle centerline.

The surface-band planner derives one or more centerlines inside the material side considering:
- bead width/shape;
- target boundary;
- lower support envelope;
- desired final outer envelope;
- local coverage;
- nozzle clearance.

No fixed half-width inset is assumed universally exact.

## 9. Multi-path surface-band coverage

A shallow terrace may require several candidate centerlines.

The optimizer may place:
- multiple paths at the same Z;
- paths at different Z;
- path segments with locally varying support/effective bead height.

Candidate properties are segment-local per ADR-0014.

No fixed vertical pass schedule is a v1 invariant.

## 10. Final combined nominal surface

For scoring, combine:
- lower structural/ZAA geometric beads;
- all candidate geometric beads;
- upper structural/ZAA geometric beads.

Original structural Orca paths remain unchanged.

The optimizer must detect when added candidate material creates overbuild that outweighs residual-error improvement.

## 11. Candidate optimization

For each eligible residual region:

1. build normalized structural baseline;
2. compute residual surface-error field;
3. derive target residual surface band;
4. generate candidate centerlines/Z choices;
5. determine local support/effective bead height;
6. compute candidate geometric flow;
7. compute execution commanded flow separately;
8. reject unsupported/crossing/nozzle-clearance invalid candidates;
9. build combined nominal finite-bead envelope;
10. calculate error metrics;
11. choose minimum-cost feasible set meeting tolerance.

First solver may use bounded grid/beam search.

Continuous optimization is optional later.

## 12. Execution quantization check

The optimizer may work at higher precision, but an injectable plan is not fully execution-valid until the G-code adapter:

1. maps print-space to machine space;
2. applies Orca-compatible XYZ quantization;
3. recomputes emitted segment lengths;
4. derives and quantizes E;
5. rechecks execution-sensitive constraints.

If quantization invalidates the solution, the plan is skipped; the injector does not mutate it.

## 13. Speed/volumetric constraint

For each segment:

[
v_{vol}=
rac{V_{max}}{q_{cmd}}
]

where (V_{max}) is resolved filament max volumetric speed.

Candidate speed must be no greater than:
- resolved outer-wall speed;
- (v_{vol});
- any lower configured plugin cap.

Geometric scoring may estimate time from the resulting conservative speed.

## 14. Collision and travel

Geometry feasibility validates:
- bead overlap;
- path crossing;
- support footprint;
- nozzle-body clearance;
- upper structural/candidate interaction.

Execution travel safety is separate:
- actual machine state from parser;
- safe-ceiling vertical lift;
- no non-extruding XY below Zsafe;
- exact state restore.

Do not mix path-planning geometry collision with G-code modal-state correctness.

## 15. Validation geometry

Initial deterministic geometry suite:
- fixed slopes: 1°, 5°, 10°, 15°, 20°, 25°, 30°;
- continuous tangent-angle sweep approximately 1°–30°;
- translated/rotated/scaled source-transform fixtures;
- synthetic ZAA varying-Z structural paths;
- shallow terraces requiring multiple centerlines.

Report:
- E_max / E_rms / E_p95 / bias;
- added path length;
- geometric added volume;
- commanded added volume;
- candidate effective bead-height range;
- estimated time;
- infeasibility reason where relevant.

Physical roughness/material calibration is a later gate.
