# Adaptive Sub-Edge Surface Reconstruction — Specification

## 1. Product goal
Adaptive Sub-Edge is a stock-OrcaSlicer Python plugin that improves surface geometry beyond Orca ZAA where residual error remains.

No custom Orca build is required for v1.

## 2. Canonical flow
Orca slice -> ZAA if applicable -> path simplification -> posSimplifyPath snapshot -> residual-error/surface-band optimization -> immutable SubEdgePlan -> plugin preview -> normal Orca G-code -> psGCodePostProcess validated additive injection -> output.

The original Orca structural toolpath remains unchanged in v1.

## 3. Single source of truth
The exact same immutable SubEdgePlan drives:
- preview;
- predicted metrics;
- G-code injection.

Injector MUST NOT recalculate geometry.

## 4. Baseline semantics
Analyzer reads final simplified paths at posSimplifyPath.

If ZAA modified a path, the snapshot contains:
- absolute command Z reconstructed from layer.print_z + path Z offset;
- local effective ZAA extrusion flow matching Orca's G-code behavior.

If ZAA did not apply, ordinary planar Orca paths naturally become the baseline.

## 5. Error-driven surface-band reconstruction
The source mesh intersection is a target material boundary, not a nozzle centerline.

Planner derives one or more printable centerlines inside the material-side residual surface band.

Candidate paths may:
- share one Z;
- use different Z values;
- have pairwise Z differences smaller than 0.08 mm.

No fixed 1/2 or 1/3 subdivision is assumed.

## 6. Minimum-height rule
Initial 0.4 mm nozzle value:
h_min = 0.08 mm.

This is the minimum **effective deposited bead height above local support**, not minimum neighboring path Z separation.

For each candidate:
h_eff = z_nozzle - z_support.

Local support comes from the predicted lower material envelope.

## 7. Final-surface model
Quality is evaluated from the combined finite-bead envelope of:
- existing lower structural/ZAA beads;
- candidate SubEdge beads;
- existing upper structural/ZAA beads.

The structural Orca outer wall is not rewritten in v1.

SubEdge width/height/flow are candidate variables/parameters constrained by calibrated printable limits.

## 8. Supported geometry
Printable v1 requires nested/self-supported top-facing geometry:
higher material sections must remain supported by lower material within tolerance.

Reject printable injection for:
- outward-expanding unsupported overhang bands;
- path crossings;
- insufficient support height;
- uncertain nozzle clearance;
- bridge/support-dependent targets.

Analysis-only mode may still report such geometry.

## 9. Optimization target
Where feasible require:
E_max <= configured tolerance.

Among feasible candidates minimize a cost including:
- E_rms / E_p95 / signed bias;
- added path length;
- added material;
- estimated added time;
- complexity/risk.

Required reporting:
E_max, E_rms, E_p95, bias, material delta, path length, time estimate.

## 10. Preview contract
Orca standard G-code viewer represents pre-post-process G-code.

Plugin preview displays the exact immutable plan to be injected:
- baseline paths;
- candidate SubEdge paths;
- bead heights/flows;
- error heatmap;
- metrics;
- plan hash;
- execution status.

Plan status is stored separately:
PLANNED / INJECTION_PASS / INJECTION_SKIPPED / INJECTION_FAIL.

## 11. Thread/lifetime contract
SlicingPipeline geometry execution runs on the slicing worker thread.

MUST NOT call orca.host.ui.* there.

All live Orca references are copied/normalized inside the adapter and discarded before returning.

## 12. G-code execution contract
v1 targets validated Bambu/Orca single-tool profiles.

At psGCodePostProcess:
1. parse/validate final G-code;
2. select exactly one matching current-session plan;
3. validate supported profile/modal/custom-layer environment;
4. anchor at the validated structural layer boundary;
5. use ADR-0007 safe-ceiling travel;
6. emit candidate paths in safe order;
7. return exactly to validated saved structural-layer state;
8. write through temp output and atomically replace only after complete success.

Original structural extrusion remains byte/semantically unchanged except unavoidable insertion markers/context.

No partial injection.

## 13. Printable v1 environment
Requires:
- fresh current-session slice;
- one printable PrintObject;
- one printable instance;
- one ModelPart volume;
- no negative/modifier volume;
- one tool/extruder;
- supported current Bambu 0.4 mm profile family;
- relative E;
- firmware retraction off;
- G-code line numbering/checksum off;
- arc fitting off;
- spiral vase off;
- ironing off;
- scarf/sloped seam off;
- support/raft off;
- no classic post_process script;
- no other slicing-pipeline plugin;
- validated motion-neutral before/layer-change custom G-code environment.

Unsupported configurations are analysis-only.

## 14. Failure behavior
Any uncertainty in:
- current plan identity;
- G-code state;
- layer-boundary anchor;
- support/clearance;
- profile compatibility;
- custom G-code motion;
causes injection to be skipped with original working G-code preserved.

## 15. Non-goals v1
- modifying Orca live perimeter graph;
- replacing ZAA;
- rewriting original structural wall flow;
- full non-planar printing;
- multi-object/multi-volume CSG;
- multitool;
- absolute-E injector;
- firmware retract;
- arc injection;
- unsupported overhang reconstruction;
- claiming Orca standard preview contains postprocessed paths.

## 16. Architecture
Implementation MUST follow:
- accepted ADRs;
- ARCHITECTURE.md;
- IMPLEMENTATION.md;
- DOCUMENT_CONTRACT.md.

Safety/architecture relaxation requires a new Accepted ADR first.
