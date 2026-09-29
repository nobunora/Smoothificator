# Development Roadmap

## Phase 0 — architecture complete
- preserve upstream Smoothificator
- document prior implementation
- define error-driven non-uniform multi-sub-edge model
- adopt ZAA-first residual-error strategy
- audit current Orca plugin bindings
- identify required C++ path-insertion extension

## Phase 1 — standalone reference engine
Python:
- analytic smooth slopes
- finite-bead post-ZAA surface model
- normal-error evaluation
- arbitrary multi-sub-edge Z optimization
- lower-Z-first ordering
- metrics/visualization

Exit: optimizer reduces residual error while respecting 0.08 mm initial spacing and cost constraints.

## Phase 2 — stock-Orca analysis plugin
Build a wheel using SlicingPipeline:
- run at posContouring
- read post-ZAA 3D paths
- access source mesh
- calculate residual error
- calculate candidate sub-edges
- log/export debug metrics only

No path mutation.

## Phase 3 — Orca C++ binding
Implement minimal safe path-insertion API:
- copied SubEdgePathSpec
- validation
- graph ownership
- deterministic ordering
- preview/G-code persistence
- atomic failure

Add tests in Orca fork.

## Phase 4 — first printable plugin
Custom Orca + Python plugin:
- inject one controlled sub-edge
- then multiple non-crossing sub-edges
- verify lower-Z-first execution
- validate travel/Z-hop and preview
- compare predicted vs generated G-code

## Phase 5 — adaptive hybrid
- ZAA baseline
- residual error map
- local arbitrary-Z optimization
- finite-bead rescoring
- support/topology/clearance validation
- cost minimization

## Phase 6 — physical calibration
Compare:
- normal layer
- fine conventional layer
- ZAA-only
- ZAA + Adaptive Sub-Edge

Measure quality, time, material and artifacts. Calibrate bead model and minimum spacing by nozzle/material.

## Phase 7 — upstream/API work
Propose the narrow path-insertion binding/hook to OrcaSlicer. If accepted, remove custom-build requirement.

## Phase 8 — production plugin
- pinned Orca compatibility
- wheel packaging
- user quality/tolerance controls
- performance optimization
- regression corpus
- safe fallback to ZAA-only/baseline
