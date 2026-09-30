# OrcaSlicer Plugin / Geometry API Research

Research target: OrcaSlicer main and official plugin sources, audited 2026-09-30.

## 1. Final v1 conclusion
Stock Orca is sufficient for v1 by combining:
- **posSimplifyPath** for post-ZAA/post-simplification read-only analysis;
- **psGCodePostProcess** for official exported-working-file modification;
- a separate Script capability for preview.

A custom Orca build is not required for the first printable implementation.

## 2. Why posContouring was rejected
Source audit of Print.cpp shows:
- Orca calls obj->contour_z();
- it fires the posContouring plugin hook only when obj->need_z_contouring() is true;
- otherwise the step is marked done without calling the plugin hook.

Therefore posContouring cannot implement the required "analyze ordinary Orca geometry when ZAA is disabled/ineligible" behavior.

## 3. Why posSimplifyPath was selected
Print.cpp runs simplify_extrusion_path() after Z Contouring and then fires posSimplifyPath for newly processed objects.

Benefits:
- sees ZAA results where they exist;
- also runs when ZAA is not needed;
- sees paths after simplification, closer to exported geometry.

Caveat:
Orca intentionally avoids re-firing this hook on cache-loaded plugin-final objects. Missing in-process plan at export therefore causes safe skip/re-slice diagnostic.

## 4. Path-coordinate discovery
PluginHostSlicing exposes ExtrusionPath.points() as native 3D scaled coordinates.

However ContourZ.cpp stores the point Z component as adjustment d relative to Layer.print_z, not absolute print Z.

Canonical conversion:

Z_abs = Layer.print_z + orca.slicing.unscale(point_z)

This conversion is mandatory before domain analysis.

## 5. Source mesh bindings
PluginHostMesh/PluginHostModel expose:
- immutable mesh vertices/triangles;
- ModelVolume.matrix() volume-to-object;
- PrintObject.trafo() object-to-print;
- source Model snapshot tied to the Print worker.

This is sufficient for v1 single-volume source mesh reconstruction.

Multi-volume CSG is not solved by the binding itself and is deferred.

## 6. Read-only path limitation
LayerRegion.perimeters and ExtrusionPath points/width/height/flow are read-only from Python.

This blocks live path injection but not v1 because execution occurs at psGCodePostProcess.

## 7. psGCodePostProcess
Official Orca sample/source confirms:
- runs after classic post_process scripts;
- has no live print/object graph;
- exposes ctx.gcode_path/ctx.host/ctx.output_name;
- edits working G-code in place;
- may fire multiple times per slice on separate working copies;
- output is not reflected in standard G-code viewer.

The same SlicingPipeline capability class may implement geometry and post-process steps.

## 8. Multiple capabilities / preview
PyPluginPackage explicitly permits register_capability() once per capability class.

Official sandbox Script examples use orca.host.ui.create_window.

Therefore one package can provide:
- SlicingPipeline capability;
- Script preview capability.

UI must be invoked from UI-safe Script execution, not slicing worker.

## 9. Cache/invalidation finding
Orca tests confirm:
- activating/changing slicing_pipeline_plugin invalidates posSlice;
- changing plugin config overrides invalidates posSlice.

This supports deterministic re-analysis after plugin/config changes.

Still, no plan at export is treated as non-injectable; plugin never reconstructs geometry from G-code.

## 10. Important execution implication: flow redistribution
Orca Flow.cpp computes non-bridge mm3/mm using rounded-rectangle area:

A = h * (w - h * (1 - pi/4))

Because intermediate passes reduce the remaining physical height for the upper outer wall, additive-only sub-edge insertion would over-extrude.

The plan/injector must rewrite upper original wall flow for the remaining height.

## 11. Features deferred by source audit
v1 injection rejects:
- shared/duplicate/multiple PrintObjects;
- multi-volume/negative/modifier objects;
- By-object sequence;
- absolute-E target regions;
- arc-fitted target geometry;
- scarf/seam-slope wall geometry;
- fuzzy/spiral modes;
- multitool;
- other mutating postprocessors/plugins.

These are engineering scope gates, not claims that future support is impossible.

## 12. Remaining engineering risk
No known source-level impossibility remains inside the narrowed v1 domain.

Largest risk:
robustly matching a geometry-time whole-loop plan to the exact exported G-code loop while preserving machine state.

Mitigations:
- single-object/loop-first scope;
- supported golden fixtures;
- parser/state machine;
- exactly-one-plan matching;
- all-or-nothing validation;
- relative-E requirement;
- arc fitting off;
- atomic replacement.
