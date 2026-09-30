# Plugin Requirements — Stock Orca Printable Architecture

## 1. Orca requirement
Target Orca builds with Python Plugin System and SlicingPipeline.

Pin exact tested Orca versions per plugin release because SlicingPipeline is experimental.

## 2. Required plugin capabilities
One plugin package MUST register:
1. SlicingPipeline capability
   - posSimplifyPath analyzer
   - psGCodePostProcess matcher/rewriter/injector
2. Script capability
   - user-triggered preview/diagnostics using copied PlanStore data

Orca package registration supports multiple capability classes.

Never call orca.host.ui.* from SlicingPipeline execute().

## 3. Why posSimplifyPath
posContouring is conditional on Orca deciding contouring is needed.

posSimplifyPath is after contouring and path simplification and is therefore the canonical v1 analysis seam.

## 4. Stock Orca feasibility
Stock Orca exposes enough read-only geometry to compute:
- source mesh;
- structural layers;
- final simplified 3D extrusion paths including any ZAA offsets;
- width/height/mm3_per_mm;
- residual error;
- complete WallPassSchedules.

psGCodePostProcess provides the exported working G-code path for intended in-place post-processing.

Therefore v1 can print without live perimeter mutation:
- analyze geometry before export;
- store immutable plan;
- rewrite original outer-wall E and insert planned intermediate paths in exported G-code.

## 5. Coordinate requirement
ExtrusionPath Z is not assumed absolute.

Adapter MUST normalize:
Z_abs = layer.print_z + unscale(point_z)

All plan/preview/injection geometry uses absolute print-space mm.

## 6. Preview
Orca standard G-code viewer is pre-post-process.

Plugin preview uses the exact immutable plan later used for injection.

Preview status combines immutable plan + separate execution status record.

## 7. Cross-hook handoff
Live geometry cannot cross hook boundaries.

PlanStore MUST:
- be process-local;
- thread-safe;
- store immutable plans;
- store execution status separately;
- permit candidate enumeration for G-code matching;
- never store Orca live objects.

At export, select a plan only if exactly one candidate matches all G-code anchors/state. Zero/multiple matches => no injection.

## 8. Printable v1 gates
All must pass:
- one PrintObject;
- one printable instance;
- one positive ModelPart volume;
- no negative/modifier/helper volumes;
- one tool/extruder;
- By Layer print sequence;
- absolute XYZ mode;
- relative E in target interval;
- arc fitting disabled;
- scarf/seam-slope disabled;
- fuzzy skin disabled;
- spiral/vase disabled;
- no classic post-processing scripts;
- no other geometry/G-code-mutating slicing-pipeline plugin;
- no support-dependent target;
- supported G-code fixture family;
- non-crossing outward/top-facing external wall.

Unsupported configurations enter analysis-only mode or INJECTION_SKIPPED.

## 9. Flow/rewrite requirement
Refinement MUST redistribute outer-wall extrusion.

The original upper external-wall loop is matched and its E increments are scaled/recomputed for the remaining effective pass height.

Intermediate passes are then added below it.

Additive-only injection is forbidden.

## 10. Packaging
Target a pure-Python wheel.

No compiled/native plugin dependency in v1.

## 11. Golden-fixture prerequisite
Before physical injection support is enabled for a printer/profile family, repository MUST contain:
- exact Orca version/profile metadata;
- original representative G-code fixture;
- parser-state expectations;
- layer/wall anchor expectations;
- expected rewritten/injected output;
- idempotence fixture.

Without a golden fixture, mode is analysis-only.

## 12. Compatibility behavior
Unknown Orca API, profile, dialect, or state defaults to non-destructive disablement.

Never use best-effort mutation.
