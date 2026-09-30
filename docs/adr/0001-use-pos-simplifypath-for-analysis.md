# ADR-0001: Use posSimplifyPath as the geometry-analysis hook

Status: Accepted
Date: 2026-09-30

## Context
The original specification selected posContouring so analysis would occur after ZAA. Source audit of OrcaSlicer Print.cpp shows posContouring's plugin hook fires only when PrintObject::need_z_contouring() is true. When ZAA is disabled or an object does not require contouring, the step is marked done without running the plugin hook.

That contradicts the required fallback behavior: analyze ordinary Orca geometry when ZAA is disabled/ineligible.

Orca runs posSimplifyPath after contouring and after the generated extrusion paths have been simplified. Its hook is object-scoped and exposes the same live PrintObject graph.

## Decision
Use **posSimplifyPath** as the sole v1 geometry-analysis hook.

The analyzer always treats paths visible at posSimplifyPath as the canonical baseline. It does not need to determine whether an individual path was actually modified by ZAA.

Record ZAA configuration as diagnostics only.

## Cache behavior
Orca intentionally does not fire geometry hooks on cache-loaded plugin-final objects. Activating/changing the slicing-pipeline plugin invalidates posSlice, so a fresh compatible slice produces the hook. If no matching plan exists at export, psGCodePostProcess MUST skip injection and report PLAN_MISSING; it MUST NOT infer a plan from G-code.

## Alternatives considered
- posContouring: rejected because conditional.
- posPerimeters: rejected because it precedes ZAA.
- multiple hooks: rejected for v1 because it complicates deduplication/state without adding value.

## Safety impact
Positive: analyzer sees geometry closer to final G-code and works whether ZAA changed the object or not.

## Compatibility impact
Requires Orca builds exposing posSimplifyPath SlicingPipeline hook.

## Test impact
Add tests/fixtures proving:
- analyzer runs with ZAA enabled;
- analyzer runs with ZAA disabled;
- missing plan at export is non-destructive.

## Migration
Replace all normative references to posContouring with posSimplifyPath.

Supersedes: none.
