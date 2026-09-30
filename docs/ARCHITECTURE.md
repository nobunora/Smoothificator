# Architecture and Responsibility Boundaries

This document is normative. Its goals are change locality, safety, deterministic execution, and clear ownership.

## 1. Dependency direction

Dependencies point inward:

```text
Orca / G-code / UI / compatibility adapters
            ↓
       Application
            ↓
          Engine
            ↓
          Domain
```

Domain and engine MUST NOT import Orca, G-code, UI, filesystem, or concrete compatibility modules.

## 2. Canonical source tree

```text
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
    material_side.py
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
  compatibility/
    orca_contract.py
    bambu_contract.py
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
    execution_frame.py
    quantization.py
    retraction.py
    downstream_clearance.py
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
  fixtures/
    gcode/
    plans/
    orca/
  regression/
  printer/
```

Do not add generic `utils.py`, `helpers.py`, `manager.py`, or `service.py` dumping grounds.

## 3. Domain ownership

The domain package owns immutable vocabulary only.

Primary types include:
- `ErrorMetrics`;
- `ToolClearanceProfile`;
- `PluginSettingsFingerprint`;
- `StructuralPathSegment`;
- `StructuralLoopReference`;
- `SurfaceBand`;
- `SubEdgeSegment`;
- `SubEdgePath`;
- `InsertionAnchor`;
- `SubEdgePlan`;
- `ExecutionConfigFingerprint`;
- Settings and stable reason/status enums.

Domain types use:
- centered Orca PrintObject slice-space;
- millimeters;
- mm³/mm;
- explicit units in field names where ambiguity is plausible.

Domain MUST NOT contain:
- Orca pybind objects;
- machine G-code coordinate offsets;
- G-code commands/strings;
- mutable runtime injection status.

## 4. Engine ownership

The engine owns pure physical/geometric decision logic:
- source-surface sectioning;
- source orientation/material-side validation;
- residual surface-band derivation;
- centerline placement;
- finite-bead prediction;
- geometric flow model;
- support/nesting;
- collision/clearance;
- error metrics;
- candidate search/optimization;
- cost scoring.

The engine receives already-normalized structural baseline data.

It MUST NOT:
- read Orca config directly;
- know hook names;
- parse/emit G-code;
- apply machine execution-frame translation;
- know printer profile filenames;
- mutate PlanStore/UI.

## 5. Application ownership

Application owns workflow and durable-in-process plugin state:
- `analyze_snapshot(snapshot, settings) -> SubEdgePlan`;
- plan validation;
- canonical serialization/hash;
- PlanStore;
- separate PlanExecutionStatus store;
- cancellation orchestration.

The immutable plan owns execution intent.

Runtime export/injection status is not part of the plan hash.

## 6. Orca adapter ownership

`orca_plugin/adapters/` is the only layer allowed to import live Orca slicing/model bindings.

It owns:
- live-object validation;
- centered slice-frame reconstruction per ADR-0012;
- scaled-coordinate conversion;
- ZAA relative-Z normalization;
- structural effective commanded-flow normalization;
- source ModelInstance/ModelVolume transform handling;
- closed-manifold orientation/material-side validation;
- resolved semantic config extraction;
- ExecutionConfigFingerprint construction;
- PluginSettingsFingerprint construction from validated plugin-owned Settings at the application boundary;
- stable snapshot/reference fingerprints.

No live Orca object or Orca-backed zero-copy array may escape `execute(ctx)`.

## 7. Compatibility ownership

`orca_plugin/compatibility/` owns version-specific facts that are external contracts, including:
- audited Orca source version/family;
- formatter precision/rounding constants;
- required config keys and semantic resolution rules;
- supported Bambu layer-boundary markers/custom-code expectations;
- profile-family compatibility descriptors.

These modules MUST NOT contain optimization policy.

Unknown/incompatible version facts fail closed.

## 8. G-code adapter ownership

`orca_plugin/gcode/` is execution-only.

It owns:
- binary line-stream lexical/parser state with raw-byte preservation;
- actual emitted machine-state reconstruction;
- plan selection/matching;
- downstream-original-motion clearance simulation against candidate material;
- seam-invariant structural-loop matching;
- execution-frame translation;
- Orca-compatible quantization;
- relative-E retraction-state handling;
- candidate command derivation from immutable plan;
- safe-ceiling travel;
- byte-preserving binary-line temp emission/sanity validation/atomic replacement;
- PluginResult mapping at the capability boundary.

It MUST NOT:
- run candidate generation/optimization;
- modify plan geometry/flow intent;
- rewrite original structural extrusion in v1;
- inspect source mesh.

## 9. UI ownership

UI consumes copied immutable plan plus runtime status/read models.

It may display:
- geometry;
- errors;
- compatibility gates;
- execution status.

It MUST NOT:
- own optimizer decisions;
- parse final G-code;
- read live slicing objects;
- change plan data to make injection possible.

## 10. Canonical centered geometry frame

All domain geometry uses Orca's centered PrintObject slice-space in mm.

Printable v1 reconstruction follows ADR-0012:
- one total ModelInstance;
- one ModelPart volume;
- reconstruct `center_offset` from instance-no-offset transformed source geometry;
- apply centered PrintObject transform;
- verify parity against PrintObject/sliced path geometry.

Coordinate conversion is forbidden outside the Orca adapter.

## 11. Structural baseline semantics

Each `StructuralPathSegment` contains enough immutable information to model the final simplified Orca baseline:
- print-space XYZ;
- width;
- nominal path height;
- local effective ZAA bead height;
- geometric path mm³/mm;
- effective commanded flow modifiers used by the audited Orca semantics;
- role/layer/reference metadata.

Do not assume spatially constant flow for ZAA paths.

## 12. Candidate plan semantics

`SubEdgeSegment` stores:
- high-precision print-space start/end XY;
- plan-space Z inherited from the parent path's constant `command_z_mm`;
- local support Z;
- effective bead height;
- width;
- `geometric_mm3_per_mm`;
- `commanded_mm3_per_mm`;
- speed limits/policy;
- validation/support metadata.

It MUST NOT store machine-coordinate XYZ or authoritative final emitted E.

Every printable v1 `SubEdgePath` is already an open execution path at one constant `command_z_mm`. Closed source contours are canonicalized/seam-clipped before the plan is frozen.

Final E is derived at export after execution-frame mapping and XYZ quantization per ADR-0021.

`SubEdgePath` is an ordered collection of segments plus path-level order/travel metadata.

## 13. Structural matching reference

The plan stores `StructuralLoopReference`, not an ordered raw point hash.

Reference semantics are invariant to:
- cyclic seam start;
- normal seam split;
- collinear subdivision;
- configured single seam-gap tail clipping.

Final matching remains strict about shape, scale, orientation class, and ambiguity.

## 14. Runtime execution state

The G-code parser owns `SavedMachineState`:
- actual emitted XYZ;
- G90/G91;
- M82/M83;
- active tool;
- relative-E/retraction state;
- feed;
- supported acceleration/modal state;
- layer/custom-code context.

The injector restores this state exactly according to ADR-0013/0018.

No domain object owns mutable machine state.

## 15. Execution-frame separation

Plan geometry remains in centered print-space.

Only `execution_frame.py` may derive/apply the validated constant machine translation ((dx,dy,dz)).

No engine/UI/application module may depend on machine offsets.

## 16. Quantization separation

Only `quantization.py` owns pinned Orca formatter behavior.

Emitter, matcher tolerances, and final execution validation use the same quantizer.

Do not call Python built-in `round()` for Orca-compatible coordinate/E formatting.

## 17. Configuration ownership

`orca_config.py` owns raw-key -> resolved-semantic-value mapping.

The fingerprint hashes canonical semantic values used by the plugin, including:
- flow modifiers;
- active retraction values;
- seam settings;
- motion/speed/Zsafe values;
- custom-code feature gates.

No other module chooses override precedence independently.

The compatibility module defines which semantics/keys are required for a supported Orca family.

## 18. Data ownership and mutation

### Live Orca data
Owner: Orca.
Lifetime: current callback only.
Never stored.

### GeometrySnapshot
Owner: application.
Copy-owned.
Large arrays are copied and marked non-writeable.

### Engine work buffers
Owner: one engine invocation.
Locally mutable only.

### SubEdgePlan
Owner: application.
Frozen and deterministic.

### PlanExecutionStatus
Owner: application infrastructure.
Mutable separately from plan.

### PlanStore
Thread-safe, bounded, process-local.
Stores immutable plans + status metadata only.

### G-code parser/emitter state
Owned by one postprocess invocation.
Never shared with optimizer/UI.

### Temp output
Owned by one injector attempt.
Parser/emitter uses binary line streams. Untouched original bytes and line endings are copied exactly. Original working file is untouched until full validation/sanity succeeds.

## 19. Component contract checklist

Every non-trivial component must define:
1. what it owns;
2. what it explicitly does not own;
3. accepted inputs, units, and coordinate frame;
4. produced outputs;
5. invariants;
6. expected failure categories;
7. allowed dependencies;
8. state it may mutate.

Adapters translate contracts; they do not redefine domain meaning.

## 20. Stable interfaces

Representative contracts:

```text
MeshSectionProvider.section(...)
SurfaceBandPlanner.plan(...)
SurfacePredictor.predict(...)
ErrorEstimator.estimate(...)
SubEdgeOptimizer.solve(...)

PlanRepository.put(...)
PlanRepository.candidates(...)
ExecutionStatusRepository.set(...)

GCodeParser.scan(...)
PlanMatcher.match(...)
ExecutionFrameResolver.resolve(...)
OrcaQuantizer.quantize_xyz/e(...)
RetractionController.plan_candidate_cycle(...)
DownstreamMotionClearanceValidator.validate(...)
PlanInjector.prepare/emit(...)
PreviewRenderer.render(...)
```

Avoid speculative interfaces that have no second implementation/test need.

## 21. Dependency rules

Forbidden:
- domain/engine -> `orca_plugin`;
- engine -> G-code/compatibility;
- G-code -> optimizer/source mesh;
- UI -> live Orca/G-code parser/optimizer;
- injector -> engine;
- adapters -> UI;
- multiple modules independently resolving Orca config precedence;
- multiple modules independently implementing formatter rounding.

CI MUST enforce material import boundaries.

## 22. Serialization and determinism

Canonical plan serialization exists only in `application/serialization.py`.

Plan hash excludes:
- timestamps;
- memory addresses;
- process-local ObjectIDs;
- final export machine offsets/status.

Use deterministic numeric canonicalization.

Plan schema is versioned.

## 23. State, concurrency, idempotency

Every mutable state has one owner.

PlanStore defines:
- lock discipline;
- bounded capacity;
- stale/current-session semantics;
- candidate enumeration;
- status update ownership.

G-code injection defines:
- one idempotency plan hash;
- already-injected marker behavior;
- no partial commit;
- duplicate postprocess behavior on separate working copies.

## 24. Failure containment

Validate risky state before side effects.

Expected unsupported/validation conditions:
- produce stable reason;
- return PluginResult.Skipped at postprocess;
- leave original G-code untouched.

Unexpected exceptions are mapped centrally according to ADR-0019.

No guessed fallback may modify printer behavior.

## 25. Observability

Structured diagnostics should reconstruct:
- plan hash / attempt id;
- plugin-settings fingerprint;
- plugin + audited Orca compatibility version;
- execution config fingerprint;
- phase durations;
- candidate/segment summary;
- structural match error;
- execution-frame translation;
- quantization deltas;
- saved/restored state digest;
- chosen speed/volumetric margin/Zsafe;
- stop/failure reason;
- final injection status.

Do not log entire models/G-code or sensitive data unnecessarily.

## 26. Performance/resource contracts

Before production readiness define and measure:
- maximum supported mesh/path/segment counts;
- optimizer search budget;
- PlanStore bounds;
- analysis cancellation latency;
- G-code streaming memory bound;
- temp disk usage;
- postprocess passes/time.

Correctness takes precedence over performance changes.

## 27. Compatibility and rollback

Each supported Orca/profile family has:
- exact version/commit;
- fixture set;
- compatibility descriptor;
- resolved config contract;
- matcher/parser expectations;
- rollback/disable rule.

Compatibility expansion requires fixtures/tests and ADR when safety semantics change.

## 28. Source-mesh validity

Printable v1 source geometry must pass ADR-0027 and ADR-0030 before engine use:
- finite vertices;
- valid triangle indices;
- current bound ModelVolume reports manifold;
- shared-edge orientation/material side is deterministic;
- mirrored/global orientation is resolved without mutating Orca mesh;
- non-degenerate transformed bounds;
- unambiguous required plane sections.

The plugin does not create an independent mesh-repair authority.

## 29. Downstream clearance ownership

ToolClearanceProfile ownership:
- schema/value object lives in domain/settings;
- selected profile id/version and margins participate in PluginSettingsFingerprint;
- physical source/measurement evidence lives in printer fixture/review records;
- G-code validator consumes the immutable profile but does not invent or modify it.



`downstream_clearance.py` consumes only:
- final parsed original motion;
- quantized machine-space candidate bead envelopes;
- a versioned ToolClearanceProfile.

It does not change candidate geometry.

It checks future unchanged Orca motion because Orca generated that motion before candidate material existed.

Software clearance is a conservative proxy. Physical hotend/nozzle envelope calibration belongs to printer-fixture evidence, not the geometry engine.

## 30. Binary G-code ownership

G-code parser/emitter follows ADR-0031:
- binary line stream;
- untouched raw bytes preserved exactly;
- local newline convention preserved for insertions;
- unsupported non-ASCII command bytes fail closed;
- opaque non-ASCII comment bytes may be preserved when they do not affect interpretation;
- temp file/atomic replacement semantics are compatibility-tested per platform.

No module is allowed to normalize the full G-code text encoding/newlines.

## 31. File and change discipline

- one responsibility per file/function;
- target <400 logical lines;
- split >600 unless generated/static;
- no generic dumping-ground modules;
- no feature + unrelated refactor/format churn;
- safety/architecture changes require ADR first;
- focused owner tests before broader integration checks;
- inspect final diff and affected execution paths.
