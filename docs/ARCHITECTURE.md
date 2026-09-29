# Architecture and Responsibility Boundaries

This document is normative. Its purpose is to make future changes local, reviewable and testable.

## 1. Architectural rule
Dependencies MUST point inward:

Orca Adapter/UI/G-code I/O -> Application orchestration -> Domain engine -> Domain models

The domain engine MUST NOT import Orca APIs, UI APIs, filesystem APIs, or G-code parser modules.

## 2. Layers

### A. Domain model
Package: adaptive_subedge/domain/

Owns immutable vocabulary only:
- geometry value objects
- ErrorMetrics
- SubEdgePath
- SubEdgePlan
- InsertionAnchor
- settings/value constraints
- reason/status enums

MUST NOT:
- read Orca
- parse G-code
- render UI
- access filesystem
- optimize using global mutable state

### B. Geometry/quality engine
Package: adaptive_subedge/engine/

Owns pure algorithms:
- finite bead model
- error estimation
- mesh sectioning abstraction
- candidate generation
- sub-edge extraction
- Z optimization
- collision/support checks
- cost scoring

Inputs/outputs are domain objects/arrays.

MUST NOT know:
- Orca hook names
- G-code syntax
- plugin UI
- PlanStore
- output files

### C. Application services
Package: adaptive_subedge/application/

Owns workflows:
- analyze_snapshot(snapshot, settings) -> SubEdgePlan
- validate_plan(plan)
- deterministic hashing/serialization
- PlanStore
- cancellation abstraction

May compose engine modules but MUST NOT directly depend on Orca live graph.

### D. Orca adapter
Package: orca_plugin/adapters/

Owns all Orca-specific read integration:
- copy ctx.print/ctx.object into GeometrySnapshot
- map Orca roles/settings/version
- detect ZAA state
- derive stable source fingerprints

This is the ONLY layer allowed to import Orca host/slicing bindings.

It MUST convert live objects to copied internal DTOs before returning.

### E. G-code execution adapter
Package: orca_plugin/gcode/

Owns:
- lexical preservation
- parser/state machine
- anchor matching
- emitter
- injection validation
- atomic working-file replacement

It consumes SubEdgePlan. It MUST NOT run geometry optimization.

### F. Preview/UI adapter
Package: orca_plugin/ui/

Owns rendering and user interaction only.

It consumes immutable plan/snapshot-derived preview DTOs.

MUST NOT:
- recalculate optimization
- mutate plan
- parse G-code to invent geometry
- access live slicing objects

### G. Plugin entrypoints
Package: orca_plugin/capabilities/

Very thin adapters:
- slicing.py: dispatch posContouring and psGCodePostProcess
- preview.py: UI-safe preview command

No algorithms here.

## 3. Dependency matrix

Allowed:
- domain -> standard library / numerical value types only
- engine -> domain
- application -> domain + engine
- Orca adapter -> domain + application interfaces + Orca API
- G-code adapter -> domain + application interfaces
- UI -> domain/application read models
- capabilities -> adapters/application

Forbidden:
- domain/engine -> orca_plugin
- engine -> G-code parser
- G-code -> optimizer
- UI -> Orca live graph
- preview -> separate plan generation
- injector -> source mesh analysis

CI SHOULD include import-boundary tests.

## 4. Data ownership

### Live Orca data
Owner: Orca.
Lifetime: execute(ctx) only.
Rule: never store.

### GeometrySnapshot
Owner: plugin application.
Immutable/copy-owned.
Contains only information needed for analysis.

### Numerical work buffers
Owner: engine function invocation.
Mutable locally only.
Never exposed as global state.

### SubEdgePlan
Owner: application.
Frozen/immutable.
Canonical serialization + deterministic hash.

### PlanStore
Owner: application infrastructure.
Stores immutable plans only.
Thread-safe bounded cache.

### G-code document/state
Owner: injector invocation.
Never shared with optimizer/UI.

## 5. Mutation policy
Mutation is allowed only:
- inside local numerical work buffers
- inside parser state while parsing
- inside PlanStore's private synchronized index
- when constructing a new output file

Public domain objects are immutable.

No function may mutate an input SubEdgePlan.

## 6. Interface contracts

MeshSectionProvider:
section(z_mm, region) -> tuple[Contour,...]

SurfacePredictor:
predict(paths, bead_profile) -> SurfaceEnvelope

ErrorEstimator:
estimate(reference, predicted) -> ErrorField + ErrorMetrics

SubEdgeOptimizer:
solve(problem) -> OptimizationResult

PlanRepository:
put(plan), get(fingerprint), update_status(plan_id,status)

GCodeParser:
parse(bytes/text) -> ParsedDocument + MachineState checkpoints

PlanInjector:
prepare(document, plan) -> InjectionResult
No filesystem write.

AtomicWriter:
replace_if_valid(path, prepared_result)

PreviewRenderer:
render(preview_model) -> UI payload

Interfaces SHOULD use Protocol/ABC where useful, but avoid framework-heavy dependency injection.

## 7. Error taxonomy
Do not throw generic exceptions across boundaries for expected failures.

Define:
- UnsupportedOrcaVersion
- SnapshotError
- GeometryUnsupported
- OptimizationInfeasible
- PlanMismatch
- GCodeUnsupported
- AnchorMismatch
- InjectionValidationError
- InjectionAlreadyPresent
- UserCancelled

Map them to stable reason codes at capability boundary.

Unexpected exceptions are caught at top-level, logged, and result in no injection.

## 8. Configuration ownership
One validated Settings object in domain/application.

Adapters map Orca/user config into Settings once.

Engine functions MUST NOT query Orca config directly.

Settings changes alter settings_hash and invalidate plan reuse.

## 9. Serialization/versioning
SubEdgePlan schema has explicit schema_version.

Canonical serializer lives in application/serialization.py only.

Never duplicate JSON encoding logic in UI or injector.

Backward compatibility policy:
- reader may support selected old schemas
- injector only accepts explicitly supported schema versions
- migration functions are isolated under application/migrations/

## 10. Performance boundary
Correctness before optimization.

GeometrySnapshot may use copied NumPy arrays for large point sets.

Engine may vectorize/parallelize internally, but outputs remain deterministic.

No caching inside mathematical functions unless cache key is explicit and testable.

## 11. Source-file size/cohesion
A file should represent one responsibility.

Guidelines:
- target < 400 logical lines
- split > 600 lines unless generated/table data
- no "utils.py" dumping ground
- helper stays private in owner module until reused by >=2 responsibilities
- shared helper moves to a narrowly named module

## 12. Change rules
Before modifying behavior:
1. identify owning module
2. update contract/test at that boundary
3. avoid edits outside owner unless interface changes
4. if interface changes, update architecture/implementation docs first
5. run owner unit tests, then integration tests

Cross-layer shortcuts require ADR.
