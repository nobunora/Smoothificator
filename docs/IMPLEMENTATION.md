# Detailed Implementation Design

## Architecture

### 1. GeometryAdapter
Provides access to:
- sliced layer polygons
- perimeter geometry
- source model/mesh surface
- normals / closest-point queries
- extrusion width and relevant print settings

### 2. BaselineSurfaceBuilder
Constructs an approximation of the surface that ordinary OrcaSlicer layers would print.

### 3. ErrorEstimator
Samples candidate outer regions and computes surface-normal error metrics.

### 4. CandidateGenerator
Creates candidate intermediate Z positions and model cross-sections.

Unlike legacy Smoothificator, it must not clone one XY perimeter at equally spaced Z values.

For each candidate Z:
C(z) = M intersect plane(Z)

The source-model cross-section is preferred over linear interpolation between adjacent perimeter paths.

### 5. SubEdgeExtractor
Computes the printable surface-only contribution from C(z), excluding geometry already adequately represented by structural layers/previous accepted sub-edges.

Responsibilities:
- contour correspondence
- clipping/difference
- minimum printable path-length checks
- support/contact checks
- topology-change handling

### 6. ZOptimizer
Optimizes:
- number of added paths k
- each path height z_i independently

Initial search strategy:
1. coarse bounded candidate search
2. retain best candidates
3. local continuous refinement
4. stop when error target is met with minimal complexity

This deliberately avoids assuming 1/2 or 1/3 spacing.

### 7. BeadModel
Predicts finite-width deposited geometry for scoring candidates.

### 8. CollisionValidator
Rejects extrusion paths that violate nozzle/body clearance assumptions. Travel collision avoidance should integrate with OrcaSlicer rather than duplicate its planner where possible.

### 9. OrcaIntegration
Hooks the algorithm into the geometry/slicing pipeline before final G-code generation.

## Data flow
Model -> slice geometry -> baseline perimeters -> error map -> candidate intermediate slices -> sub-edge extraction -> bead/error simulation -> optimization -> accepted paths -> Orca path planning -> G-code

## Smoothificator migration
Reusable concepts/code:
- GPLv3 licensing lineage
- Orca/Prusa terminology knowledge
- adaptive layer metadata concepts
- test cases demonstrating outer-wall-only refinement

To replace:
- regex G-code parsing as core architecture
- external-perimeter block duplication
- equal pass count calculation
- equal extrusion split assumption
- identical XY paths at multiple Z values
- direct G-code travel insertion

Legacy scripts should remain available during early development as reference/baseline, but the new engine should live in separate modules.

## Proposed source layout
adaptive_subedge/
  geometry_adapter.py
  baseline_surface.py
  error_estimator.py
  candidate_generator.py
  subedge_extractor.py
  z_optimizer.py
  bead_model.py
  collision.py
  settings.py

orca_plugin/
  plugin.json
  main.py
  integration.py

tests/
  geometry/
  unit/
  regression/

## Initial settings
- enabled
- minimum_z_spacing_mm = 0.08
- maximum_normal_error_mm
- error_metric
- max_added_paths_per_interval (guardrail)
- optimization_quality
- bead_model
- debug_visualization

The user-facing UI should expose error/quality intent rather than requiring users to select a fixed subdivision ratio.
