# Architecture and Responsibility Boundaries

This document is normative.

## 1. Dependency direction
Dependencies point inward:

Orca/UI/G-code adapters -> application orchestration -> engine -> domain

Domain/engine never import Orca, UI, filesystem or G-code syntax.

## 2. Normative packages

adaptive_subedge/
- domain/: immutable value objects, settings, metrics, plan, status/reason codes
- engine/: bead/error/mesh-section/candidate/subedge/Z/collision/cost algorithms
- application/: analyzer workflow, serialization, hashing, PlanStore/runtime records
- ports/: narrow interfaces for cancellation and planar geometry operations

orca_plugin/
- adapters/: Orca live-graph -> copied snapshot/config/fingerprint
- capabilities/: slicing + preview entrypoints only
- ui/: preview models/rendering only
- gcode/: dialect, lexer/parser/state/identity/anchors/emitter/injector/atomic writer

## 3. Responsibility rules

### domain
Owns immutable vocabulary:
- GeometrySnapshot DTO/value structures
- ErrorMetrics
- SubEdgePath
- SubEdgePlan
- SliceIdentity / GCodeIdentity value types
- Settings
- reason/status enums

No I/O, Orca, optimization or G-code.

### engine
Pure algorithms:
- source-mesh plane sectioning
- finite bead model
- residual error
- candidate generation
- sub-edge extraction
- Z/flow optimization
- support/collision checks
- cost scoring

No Orca/G-code/UI/PlanStore.

### application
Owns workflows:
- analyze_snapshot(...)
- plan validation
- canonical serialization/hash
- PlanStore
- PlanRuntimeRecord / InjectionAttempt history

SubEdgePlan stays immutable. Injection status is NOT stored inside the plan.

### Orca adapters
Only layer allowed to import Orca host/slicing bindings.
- copy live graph
- validate v1 support gates
- establish/validate coordinate frame
- map config
- implement Orca-backed planar geometry port if used

No live Orca refs survive execute(ctx).

### G-code adapter
Consumes an accepted immutable plan.
- parse/state-track
- compute GCodeIdentity
- find exactly one matching plan
- validate layer-boundary insertion anchors
- emit safe blocks
- atomic replacement

It MUST NOT optimize geometry or inspect source mesh.

### UI
Consumes copied plan/runtime records only.
Never generates or mutates plans.

## 4. Analyzer hook
Per ADR-0001, analysis occurs at Orca Step.posSimplifyPath, after ZAA and simplify_extrusion_path().

v1 supports exactly one printable object/instance, so the per-object hook yields one plan.

Cache-loaded exports without a fresh current-session plan are analysis-only / injection-skipped.

## 5. Data ownership

Live Orca graph:
- Orca-owned
- valid only during execute(ctx)
- never stored

GeometrySnapshot:
- plugin-owned copy
- immutable across boundaries

Numerical work arrays:
- local mutable buffers only

NumPy arrays stored inside frozen objects MUST be defensive copies and marked non-writeable, or converted to immutable tuples. A frozen dataclass alone is not considered deep immutability.

SubEdgePlan:
- immutable/canonical/hashable

PlanRuntimeRecord:
- mutable only inside PlanStore lock
- contains status/attempt history, never geometry mutation

G-code parser document/state:
- injector-local only

## 6. Identity model
Geometry analysis and G-code export have no shared live Print handle.

Plan matching therefore uses:
- plugin/session generation
- Orca version
- selected settings/config fingerprint
- structural layer schedule fingerprint
- expected world/print-space geometry fingerprint (including selected layer XY bounds)
- plan anchors

Post-process MUST select exactly one matching plan. Zero or multiple matches => skip.

PlanStore may deduplicate identical plan hashes.

## 7. Coordinate-frame contract
Raw ModelVolume mesh is local. Volume and instance/PrintObject transforms are exposed by Orca.

The adapter MUST produce one canonical print-mm frame and prove it with tests:
- transformed source bbox
- PrintObject/sliced path bbox
- exported G-code bbox

Transforms are allowed in v1 only after these validations pass. Coordinate uncertainty disables injection.

## 8. Ports

PlanarGeometryOps:
- offset
- union
- difference
- intersection
using engine/domain data only.

The Orca implementation may internally use Python-owned orca.host Polygon/ExPolygon value objects during execute(ctx), then copy results back to domain data.

CancellationPort:
- cancelled() -> bool

No interface may return a live Orca object.

## 9. Error taxonomy
Expected typed failures:
- UnsupportedOrcaVersion
- UnsupportedPrintConfiguration
- SnapshotError
- CoordinateFrameError
- GeometryUnsupported
- OptimizationInfeasible
- FreshSliceRequired
- PlanMismatch
- GCodeUnsupported
- AnchorMismatch
- InjectionValidationError
- InjectionAlreadyPresent
- UserCancelled

Top-level unexpected exceptions result in no injection.

## 10. Configuration
One validated Settings object.
Orca/plugin config is mapped once.

Settings changes change settings_hash and invalidate plan reuse.

## 11. Serialization
Canonical serializer lives only in application/serialization.py.
SubEdgePlan has schema_version.
Runtime/injection status is serialized separately and never changes plan_hash.

## 12. Source-file boundaries
Target <400 logical lines; split >600 unless generated data.
No generic utils.py.
Helpers stay private until genuinely shared.

## 13. Forbidden imports
- domain/engine -> orca_plugin
- engine -> gcode
- gcode -> optimizer/candidate modules
- UI -> analyzer/optimizer/live Orca graph
- injector -> mesh/error estimator

CI MUST enforce dependency boundaries.

## 14. Change process
Architecture/safety changes require an Accepted ADR before implementation.
Normal algorithm changes should remain local to owner module + tests.
