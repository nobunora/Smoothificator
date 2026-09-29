# Plugin Requirements — Stock Orca Printable Architecture

## Orca
Target builds with Python Plugin System + SlicingPipeline (officially Nightly or releases > 2.4.2). Pin exact tested versions.

## Capabilities
One plugin package registers multiple capabilities:

1. SlicingPipeline capability
   - posSimplifyPath Analyzer
   - psGCodePostProcess Injector
2. Script capability
   - preview/diagnostics on UI thread

Official Orca supports multiple capabilities per plugin package.

## Thread rules
SlicingPipeline execution is not a UI entrypoint. Never call orca.host.ui.* there.

Script capability runs on the main/UI thread and may create the preview window, but must keep heavy work outside UI.

## Current-session state
Capability/module state exists for the plugin load lifetime, but live slicing graph objects do not.

Use a shared thread-safe module/application PlanStore containing copied immutable plans/runtime records only.

Fresh slice is mandatory before first printable injection after plugin load/reload.

## v1 printable gates
- one printable object
- one printable instance
- one ModelPart volume
- no modifier/negative volume
- one tool/extruder
- no other active slicing-pipeline capability
- classic post_process empty
- supported G-code dialect/profile
- validated coordinate transform
- plan generated in current session
- non-crossing outward/top-facing target region

Unsupported => analysis-only or injection skipped.

## Post-process execution
psGCodePostProcess edits ctx.gcode_path after classic scripts.

Because v1 forbids classic scripts/other slicing-pipeline capabilities, the validated Orca file is the only mutation target.

The injector uses streaming parse/validation and temp-file emission, then atomic same-directory replacement.

## Standard preview limitation
Orca standard G-code viewer maps the pre-post-process file.

Plugin Script capability provides a separate preview from the exact plan hash.

## Dependencies
Target pure-Python wheel.

NumPy is required for mesh/path arrays.

Avoid mandatory compiled geometry dependencies in v1. Orca-backed planar geometry operations may be accessed through an abstract adapter/port during the live hook, with copied results returned to the engine.

## Compatibility
Unknown Orca/API/dialect changes default to injection disabled, never best-effort mutation.
