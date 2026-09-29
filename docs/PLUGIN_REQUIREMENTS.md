# Plugin Requirements — Stock Orca Printable Architecture

## Orca version
Target Orca builds with Python Plugin System and SlicingPipeline. Official docs currently state Nightly or releases > 2.4.2. Pin exact tested versions because SlicingPipeline is experimental.

## Capabilities
Plugin package MUST provide:
1. SlicingPipeline capability:
   - posContouring analyzer
   - psGCodePostProcess injector
2. Script/UI-safe capability:
   - open/refresh plugin preview and diagnostics from copied PlanStore data

Never call orca.host.ui.* from SlicingPipeline execute().

## Why stock Orca is sufficient
Geometry hooks expose enough data to calculate source geometry, post-ZAA 3D paths, bead surface, residual error and optimized SubEdgePlan.

psGCodePostProcess officially exposes the working exported G-code path for in-place editing.

Therefore v1 prints arbitrary-Z sub-edges by translating the already-computed geometry plan into validated G-code, not by mutating Orca's read-only perimeter graph.

## Preview
Orca standard G-code viewer uses pre-post-process G-code and will not display injected paths.

The plugin MUST provide a separate preview based on the exact immutable SubEdgePlan used for injection.

UI status MUST distinguish planned vs injection-validated state.

## Cross-hook state
ctx.print/ctx.object do not exist at psGCodePostProcess and live references expire after geometry execute().

The analyzer MUST copy all data and store immutable plans in a thread-safe PlanStore. Injector may only consume a matching stored plan.

No geometry reconstruction from final G-code is permitted when a plan is missing.

## G-code safety
Injector must be parser/state-machine based, all-or-nothing, idempotent and atomic.

Unsupported dialect/state/anchor => skip and preserve original output.

## Plugin packaging
Target a pure-Python wheel. Do not require platform-specific compiled extensions for v1.

## First supported domain
- stock supported Orca
- 0.4 mm nozzle
- PLA first
- single tool/extruder
- outward/top-facing non-crossing surfaces
- default min Z spacing 0.08 mm
- ZAA-first where available
- no downward-facing reconstruction

## Compatibility
Each release MUST declare tested Orca versions/profiles. Unknown Orca/plugin API changes default to analysis-only or injection-disabled behavior, never best-effort mutation.
