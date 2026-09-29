# OrcaSlicer Plugin / Geometry API Research

Research target: OrcaSlicer main and official plugin docs, audited 2026-09-29.

## Confirmed plugin model
Orca plugin packages may register multiple capabilities. This project uses:
- one SlicingPipeline capability
- one Script preview capability

Capabilities are instantiated for the plugin load lifetime.

## Confirmed host data
Python bindings expose:
- Print / PrintObject / Layer / LayerRegion
- Print-owned Model snapshot
- ModelObject/ModelInstance/ModelVolume transforms
- TriangleMesh vertices/triangles/normals
- Surface/ExPolygon geometry and 2D boolean/offset operations
- extrusion tree
- 3D ExtrusionPath points
- width/height/mm3_per_mm
- config values

ModelVolume mesh is local; volume.matrix maps volume->object and ModelInstance.matrix maps object->world. Coordinate use still requires integration tests against sliced paths/exported G-code.

## Hook order audit
Orca Print.cpp shows:
1. Z contouring via obj->contour_z()
2. posContouring hook only if need_z_contouring() is true
3. support/detect-overhang steps
4. psSkirtBrim
5. obj->simplify_extrusion_path()
6. posSimplifyPath hook on fresh slicing objects

Therefore posContouring is unsuitable as universal Analyzer and psSkirtBrim is too early relative to simplification.

ADR-0001 selects posSimplifyPath.

## Cache caveat
Source explicitly prevents posSimplifyPath plugin hook on cache-loaded plugin-final objects.

No fresh current-session plan => injection must skip and request re-slice.

## Post-process seam
psGCodePostProcess:
- runs from export path after classic post_process scripts
- ctx.print/object are None
- ctx.gcode_path/host/output_name are present
- edits working file in place
- may run more than once on separate working copies
- result is not mapped into standard G-code preview

## G-code layer markers
Orca emits reserved layer-change and height tags as processor metadata. BBL and non-BBL Z marker formatting differs (for example Z_HEIGHT vs Z). Parser must support tested dialect forms rather than infer structural layers from arbitrary Z moves, especially because ZAA introduces non-planar Z movement.

## Why source geometry scope is limited
Raw individual volume meshes are accessible, but plugin API does not provide a single arbitrary-Z cross-section of fully evaluated multi-volume CSG/modifier geometry.

Printable v1 therefore restricts to one ModelPart volume. This avoids reimplementing Orca CSG.

## Planar geometry
orca.host Polygon/ExPolygon expose offset/union/difference/intersection. The engine remains Orca-independent by using a PlanarGeometryOps port; the Orca adapter may call these during execute(ctx) and copy results out.

## Flow parity
Orca Flow::mm3_per_mm() for non-bridge rounded rectangle is:

h * (w - h * (1 - pi/4))

Use this as initial bead-volume parity model.

## Stock-Orca feasibility
No custom Orca is required for v1:
- geometry intelligence at posSimplifyPath
- execution at psGCodePostProcess
- preview via Script capability

The principal risk is safe G-code translation, not API access.

## v1 interference policy
Because classic scripts run before psGCodePostProcess and multiple slicing-pipeline capabilities can mutate output in configured order, v1 printable mode requires:
- classic post_process empty
- no other active slicing-pipeline capability

Later interoperability requires a separate ADR/test matrix.
