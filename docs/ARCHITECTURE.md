# Architecture and Responsibility Boundaries

This document is normative. Its purpose is to make future changes local, reviewable and testable.

## 1. Dependency direction

Dependencies MUST point inward:

Orca adapters / UI / G-code I/O -> Application -> Engine -> Domain

The domain and engine MUST NOT import Orca APIs, UI APIs, filesystem APIs, or G-code parser modules.

## 2. Canonical package ownership

### adaptive_subedge/domain/
Immutable vocabulary only:
- geometry DTOs
- ErrorMetrics
- WallPass / WallPassSchedule
- OriginalWallRewrite
- SubEdgePlan
- InsertionAnchor
- Settings/value constraints
- status/reason enums
- typed expected-failure classes

### adaptive_subedge/engine/
Pure algorithms:
- finite-bead model
- error estimation
- mesh sectioning
- candidate generation
- surface-only extraction
- Z/pass optimization
- support/clearance validation
- cost scoring
- flow-area calculation

MUST NOT know Orca hook names or G-code syntax.

### adaptive_subedge/application/
Workflow and stable state:
- analyze_snapshot(snapshot, settings) -> SubEdgePlan
- plan validation
- canonical serialization/hashing
- PlanStore
- execution-status repository
- cancellation abstraction

### adaptive_subedge/ports/
Narrow interfaces for replaceable services:
- MeshSectionProvider
- PlanRepository
- CancellationToken
- optional SurfacePredictor interface

### orca_plugin/adapters/
The ONLY code allowed to import Orca geometry/slicing bindings.

Responsibilities:
- copy live ctx.print/ctx.object data
- convert Orca scaled/path-local coordinates into canonical coordinates
- map Orca config/settings
- capture source mesh + transforms
- build stable source fingerprints

All live Orca references terminate here.

### orca_plugin/capabilities/
Thin Orca entrypoints:
- slicing.py handles posSimplifyPath and psGCodePostProcess
- preview.py is a Script/UI-safe capability

No geometry algorithms.

### orca_plugin/ui/
Rendering only:
- PreviewModel creation from immutable plan/status data
- HTML/window rendering
- user-visible diagnostics

MUST NOT optimize or mutate plans.

### orca_plugin/gcode/
Execution adapter:
- lexer/parser/state machine
- plan matching
- anchors
- original-wall rewrite
- sub-edge emission
- validation
- atomic file replacement

MUST NOT import optimizer/candidate-generation modules.

## 3. Canonical coordinate system

All domain/engine geometry is **absolute print-space millimeters**.

The Orca adapter MUST normalize before any domain object is constructed.

Important Orca detail:
- ExtrusionPath XY points are scaled print-object path coordinates.
- ContourZ stores point Z as a **layer-relative offset**.
- Therefore:
  Z_abs_mm = layer.print_z + orca.slicing.unscale(point_z)

Source mesh:
- ModelVolume.mesh() vertices are volume-local mm.
- For v1's single positive volume, transform to print space using the audited volume-to-object and PrintObject object-to-print transforms.
- GUI/world-model references MUST NOT be used from a slicing hook.

No engine module may perform Orca scaling/unscaling.

## 4. Data ownership

### Live Orca data
Owner: Orca.
Lifetime: execute(ctx) only.
Never stored.

### GeometrySnapshot
Owner: plugin application.
Copy-owned, immutable at boundary.
Large NumPy arrays MUST be copied and marked non-writeable before storage.

### Work buffers
Owner: one engine call.
May be mutable locally only.

### SubEdgePlan
Owner: application.
Frozen, canonical serialized, deterministic hash.
Contains geometry/execution intent only.

### PlanExecutionStatus
Owner: application infrastructure.
Mutable status separate from SubEdgePlan:
PLANNED / INJECTION_PASS / INJECTION_SKIPPED / INJECTION_FAIL.

Changing status MUST NOT change plan_hash.

### PlanStore
Thread-safe bounded process-local store of immutable plans plus separate status records.

### G-code document/state
Owned by one injector invocation.
Never shared with optimizer/UI.

## 5. Plan decomposition

A refined structural interval is represented as a WallPassSchedule.

It MUST contain:
- interval Z0/Z1
- original outer-wall reference/anchor
- zero or more intermediate WallPass records
- one OriginalWallRewrite describing the reduced remaining top-pass extrusion
- common schedule ordering

Each WallPass uses:
- absolute command_z_mm
- effective_height_mm
- XY contour
- width_mm
- mm3_per_mm
- ordering index

The plan MUST NOT represent sub-edges as additive material while leaving the top outer wall unchanged.

## 6. Mutation policy

Allowed mutation only:
- local numerical work buffers
- parser state during parsing
- private synchronized PlanStore indexes/status
- construction of a new output file

Public cross-boundary domain objects are immutable.

No function may mutate an input SubEdgePlan.

## 7. Dependency matrix

Allowed:
- domain -> stdlib / value-array types
- engine -> domain
- application -> domain + engine + ports
- Orca adapter -> domain/application interfaces + Orca
- G-code adapter -> domain/application interfaces
- UI -> domain/application read models
- capabilities -> adapters/application/G-code/UI entrypoints

Forbidden:
- domain/engine -> orca_plugin
- engine -> G-code
- G-code -> optimizer/candidate generation/source mesh analysis
- UI -> live Orca graph
- UI -> plan generation
- injector -> engine
- adapters -> UI

CI MUST enforce these boundaries.

## 8. Stable interfaces

MeshSectionProvider:
section(z_mm, region) -> tuple[Contour,...]

SurfacePredictor:
predict(pass_schedule, bead_profile) -> SurfaceEnvelope

ErrorEstimator:
estimate(reference, predicted) -> ErrorField + ErrorMetrics

SubEdgeOptimizer:
solve(problem) -> OptimizationResult

PlanRepository:
put(plan), candidates(), get(plan_hash)

ExecutionStatusRepository:
set(plan_hash,status,reason), get(plan_hash)

GCodeParser:
parse(text/bytes) -> ParsedDocument + checkpoints

PlanMatcher:
match(document, candidate_plans) -> exactly one plan or typed failure

PlanInjector:
prepare(document, plan) -> PreparedInjection
No filesystem write.

AtomicWriter:
replace_if_valid(path, prepared)

PreviewRenderer:
render(preview_model) -> UI payload

## 9. Error taxonomy

Expected failures use typed exceptions/reason codes:
- UnsupportedOrcaVersion
- SnapshotError
- GeometryUnsupported
- OptimizationInfeasible
- PlanMissing
- PlanAmbiguous
- PlanMismatch
- GCodeUnsupported
- AnchorMismatch
- InjectionValidationError
- InjectionAlreadyPresent
- UserCancelled

Unexpected exceptions are caught at the capability boundary, logged, and result in no injection.

## 10. Configuration ownership

One validated Settings object.

Adapters map Orca/user config into Settings exactly once per analysis.

Engine modules MUST NOT query Orca config.

Settings changes alter settings_hash and invalidate reuse.

## 11. Serialization and determinism

Canonical plan serialization exists only in application/serialization.py.

plan_hash MUST exclude:
- timestamps
- process-local addresses
- nondeterministic Orca ObjectIDs

Stable geometry should be represented using canonical fixed-unit integers/quantized values or deterministic binary encodings, not locale-dependent float formatting.

Migrations live under application/migrations/.

## 12. Performance

Correctness before optimization.

Copied mesh/path arrays may remain NumPy but MUST be read-only after snapshot construction.

Engine may vectorize/parallelize while preserving deterministic output.

No hidden global algorithm caches.

## 13. File cohesion

Guidelines:
- one responsibility per file
- target < 400 logical lines
- split > 600 lines unless generated/static table
- no generic utils.py
- helpers remain private until genuinely reused
- shared helpers go into narrowly named modules

## 14. Change procedure

Before behavior changes:
1. identify owning module
2. update boundary contract/test
3. avoid unrelated modules
4. if interface/safety architecture changes, write/update ADR first
5. update normative docs
6. run owner unit tests
7. run integration/regression tests

Cross-layer shortcuts require an ADR.
