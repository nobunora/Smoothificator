# Adaptive Sub-Edge Surface Reconstruction — Specification

## Product goal
Adaptive Sub-Edge extends OrcaSlicer ZAA using **stock OrcaSlicer + Python plugin only**.

Canonical flow:
Orca baseline -> ZAA -> posContouring analysis -> immutable SubEdgePlan -> Orca G-code -> psGCodePostProcess validation/injection -> output.

No custom Orca build is required for v1.

## Single source of truth
The exact same immutable SubEdgePlan MUST drive:
- plugin preview
- predicted metrics
- G-code injection

The injector MUST NOT recalculate geometry.

## ZAA-first
Use post-ZAA paths as baseline where ZAA is enabled/applicable. If unavailable, record baseline_mode="orca".

## Error-driven geometry
For structural interval [Z0,Z1]:

Z0 < z1 < ... < zk < Z1

Each z_i is independently optimized. Fixed 1/2 or 1/3 subdivision is not assumed.

Initial 0.4 mm nozzle minimum adjacent Z spacing: 0.08 mm, configurable/profile-driven.

## Ordering and collision
For non-crossing z_A < z_B < z_C, print A -> B -> C.

v1 accepts outward/top-facing, non-crossing contours only. Reject contour crossing, insufficient support, uncertain inward/concave nozzle clearance, bead-clearance violation, or ambiguous insertion anchors.

## Optimization
Require E_max <= configured tolerance where feasible. Among feasible plans minimize error/cost using E_rms, added time, material and complexity.

Required metrics:
- E_max normal error
- E_rms
- E_p95
- signed bias
- added path length/volume
- estimated added time

## Preview contract
Preview means plugin-owned visualization of SubEdgePlan. Orca standard G-code viewer displays the pre-psGCodePostProcess file and does not contain injected paths.

Preview/injection MUST share plan_id and deterministic plan_hash.

Status:
- PLANNED
- INJECTION PASS
- INJECTION SKIPPED
- INJECTION FAIL

## Thread/lifetime contract
SlicingPipeline hooks run on Orca's slicing worker thread.

MUST NOT call orca.host.ui.* from SlicingPipeline execute().

ctx.print/ctx.object/live geometry references MUST NOT survive execute(). Copy required geometry/config into plugin-owned values before returning.

UI/preview MUST use only copied plan/snapshot data through a UI-safe capability.

## G-code injection contract
At psGCodePostProcess, edit ctx.gcode_path in place only after complete validation.

Injector MUST:
- parse statefully, not blindly regex-replace;
- identify exact layer/object/path anchors;
- validate Z/XY/config fingerprints;
- preserve/restore positioning, extrusion, feed/retraction/tool state;
- inject lower-Z-first;
- be idempotent using versioned markers;
- validate entire plan before writing;
- write atomically;
- refuse partial injection.

On mandatory validation failure, original Orca output MUST remain unchanged.

## First supported domain
- stock Orca with Python Plugin System/SlicingPipeline
- 0.4 mm nozzle
- PLA calibration first
- outward/top-facing slopes
- non-crossing sub-edges
- 0.08 mm default minimum spacing
- ZAA-first when applicable
- single extruder/tool first
- no downward-facing reconstruction

## Non-goals v1
- custom Orca dependency
- live perimeter mutation
- replacing ZAA
- full non-planar printing
- multimaterial/tool-change injection
- intentional collision smoothing
- claiming standard Orca preview includes injected paths


## Architecture quality requirements
The implementation MUST follow the responsibility/dependency rules in [ARCHITECTURE.md](ARCHITECTURE.md).

Required properties:
- domain algorithms are independent of Orca and G-code syntax;
- Orca live-data access is isolated to an adapter boundary;
- Preview and Injector are consumers of the same immutable plan, never producers;
- G-code execution is isolated from geometry optimization;
- configuration is mapped once into a validated settings object;
- public cross-boundary data is immutable;
- expected failures use stable typed reason codes;
- architecture/safety changes require ADR review before code changes.

The design goal is change locality: modifying one algorithm or external integration SHOULD NOT require unrelated safety-critical modules to change.
