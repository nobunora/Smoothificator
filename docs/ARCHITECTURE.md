# Architecture and Responsibility Boundaries

This document is normative. Its goal is change locality, testability, and safety.

## 1. Dependency direction

Dependencies point inward:

Orca adapters / UI / G-code I/O -> Application -> Engine -> Domain

Domain and engine never import Orca, UI, filesystem, or G-code modules.

## 2. Canonical packages

adaptive_subedge/domain/
- geometry.py
- metrics.py
- plan.py
- settings.py
- status.py
- errors.py

adaptive_subedge/engine/
- bead_model.py
- flow_model.py
- error_estimator.py
- mesh_section.py
- surface_band.py
- candidate_generator.py
- z_optimizer.py
- support.py
- collision.py
- cost_model.py

adaptive_subedge/application/
- analyzer.py
- plan_store.py
- execution_status.py
- serialization.py
- hashing.py
- migrations/

adaptive_subedge/ports/
- mesh_section_provider.py
- plan_repository.py
- cancellation.py

orca_plugin/adapters/
- geometry_snapshot.py
- orca_config.py
- transforms.py
- fingerprint.py

orca_plugin/capabilities/
- slicing.py
- preview.py

orca_plugin/ui/
- preview_model.py
- preview_renderer.py

orca_plugin/gcode/
- lexer.py
- parser.py
- state.py
- matcher.py
- anchors.py
- validation.py
- emitter.py
- injector.py
- atomic_writer.py

## 3. Responsibility boundaries

### Domain
Immutable value objects only:
- GeometrySnapshot DTOs
- ErrorMetrics
- SurfaceBand / SubEdgePath
- SubEdgePlan
- InsertionAnchor
- Settings
- status/reason enums

No Orca or G-code knowledge.

### Engine
Pure algorithms:
- source-surface sectioning
- target-boundary to printable centerline layout
- finite-bead prediction
- ZAA/local-flow normalization inputs
- residual-error estimation
- candidate path/flow optimization
- support/clearance/collision scoring
- cost model

No Orca hooks, G-code syntax, UI, or PlanStore.

### Application
Orchestration:
- analyze_snapshot(snapshot, settings)
- plan validation
- deterministic serialization/hashing
- PlanStore
- execution status

### Orca adapter
Only layer allowed to import Orca geometry/slicing bindings.

It:
- copies live ctx data;
- transforms coordinates;
- converts path-local Z offsets to absolute Z;
- reconstructs effective local ZAA flow metadata;
- maps config/gates;
- builds stable fingerprints.

No live Orca object may escape this layer.

### G-code adapter
Execution only:
- parse final G-code;
- select exactly one matching plan;
- validate machine state/anchors;
- emit additive SubEdge paths;
- restore state;
- atomically replace working file.

It MUST NOT optimize geometry or alter Orca's original structural extrusion in v1.

### UI
Consumes plan/status read models only. No optimization, G-code parsing, or live Orca access.

## 4. Canonical coordinate frame

All domain geometry uses **absolute print-space millimeters**.

Orca path binding:
- XY: scaled path coordinates -> unscale to mm.
- Z: ContourZ stores a layer-relative offset d.
- absolute Z:
  Z_abs = layer.print_z + unscale(path_point.z)

Source mesh:
- ModelVolume.mesh() is volume-local mm.
- v1 uses one ModelPart volume.
- adapter applies audited volume->object and PrintObject object->print transforms.

Coordinate conversion is forbidden outside the Orca adapter.

## 5. ZAA local-flow normalization

For a Z-contoured non-ironing segment:
- d = path-relative Z offset at segment endpoint;
- command Z = nominal layer Z + d;
- Orca G-code scales extrusion by:
  (path.height + d) / path.height.

The snapshot MUST carry enough data to reproduce this local effective extrusion in the finite-bead model.

Engine must not assume one constant mm3_per_mm for a ZAA path.

## 6. Data ownership

Live Orca data:
- owned by Orca;
- valid only during execute(ctx);
- never stored.

GeometrySnapshot:
- plugin-owned copy;
- large arrays copied and marked read-only.

Engine work buffers:
- local mutable arrays allowed;
- never global.

SubEdgePlan:
- frozen/immutable;
- deterministic hash;
- geometry/execution intent only.

PlanExecutionStatus:
- separate mutable status record;
- status changes never alter plan hash.

PlanStore:
- process-local;
- thread-safe;
- bounded;
- stores immutable plans and separate status records.

G-code parser state:
- one injector invocation only.

## 7. SubEdgePlan semantics

A SubEdgePlan contains only **additional** printable paths for v1.

Each SubEdgePath contains:
- path id
- structural interval id
- absolute nozzle Z profile or constant Z, as defined by candidate
- printable centerline geometry in print-space mm
- effective bead height relative to local support
- width
- mm3_per_mm / volume-per-length
- speed policy
- order group
- source error region
- insertion anchor/fingerprint

The original Orca structural outer wall remains unchanged in v1.

Final quality is evaluated from the combined envelope:
- lower structural/ZAA beads
- candidate sub-edge beads
- upper structural/ZAA beads

## 8. Surface-band model

A mesh-plane intersection is a **material boundary**, not automatically a nozzle centerline.

Engine derives a printable surface band inside the material side and lays out one or more centerlines.

Multiple centerlines may exist:
- at the same Z;
- at different Z;
- with small pairwise Z differences.

Feasibility is based on local support height, bead overlap, nozzle clearance, and nesting—not a fixed neighbor-Z rule.

## 9. Interfaces

MeshSectionProvider:
section(z_mm, region) -> boundary geometry

SurfaceBandPlanner:
plan(reference_boundary, support_surface, settings) -> candidate centerlines

SurfacePredictor:
predict(structural_beads, candidate_beads) -> SurfaceEnvelope

ErrorEstimator:
estimate(reference, predicted) -> ErrorField + ErrorMetrics

SubEdgeOptimizer:
solve(problem) -> OptimizationResult

PlanRepository:
put(plan), candidates(), get(plan_hash)

ExecutionStatusRepository:
set(plan_hash,status,reason), get(plan_hash)

GCodeParser:
parse_stream(source) -> events/state checkpoints

PlanMatcher:
match(document_metadata, candidate_plans) -> exactly one plan or typed failure

PlanInjector:
emit(source, temp_output, plan) -> InjectionResult

PreviewRenderer:
render(plan,status) -> UI payload

## 10. Dependency rules

Forbidden:
- domain/engine -> orca_plugin
- engine -> G-code
- G-code -> optimizer/source mesh
- UI -> live Orca
- UI -> optimizer
- injector -> engine
- adapters -> UI

CI MUST enforce import boundaries.

## 11. Serialization/determinism

Canonical plan serialization exists only in application/serialization.py.

plan_hash excludes:
- timestamps
- memory addresses
- process-local Orca ObjectIDs

Use deterministic fixed-unit/quantized values or deterministic binary representation. Never locale-dependent float formatting.

## 12. File and change rules

- one responsibility per file
- target <400 logical lines
- split >600 unless generated/static data
- no generic utils.py
- safety/architecture changes require Accepted ADR first
- owner-module tests before integration tests
- lower-precedence docs never override accepted ADRs
