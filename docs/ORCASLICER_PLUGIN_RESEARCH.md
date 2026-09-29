# OrcaSlicer Plugin / Geometry API Research

Research target: OrcaSlicer main and official plugin documentation, 2026-09.

## Conclusion
A Python SlicingPipeline plugin can inspect substantial live geometry and mutate selected 2D slice surfaces today. **It cannot currently implement the defining Adaptive Sub-Edge operation by itself:** inserting a new external 3D extrusion contour at an arbitrary Z between structural layers.

Production therefore requires:
1. compatible Orca with Python Plugin System;
2. a small Orca C++/pybind path-insertion extension;
3. the Adaptive Sub-Edge algorithm as a Python plugin/wheel.

If the binding is upstreamed, ordinary Orca users could install only the plugin. Until then, a compatible custom Orca build is required.

## Version condition
Official Orca documentation lists the Python Plugin System as available in:
- Nightly builds, or
- releases greater than 2.4.2.

SlicingPipeline is explicitly research/experimental.

## Packaging
Orca accepts:
- one .py plugin using PEP 723 metadata, or
- a .whl plugin.

This project is multi-module, so the target package is a pure-Python wheel.

## Relevant SlicingPipeline steps
Current Step enum includes:
- posSlice
- posPerimeters
- posEstimateCurledExtrusions
- posPrepareInfill
- posInfill
- posIroning
- posContouring
- posSupportMaterial
- posDetectOverhangsForLift
- posSimplifyPath
- psWipeTower
- psSkirtBrim
- psGCodePostProcess

Geometry-step references are valid only during execute(ctx).

## Confirmed readable live data
Current bindings expose:
- Print / PrintObject
- Layer / LayerRegion
- Print-owned Model snapshot / ModelObject
- Surface / SurfaceCollection
- ExPolygon geometry
- extrusion tree
- ExtrusionPath
- native 3D path points
- width
- height
- mm3_per_mm
- resolved configuration

This is enough to implement read-only post-ZAA analysis and the residual-error engine.

## Confirmed mutable data
At posSlice, LayerRegion.slices is a mutable SurfaceCollection supporting set/append/clear and geometry/type changes. Layer.make_slices() rebuilds merged islands afterward.

Therefore Python can alter existing layer 2D slice geometry and let later perimeter generation cascade.

## Blocking API limitations

### Perimeters are read-only
LayerRegion.perimeters is exposed for inspection but no append/set operation is bound.

### ExtrusionPath is read-only
points() returns a read-only NumPy view. width, height and mm3_per_mm are read-only.

### Layer Z is read-only
print_z, slice_z and height are read-only. No Python API creates/inserts an arbitrary-Z Layer.

### Result
Editing posSlice geometry cannot represent a new independently positioned intermediate surface contour. A pure Python plugin cannot currently create the project's required arbitrary-Z sub-edge.

## ZAA integration
Orca Z Contouring/ZAA adjusts Z of individual extrusion points on eligible top-facing curved/sloped surfaces while leaving nominal layer height elsewhere unchanged.

Relevant settings include:
- zaa_enabled
- zaa_min_z
- zaa_minimize_perimeter_height
- zaa_dont_alternate_fill_direction

Current official scope is top-facing curved/sloped surfaces; downward-facing/upside-down curves are not handled.

Adaptive Sub-Edge therefore treats post-ZAA geometry as its preferred baseline and works on residual error.

## Conditions for plugin operation

### User/runtime conditions
- Orca Nightly or release > 2.4.2
- Python Plugin System available
- SlicingPipeline capability enabled/usable
- NumPy available if required by geometry bindings
- compatible Adaptive Sub-Edge path-insertion binding present

### Geometry conditions for first release
- source model mesh accessible through Print snapshot
- outward/top-facing target surface
- non-crossing candidate contours
- candidate spacing >= configured minimum (initially 0.08 mm)
- enough support/contact for each added contour
- no validated hard nozzle-body collision

### ZAA condition
Hybrid mode prefers ZAA enabled. If ZAA is disabled or a region is ineligible, the plugin may use ordinary perimeter geometry as the baseline, but should report that ZAA-first optimization was unavailable.

## Required Orca extension
Expose a narrow, stable operation that copies validated Python data into Orca-owned extrusion geometry. Do not expose arbitrary internal pointer mutation.

Candidate API:
append_subedge_paths(specs)

Each spec contains 3D points, width, height, flow, role and ordering metadata.

The binding must preserve graph invariants and downstream preview/G-code behavior.

## Preferred execution point
Analyze at posContouring because ZAA has run and 3D contoured paths are available.

If mutation at this point is unsafe, add a dedicated post-contouring plugin hook/API rather than falling back to regex G-code rewriting.

## Development modes

### Mode 1 — stock Orca, read-only research plugin
Possible now:
- inspect post-ZAA paths
- compute residual errors
- visualize/log candidate sub-edges
- benchmark optimizer

### Mode 2 — custom Orca + plugin
Required for first working geometry-injection prototype.

### Mode 3 — stock Orca + plugin
Possible only after the required insertion binding/hook is accepted upstream.

## Source-level evidence
Current Orca source comments explicitly describe:
- SlicingPipeline as research/experimental
- SurfaceCollection 2D mutators
- LayerRegion.slices as the primary posSlice mutation target
- LayerRegion.perimeters as read-only
- ExtrusionPath points as read-only
- Layer Z/height as read-only
- 3D path points already native in the extrusion graph

These findings make a narrow path-insertion binding substantially smaller than building a separate slicer engine.
