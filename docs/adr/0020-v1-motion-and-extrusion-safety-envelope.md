# ADR-0020: Define the v1 motion, speed, pressure-advance, and calibration safety envelope

Status: Accepted
Date: 2026-09-30

## Context

Injected SubEdge paths bypass Orca's normal `GCode::_extrude()` orchestration. Orca normally applies role-based speed/acceleration/flow and may dynamically alter pressure advance or execute extrusion-role-change custom G-code.

The postprocessor must not silently assume those behaviors.

Safe-ceiling travel also requires a machine Z limit.

## Decision

Printable v1 adds the following gates and motion rules.

### Unsupported execution features

Injection is disabled when:
- Orca calibration/tower mode is detected in the final G-code or supported profile metadata;
- adaptive pressure advance is enabled;
- machine, filament, or process extrusion-role-change G-code is non-empty;
- firmware retraction is enabled;
- line-number/checksum output is enabled;
- arc fitting is enabled;
- unsupported tool/multifilament state is present.

Static filament pressure advance may remain enabled because the currently active firmware PA state is inherited and is not changed by the plugin.

### Candidate extrusion speed

For each candidate segment:

commanded_q = commanded_mm3_per_mm

volumetric_limit_speed =
    filament_max_volumetric_speed / commanded_q

candidate_speed MUST NOT exceed:
- resolved outer-wall speed;
- volumetric_limit_speed;
- optional plugin/user SubEdge speed cap if configured.

Missing/non-positive required speed or volumetric limit disables injection.

The plugin does not silently increase any Orca speed.

### Acceleration / jerk / pressure state

v1 does not emit new acceleration, jerk, or PA commands.

It parses and preserves the machine state at the insertion anchor. Candidate moves run under that unchanged modal acceleration/PA state at the conservative candidate speed. A future dedicated role-state block requires another ADR.

### Safe ceiling

Use the active resolved Z-hop/travel-lift value as the initial v1 safe-ceiling lift.

Require:
- lift > 0;
- Zsafe = max(actual saved Z, target upper structural machine Z) + lift;
- Zsafe <= active tool printable-height limit (extruder-specific limit when defined, otherwise printer printable_height).

Use resolved travel speed for XY safe-ceiling travel and resolved Z travel speed for vertical moves, subject to supported fixture behavior.

If a valid Zsafe cannot be established, skip the interval/injection.

### G-code comments

Verbose G-code/comments are required for initial printable fixtures as additional matching evidence, but geometry/state matching remains authoritative.

The plugin MUST NOT silently change the user's Orca process settings. Unsupported settings are reported as analysis-only requirements.

## Requirements / invariants introduced

Execution config fingerprint expands to include all safety-relevant values above, including:
- adaptive_pressure_advance;
- enable_pressure_advance state for diagnostics;
- change_extrusion_role_gcode variants;
- outer_wall_speed;
- filament_max_volumetric_speed;
- travel_speed / travel_speed_z;
- z_hop / active filament override;
- printable_height / active extruder printable height;
- gcode_comments.

## Alternatives considered

- Reimplement all Orca role setup: rejected for v1 complexity/risk.
- Hard-code candidate speed/lift: rejected.
- Assume machine has vertical clearance: rejected.

## Safety impact

Critical for motion and extrusion-rate bounds.

## Compatibility impact

Initial physical testing requires a deliberately constrained process/profile configuration. Bambu's normal process may have arc fitting enabled, so the plugin reports that requirement instead of changing it.

## Performance / resource impact

Conservative speeds increase test print time but do not alter analysis complexity materially.

## Observability impact

Preview/status reports:
- each failed gate;
- chosen speed bound;
- volumetric utilization;
- Zsafe and printable-height margin.

## Test / validation impact

Add fixtures for:
- adaptive PA rejection;
- role-change custom G-code rejection;
- arc-fitting rejection;
- Bambu default arc-on analysis-only result;
- speed cap;
- max-volumetric cap;
- zero/missing z-hop rejection;
- printable-height overflow rejection;
- calibration-mode rejection.

## Migration / rollout

Update PLUGIN_REQUIREMENTS, ExecutionConfigFingerprint, preview diagnostics, and fixture gate.

## Rollback / disable condition

Any unknown role/motion/PA/calibration behavior disables injection.

## Open questions

Explicit candidate acceleration/PA control may be evaluated only after initial physical PoC.

Supersedes: none.
