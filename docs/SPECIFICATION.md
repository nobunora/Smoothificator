# Adaptive Sub-Edge Surface Reconstruction — Specification

## Product goal
Adaptive Sub-Edge extends OrcaSlicer ZAA using **stock OrcaSlicer + Python plugin only**.

Canonical flow:

Orca baseline -> ZAA/normal path generation -> posSimplifyPath analysis -> immutable SubEdgePlan -> Orca G-code -> psGCodePostProcess validation/rewrite/injection -> output.

No custom Orca build is required for v1.

## Single source of truth
The exact same immutable SubEdgePlan MUST drive:
- plugin preview;
- predicted metrics;
- original-wall rewrite;
- intermediate-pass injection.

The G-code stage MUST NOT recalculate geometry.

## Baseline rule
The analyzer always uses the final object extrusion geometry visible at posSimplifyPath.

It does not need to know whether each path was actually modified by ZAA.

ZAA configuration is recorded as diagnostics. If ZAA is enabled and applicable, its result is naturally present in the baseline paths. If not, normal Orca paths are analyzed.

## Error-driven pass schedule
For structural interval [Z0,Z1]:

Z0 < z1 < ... < zk < Z1

Each z_i is independently optimized. Fixed 1/2 or 1/3 subdivision is not assumed.

All domain Z values are **absolute nozzle/path command Z in print-space millimeters**.

Initial 0.4 mm-nozzle minimum adjacent pass height/spacing: 0.08 mm, configurable/profile-driven.

## Outer-wall extrusion redistribution
Sub-edges are not purely additive.

For a refined outer-wall interval:
- intermediate passes are added at optimized Z values;
- the original outer-wall path at Z1 remains at Orca's original XY geometry;
- its extrusion is reduced to the remaining local top-pass height.

If ZAA made the upper wall non-planar, the remaining top-pass height is computed per matched extrusion segment from that segment's actual absolute command Z.

Pass heights are derived from adjacent command Z values.

This prevents systematic over-extrusion at the upper structural wall.

v1 refines one entire matched external-perimeter loop with one common pass schedule. Segment-local schedules are deferred.

## Ordering and collision
For non-crossing z_A < z_B < z_C, print A -> B -> C.

v1 accepts outward/top-facing, non-crossing outer-wall loops only.

Reject:
- contour crossing;
- insufficient support/contact;
- inward/concave nozzle-body uncertainty;
- bead-clearance violation;
- ambiguous wall anchors/state.

## Optimization
Target:
E_max <= configured tolerance where feasible.

Among feasible schedules minimize:
- E_rms;
- added/redistributed material cost;
- added time;
- path complexity.

Required metrics:
- E_max normal error;
- E_rms;
- E_p95;
- signed bias;
- added path length;
- total material delta;
- estimated added time.

## Coordinate contract
All engine/domain geometry is absolute print-space mm.

Orca adapter MUST convert ZAA path Z correctly:

Z_abs = layer.print_z + unscale(path_point.z)

because Orca ContourZ stores path point Z as a layer-relative offset.

Source mesh geometry MUST be transformed into the same print-space frame before comparison.

## Preview contract
Preview means plugin-owned visualization of the exact SubEdgePlan.

Orca standard G-code viewer shows the pre-psGCodePostProcess file and does not contain injected paths.

Preview/injection MUST share plan_id and deterministic plan_hash.

Execution status is stored separately:
- PLANNED
- INJECTION_PASS
- INJECTION_SKIPPED
- INJECTION_FAIL

Status changes MUST NOT mutate plan_hash.

## Thread/lifetime contract
SlicingPipeline hooks run on Orca's slicing worker thread.

MUST NOT call orca.host.ui.* from SlicingPipeline execute().

Live ctx.print/ctx.object/geometry references MUST NOT survive execute(). Required data must be copied into immutable/read-only plugin-owned values.

## G-code injection contract
At psGCodePostProcess, edit ctx.gcode_path only after complete parse/match/validation.

Injector MUST:
- parse statefully;
- select exactly one matching stored plan;
- identify exact layer/outer-wall anchors;
- validate Z/XY/config/state fingerprints;
- rewrite the original top-wall E for reduced effective height;
- inject intermediate passes lower-Z first;
- preserve/restore state;
- be idempotent;
- validate complete output before replacing file;
- refuse partial injection.

Any mandatory failure leaves original Orca output unchanged.

## v1 printable domain
Injection is enabled only for:
- one printable PrintObject;
- one printable instance;
- one positive ModelPart volume;
- no negative/modifier/helper volumes;
- single tool/extruder;
- By Layer print sequence;
- absolute XYZ positioning;
- relative E in target intervals;
- arc fitting disabled;
- scarf/seam-slope disabled;
- fuzzy skin disabled;
- spiral/vase disabled;
- no classic post-processing scripts;
- no other mutating slicing-pipeline plugin;
- no support-dependent refined region;
- not the first printed layer;
- no bridge-role target segment;
- supported Orca/printer G-code fixture family;
- outward/top-facing non-crossing external wall.

Unsupported cases may be analyzed but MUST be marked non-injectable.

## Non-goals v1
- custom Orca dependency;
- live perimeter mutation;
- replacing ZAA;
- full non-planar printing;
- partial-loop/local k(s) refinement;
- multimaterial/tool-change injection;
- absolute-E rewrite;
- intentional collision smoothing;
- claiming standard Orca preview includes injected paths.

## Architecture quality requirements
Implementation MUST follow ARCHITECTURE.md and accepted ADRs.

Required properties:
- engine independent from Orca and G-code;
- Orca access isolated to adapters;
- Preview and Injector consume plans, never create them;
- G-code execution isolated from geometry optimization;
- validated settings passed explicitly;
- public cross-boundary data immutable;
- typed reason codes for expected failures;
- architecture/safety changes require ADR first.
