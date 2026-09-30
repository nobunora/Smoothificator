# ADR-0011: Validate final export configuration through ctx.config_value

Status: Accepted
Date: 2026-09-30

## Context
The geometry plan is created during posSimplifyPath, while G-code injection happens later at psGCodePostProcess.

A plan is only safe if the resolved settings relevant to geometry/extrusion/execution have not changed between planning and export.

Orca's SlicingPipelineContext implementation explicitly keeps config_value(key) available at psGCodePostProcess by reading the full export configuration even though ctx.print and ctx.object are None.

Relying only on G-code header comments to reconstruct settings would be less direct and more profile/dialect dependent.

## Decision
Define a versioned ExecutionConfigFingerprint from a fixed allowlist of safety-relevant resolved config keys.

Compute it:
1. during geometry analysis from the live resolved config;
2. again during psGCodePostProcess using ctx.config_value(key).

Injection is allowed only when the canonical fingerprints are identical.

Initial v1 fingerprint MUST include, at minimum, keys needed to validate:
- nozzle diameter
- filament diameter
- filament flow ratio
- use_relative_e_distances
- use_firmware_retraction
- gcode_add_line_number
- enable_arc_fitting
- spiral/vase mode
- ironing state relevant to target
- scarf/sloped seam state
- support/raft gates
- print sequence
- active single-tool/extruder assumptions
- before_layer_change_gcode
- layer_change_gcode
- z_offset
- extruder XY offset or equivalent active offset config
- classic post_process setting

The exact key names are verified against the pinned Orca version before implementation and stored centrally in the Orca config adapter.

## G-code validation remains required
Config fingerprint equality does NOT replace final G-code parsing.

The injector still validates:
- modal state actually present in G-code;
- structural anchors;
- execution-frame translation;
- custom-code/motion assumptions;
- exact supported dialect markers.

## Alternatives considered
- G-code header only: rejected as primary source.
- Trust the plan without export-time config check: rejected.
- Hash every Orca config key: rejected because irrelevant changes would unnecessarily invalidate plans and schema stability.

## Safety impact
Prevents stale-plan injection after a settings change and gives reliable final validation for filament flow ratio and coordinate-affecting settings.

## Test impact
Add:
- same-config acceptance;
- one-key changes for every required safety key -> rejection;
- canonical serialization independent of map ordering;
- missing required key -> injection disabled.

Supersedes: none.
