# Implementation Specification — Stock Orca Plugin

This document is normative. Coding agents MUST follow it unless an Accepted ADR supersedes a requirement.

## 0. Canonical architecture
Use **stock OrcaSlicer + Python plugin only**.

Two SlicingPipeline steps:
1. **posSimplifyPath** — copy final object path geometry after ZAA/contouring and simplification; analyze; create immutable SubEdgePlan.
2. **psGCodePostProcess** — parse exported working G-code; select exactly one matching plan; rewrite target original outer wall and insert intermediate passes.

A separate Script capability provides preview/diagnostics from copied plan data.

No custom Orca C++ changes in v1.

## 1. Why posSimplifyPath
Do NOT use posContouring as the canonical analyzer hook.

Orca calls the posContouring plugin hook only when need_z_contouring() is true. That prevents analysis of ZAA-disabled/ineligible objects.

posSimplifyPath runs after contouring and produces geometry closer to export.

If Orca does not re-fire the geometry hook because a plugin-final slice is cache-loaded, export injection requires an already present matching plan. Missing plan => skip and request re-slice.

## 2. Orca thread/lifetime rules
SlicingPipeline geometry hooks run on the slicing worker thread.

Never call orca.host.ui.* from SlicingPipeline execute().

Live ctx.print/ctx.object/pybind references are valid only during execute(). All required data MUST be copied before returning.

At psGCodePostProcess:
- ctx.print and ctx.object are None;
- ctx.gcode_path is the working exported G-code;
- ctx.host and ctx.output_name are available;
- output may be processed more than once on separate working copies;
- result is not represented in Orca standard G-code preview.

## 3. Required package structure

adaptive_subedge/
  domain/
    geometry.py
    metrics.py
    plan.py
    settings.py
    status.py
    errors.py
  engine/
    bead_model.py
    flow_model.py
    error_estimator.py
    mesh_section.py
    candidate_generator.py
    subedge_extractor.py
    z_optimizer.py
    collision.py
    cost_model.py
  application/
    analyzer.py
    plan_store.py
    execution_status.py
    serialization.py
    hashing.py
    migrations/
  ports/
    mesh_section_provider.py
    plan_repository.py
    cancellation.py

orca_plugin/
  adapters/
    geometry_snapshot.py
    orca_config.py
    transforms.py
    fingerprint.py
  capabilities/
    slicing.py
    preview.py
  ui/
    preview_model.py
    preview_renderer.py
  gcode/
    lexer.py
    parser.py
    state.py
    matcher.py
    anchors.py
    validation.py
    outer_wall_rewrite.py
    emitter.py
    injector.py
    atomic_writer.py

tests/
  architecture/
  unit/
  analytic/
  fixtures/gcode/
  fixtures/plans/
  integration/
  regression/
  printer/

The obsolete flat module layout is removed. ARCHITECTURE.md is authoritative.

## 4. Canonical coordinate normalization

### 4.1 Path coordinates
Domain coordinates MUST be absolute print-space mm.

Orca ExtrusionPath point Z after ContourZ is layer-relative.

Adapter conversion:
Z_abs = Layer.print_z + orca.slicing.unscale(point_z)

XY:
X_mm = unscale(point_x)
Y_mm = unscale(point_y)

No domain/engine code may call Orca unscale.

### 4.2 Source mesh
v1 supports one positive ModelPart volume.

Mesh vertices are local mm. Adapter applies:
print_vertex = PrintObject.trafo() @ ModelVolume.matrix() @ local_vertex

Implementation MUST verify matrix convention with a transform fixture before relying on this formula. If fixture fails, update adapter/ADR before algorithms.

Do not use GUI live model references from a slicing hook.

## 5. Immutable data model

### GeometrySnapshot
Frozen boundary object containing copied/read-only:
- Orca version
- stable snapshot fingerprint
- print-space source mesh vertices/triangles
- structural layer intervals
- post-simplify outer-wall path geometry
- original path width/height/mm3_per_mm/role
- relevant resolved config
- ZAA config diagnostics
- nozzle diameter
- filament diameter
- printer/profile compatibility flags

Large NumPy arrays MUST be copied and flags.writeable=False before storage.

### WallPass
Frozen:
- pass_id
- command_z_mm
- effective_height_mm
- points_xy_mm
- width_mm
- mm3_per_mm
- ordering_index
- source_error_region_id

### OriginalWallSegmentRewrite
Frozen, one record per matched original upper-wall extrusion segment:
- segment anchor/fingerprint
- original segment start/end XYZ
- original width_mm
- original mm3_per_mm
- local/representative absolute top command Z
- target effective_height_mm
- target mm3_per_mm
- relative-E scale/rewrite rule

### OriginalWallRewrite
Frozen:
- matched original loop anchor
- expected original-loop fingerprint
- ordered OriginalWallSegmentRewrite records
- rewrite mode

### WallPassSchedule
Frozen:
- interval Z0/Z1
- intermediate_passes
- original_wall_rewrite
- target loop fingerprint
- highest_intermediate_z_mm

### InsertionAnchor
Frozen:
- expected layer interval
- expected nearby XY
- expected comment/type context
- expected state
- tolerance/fingerprint

### SubEdgePlan
Frozen:
- schema_version
- plugin_version
- plan_id
- deterministic plan_hash
- Orca version
- settings_hash
- geometry_hash
- baseline metadata
- wall_pass_schedules
- anchors
- metrics_before
- metrics_after_predicted
- cost estimates

Runtime ObjectIDs and timestamps MUST NOT participate in stable plan_hash.

### PlanExecutionStatus
Separate mutable record:
PLANNED / INJECTION_PASS / INJECTION_SKIPPED / INJECTION_FAIL + stable reason code.

Status MUST NOT mutate SubEdgePlan.

## 6. v1 supported injection domain
Injection MUST be disabled unless all are true:
- exactly one printable PrintObject;
- exactly one printable instance;
- exactly one positive ModelPart volume;
- no negative/modifier/support helper volumes;
- single tool/extruder;
- print sequence By Layer;
- wall sequence Outer Wall -> Inner Wall;
- infill-first disabled;
- target G-code uses absolute XYZ positioning;
- target G-code uses relative extrusion for target intervals;
- arc fitting disabled;
- scarf/seam-slope feature disabled;
- fuzzy skin disabled;
- spiral/vase mode disabled;
- no classic post-processing scripts;
- no other active geometry/G-code-mutating slicing-pipeline plugin;
- no support-dependent refined region;
- not the first printed layer;
- no bridge-role target segment;
- target external-wall loop is simple, deterministically matchable, non-crossing and self-supported/top-facing;
- supported Orca/profile fixture exists.

Analysis MAY run outside this domain, but plan must be marked non-injectable with reason codes.

## 7. posSimplifyPath analyzer sequence
For the one supported PrintObject:
1. check cancellation;
2. read and validate Settings;
3. enforce/record injection-domain gates;
4. copy Orca graph into GeometrySnapshot;
5. release all reliance on live references;
6. identify external-perimeter loops;
7. build finite-bead post-simplify baseline surface;
8. compute residual normal-error map;
9. skip compliant loops;
10. for each eligible loop/interval, generate candidate Z schedules;
11. obtain true source-mesh cross-sections;
12. generate complete intermediate external-loop contours;
13. derive pass heights from adjacent command Z values;
14. compute flow using FlowModel;
15. compute segment-wise reduced top original-wall flow from the actual ZAA top-wall absolute Z profile;
16. reject schedules where any top segment leaves less than minimum printable height above the highest intermediate pass;
17. validate support/non-crossing/clearance;
18. re-score finite-bead surface;
19. select lowest-cost feasible full-loop schedule;
20. construct immutable SubEdgePlan;
21. store plan and PLANNED status.

Heavy loops MUST poll cancellation at bounded intervals.

## 8. v1 refinement granularity
v1 refines **one whole matched external-perimeter loop using one common Z schedule**.

Do NOT implement local k(s) / z_i(s) or partial-loop rewriting in v1.

A future partial-loop implementation requires an ADR because it changes G-code rewrite semantics and plan schema.

## 9. Flow model
For non-bridge width w and pass height h:

mm3_per_mm = h * (w - h * (1 - pi/4))

Reject non-positive flow and v1 cases where width < height.

Intermediate pass height:
h1 = z1-Z0
hi = zi-z(i-1)

Upper original wall is evaluated per matched segment j because ZAA may make it non-planar:

Z_top_j = Z1 + d_j
h_top_j = Z_top_j - z_k

Each h_top_j must satisfy the configured minimum printable height/clearance.

The injector MUST rewrite each matched original upper-wall extrusion segment from its original mm3_per_mm to the target value computed from that segment's width and h_top_j.

With a planar non-ZAA wall all h_top_j are equal.

No-refinement schedule MUST leave original wall byte-identical.

## 10. Geometry/error model
Candidate contours SHOULD be true plane intersections with transformed source mesh.

Required metrics:
- E_max
- E_rms
- E_p95
- signed mean/bias

Finite-width/height beads are mandatory in scoring.

Solver v1:
1. bounded coarse candidate Z grid;
2. enumerate/beam candidate k schedules;
3. local Z refinement;
4. early stop at quality tolerance;
5. choose minimum-cost feasible schedule.

No fixed 1/2 or 1/3 assumption.

## 11. PlanStore and plan matching
PlanStore is process-local, thread-safe, bounded and stores immutable plans.

Do NOT assume ctx.output_name or Orca runtime ObjectID uniquely maps to a plan.

At psGCodePostProcess:
1. parse entire G-code;
2. enumerate current stored injectable plan candidates compatible with Orca/settings family;
3. validate each candidate against header/config/layer/loop anchors;
4. exactly one candidate MUST match;
5. zero matches => PLAN_MISSING/PLAN_MISMATCH skip;
6. multiple matches => PLAN_AMBIGUOUS skip.

The matcher MUST use stable geometry/state fingerprints, not process-global ObjectIDs.

## 12. Preview
Preview is plugin-owned and consumes:
- immutable SubEdgePlan;
- separate PlanExecutionStatus.

Use a Script capability/UI-safe context and orca.host.ui.create_window or equivalent supported host UI.

Preview MUST show:
- baseline post-simplify/ZAA paths;
- planned intermediate passes;
- rewritten upper wall indication;
- residual error heatmap;
- before/after metrics;
- command Z and effective height per pass;
- added/redistributed material and time estimate;
- plan hash/status.

Preview MUST NOT create or modify plan geometry.

## 13. G-code parser
No regex-only mutation.

v1 parser tracks:
- current X/Y/Z;
- G90/G91;
- M82/M83;
- current E;
- feed rate;
- retraction/unretraction;
- active tool;
- layer/object/type comments;
- target outer-wall loop boundaries;
- recognized state-changing commands for supported fixture.

Unknown commands are preserved byte-for-byte. Unknown state-changing behavior in/around a target interval => injection disabled.

G2/G3 target geometry is unsupported in v1; arc fitting must be disabled.

## 14. Outer-wall matching and rewrite
For every WallPassSchedule:
1. find structural interval;
2. find exact original outer-wall loop;
3. validate loop fingerprint, Z, role/comment context and state;
4. verify relative extrusion mode;
5. map each G-code extrusion move to its planned OriginalWallSegmentRewrite;
6. compute the move's relative-E rewrite using the segment target/original mm3_per_mm ratio;
7. preserve non-extrusion moves/comments/order;
8. ensure rewritten loop remains geometrically identical to Orca output.

Do not change XY of the original top loop in v1.

## 15. Intermediate-pass emission
Intermediate passes are inserted after completion of the lower structural layer and before execution of the upper structural layer's target outer wall.

Actual insertion anchor/order MUST be verified against golden fixture before enabling printer mode.

For each intermediate pass:
- process lower command Z to higher command Z;
- travel/retract using supported known state;
- emit linear G1 XY moves only;
- E derived from planned mm3_per_mm and filament area;
- conservative configurable speed;
- restore state required by original G-code.

The emitter MUST NOT silently invent unsupported firmware commands.

## 16. Idempotence
Markers:

; ADAPTIVE_SUBEDGE_BEGIN plan=<hash> version=<version>
...
; ADAPTIVE_SUBEDGE_END plan=<hash>

A matching marker means already injected. Do not inject twice.

## 17. Atomicity
1. read original;
2. parse fully;
3. match exactly one plan;
4. validate all anchors and state;
5. build full modified output separately;
6. parse/sanity-check modified output;
7. only then replace working file.

Any failure leaves original unchanged.

## 18. Cache behavior
If export occurs without a matching in-process plan:
- do not reconstruct from G-code;
- do not inject;
- status PLAN_MISSING;
- user diagnostic says re-slice with plugin enabled.

Plugin activation/config changes are expected to invalidate slicing; tests must verify supported Orca versions.

## 19. Test gates

### Gate A — architecture
- import-boundary tests
- frozen DTO tests
- canonical serialization/hash determinism
- no live Orca refs

### Gate B — coordinate adapter
- transformed mesh fixture
- scaled XY conversion
- ContourZ relative-Z -> absolute-Z fixture

### Gate C — pure engine
- flow formula vs Orca Flow reference cases
- planar and varying-Z top-wall segment rewrite model
- bead model
- error metrics
- optimizer constraints
- whole-loop schedule
- no-refinement identity

### Gate D — Orca analyzer
- ZAA enabled
- ZAA disabled
- posSimplifyPath firing
- unsupported feature gates
- plan generation

### Gate E — parser dry-run
Before any write:
- supported Bambu/Orca golden G-code fixture
- absolute XY + relative E verification
- layer/outer-wall anchor report
- no file modifications

### Gate F — rewrite/emitter offline
- outer-wall E rescaling
- intermediate lower-Z-first path output
- parser round-trip
- idempotence
- state restoration
- original unchanged on failure

### Gate G — atomic postprocess on copies
- psGCodePostProcess integration
- exactly-one plan match
- multiple/no plan skip
- repeated export/upload copies

### Gate H — physical printer coupon
Only after A-G pass.
Simple single-volume slope coupon first.

## 20. Required physical comparison
Compare:
- normal layer
- fine conventional layer
- ZAA-only
- ZAA + Adaptive Sub-Edge

Record error, roughness, time, material, wall artifacts and failure modes.

## 21. Coding-agent rules
- do not modify legacy Smoothificator scripts unless explicitly tasked;
- no custom Orca C++ in v1;
- no posContouring analyzer;
- no regex-only injection;
- no UI call from SlicingPipeline execute();
- no live Orca object storage;
- no additive-only sub-edge model;
- no uniform top-wall flow assumption when ZAA makes the upper wall non-planar;
- no partial-loop refinement in v1;
- no absolute-E injection in v1;
- no partial file writes;
- no unsupported-feature guessing;
- deterministic behavior for identical input/settings;
- tests accompany every behavior change;
- safety/architecture relaxation requires Accepted ADR first.
