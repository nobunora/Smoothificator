# OrcaSlicer Plugin / Geometry API Research

Research target: OrcaSlicer main and official plugin docs, 2026-09.

## Conclusion
Stock Orca is sufficient for the v1 architecture by combining two official SlicingPipeline seams:

- posContouring: read post-ZAA geometry and compute SubEdgePlan
- psGCodePostProcess: edit the exported working G-code in place

A custom Orca build is not required for v1.

## Plugin availability
Official docs: Python Plugin System is available in Nightly or releases greater than 2.4.2. SlicingPipeline is research/experimental, so releases must pin tested Orca versions.

## Relevant API behavior
At geometry steps:
- ctx.print / ctx.object expose live slicing graph
- references live only during execute(ctx)
- pipeline capability runs on slicing worker thread
- do not call orca.host.ui.* from that thread

At psGCodePostProcess:
- ctx.print / ctx.object are None
- ctx.gcode_path points to the working exported G-code
- ctx.host / ctx.output_name are available
- plugin edits file in place
- step may run separately for export/upload
- output is not reflected in Orca standard G-code preview

## Readable geometry
Bindings expose Print, PrintObject, Layer, LayerRegion, Print-owned Model snapshot, Surface/ExPolygon, extrusion tree, native 3D ExtrusionPath points, width, height, mm3_per_mm and config.

This is enough for post-ZAA error analysis and plan generation.

## Read-only limitation
Perimeters/path points/layer Z cannot currently be arbitrarily mutated from Python.

This no longer blocks v1 because the plugin does not attempt live path injection. It converts a geometry-derived plan to G-code at psGCodePostProcess.

## Preview implication
Standard Orca G-code viewer maps the pre-post-process file, so injected sub-edges are absent there.

Stock Orca still permits plugin-owned preview: the plan is copied into plugin-owned data, then a UI-safe Script capability may display a host-owned HTML window/panel. The slicing hook itself must not invoke UI.

## Required architectural separation
Analyzer:
model + post-ZAA geometry -> immutable SubEdgePlan

Preview:
SubEdgePlan -> visualization

Injector:
SubEdgePlan + exported G-code -> validated G-code insertion

Preview and injector share plan hash. Injector must not perform geometry optimization.

## Why this is safer than legacy Smoothificator
Legacy Smoothificator infers/refines outer walls from final G-code.

This design makes geometric decisions while source mesh and ZAA paths are still available, then uses final G-code only as an execution target. Anchor validation must prove that the G-code corresponds to the planned geometry before insertion.

## Filesystem/audit
Official slicing docs state writing ctx.gcode_path at psGCodePostProcess is an intended operation; that working folder is approved for the call. Other filesystem/network/process operations remain subject to plugin audit policy.

## Remaining technical risks
- reliable plan identity across slice/export calls
- robust Orca G-code state parsing
- exact anchor matching
- Bambu/other firmware dialect differences
- preview is plan-level, not Orca standard postprocessed viewer
- SlicingPipeline API may change because it is experimental

These risks are addressed by deterministic hashing, explicit version support, stateful parser, all-or-nothing injection and analysis-only fallback.
