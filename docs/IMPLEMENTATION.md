# Implementation Specification — Stock Orca Adaptive Sub-Edge Plugin

This document is normative for implementation. Coding agents MUST follow it unless an Accepted ADR explicitly supersedes a requirement.

See also:
- ARCHITECTURE.md
- SPECIFICATION.md
- ERROR_MODEL.md
- PLUGIN_REQUIREMENTS.md
- DEPENDENCY_AUDIT.md
- docs/adr/

---

## 0. v1 architecture

Use **stock OrcaSlicer + Python plugin only**.

One plugin package registers:
1. SlicingPipeline capability
   - `posSimplifyPath`: Analyzer
   - `psGCodePostProcess`: Injector
2. Script capability
   - Preview / diagnostics on UI thread

Canonical data flow:

```text
fresh Orca slice
  -> ZAA if applicable
  -> Orca simplify_extrusion_path()
  -> posSimplifyPath
       -> OrcaAdapter copies live graph
       -> GeometrySnapshot
       -> Analyzer / Engine
       -> immutable SubEdgePlan
       -> PlanStore
  -> Orca normal G-code generation
  -> psGCodePostProcess
       -> parse exported G-code
       -> GCodeIdentity + anchors
       -> exactly-one Plan match
       -> full validation
       -> streaming temp-file injection
       -> sanity parse
       -> atomic replace
  -> output

Script Preview
  -> reads copied PlanStore data only
  -> renders exact plan hash used by Injector
```

No Orca C++ modification in v1.

---

## 1. Required v1 gates

Printable Injection is enabled only when every gate passes.

### 1.1 Orca/plugin
- explicitly supported Orca version
- Python Plugin System available
- SlicingPipeline available
- this plugin is the only active slicing-pipeline capability
- classic `post_process` is empty
- current plugin load contains a fresh `posSimplifyPath` plan

### 1.2 Model
- exactly one printable PrintObject
- exactly one printable ModelInstance
- exactly one ModelPart volume
- no NegativeVolume
- no ParameterModifier
- no multimaterial painting/tool assignment changes
- validated coordinate frame
- target region is nested top-facing geometry:
  higher-Z material section contained in lower-Z material section within tolerance
- no outward-growing/downward-facing overhang target

### 1.3 Print process
- single tool/extruder
- 0.4 mm nozzle initial physical target
- PLA initial calibration target
- spiral vase off
- ironing off
- scarf/sloped seam off
- support off
- raft off
- arc fitting off
- G-code line numbering/checksum mode off

### 1.4 Extrusion / firmware
- relative E enabled
- firmware retraction off
- supported Bambu/Orca Marlin-style profile family
- before/layer-change custom G-code environment validates as supported/motion-neutral

Any failure -> analysis-only or Injection SKIPPED. Never silently relax gates.

---

## 2. Normative source tree

```text
adaptive_subedge/
  domain/
    coordinates.py
    geometry.py
    extrusion.py
    metrics.py
    plan.py
    settings.py
    status.py
    errors.py
    identity.py

  engine/
    bead_model.py
    baseline_surface.py
    error_estimator.py
    mesh_section.py
    surface_band.py
    path_layout.py
    candidate_generator.py
    z_optimizer.py
    support.py
    nozzle_clearance.py
    cost_model.py

  application/
    analyzer.py
    plan_store.py
    serialization.py
    hashing.py
    validation.py
    migrations/

  ports/
    planar_geometry.py
    cancellation.py

orca_plugin/
  adapters/
    geometry_snapshot.py
    coordinate_frame.py
    orca_config.py
    planar_geometry_orca.py
    fingerprint.py

  capabilities/
    slicing.py
    preview.py

  ui/
    preview_model.py
    preview_renderer.py

  gcode/
    dialect.py
    lexer.py
    parser.py
    state.py
    structural_layers.py
    identity.py
    anchors.py
    validation.py
    emitter.py
    injector.py
    atomic_writer.py

tests/
  architecture/
  unit/
  analytic/
  fixtures/
    gcode/
    plans/
    meshes/
  integration/
  regression/
```

No duplicate flat module layout is permitted.

---

## 3. Dependency boundaries

Normative dependency direction:

```text
orca_plugin adapters / ui / gcode
           ↓
adaptive_subedge application
           ↓
adaptive_subedge engine
           ↓
adaptive_subedge domain
```

Forbidden:
- domain -> engine/application/orca_plugin
- engine -> application/orca_plugin/G-code
- G-code -> optimizer/candidate/error-estimator
- UI -> Analyzer/optimizer/live Orca graph
- Injector -> source mesh / geometry analysis
- Preview -> independent plan generation

CI MUST enforce forbidden imports.

---

## 4. Coordinate conventions

### 4.1 Canonical domain frame
All domain geometry is expressed in **print-space millimetres** after OrcaAdapter normalization.

Domain engine never sees Orca scaled integer coordinates.

### 4.2 Source mesh
ModelVolume mesh vertices are local to the volume.

Adapter must transform them to canonical print frame using the bound Orca transform chain and verify the result against:
- PrintObject/sliced-path bounds
- known translated/rotated/scaled test models
- final G-code XY bounds

Do not guess transform order.

### 4.3 Orca extrusion XY
Raw extrusion-path XY is copied and converted to print-space mm by the adapter.

### 4.4 Orca ZAA path Z
**Critical:** raw `ExtrusionPath.points().z` after ZAA is a Z offset, not absolute machine/nozzle Z.

For path point offset d:

```text
z_nozzle_abs = layer.print_z + d
```

Store both raw offset and normalized absolute Z for diagnostics.

Normal planar paths generally have d=0.

### 4.5 Candidate Sub-edge Z
Domain `nozzle_z_mm` is absolute print-space nozzle height.

No candidate stores Orca-style relative Z offsets.

---

## 5. Extrusion / bead semantics

### 5.1 Orca parity model
For normal non-bridge rounded-rectangle bead:

```text
q = mm3_per_mm
  = h * (w - h * (1 - pi/4))
```

where:
- h = effective deposited bead height
- w = bead width

### 5.2 ZAA baseline flow
Orca GCode.cpp scales non-ironing ZAA extrusion by:

```text
ratio = (nominal_height + z_offset) / nominal_height
q_effective = q_nominal * ratio
h_effective = nominal_height + z_offset
```

Analyzer MUST reproduce this for post-ZAA baseline prediction.

Ironing is disabled in printable v1.

### 5.3 Sub-edge effective height
0.08 mm is initially the **minimum effective deposited bead height above local support**, not minimum Z separation between neighboring Sub-edges.

For candidate segment:

```text
h_effective = nozzle_z - support_surface_z
```

Require:
- h_effective >= settings.min_bead_height_mm
- h_effective <= supported maximum for profile/nozzle
- finite-bead / nozzle-clearance constraints pass

Two neighboring paths MAY differ in nozzle Z by less than 0.08 mm.

### 5.4 Flow ownership
Engine owns target width/height/q.

Emitter MUST NOT invent or retune flow.

v1 default candidate width SHOULD start from resolved outer-wall width and compute q using the rounded-rectangle model. Width optimization is a later extension unless needed by tests.

### 5.5 Segment-local extrusion
Domain representation MUST allow q/effective-height to vary by segment if the predicted support surface varies.

Do not force a single path-wide extrusion value if physics model says support gap differs materially.

---

## 6. Domain data types

All cross-boundary domain types are immutable.

### 6.1 Point / polyline
`Point2`, `Point3` value objects in mm.

Large arrays may use NumPy only if:
- defensively copied
- marked non-writeable before storage
- never aliased to Orca buffers

### 6.2 StructuralLayer
Frozen:
- layer_index
- print_z_mm
- slice_z_mm
- nominal_height_mm
- surface_relevant_paths

### 6.3 BaselineExtrusionSegment
Frozen:
- p0_abs_mm
- p1_abs_mm
- role
- width_mm
- nominal_height_mm
- effective_height_start/end
- effective_q_start/end
- source_path_id
- zaa_offset_start/end

### 6.4 SubEdgeSegment
Frozen:
- p0_xy_mm
- p1_xy_mm
- nozzle_z_mm
- width_mm
- effective_height_mm or endpoint heights
- mm3_per_mm
- support_z_mm or support references

### 6.5 SubEdgePath
Frozen:
- path_id
- interval_id
- source_error_region_id
- segments
- constant nozzle_z_mm for v1
- ordering_index
- predicted volume
- predicted time

### 6.6 InsertionAnchor
Frozen:
- lower/upper structural Z
- structural layer tag fingerprint
- expected changing-layer marker
- expected machine state constraints
- config/profile hash
- coordinate/geometry fingerprint

### 6.7 SubEdgePlan
Frozen:
- schema_version
- plugin_version
- plan_id
- deterministic plan_hash
- Orca version
- session_generation
- settings_hash
- geometry_hash
- config_hash
- machine/profile identity
- structural layer schedule
- paths
- anchors
- metrics_before
- metrics_after_predicted
- diagnostic metadata not participating in hash only when explicitly marked

### 6.8 Runtime status
Injection state is NOT part of SubEdgePlan.

Separate `PlanRuntimeRecord` / `InjectionAttempt` stores:
- PLANNED
- INJECTION_PASS
- INJECTION_SKIPPED
- INJECTION_FAIL
- timestamp
- output name/host
- reason code

---

## 7. GeometrySnapshot Adapter

File: `orca_plugin/adapters/geometry_snapshot.py`

This is the only Orca live-graph entry for analysis.

### 7.1 Mandatory tasks
1. Verify v1 gates.
2. Copy Orca version/config.
3. Verify one object/instance/ModelPart.
4. Copy source mesh vertices/triangles.
5. Transform source mesh to canonical print frame.
6. Copy layers and surface-relevant extrusion paths.
7. Normalize path XY to mm.
8. Normalize path Z offsets to absolute nozzle Z.
9. Reconstruct ZAA effective segment height/q.
10. Copy only required settings/profile values.
11. Construct immutable `GeometrySnapshot`.
12. Return no live Orca refs.

### 7.2 Surface-relevant path roles
Baseline model MUST include, when present:
- external perimeter / outer wall
- perimeter if it contributes to exposed surface
- top solid infill
- other explicitly modeled exposed roles

Ironing is rejected for printable v1.

Do not model only outer walls when top-surface paths define the actual exposed slope.

### 7.3 Z ambiguity gate
Scarf/sloped seam is rejected so nonzero raw path-Z offsets have a known ZAA interpretation.

---

## 8. Analyzer workflow

File: `adaptive_subedge/application/analyzer.py`

Called from `posSimplifyPath`.

Sequence:
1. check cancellation
2. adapter gate validation
3. build immutable snapshot
4. compute SliceIdentity/fingerprint
5. build post-ZAA baseline finite-bead surface
6. compute residual error field
7. detect target regions above tolerance
8. verify nested top-facing support condition
9. generate candidate nozzle-Z values and source boundaries
10. convert boundaries to valid material-side tool-center candidates
11. compute local support surface and effective bead height
12. lay out candidate paths with width/spacing
13. optimize path subset/Z/flow within v1 degrees of freedom
14. run nozzle/support/collision feasibility
15. score combined final surface including unchanged upper structural layer
16. create deterministic immutable plan
17. store plan in PlanStore
18. return

Poll cancellation during expensive loops.

---

## 9. Source section vs toolpath

A mesh-plane intersection `C(z)` is a geometric boundary, NOT a nozzle centerline.

Never emit C(z) directly as G-code.

### 9.1 SurfaceBand
Engine derives material/exposed region around target surface.

For v1 nested top-facing geometry:
- higher cross-section must be contained within lower cross-section
- candidate centerlines lie on material side
- line-width/bead envelope determines offset/spacing

### 9.2 PathLayout
`path_layout.py` converts geometric target boundary/band to one or more extrusion centerlines.

It may create many paths whose neighboring nozzle-Z differences are small.

Quality is evaluated from final bead envelope, not centerline proximity.

---

## 10. Optimizer

No fixed 1/2 or 1/3 pitch.

### 10.1 Search variables
v1:
- candidate path selection
- each path nozzle Z
- optionally per-segment q derived from effective bead height

Width starts fixed to resolved outer-wall width unless an Accepted ADR changes it.

### 10.2 Z search domain
For interval lower structural surface around Z0 and upper nominal Z1:
- candidate nozzle Z is between supported lower + min_bead_height and upper structural Z
- pairwise Z difference has no fixed 0.08 minimum
- machine Z quantization and nozzle clearance apply

### 10.3 Feasibility
Reject candidates for:
- bead height below minimum
- bead height/width/flow outside profile limits
- outward-growing unsupported geometry
- contour/path crossing
- unacceptable nozzle envelope intersection
- excessive overbuild
- insufficient material-side support
- NaN/invalid geometry

### 10.4 Objective
Primary target:
`E_max <= tolerance` where feasible.

Then minimize weighted:
- E_rms
- E_p95
- added time
- added volume
- starts/stops
- path count

If no feasible solution: no modification for that region.

---

## 11. Nozzle clearance

File: `engine/nozzle_clearance.py`

Do not assume A->B alone proves clearance when neighbor Z differences are small.

v1 nozzle model is configurable and conservative:
- flat/tip clearance radius
- cone/body envelope parameters as available
- safety margin

Unknown nozzle geometry may block physical Injection while still allowing analysis.

Non-extruding XY travel is handled separately by safe-ceiling policy.

---

## 12. PlanStore / identity

### 12.1 PlanStore
Thread-safe, process-local, bounded.

Stores:
- immutable plans
- runtime records separately

No Orca refs.

### 12.2 Fresh-slice generation
Each successful `posSimplifyPath` analysis increments/records current plugin session generation.

Orca cache may skip the hook. Therefore a cached export with no current matching plan is rejected.

### 12.3 Plan matching
Post-process must find exactly one matching plan using:
- plugin session
- Orca version
- settings/config hash
- machine/profile identity
- structural layer schedule
- geometry/layer fingerprint
- G-code anchors

Zero or multiple matches -> skip.

---

## 13. Preview

Script capability executes on UI thread.

Preview consumes copied plan/runtime only.

Show:
- post-ZAA baseline reference
- candidate/final Sub-edge paths
- nozzle Z per path
- effective bead height
- residual error heatmap
- before/after metrics
- predicted added volume/time
- plan hash
- runtime Injection status

Never compute a second plan for preview.

---

## 14. G-code dialect v1

Initial executable dialect:
current validated Orca Bambu 0.4 mm single-tool Marlin-style output.

Mandatory config:
- relative E
- firmware retraction off
- arc fitting off
- line numbers off
- spiral vase off
- ironing off
- scarf seam off

Parser may understand more states for diagnostics, but Injector refuses unsupported executable states.

---

## 15. Structural layer parsing

Do not infer structural layer boundaries from arbitrary Z moves because ZAA itself emits variable Z.

Use Orca reserved layer metadata:
- Layer_Change tag
- BBL `Z_HEIGHT` or non-BBL `Z`
- HEIGHT tag

For initial Bambu dialect also validate the expected changing-layer marker/state.

---

## 16. Initial Bambu layer-boundary injection point

Orca source order:
1. structural layer tags
2. before_layer_change_gcode
3. Orca `change_layer(print_z)`
4. layer_change_gcode
5. `;_SET_FAN_SPEED_CHANGING_LAYER`

Current inspected stock Bambu A1/P1P/P1S/X1 Carbon 0.4 templates:
- before-layer code effectively empty
- layer-change code contains only notification/progress M73/M991

v1 Injector validates this environment.

Insertion for interval [Z0,Z1] occurs immediately after the validated upper structural transition / changing-layer marker and before upper-layer extrusion.

If expected marker/state is absent or custom G-code is motionful/unknown -> skip.

---

## 17. Safe-ceiling execution policy

At injection anchor save:
- X/Y/Z
- relative-E mode
- logical E state
- feed rate
- retraction state
- active tool
- other tracked modal state

Let:
`Zsafe = max(saved_z, Z1 + configured_travel_lift)`

Default travel lift is resolved from supported profile/config and must be >0 for physical v1 unless an ADR/test explicitly changes this.

For each Sub-edge path, ordered by nozzle Z:
1. ensure retracted state
2. raise to Zsafe
3. travel XY at Zsafe to path start
4. descend vertically to path nozzle Z
5. unretract
6. extrude path
7. retract
8. raise to Zsafe

Between Sub-edge paths, **no non-extruding XY movement below Zsafe**.

After final path:
1. at Zsafe travel back to saved boundary XY
2. descend to saved boundary Z (upper structural layer state)
3. restore retraction/E/feed/modal state exactly
4. resume original G-code

Original timelapse/custom code after the anchor remains untouched and sees the same saved state.

---

## 18. G-code parser/state machine

Files under `orca_plugin/gcode/`.

No regex-only mutation.

Track:
- G90/G91 XYZ mode
- M82/M83 E mode
- X/Y/Z
- E
- F
- G92 coordinate resets
- retraction/unretraction in supported relative-E dialect
- active tool
- structural layer tags
- relevant Bambu layer markers
- comments/raw lines
- unsupported state-changing commands

Unknown line is preserved byte-for-byte.

Unknown state-changing semantics inside/around an injection interval -> skip.

v1 relative-E requirement simplifies E restoration. Absolute-E is parsed/diagnosed but not injectable.

---

## 19. G-code anchors

`InsertionAnchor` is not a best-effort hint; it is a validation contract.

Validate:
- structural upper Z
- structural HEIGHT
- layer ordinal/schedule
- expected marker order
- profile/config hash
- current XY/Z state sanity
- relative-E state
- active tool
- no existing adaptive marker

All planned intervals validate before any output file modification.

---

## 20. Streaming injection and atomicity

Do NOT load/rewrite hundreds of MB in one giant string.

Pass 1:
- stream-parse original
- compute GCodeIdentity
- validate all anchors/states
- record byte/line insertion positions and saved states

If any failure -> original untouched.

Pass 2:
- create temp file in same directory
- stream-copy original
- emit validated blocks at insertion positions

Pass 3:
- stream/sanity parse temp
- verify adaptive markers, structural layers and parser final-state invariants

Then atomic replace of working `ctx.gcode_path`.

If atomic replace cannot be guaranteed -> skip.

---

## 21. Idempotence

Emit versioned markers:

```text
; ADAPTIVE_SUBEDGE_BEGIN plan=<hash> version=<version> interval=<id>
...
; ADAPTIVE_SUBEDGE_END plan=<hash> interval=<id>
```

Matching marker already present -> no second injection.

Different/conflicting adaptive marker -> fail/skip.

---

## 22. Emission flow

For segment length L and accepted q:

```text
volume = L * q
filament_area = pi * filament_diameter^2 / 4
E_relative = volume / filament_area
```

Emitter uses accepted per-segment q only.

Emitter does not recompute bead physics.

Speed:
- configurable conservative Sub-edge speed
- initially capped by resolved outer-wall speed and filament volumetric limit
- exact physical defaults established during calibration, not guessed

---

## 23. Bambu profile whitelist/gates

Before physical v1, build golden fixtures for:
- A1 0.4
- P1P/P1S 0.4
- X1 Carbon 0.4

For each tested Orca release record:
- machine profile identity/hash
- process profile identity/hash
- layer-change template hash
- expected tags/markers
- relative-E config
- retraction config
- arc/line-number config

A changed unrecognized template/profile defaults to analysis-only until fixtures are updated.

---

## 24. Testing gates

### Phase A — architecture
- forbidden import tests
- deep immutability
- serializer/hash determinism
- typed errors
- PlanStore concurrency

### Phase B — physics/reference
- Orca Flow formula parity
- ZAA absolute-Z normalization parity
- ZAA local flow scaling parity
- ideal fixed slopes
- dense shallow-slope paths with pairwise dz <0.08
- geometric-boundary -> material-side centerline
- nested support
- overbuild
- nozzle envelope

### Phase C — Orca snapshot
- ZAA on/off
- translated model
- rotated model
- scaled model
- one object/instance/volume gates
- rejected modifier/negative/support/scarf/ironing
- cache/fresh-slice behavior
- path/mesh/G-code coordinate-frame consistency

### Phase D — parser read-only
Golden actual Orca outputs:
- structural layer tags
- ZAA variable-Z moves
- Bambu layer-change templates
- relative E/retractions/G92
- timelapse blocks
- unknown command preservation

### Phase E — dry run
- exact anchor matching
- safe-ceiling route
- lower-Z-first
- state restoration
- no output write
- generated diff review

### Phase F — atomic injector
- temp emission
- sanity parse
- atomic replace
- idempotence
- forced failure leaves original byte-identical
- repeated export/upload copies

### Phase G — physical
Only after all previous gates.
Manual G-code review required for first runs.

---

## 25. Coding-agent rules

Luna/Codex MUST:
- implement one roadmap phase at a time
- run phase tests before proceeding
- stop and update docs/ADR if source/API facts contradict specification
- never broaden supported scope opportunistically
- never modify legacy Smoothificator scripts unless explicitly tasked
- never add custom Orca C++ in v1
- never store live Orca/pybind graph refs
- never call UI from SlicingPipeline hook
- never make Injector depend on optimizer
- never write partial G-code
- never use regex-only mutation fallback
- never weaken a safety gate without Accepted ADR
- keep deterministic output for identical input/settings
- report every specification change with old/new behavior, reason, affected files and retest scope
