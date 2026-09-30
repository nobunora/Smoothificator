# OrcaSlicer Plugin / Geometry API Research

Research target: OrcaSlicer main and official plugin sources, audited through 2026-09-30.

## 1. Feasibility conclusion
A conservative printable v1 is feasible on **stock OrcaSlicer** using:
- posSimplifyPath for geometry analysis;
- psGCodePostProcess for final working-file injection;
- Script capability for preview.

No custom Orca build is required.

## 2. Hook selection
Print.cpp shows:
- posContouring hook only fires when need_z_contouring() is true;
- simplify_extrusion_path() occurs later;
- posSimplifyPath fires after simplification for freshly processed objects.

Therefore posSimplifyPath is the canonical analyzer hook.

Cache-loaded plugin-final objects intentionally do not re-fire it. Missing current-session plan => no injection.

## 3. Plugin package/UI capability
PyPluginPackage permits register_capability() for each capability class.

Official sandbox plugins demonstrate ScriptPluginCapabilityBase and orca.host.ui.create_window.

One plugin package can therefore provide:
- SlicingPipeline analyzer/injector capability;
- Script preview capability.

## 4. Readable slicing graph
Bindings expose:
- Print / PrintObject
- Layer / LayerRegion
- source Model snapshot / ModelObject
- ModelVolume mesh and transforms
- Surface/ExPolygon
- extrusion tree
- ExtrusionPath 3D points
- width / height / mm3_per_mm
- resolved config

This is enough for read-only planning.

## 5. Coordinate finding
PluginHostSlicing exposes path points in scaled native coordinates.

ContourZ.cpp stores point Z as relative offset d, not absolute layer Z.

Adapter must use:
Z_abs = layer.print_z + unscale(d)

## 6. ZAA G-code flow finding
GCode.cpp explicitly handles path.z_contoured:

For each line endpoint:
- z_diff = unscale(line.b.z())
- z = nominal_z + z_diff
- for non-ironing:
  extrusion_ratio = (path.height + z_diff) / path.height
- emitted E = nominal dE * extrusion_ratio

Therefore a correct predictor needs local Z **and local effective flow**.

This source verification supports ADR-0006.

## 7. Mesh bindings
ModelVolume.mesh():
- immutable mesh snapshot;
- local coordinates in mm.

Bindings expose:
- ModelVolume.matrix() volume->object
- PrintObject.trafo() object->print

v1 limits printable mode to one ModelPart volume, avoiding arbitrary multi-volume CSG reconstruction.

## 8. Mutable geometry limits
LayerRegion.slices is mutable at posSlice.

Generated perimeters/ExtrusionPath geometry is read-only from public Python bindings.

This is not a v1 blocker because v1 injects only new SubEdge G-code after export rather than mutating live paths.

## 9. psGCodePostProcess
Official source/sample confirms:
- runs from export path after classic post_process scripts;
- ctx.print/ctx.object are None;
- ctx.gcode_path is working file;
- ctx.host/output_name are available;
- plugin edits file in place;
- may run multiple times on separate working copies;
- result does not appear in standard Orca preview.

## 10. Why final G-code is not used for geometry design
The geometry plan is created at posSimplifyPath where:
- source mesh is available;
- structural/ZAA paths are available;
- local effective flow can be reconstructed.

Final G-code is execution target only.

If no matching immutable current-session plan exists, injector skips.

## 11. Bambu layer-boundary research
Source/profile audit behind ADR-0007 found the supported Bambu layer-change environment can be identified around structural layer transition markers.

v1 safe execution:
- validated profile/custom layer G-code only;
- safe-ceiling lift before any injected lateral travel;
- vertical descent to candidate;
- restore saved upper-layer state before resuming Orca.

Unknown/motion-producing custom layer code disables injection.

## 12. G-code-mode reduction
ADR-0008 intentionally limits physical v1 to:
- relative E
- firmware retract off
- line numbers/checksum off
- arc fitting off
- single tool
- spiral/ironing/scarf/support/raft off

Parser may observe other modes but must not inject outside supported contract.

## 13. File-size finding
Large G-code may be hundreds of MB.

Injector architecture should stream:
1. validation pass;
2. temp emission pass;
3. sanity pass;
then atomic replace.

Do not make full-file memory loading a requirement.

## 14. Remaining technical risk
Largest remaining risk is correct and robust G-code state/anchor handling, not Orca geometry access.

This risk is isolated in orca_plugin/gcode and gated by golden fixtures before physical printing.


## 15. Print-space vs final G-code coordinate finding
GCode::point_to_gcode() applies the current instance origin (m_origin) and active extruder XY offset. PrintApply separates instance XY translation into PrintInstance.shift, and GCode sets m_origin from that shift. GCode::change_layer() also applies printer z_offset to structural machine Z.

Therefore plugin plan coordinates cannot be emitted directly.

ADR-0009 requires final-G-code anchor matching to derive/validate one constant translation (dx,dy,dz) for the v1 one-instance/one-tool case before emission.

## 16. Volumetric-to-E conversion finding
Extruder.cpp caches:

m_e_per_mm3 = filament_flow_ratio / filament_crossection

Therefore injected candidate E must include the active filament_flow_ratio rather than assuming E = volume / area.

ADR-0010 defines the v1 conversion and required parity tests.
