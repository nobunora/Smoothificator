# ADR-0015: Match Orca's effective external-wall flow modifiers for SubEdge extrusion

Status: Accepted
Date: 2026-09-30

## Context

ADR-0010 correctly established that `filament_flow_ratio` affects volumetric-to-E conversion, but its formula is incomplete for current OrcaSlicer.

Audited OrcaSlicer commit `789f848694b955d293ca6b277d1c8046aa6f7436`, `GCode::_extrude()`, computes effective path flow from geometric `path.mm3_per_mm` using:
- `print_flow_ratio`;
- `filament_flow_ratio`;
- role-specific flow ratios when `set_other_flow_ratios` is enabled;
- then converts volume to filament length using filament cross-section.

For `erExternalPerimeter` outside the first layer and outside mixed sublayer modes:

commanded_q = geometric_q
              * print_flow_ratio
              * filament_flow_ratio
              * external_role_factor

where:
- external_role_factor = outer_wall_flow_ratio when `set_other_flow_ratios=true`;
- otherwise external_role_factor = 1.

The emitted relative E per segment is:

E = length * commanded_q / filament_area

For ZAA structural paths, Orca additionally applies the local ZAA height ratio defined by ADR-0006.

Small Area Flow Compensation does not apply to external-perimeter role in the audited source.

## Decision

SubEdge v1 is treated as external-surface / external-perimeter-equivalent extrusion for flow-modifier purposes.

Every candidate segment stores two distinct volumetric quantities:
- `geometric_mm3_per_mm`: finite-bead model target before slicer calibration multipliers;
- `commanded_mm3_per_mm`: geometric value after Orca-compatible print/filament/role flow modifiers.

For v1:

role_factor =
    outer_wall_flow_ratio if set_other_flow_ratios
    else 1

commanded_q =
    geometric_q
    * print_flow_ratio
    * filament_flow_ratio
    * role_factor

E =
    segment_length
    * commanded_q
    / filament_cross_section

The baseline structural-surface predictor also records Orca's effective commanded flow modifiers so candidate-vs-baseline comparisons do not mix geometric and command-volume semantics.

Physical bead prediction remains an ideal commanded-volume model until empirical calibration is introduced. The documentation must not claim that `filament_flow_ratio` maps perfectly to physical deposited volume.

## Requirements / invariants introduced

The execution config fingerprint MUST include:
- `print_flow_ratio`;
- `filament_flow_ratio`;
- `set_other_flow_ratios`;
- `outer_wall_flow_ratio`;
- `filament_diameter`.

First-layer flow ratios remain out of v1 because first-layer refinement is unsupported.

## Alternatives considered

- Use only filament_flow_ratio: rejected; disagrees with Orca external-wall E.
- Ignore calibration ratios in geometry and copy E from neighboring G-code: rejected; neighboring paths may have different ZAA/role/local-flow behavior.

## Safety impact

Critical for material amount and dimensional quality.

## Compatibility impact

Flow semantics are explicitly tied to the audited Orca source family and must be parity-tested when upgrading compatibility.

## Performance / resource impact

Negligible.

## Observability impact

Report geometric and commanded flow separately; never label one as the other.

## Test / validation impact

Add source-parity cases for:
- all ratios = 1;
- non-unity print_flow_ratio;
- non-unity filament_flow_ratio;
- enabled outer_wall_flow_ratio;
- disabled set_other_flow_ratios;
- ZAA baseline local ratio combined with global modifiers.

## Migration / rollout

Mark ADR-0010 as superseded for the complete v1 E formula. Its requirement to account for filament flow ratio remains incorporated here.

## Rollback / disable condition

Missing/unknown required flow modifier => analysis may continue, injection is disabled.

## Open questions

Empirical mapping from commanded volume to actual bead geometry is deferred to calibration phases.

Supersedes: ADR-0010.
