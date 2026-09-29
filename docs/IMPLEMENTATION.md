# Implementation Specification — Stock Orca Plugin

This document is normative. Coding agents MUST follow it unless a later ADR explicitly supersedes a requirement.

## 0. Architecture
Use **stock OrcaSlicer + Python plugin only**.

Two SlicingPipeline hooks:
1. posContouring: analyze post-ZAA geometry and create immutable SubEdgePlan.
2. psGCodePostProcess: validate exported G-code and inject that exact plan.

No Orca C++ changes in v1.

## 1. Orca execution facts
SlicingPipeline execute(ctx) runs on the slicing worker thread. Never call orca.host.ui.* there.

Geometry hooks expose live ctx.print/ctx.object only during execute().

At psGCodePostProcess:
- ctx.print/ctx.object are None
- ctx.gcode_path is the working exported G-code
- ctx.host/output_name are available
- file is edited in place
- hook may run multiple times on separate working copies
- post-process result is not reflected in Orca standard G-code preview

## 2. Package layout
adaptive_subedge/
- geometry_snapshot.py
- baseline_surface.py
- error_estimator.py
- mesh_section.py
- candidate_generator.py
- subedge_extractor.py
- z_optimizer.py
- bead_model.py
- collision.py
- cost_model.py
- plan.py
- plan_store.py
- settings.py
- hashing.py

orca_plugin/
- package.py
- slicing_capability.py
- preview_capability.py
- preview_renderer.py
- gcode/lexer.py
- gcode/parser.py
- gcode/state.py
- gcode/anchors.py
- gcode/emitter.py
- gcode/injector.py
- gcode/validation.py

tests/
- unit/
- analytic/
- fixtures/gcode/
- fixtures/plans/
- integration/
- regression/

## 3. Immutable data model

GeometrySnapshot MUST contain copied values only:
- Orca version
- object id/transform
- copied source-mesh representation needed by algorithm
- layers
- copied post-ZAA outer-path XYZ points in mm
- width/height/mm3_per_mm/role
- relevant resolved config
- ZAA settings
- nozzle/filament data

No pybind/live Orca object may be retained.

SubEdgePath (frozen):
- path_id, object_id, interval_id
- z_mm
- points_xy_mm
- width_mm, height_mm, mm3_per_mm
- estimated_volume_mm3
- ordering_index
- source_error_region_id

InsertionAnchor (frozen):
- expected Z0/Z1
- object/layer identifiers when available
- nearby expected XY
- expected Orca comment/marker context
- tolerances
- anchor fingerprint

SubEdgePlan (frozen):
- schema_version, plugin_version
- plan_id, deterministic plan_hash
- Orca version
- baseline_mode
- settings_hash, geometry_hash
- paths, anchors
- metrics_before, metrics_after_predicted

Timestamp may exist for diagnostics but MUST NOT affect deterministic hash.

## 4. posContouring analyzer
Mandatory sequence:
1. check cancellation
2. read settings
3. copy required live data into GeometrySnapshot
4. never retain live references
5. identify eligible outer regions
6. build post-ZAA finite-bead surface
7. compute residual normal-error map
8. skip compliant regions
9. generate arbitrary-Z mesh sections
10. extract printable surface-only candidates
11. optimize k and independent z_i
12. validate non-crossing/support/clearance
13. re-score finite-bead surface
14. create immutable SubEdgePlan
15. store in PlanStore using deterministic slice fingerprint
16. return concise diagnostics

Heavy work MUST poll ctx.cancelled() regularly.

## 5. Geometry/error rules
Candidate contour SHOULD be true source-mesh plane intersection.

Required error metrics: E_max, E_rms, E_p95, signed mean.

Bead model v1: configurable rounded-rectangle or ellipse using width/height.

Never evaluate quality as zero-width paths only.

Optimizer MUST NOT hardcode 1/2 or 1/3.

Constraints:
- adjacent z >= min_z_spacing
- non-crossing
- support/contact valid
- max path count guardrail
- next structural layer clearance valid

Solver v1:
coarse bounded Z grid -> beam/enumeration over k -> local refinement -> early tolerance stop -> minimum-cost feasible solution.

## 6. PlanStore
Cross-hook handoff uses copied plugin-owned data only.

Requirements:
- process-local
- thread-safe
- immutable plans
- deterministic slice/output fingerprint key
- bounded LRU
- invalidation on incompatible new slice
- no Orca object references
- repeated psGCodePostProcess calls reuse plan read-only

If lookup is ambiguous/missing, injector skips. It MUST NOT reconstruct geometry from G-code.

## 7. Preview
Provide plugin-owned preview/diagnostic UI.

Do not call UI APIs from slicing worker. Use a Script/UI-safe capability to read copied PlanStore data and create/refresh host-owned HTML window/panel.

Preview MUST show:
- post-ZAA reference paths
- planned sub-edges
- residual error heatmap
- before/after predicted metrics
- sub-edge Z values
- plan hash
- injection status

Renderer and injector MUST consume the same plan serialization/hash.

## 8. G-code parser
No ad-hoc regex-only injection.

Track at minimum:
- X/Y/Z
- absolute/relative XYZ mode
- absolute/relative extrusion mode
- current E
- feed rate
- retraction/unretraction state where detectable
- active tool
- layer/object/type comments
- required machine-specific state

Unknown commands are preserved. If an unknown command invalidates tracked-state confidence in target interval, skip injection.

Support only explicitly tested Orca dialect/profile families.

## 9. Anchor validation
Before any modification:
1. parse complete G-code
2. locate every structural interval
3. locate expected outer-wall neighborhood
4. validate Z
5. validate nearby XY/comment fingerprint
6. validate extrusion/tool/state assumptions
7. validate all paths/anchors

All-or-nothing. No partial injection.

## 10. Extrusion emitter
For path length L and q=mm3_per_mm:
V=L*q

Convert V to filament E using configured filament cross-sectional area.

Correctly handle detected extrusion mode.

Each block:
1. establish safe retraction/travel state
2. travel to start safely
3. set required Z
4. extrude planned path
5. process paths lower-Z first
6. restore state expected by following Orca G-code

Speed is conservative/configurable and initially capped from outer-wall speed.

## 11. Idempotence
Use:
; ADAPTIVE_SUBEDGE_BEGIN plan=<hash> version=<version>
...
; ADAPTIVE_SUBEDGE_END plan=<hash>

Existing matching marker => validate and do not inject again.

## 12. Atomicity
1. read original
2. parse fully
3. validate all
4. build complete modified output separately
5. sanity-parse modified output
6. replace working file only after success

Failure leaves original unchanged.

## 13. v1 safety gates
Skip injection for:
- multi-tool/tool change in target interval
- unknown extrusion mode transition
- unsupported state-changing command
- anchor mismatch
- plan/settings mismatch
- crossing contours
- unsupported geometry
- NaN/Inf
- ambiguous anchors

## 14. Tests
Unit:
- plan hashing
- optimizer constraints
- bead model
- G-code state machine
- E conversion
- anchor matching
- idempotence
- atomic failure

Golden G-code fixtures per supported Orca/profile version.

Geometry coupons: smooth 1–30 degree curve and fixed 1/5/10/15/20/25/30 degree slopes.

Regression comparison:
normal / ZAA-only / ZAA+SubEdge / fine conventional layer.

Mandatory invariants:
- no partial injection
- no duplicate injection
- lower-Z-first
- preview plan hash == injected plan hash
- original unchanged on failure
- no live Orca references after analyzer returns

## 15. Logging
Structured:
plan hash, Orca version, baseline mode, paths added, error before/after, added length/volume/time estimate, injection result, reason code.

## 16. Coding-agent rules
- do not modify legacy Smoothificator scripts unless explicitly tasked
- new code goes under adaptive_subedge/ and orca_plugin/
- no custom Orca C++ in v1
- no regex-only fallback
- no UI call from SlicingPipeline execute()
- no storing live/pybind graph objects
- no partial file writes
- no unsupported-feature guessing
- tests required with behavior changes
- deterministic output for identical input/settings
- use explicit frozen dataclasses/types and pure functions where practical
- any safety relaxation requires an ADR before implementation


## 17. Responsibility and source-boundary contract

The normative architecture is [ARCHITECTURE.md](ARCHITECTURE.md). Implementation MUST conform to it.

### Required package structure

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
    anchors.py
    validation.py
    emitter.py
    injector.py
    atomic_writer.py

### Boundary rules
- domain and engine MUST NOT import orca_plugin.
- engine MUST NOT import G-code modules.
- gcode MUST NOT import optimizer/candidate generation.
- UI MUST NOT create/modify plans.
- capabilities contain orchestration glue only.
- Orca live objects MUST terminate at adapters/geometry_snapshot.py.
- canonical plan serialization exists only in application/serialization.py.
- settings are validated once and passed explicitly.
- no generic utils.py module.

### Change-locality target
A normal algorithm change (for example replacing Z optimizer) SHOULD require changes only in:
- its engine module
- its direct unit tests
- optionally analyzer wiring if interface changes

It SHOULD NOT require edits to G-code parser, injector, preview renderer or Orca adapter.

A G-code dialect change SHOULD be isolated to orca_plugin/gcode plus fixtures/tests and MUST NOT alter geometry engine.

An Orca API change SHOULD be isolated to orca_plugin/adapters/capabilities and MUST NOT alter domain algorithms.

### Data separation
Use frozen dataclasses for cross-boundary domain objects.

Mutable NumPy arrays are permitted only as private work buffers. Convert/copy before storing in immutable snapshots/plans as needed to prevent alias mutation.

PlanStore stores only immutable plan data/status metadata; it is not an algorithm cache.

### Import-boundary tests
Add tests that fail if forbidden dependencies appear. At minimum:
- adaptive_subedge/domain cannot import orca_plugin
- adaptive_subedge/engine cannot import orca_plugin or orca_plugin.gcode
- orca_plugin/gcode cannot import adaptive_subedge.engine.z_optimizer/candidate_generator
- orca_plugin/ui cannot import analyzer/optimizer

### ADR gate
Architecture/safety changes listed in ADR_PROCESS.md require an Accepted ADR before implementation.
