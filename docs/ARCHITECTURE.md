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
- ExecutionConfigFingerprint
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
- builds the versioned resolved-settings ExecutionConfigFingerprint;
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
- derive/validate the constant print-space -> G-code-space execution translation;
- validate machine state/anchors;
- apply that translation to candidate coordinates at emission time only;
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

ExecutionFrameResolver:
resolve(plan_reference_geometry, gcode_reference_geometry) -> validated constant (dx,dy,dz)

PlanInjector:
emit(source, temp_output, plan) -> InjectionResult

PreviewRenderer:
render(plan,status) -> UI payload

## 10. Dependency rules

Forbidden:
- domain/engine -> orca_plugin
- engine -> G-code
- G-code -> optimizer/source mesh
- domain/engine -> machine G-code coordinate offsets
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


## 13. Component contract checklist

Every non-trivial component must have an explicit or evident contract covering:
1. what it owns;
2. what it explicitly does not own;
3. accepted inputs and units/coordinate frame;
4. produced outputs;
5. invariants;
6. expected failure categories;
7. allowed dependencies;
8. state it may mutate.

A component whose responsibility cannot be summarized precisely probably owns too much.

Adapters translate contracts; they do not redefine domain meaning.

## 14. State, concurrency, and idempotency

Every mutable state must have one owner.

For PlanStore / execution status / G-code mutation define:
- allowed readers/writers;
- locking/synchronization;
- stale-plan detection;
- duplicate-execution behavior;
- partial-update prevention;
- idempotency key/hash;
- cancellation behavior.

Prefer immutable values and single-writer transitions.

No shared mutable global geometry state.

## 15. Failure containment

Boundary code must fail closed.

Required containment:
- validate risky input/state before side effects;
- explicit error conversion at boundaries;
- bounded memory/work where practical;
- cancellation polling in expensive analysis;
- no partial G-code replacement;
- no retry without one owner, budget, and idempotency;
- no fallback that silently changes geometry or machine behavior.

For physical execution, an unsupported/ambiguous state is an injection skip, not a guessed recovery.

## 16. Observability contract

Important operations must be reconstructable from structured diagnostics without logging full models/G-code unnecessarily.

Record where applicable:
- plan hash / execution attempt id;
- Orca/plugin version;
- profile/config fingerprint;
- phase name and duration;
- decision/result reason code;
- number/summary of candidate paths;
- validation gate that stopped execution;
- external effect attempted;
- final injection status.

Do not log secrets, credentials, or unbounded raw payloads.

## 17. Compatibility and rollback

Every compatibility expansion must define:
- supported Orca/profile/firmware versions;
- fixture evidence;
- breaking assumptions;
- migration/schema handling when relevant;
- rollback/disable condition;
- removal condition for temporary compatibility paths.

Compatibility wrappers or profile-specific branches are temporary debt and need an owner and deletion gate.

## 18. Performance/resource contracts

Before declaring production readiness, measure and record limits for critical paths:
- maximum expected model/path size;
- analyzer execution time budget;
- PlanStore bound;
- G-code streaming memory behavior;
- temp-file disk usage;
- maximum candidate/search budget;
- cancellation responsiveness.

Do not trade correctness for performance silently.

A structural refactor that materially changes allocations, passes over G-code, or data copies requires before/after measurement or an explicit accepted risk.

## 19. Security / external-input boundaries

Treat as untrusted boundaries:
- model/file input;
- G-code working file;
- plugin/user configuration;
- external paths/URLs if ever introduced.

Rules:
- validate before domain use;
- use least privilege;
- never put secrets in domain models/logs;
- do not let convenience adapters bypass safety policy;
- distinguish validation failure from compatibility failure and infrastructure failure.

## 20. Architecture evidence

Behavior and architecture are validated separately.

Behavior evidence:
- unit/integration/golden/physical tests.

Architecture evidence:
- import-boundary tests;
- one-owner review;
- no bypass path around authoritative owner;
- no duplicate policy implementation;
- no live Orca types leaking inward;
- no G-code implementation depending on optimizer internals.

Green behavioral tests do not prove architectural ownership is correct.
