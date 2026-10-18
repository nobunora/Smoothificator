# ADR-0001: Analyze after path simplification

Status: Accepted
Date: 2026-09-29

## Context
The initial specification used `posContouring` as the analysis hook because ZAA runs immediately before it.

Source audit of OrcaSlicer `Print.cpp` found two problems:

1. `posContouring` plugin execution only occurs when `need_z_contouring()` is true. If ZAA is disabled or the object does not require contouring, no `posContouring` hook is fired.
2. Orca performs `simplify_extrusion_path()` later. A plan derived at `posContouring` is therefore based on path geometry that can still change before G-code generation.

Orca exposes `posSimplifyPath` immediately after `simplify_extrusion_path()`.

## Decision
Use `posSimplifyPath` as the v1 analysis hook.

The analyzer reads each fresh-sliced object's finalized/simplified 3D extrusion paths there.

For v1, only one printable object and one printable instance are supported, so a per-object hook produces one unambiguous plan.

## Important cache behavior
Orca intentionally does not fire the `posSimplifyPath` plugin hook for cache-loaded plugin-final objects.

Therefore printing injection requires a matching plan generated from a fresh slice in the current plugin load/session. If none exists, post-processing MUST skip injection and request a fresh slice.

## Alternatives considered
- `posContouring`: rejected because it is conditional on Z contouring and precedes path simplification.
- `psSkirtBrim`: rejected because it runs before `simplify_extrusion_path()`.
- `posDetectOverhangsForLift`: post-ZAA but still before simplification.

## Safety impact
Positive. Analysis is performed on geometry closer to the final exported toolpath.

## Compatibility impact
The plugin requires a fresh slice before the first injection after plugin load/reload.

## Test impact
Add integration tests proving:
- hook runs with ZAA on;
- hook runs with ZAA off;
- cache-only export without a current plan skips injection;
- plan geometry corresponds to post-simplification paths.
