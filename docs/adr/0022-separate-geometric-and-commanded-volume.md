# ADR-0022: Separate geometric bead volume from calibrated commanded extrusion volume

Status: Accepted
Date: 2026-09-30

## Context

ADR-0015 defines Orca-compatible commanded extrusion modifiers such as:
- print_flow_ratio;
- filament_flow_ratio;
- optional outer_wall_flow_ratio.

Those values are calibration/execution controls. Treating them as if they directly redefine the ideal bead geometry would make a calibrated setting such as filament_flow_ratio=0.98 automatically predict a 2% smaller physical bead, which is not a justified physical model.

ZAA is different: its local ratio is explicitly coupled to a changed local nozzle Z/effective layer height and is part of Orca's geometric contouring behavior.

## Decision

Every structural/candidate segment distinguishes three concepts.

### Geometric volume model

Used by the ideal finite-bead geometry engine.

For a normal candidate:
- geometric_mm3_per_mm comes from the chosen width/height bead model.

For a ZAA structural segment:
- start from the path's nominal geometric volume;
- apply the local ZAA geometry-directed height ratio needed to model the locally reduced deposition target;
- pair it with the local effective bead height.

This creates the v1 nominal geometric envelope.

### Commanded volume

Used for G-code/E generation and execution diagnostics.

commanded_mm3_per_mm =
    geometric_mm3_per_mm
    * print_flow_ratio
    * filament_flow_ratio
    * applicable role flow ratio

### Empirical physical volume

Not yet modeled from first principles.

Future calibration may map commanded settings, material, speed, temperature, pressure state, and measured bead geometry to an empirical envelope.

Until then:
- geometry/error optimization uses the nominal geometric envelope;
- G-code E uses commanded volume;
- reports show both;
- no claim is made that commanded calibration multipliers linearly equal physical bead-size multipliers.

## Requirements / invariants introduced

- `geometric_mm3_per_mm` and `commanded_mm3_per_mm` are distinct fields/derived values.
- Surface-error scoring MUST NOT silently use global flow calibration multipliers as geometric shrink/expansion.
- ZAA local height/volume behavior is modeled separately from global calibration multipliers.
- Physical-print results may cause this model to be revised through a later ADR.

## Alternatives considered

- Use commanded volume directly as bead geometry: rejected as uncalibrated.
- Ignore commanded volume entirely: rejected because G-code E and volumetric-speed limits require it.

## Safety impact

High for optimizer correctness and interpretation of predicted quality.

## Compatibility impact

Clarifies the meaning of fields introduced by ADR-0014/0015.

## Performance / resource impact

Negligible.

## Observability impact

Preview/debug metrics label:
- geometric volume;
- commanded volume;
- calibration multiplier;
separately.

## Test / validation impact

Add tests proving:
- changing filament_flow_ratio changes emitted E but not ideal geometric envelope;
- changing ZAA local height changes geometric local envelope;
- commanded volumetric-speed checks still use commanded volume.

## Migration / rollout

Update ERROR_MODEL, plan DTO definitions, and baseline predictor before engine implementation.

## Rollback / disable condition

None; this is a modeling separation. If empirical data disproves the nominal geometry approximation, revise through calibration ADR.

## Open questions

Empirical bead correction model is deferred to physical calibration.

Supersedes: any earlier wording that treated global flow calibration ratios as direct physical bead-size multipliers.
