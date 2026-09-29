# Detailed Implementation Specification

## 1. Production architecture
Final target:

**small Orca C++/pybind extension + Python SlicingPipeline plugin**

Current Orca Python bindings expose live geometry and mutable 2D slice surfaces, but generated perimeter paths and their 3D points are read-only, and arbitrary intermediate-Z layers/paths cannot be inserted. Therefore a pure Python plugin is sufficient for analysis/prototyping but not final sub-edge injection.

## 2. Processing stages
A. Orca baseline slicing/perimeters  
B. Orca ZAA/Z Contouring  
C. Read post-ZAA 3D outer paths  
D. Build finite-width predicted surface  
E. Compute residual normal-error map  
F. Generate arbitrary-Z intermediate model contours only where needed  
G. Optimize number and independent Z positions of sub-edges  
H. Validate support/topology/clearance  
I. Inject accepted paths through the C++ binding  
J. Print non-crossing paths from lowest Z to highest Z  
K. Continue normal Orca downstream path/G-code processing

## 3. Core modules

### GeometryAdapter
Reads Print/PrintObject/Layer/LayerRegion, source mesh, post-ZAA ExtrusionPaths and resolved settings. Handles coordinate transforms and model cross-sections.

### BaselineSurfaceBuilder
Builds a finite-width deposited-envelope approximation from post-ZAA paths.

### ErrorEstimator
Computes maximum, RMS, percentile and signed surface-normal error against the source model.

### CandidateGenerator
At arbitrary candidate Z:

C(z) = model intersect plane(Z)

Prefer true mesh cross-sections over interpolation between neighboring paths.

### SubEdgeExtractor
Keeps only the surface contribution required to reduce residual error. Checks minimum length, support/contact, topology changes and contour crossing.

### ZOptimizer
Variables:
- k: number of added contours
- z_1..z_k: independent heights

Constraints:
- ordered Z
- configurable minimum adjacent spacing
- no contour crossing
- printable support/contact
- maximum path-count guardrail

Initial solver:
1. coarse candidate grid
2. beam/branch selection over k
3. local continuous refinement of z_i
4. early stop when tolerance is met
5. select lowest total cost

### BeadModel
Initial rounded-rectangle/elliptical profile using Orca width, height and flow. Later calibrate by nozzle/material/speed/temperature.

### CollisionValidator
For monotonic non-crossing contours, bottom-to-top ordering is normal and not treated as a special collision case. Reject concave/inward nozzle-body conflicts, excessive real/predicted bead height, unsupported paths and unsafe transitions.

### CostModel
Scores added path length, material, estimated time, starts/stops and error reduction.

## 4. Required Orca C++ API extension
Minimum concept:

SubEdgePathSpec
- points3d
- width
- height
- mm3_per_mm
- extrusion role
- ordering/group id

Insertion API, e.g.:
- append_subedge_paths(list[SubEdgePathSpec])

Requirements:
- C++ copies/owns data
- validates coordinates and extrusion parameters
- inserts into a graph location that survives preview and G-code generation
- maintains/invalidate caches correctly
- preserves deterministic ordering
- rejects invalid pipeline stages

If direct LayerRegion.perimeters insertion breaks invariants, add a dedicated sub-edge collection consumed by downstream extrusion/G-code generation.

## 5. Hook strategy
Preferred evaluation point: **posContouring**, because Orca ZAA has already produced contoured paths and the project needs post-ZAA residual error.

If injection at posContouring cannot safely participate in later processing, add a dedicated Orca hook immediately after contouring, e.g. posAdaptiveSubEdgeAfterContouring.

Injected paths should still flow through later simplification/order/travel/G-code logic wherever compatible.

## 6. Python package layout
adaptive_subedge/
- geometry_adapter.py
- baseline_surface.py
- error_estimator.py
- candidate_generator.py
- subedge_extractor.py
- z_optimizer.py
- bead_model.py
- collision.py
- cost_model.py
- settings.py

orca_plugin/
- __init__.py
- capability.py
- integration.py

tests/
- unit/
- analytic/
- mesh/
- regression/
- printer/

Distribution target: pure-Python wheel once the required binding exists in Orca.

## 7. Plugin pseudocode
execute(ctx):
    if ctx.step != Step.posContouring:
        return Success
    if not required_binding_available():
        return RecoverableError

    mesh = ctx.object.model_object()
    paths = read_post_zaa_outer_paths(ctx.object)
    predicted = build_surface(paths)
    residual = estimate_error(mesh, predicted)

    for region in residual.regions_above(tolerance):
        solution = optimize_subedges(mesh, region)
        if solution.feasible and validate(solution):
            append_subedge_paths(solution.paths)

    return Success

## 8. Failure behavior
Unsupported topology, missing binding, cancellation, invalid geometry or numerical failure must result in **no sub-edge modification**, never a partially modified slice.

## 9. First implementation scope
- 0.4 mm nozzle
- PLA first
- top-facing/outward-monotonic slopes first
- non-crossing sub-edges
- default minimum Z spacing 0.08 mm
- ZAA-enabled baseline where eligible
- no downward-facing surfaces initially
