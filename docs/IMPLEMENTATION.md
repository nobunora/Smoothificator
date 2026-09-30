# Implementation Specification — Stock Orca Plugin

This document is normative. Coding agents MUST follow it unless a later Accepted ADR supersedes a requirement.

## 0. Canonical v1 architecture

Use **stock OrcaSlicer + Python plugin only**.

Plugin capabilities:
1. SlicingPipeline capability:
   - posSimplifyPath -> copy/normalize final geometry, analyze, create immutable SubEdgePlan.
   - psGCodePostProcess -> parse final G-code, select exactly one plan, inject additive SubEdge paths.
2. Script capability:
   - preview/diagnostics using copied plan/status data.

No Orca C++ modification in v1.

The original Orca structural G-code is not rewritten in v1. SubEdge is additive-only at execution time, but candidate flow is optimized against the final combined finite-bead surface so additive overfill is explicitly modeled.

## 1. Normative ADRs

Before implementation, read:
- ADR-0001 analyzer after path simplification
- ADR-0002 v1 supported geometry/plugin environment
- ADR-0003 combined final surface / candidate flow
- ADR-0004 minimum effective bead height
- ADR-0005 surface-band centerlines/nesting
- ADR-0006 Orca ZAA Z/flow semantics
- ADR-0007 Bambu structural-layer-boundary safe-ceiling injection
- ADR-0008 relative-E Bambu profile restriction
- ADR-0009 validated print-space -> G-code-space translation
- ADR-0010 Orca-compatible filament flow-ratio E conversion

If this file conflicts with those ADRs, ADR wins.

## 2. Required source tree

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
    surface_band.py
    candidate_generator.py
    z_optimizer.py
    support.py
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
    emitter.py
    injector.py
    atomic_writer.py

tests/
  architecture/
  unit/
  analytic/
  integration/
  fixtures/gcode/
  fixtures/plans/
  regression/
  printer/

Do not add a generic utils.py.

## 3. Orca execution model

### posSimplifyPath
Selected because:
- it runs after Z Contouring;
- it runs after simplify_extrusion_path();
- unlike posContouring it is not conditional on ZAA need for a fresh processed object.

Caveat:
Orca intentionally avoids firing geometry hooks on cache-loaded plugin-final objects.

If no current-session matching plan exists at export, skip injection and instruct re-slice.

### psGCodePostProcess
At this step:
- ctx.print = None
- ctx.object = None
- ctx.gcode_path points to working exported file
- ctx.host/output_name available
- hook may run more than once on separate working copies
- output is not reflected in standard Orca preview

## 4. Snapshot adapter

orca_plugin/adapters/geometry_snapshot.py is the only module allowed to touch live slicing objects.

It MUST:
1. verify supported object/profile gates;
2. copy source mesh;
3. copy layer structural metadata;
4. copy simplified external-perimeter paths;
5. normalize coordinates/flows;
6. copy required config;
7. release all live references.

### 4.1 XY normalization
Use orca.slicing.unscale() to convert scaled path coordinates to print-space mm.

### 4.2 Z normalization
Orca ContourZ stores path point Z as layer-relative offset d.

For every path point:
Z_abs = layer.print_z + unscale(point.z)

Store raw offset only as diagnostic metadata.

### 4.3 ZAA local flow normalization
For Z-contoured non-ironing line endpoint offset d:
effective_height = path.height + d
effective_mm3_per_mm = path.mm3_per_mm * effective_height / path.height

This mirrors Orca GCode.cpp.

Reject/analysis-only if effective_height is invalid/non-positive.

### 4.4 Source mesh transform
v1:
- exactly one ModelPart volume;
- mesh vertices are local mm;
- apply volume.matrix() then PrintObject.trafo() to print-space.

Before engine implementation, create a transform fixture proving this convention against known translated/rotated/scaled coupon geometry.

### 4.5 Snapshot immutability
NumPy arrays copied from Orca MUST be copied into plugin ownership and set writeable=False.

No pybind object or zero-copy view whose base is Orca may survive execute().

## 5. Domain model

### ErrorMetrics
Frozen:
- e_max_mm
- e_rms_mm
- e_p95_mm
- signed_mean_mm

### StructuralPathSegment
Frozen:
- absolute start/end XYZ
- effective local bead height
- effective local mm3_per_mm
- width
- role
- source layer id
- stable geometry fingerprint

### SurfaceBand
Frozen:
- source error region
- target material boundary geometry
- supporting lower-envelope reference
- nesting/support metadata

### SubEdgePath
Frozen:
- path_id
- interval_id
- ordered print-space XYZ centerline
- nominal/effective bead height model
- width_mm
- mm3_per_mm
- estimated volume
- speed policy
- ordering key
- support metadata
- source error region

A path may be constant-Z or may later support a bounded Z profile, but v1 candidate generation should prefer constant-Z centerlines where possible.

### InsertionAnchor
Frozen:
- target structural layer interval
- stable layer/comment fingerprint
- expected saved boundary XYZ/state
- tolerance
- target profile family

### SubEdgePlan
Frozen:
- schema/plugin version
- deterministic plan hash
- Orca version/profile fingerprint
- source geometry/config hash
- paths
- anchors
- metrics before/after predicted
- added length/volume/time estimate
- injectability status/reason

Do not include timestamps or runtime Orca ObjectIDs in hash.

### PlanExecutionStatus
Separate mutable store:
PLANNED / INJECTION_PASS / INJECTION_SKIPPED / INJECTION_FAIL + reason.

## 6. Surface geometry model

### 6.1 Boundary != centerline
Mesh-plane intersection is a target material boundary.

Never emit it directly as nozzle centerline.

surface_band.py derives printable centerline candidates inside material using:
- target boundary
- bead width/shape
- support envelope
- nesting
- final envelope error

### 6.2 Multiple paths
A residual shallow terrace may require multiple paths.

Candidate set may include:
- several centerlines at same Z;
- several at different Z;
- pairwise Z differences below 0.08 mm.

No fixed 1/2 or 1/3 rule.

### 6.3 Nesting
Printable v1 requires top-facing/self-supported nesting:
higher material cross-section must be contained by lower support within tolerance.

Outward-expanding unsupported regions are analysis-only.

## 7. Bead/flow model

### 7.1 Candidate bead
Initial non-bridge cross-section matches Orca rounded rectangle:

A = h * (w - h * (1 - pi/4))
mm3_per_mm = A

Candidate flow/width/height are part of optimization within configured/calibrated limits.

### 7.2 Minimum 0.08 rule
h_min = 0.08 mm initial 0.4-nozzle value.

It applies to effective bead height above local support:

h_eff = z_nozzle - z_support

It does NOT impose |z_i-z_j| >= 0.08 between candidates.

### 7.3 Combined final surface
Predict:
- lower structural/ZAA beads
- candidate SubEdge beads
- upper structural/ZAA beads unchanged

A candidate that causes unacceptable overbuild due structural bead overlap is rejected or assigned different candidate flow.

Do not rewrite original structural wall flow in v1.

## 8. Error estimator

Primary:
surface-normal / closest-reference signed distance.

Required:
- E_max
- E_rms
- E_p95
- signed bias

Sampling density MUST be explicitly configured/tested and deterministic.

## 9. Optimizer

Inputs:
- final simplified structural/ZAA geometry
- source surface bands
- support envelope
- printer/material candidate limits
- error tolerance
- cost weights

Search:
1. generate candidate centerlines/height choices;
2. derive local support and effective bead height;
3. derive candidate flow;
4. combine with unchanged structural beads;
5. reject unsupported/crossing/clearance-invalid candidates;
6. compute final error;
7. choose minimum-cost feasible set.

The first optimizer may use bounded grid/beam search. Avoid premature continuous optimization.

Determinism is mandatory.

## 10. v1 printable environment

Injection MUST be disabled unless all gates pass:

Geometry:
- one printable PrintObject
- one printable instance
- one ModelPart volume
- no negative/modifier volumes
- nested/self-supported target
- no support/raft
- no bridge target
- no ironing
- no scarf/sloped seam
- no spiral vase

Plugin environment:
- fresh current-session slice
- no classic post_process script
- no other slicing-pipeline plugin

Printer/G-code:
- validated Bambu/Orca 0.4 mm profile family
- one tool
- use_relative_e_distances=true
- use_firmware_retraction=false
- gcode_add_line_number=false
- enable_arc_fitting=false
- validated motion-neutral before_layer_change_gcode/layer_change_gcode environment

Analysis may run outside these gates, but injection is forbidden.

## 11. PlanStore

Process-local, thread-safe, bounded.

Store immutable plans and separate status records.

Do not map by runtime object pointer/id.

At export, matcher considers current-session injectable candidate plans.

Exactly one plan must match final G-code fingerprints.

Zero matches:
PLAN_MISSING/PLAN_MISMATCH -> skip.

Multiple:
PLAN_AMBIGUOUS -> skip.

Never reconstruct optimization from G-code.

## 12. Preview

Script capability opens/refreshes host-owned UI using copied plan/status data.

Preview MUST show:
- structural baseline/ZAA paths
- target material boundary
- planned SubEdge centerlines
- bead height/flow
- support/nesting diagnostics
- error heatmap
- before/after metrics
- material/time estimate
- plan hash/status

Preview and injector consume same plan serialization.

No UI call from SlicingPipeline worker.

## 13. G-code parser

Parser/state machine, not regex-only.

Track:
- G90/G91
- M82/M83
- XYZ/E
- feed
- retraction state
- active tool
- layer/reserved tags
- object/type comments
- custom layer-change region
- supported Bambu-specific state required by fixture

Unknown state-changing command in relevant region disables injection.

Line-number/checksum mode unsupported v1.

Arc target unsupported v1.

## 14. Execution-frame resolution, injection anchor and safe-ceiling execution

Use ADR-0007 and ADR-0009.

### 14.1 Execution-frame resolution
SubEdgePlan geometry is print-space mm and MUST NOT be emitted directly.

Before validating insertion paths:
1. match known baseline structural path geometry from the plan to the corresponding final G-code path;
2. derive dx/dy from multiple corresponding XY samples;
3. derive dz from planned structural layer Z versus actual machine G-code structural Z;
4. require one constant translation within configured tolerances;
5. reject ambiguous, non-constant, rotated/scaled/sheared mappings.

The resolver returns an immutable ExecutionFrameTranslation(dx_mm, dy_mm, dz_mm).

Only orca_plugin/gcode may apply this translation.

### 14.2 Safe-ceiling execution

For each structural interval:
1. identify validated upper structural layer boundary using reserved tags/known Bambu profile markers;
2. confirm configured before/layer-change custom G-code is supported/motion-neutral;
3. capture saved upper-layer state;
4. choose machine-coordinate Zsafe >= actual upper structural machine Z + configured travel lift;
5. for every added path:
   - retract/known safe state;
   - raise vertically to Zsafe;
   - non-extruding XY travel at Zsafe only;
   - descend vertically to candidate start Z;
   - unretract;
   - print candidate;
   - retract;
   - raise to Zsafe;
6. after final path:
   - return at Zsafe to saved boundary XY;
   - descend to saved upper structural Z;
   - restore feed/retraction/modal state;
   - resume original G-code.

No non-extruding XY travel below Zsafe in printable v1.

Original Orca extrusion lines remain untouched.

## 15. Relative-E emitter

v1 only injects when M83/relative E semantics are verified for target region/profile.

For candidate move length L:
volume = L * mm3_per_mm
filament_area = pi * filament_diameter^2 / 4
E_per_mm3 = filament_flow_ratio / filament_area
E = volume * E_per_mm3

This MUST match Orca Extruder::e_per_mm3() behavior for the active v1 filament.

filament_diameter and filament_flow_ratio are captured during planning and validated against the supported final profile/fixture before injection.

Do not implement absolute-E restoration in v1.

## 16. Idempotence

Markers:
; ADAPTIVE_SUBEDGE_BEGIN plan=<hash> version=<version>
...
; ADAPTIVE_SUBEDGE_END plan=<hash>

If matching markers exist, do not inject twice.

## 17. Streaming/atomic file processing

Do NOT require loading a hundreds-of-MB G-code fully into memory.

Use a multi-pass design:

Pass 1 — validation:
- stream parse;
- identify profile/state/anchors;
- match exactly one plan;
- validate every planned insertion.

Pass 2 — emission:
- re-open original;
- stream to temp file;
- inject validated blocks at anchors;
- preserve original bytes/lines elsewhere.

Pass 3 — sanity:
- parse temp output;
- verify markers/count/state invariants.

Then atomically replace ctx.gcode_path.

On any failure delete temp and leave original unchanged.

## 18. Cache behavior

If posSimplifyPath did not run for current session and no matching plan exists:
- skip injection;
- status PLAN_MISSING;
- diagnostic: re-slice with plugin enabled.

Do not force geometry inference from cached/final G-code.

## 19. Implementation/test gates

### Gate A — architecture skeleton
- package tree
- frozen DTOs
- typed errors
- import-boundary tests
- serializer/hash
- PlanStore/status

### Gate B — Orca semantics parity
- ContourZ relative-Z normalization
- ZAA GCode local flow scaling parity
- source transform fixture

### Gate C — pure geometry engine
- boundary/centerline distinction
- bead model
- effective support height
- multi-path shallow terrace
- nesting rejection
- error metrics
- deterministic optimizer

### Gate D — stock Orca analyzer
- ZAA on/off
- posSimplifyPath
- fresh/cache behavior
- feature gates
- real plan generation

### Gate E — Bambu fixture acquisition
Before any injection:
- exact Orca commit/version
- A1/P1S-P1P/X1 current 0.4 profiles as chosen
- relative E confirmed
- layer custom G-code validated
- line number/firmware retract/arcs off
- structural boundary manually verified

### Gate F — read-only parser/matcher
No writes.

### Gate G — offline emitter
Generate blocks against fixture copy; safe-ceiling/state tests.

### Gate H — streaming atomic postprocess
Working copies only; failure byte-preservation.

### Gate I — physical coupon
Only after A-H pass.

## 20. Coding-agent hard rules

- do not modify legacy Smoothificator scripts unless tasked;
- no custom Orca C++;
- use posSimplifyPath, not posContouring;
- no storing live Orca refs;
- no UI from slicing worker;
- no raw mesh-boundary-as-centerline;
- no pairwise 0.08-Z-spacing assumption;
- no original-wall flow rewrite in v1;
- no regex-only injector;
- no full-file mandatory in-memory rewrite;
- no unsupported profile guessing;
- no direct emission of print-space XY/Z without validated execution-frame translation;
- no E conversion that omits filament_flow_ratio;
- no partial writes;
- deterministic output;
- tests with every behavior change;
- ADR required before relaxing any safety/architecture constraint.
