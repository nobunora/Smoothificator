# Surface Error, Bead, Support, and Flow Model

This document defines the v1 nominal geometry model. It does not claim to be a complete empirical extrusion model.

## 1. Coordinate frame

All engine geometry uses Orca centered PrintObject slice-space in millimeters.

The Orca adapter owns:
- scaled XY -> mm;
- centered source-mesh reconstruction per ADR-0012;
- ZAA relative-Z -> absolute centered-slice Z.

No engine code performs Orca transform reconstruction.

## 2. Surface error

Let:
- M = ideal source-model material boundary;
- P = predicted nominal printed bead envelope.

For a sampled point q and corresponding/closest source point p with outward normal n:

e_n = dot(q - p, n)

Required metrics:
- E_max = maximum absolute error;
- E_rms;
- E_p95;
- signed mean/bias.

Underfill and overbuild both count as error.

## 3. Structural baseline

The baseline uses final simplified Orca structural paths visible at posSimplifyPath.

### Normal planar segment

Use:
- path width;
- path nominal height;
- path nominal geometric mm3/mm;
- absolute layer/path Z.

### ZAA segment

For local ZAA offset d:

h_local = path.height + d

zaa_ratio = h_local / path.height

q_geom_zaa = path.mm3_per_mm * zaa_ratio

The local nominal finite-bead model uses h_local and q_geom_zaa.

Global print/material calibration flow ratios are execution controls and are not multiplied into the ideal geometric envelope.

## 4. Candidate geometric bead model

For a supported non-bridge candidate with effective bead height h and nominal width w:

q_geom = h * (w - h * (1 - pi/4))

Constraints:
- h > 0;
- w > 0;
- calibrated printable bounds apply;
- invalid/non-positive cross-section is infeasible.

Given h and geometric line volume q, effective width may be reconstructed as:

w = q / h + h * (1 - pi/4)

## 5. Geometric versus commanded volume

### Geometric volume

Used for nominal surface prediction and optimization.

### Commanded volume

Used for E generation and volumetric-speed limits.

For v1 external-surface candidate:

q_cmd = q_geom * print_flow_ratio * filament_flow_ratio * outer_role_factor

outer_role_factor = outer_wall_flow_ratio when set_other_flow_ratios is enabled, otherwise 1.

### Empirical physical volume

Not yet modeled from first principles.

A calibration multiplier such as filament_flow_ratio = 0.98 MUST NOT be interpreted as exactly 2% smaller real bead geometry.

Physical calibration may later add a measured mapping from commanded conditions to actual bead envelope.

## 6. Effective bead height

Initial 0.4 mm nozzle research value:

h_min_mm = 0.08

For candidate segment j:

h_eff_j = nozzle_z_j - support_z_j

This is effective deposited height above local supporting material.

It is NOT a minimum pairwise Z gap between candidate paths.

## 7. v1 candidate Z topology

Each printable v1 SubEdgePath has one constant command_z_mm.

Segments within a path may have different effective bead height because local support Z varies.

Different paths may:
- share one command Z;
- use independently optimized different command Z values.

Continuously varying-Z candidate paths are out of scope.

## 8. Local support envelope

For each candidate segment:
1. query predicted material below/at the footprint;
2. determine local support height and overlap;
3. derive h_eff;
4. reject insufficient contact/support;
5. evaluate bead overlap with structural and candidate material.

Candidate execution order is deterministic by structural interval, command Z, and stable tie-break.

A lower-Z earlier candidate may support a later higher-Z candidate when overlap/contact is valid.

Same-Z candidates must not rely on each other as required vertical support in v1.

Support dependencies must be acyclic.

Printable v1 requires nested/self-supported top-facing surface bands.

## 9. Material boundary versus nozzle centerline

A mesh-plane intersection is a target material boundary.

It MUST NOT be emitted directly as the nozzle centerline.

The surface-band planner derives one or more centerlines inside the material side using:
- target boundary;
- bead shape/width;
- lower support envelope;
- desired final outer envelope;
- local coverage;
- tool-clearance constraints.

## 10. Candidate seam/gap

If a planned centerline is closed, the engine converts it to an explicit open execution path before plan finalization.

The deterministic seam/start and gap:
- are part of plugin settings/plan identity;
- are included in finite-bead scoring;
- are shown in preview;
- cannot be changed by postprocess.

## 11. Final combined nominal surface

For completed-part error/overbuild scoring, FinalSurfaceEnvelope combines:
- lower structural/ZAA geometric beads;
- all candidate geometric beads;
- upper structural/ZAA geometric beads.

Original structural Orca paths remain unchanged.

The optimizer rejects candidate material that causes unacceptable overbuild even if it improves another region.

## 12. Candidate optimization

For each eligible residual region:
1. build normalized structural baseline;
2. compute residual error field;
3. derive target residual surface band;
4. generate constant-Z candidate centerlines;
5. apply deterministic candidate seam/gap;
6. determine local support/effective bead height;
7. compute candidate geometric volume;
8. compute commanded volume separately;
9. reject support/crossing/clearance-invalid candidates;
10. build combined nominal bead envelope;
11. calculate error metrics;
12. choose minimum-cost feasible set.

Initial solver may use deterministic bounded grid/beam search.

## 13. Execution quantization

An injectable plan is not fully execution-valid until the G-code adapter:
1. maps print-space to machine space;
2. applies Orca-compatible XYZ quantization;
3. recomputes emitted segment lengths;
4. derives and quantizes E;
5. rechecks execution-sensitive constraints.

Postprocess skips an invalidated plan rather than mutating it.

## 14. Speed / volumetric constraint

For each segment:

v_vol = V_max / q_cmd

Candidate speed must not exceed:
- resolved outer-wall speed;
- v_vol;
- optional lower plugin cap;
- any lower fixture-required matched structural-wall feed.

Filament adaptive volumetric speed is disabled in v1.

## 15. Collision layers

### Planning-time geometry checks

Validate:
- bead overlap;
- candidate crossing;
- support footprint;
- simplified tool/nozzle clearance;
- upper structural/candidate nominal interaction.

### Final execution checks

After final G-code exists:
- reconstruct actual machine state;
- use safe-ceiling injection travel;
- apply ToolClearanceProfile;
- validate quantized candidate material against subsequent unchanged original Orca motions.

Planning-time clearance does not replace downstream execution clearance.

## 16. First-layer exclusion

Printable v1 does not refine the first printed/model layer.

The first printable SubEdge interval requires ordinary model material below the candidate support.

## 17. Validation geometry

Initial deterministic suite:
- fixed slopes 1, 5, 10, 15, 20, 25, 30 degrees;
- continuous approximately 1–30 degree surface;
- translated/rotated/scaled source-transform fixtures;
- synthetic ZAA varying-Z structural paths;
- shallow terraces requiring multiple centerlines;
- varying local support under one constant-Z candidate path;
- candidate seam/gap fixtures.

Report:
- E_max / E_rms / E_p95 / bias;
- path length;
- geometric added volume;
- commanded added volume;
- effective bead-height range;
- estimated time;
- infeasibility reason.

Physical roughness/bead/tool-clearance calibration is a later gate.
