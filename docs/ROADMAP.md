# Development Roadmap

## Phase 0 — Design baseline
- preserve upstream Smoothificator scripts
- document legacy behavior
- define error-driven, non-uniform sub-edge model
- verify Orca plugin geometry capabilities

## Phase 1 — Standalone geometry reference implementation
Python prototype independent of G-code:
- analytic 1–30 degree smooth test surface
- arbitrary mesh cross-section interface
- 0.2/0.24 mm baseline slicing
- finite-width bead model
- normal-error evaluation
- arbitrary multi-sub-edge Z optimization
- visualization and metrics

Exit criterion: optimizer consistently improves defined surface-error metrics without violating 0.08 mm spacing.

## Phase 2 — Orca read-only geometry plugin
- package minimal plugin
- inspect posSlice/posPerimeters objects
- dump safe debug geometry/metadata
- confirm version and threading behavior

No geometry mutation yet.

## Phase 3 — Geometry injection PoC
- insert one controlled intermediate contour
- confirm it reaches standard path/G-code generation
- validate extrusion width/flow metadata
- validate travel and Z-hop behavior

## Phase 4 — Adaptive engine integration
- error map
- local candidate generation
- arbitrary Z optimizer
- multiple sub-edges
- topology transitions
- collision validation

## Phase 5 — Calibration
- print calibration surfaces
- compare predicted vs measured surface
- calibrate bead model
- establish nozzle/material-specific minimum spacing profiles

## Phase 6 — Productionization
- UI/settings
- performance optimization
- regression corpus
- failure-safe fallback to baseline slicing
- documentation and release packaging
