# Plugin Requirements — Stock Orca Printable Architecture

## Orca
Target Orca builds with Python Plugin System + SlicingPipeline. Pin exact tested version/build because the API is experimental.

## Capabilities
One package registers:
1. SlicingPipeline
   - posSimplifyPath Analyzer
   - psGCodePostProcess Injector
2. Script capability
   - Preview/diagnostics on UI thread

Never call host UI from SlicingPipeline execution.

## Shared state
PlanStore is plugin-owned, thread-safe, process-local.

Live Orca objects never enter PlanStore.

Fresh slice in current plugin load is required for Injection.

## Printable v1 model gates
- one object
- one instance
- one ModelPart volume
- no NegativeVolume/ParameterModifier
- no support/raft
- nested top-facing target
- validated coordinate frame

## Printable v1 process gates
- one tool/material
- 0.4 mm nozzle initial target
- relative E
- firmware retraction off
- arc fitting off
- line number/checksum mode off
- spiral vase off
- ironing off
- scarf seam off
- no other slicing-pipeline capability
- classic post_process empty

## Initial printer profile family
Current stock Bambu/Orca A1, P1P/P1S and X1 Carbon 0.4 mm profile family is the first Golden-G-code target.

Current inspected layer-change template contains motion-neutral M73/M991 notifications and before-layer code is empty through the inspected inheritance chain.

Profile/template hashes and config are revalidated per Orca release.

## Geometry dependencies
NumPy required.

Avoid mandatory external compiled polygon libraries in v1.

Planar boolean/offset operations use a domain port; Orca-backed geometry implementation may be used during the live hook and must return copied domain data.

## Nozzle model
Physical Injection requires validated nozzle-envelope parameters/safety margin.

If unavailable, Analyzer/Preview may operate but Injector remains disabled.

## Preview
Standard Orca G-code viewer is pre-post-process.

Plugin Preview displays the exact immutable plan and runtime Injection status.

## Post-process
Injector edits ctx.gcode_path only after full validation.

Unknown profile/API/dialect/state defaults to Injection disabled.
