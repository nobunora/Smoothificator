# Architecture and Responsibility Boundaries

This document is normative.

## Dependency direction
Orca/UI/G-code adapters -> application -> engine -> domain

Domain and engine never import Orca, UI, filesystem or G-code syntax.

## Normative packages

adaptive_subedge/
- domain/: immutable coordinates, extrusion values, metrics, plan, settings, identity, errors/status
- engine/: bead/error/section/band/path-layout/candidate/Z/support/nozzle/cost algorithms
- application/: Analyzer, canonical serialization/hash, PlanStore/runtime records
- ports/: planar geometry and cancellation interfaces

orca_plugin/
- adapters/: Orca live graph -> copied normalized snapshot/config/frame/fingerprints
- capabilities/: thin slicing/preview entrypoints
- ui/: plan preview only
- gcode/: dialect/parser/state/layers/identity/anchors/emitter/injector/atomic writer

## Domain
Owns values only.

Invariant:
- all canonical domain Z values are absolute print-space millimetres
- Orca ZAA relative offsets never cross the adapter boundary as canonical Z

Domain types include:
- GeometrySnapshot
- StructuralLayer
- BaselineExtrusionSegment
- SubEdgeSegment / SubEdgePath
- ErrorMetrics
- SubEdgePlan
- SliceIdentity / GCodeIdentity
- Settings
- reason/status enums

## Engine
Pure algorithms:
- finite bead prediction
- residual error
- source mesh sections
- surface-band derivation
- tool-center path layout
- candidate generation
- Z/flow selection
- support feasibility
- nozzle envelope
- cost scoring

No Orca/G-code/UI/PlanStore.

## Application
Owns workflows and immutable-plan lifecycle:
- analyze_snapshot
- plan validation
- serialization/hash
- PlanStore
- PlanRuntimeRecord / InjectionAttempt

Runtime Injection state never mutates SubEdgePlan.

## Orca Adapter
Only code allowed to import Orca slicing/host bindings for analysis.

Responsibilities:
- validate v1 configuration gates
- copy live graph
- resolve coordinate frame
- normalize scaled coordinates
- convert Orca ZAA path offset d -> absolute Z = layer.print_z + d
- reproduce ZAA effective bead height/flow metadata
- classify surface-relevant roles
- copy source mesh
- return immutable domain snapshot

No live Orca ref survives execute(ctx).

## G-code Adapter
Consumes accepted immutable plan only.

It:
- parses structural layers/state
- computes GCodeIdentity
- selects exactly one matching plan
- validates Bambu/profile anchor
- emits accepted q as relative E
- performs safe-ceiling routing
- atomically replaces output

It never optimizes or analyzes source mesh.

## UI
Consumes plan/runtime read models only.
It never produces geometry.

## Analyzer hook
Per ADR-0001: posSimplifyPath after Orca ZAA and simplify_extrusion_path().

Fresh slice required because Orca may skip this hook on cached plugin-final objects.

## Data ownership
Live Orca: execute(ctx) lifetime only.

Stored NumPy arrays:
- defensive copy
- writeable=False
or immutable tuples.

SubEdgePlan: frozen/canonical/hashable.

Runtime records: mutable only under PlanStore synchronization.

Parser state: Injector-local.

## Identity
Plan matching combines:
- plugin session generation
- Orca version
- validated config/profile
- layer schedule
- geometry/path fingerprint
- anchors

Exactly one match required.

## Coordinate-frame contract
Volume mesh is local.

Adapter establishes one print-mm frame and tests:
- transformed source bounds
- sliced path bounds
- exported G-code bounds

Unknown transform semantics => Injection disabled.

## PlanarGeometryOps port
Operations:
- offset
- union
- difference
- intersection

Orca-backed implementation may use Python-owned orca.host Polygon/ExPolygon while inside hook, then copies results into domain values.

## Error taxonomy
Expected failures:
- UnsupportedOrcaVersion
- UnsupportedPrintConfiguration
- SnapshotError
- CoordinateFrameError
- GeometryUnsupported
- OptimizationInfeasible
- NozzleModelUnavailable
- FreshSliceRequired
- PlanMismatch
- GCodeUnsupported
- AnchorMismatch
- InjectionValidationError
- InjectionAlreadyPresent
- UserCancelled

Expected failures map to stable reason codes.

## Configuration
One validated Settings object.

Settings hash invalidates plan reuse.

Physical settings explicitly distinguish:
- min_bead_height_mm
- travel_lift_mm
- nozzle-envelope parameters
- quality tolerance

There is no min_neighbor_z_spacing setting in v1.

## Serialization
Canonical plan serializer exists only in application/serialization.py.

Runtime status serialized separately.

## Source boundaries
Target <400 logical lines.
Split >600 unless generated data.
No generic utils.py.

## Forbidden imports
CI enforces:
- domain/engine -> orca_plugin forbidden
- engine -> gcode forbidden
- gcode -> optimizer/candidate/error estimator forbidden
- UI -> analyzer/optimizer/live Orca forbidden
- Injector -> source mesh forbidden

## Change process
Architecture/safety changes require Accepted ADR first.
