# ADR-0063: Bound candidate segment granularity and adjacent flow/shape transitions

Status: Accepted
Date: 2026-10-08

## Context

SubEdgePath is constant-Z, but ADR-0014 allows segment-local effective height, width, geometric flow, and commanded flow.

A numerically valid optimizer could therefore produce very short alternating segments such as:

- segment A: low q_cmd;
- segment B: much higher q_cmd over a tiny distance;
- segment C: back to low q_cmd.

v1 explicitly disables Orca extrusion-rate smoothing / Pressure Equalizer for printable injection.

Real extrusion pressure and bead shape cannot change instantaneously at an arbitrarily short polyline segment boundary.

Even when final XYZ length and E quantize to nonzero values, extreme segment granularity or abrupt width/height/volumetric-rate steps can cause:
- pressure transients;
- local over/under extrusion;
- corner blobs/gaps;
- a physical bead envelope that materially diverges from NominalBeadSolidV1.

The implementation must not invent universal transition limits without fixture evidence, but physical injection still needs an explicit contract.

## Decision

Introduce a versioned CandidateSegmentRegularityPolicy in plugin Settings.

### Required physical-fixture settings

For physical injection the exact fixture supplies reviewed/calibrated limits for at least:
- min_candidate_segment_length_mm;
- min_candidate_segment_time_s;
- max_adjacent_commanded_volumetric_rate_step_mm3_s;
- max_adjacent_width_step_mm;
- max_adjacent_effective_height_step_mm.

These participate in PluginSettingsFingerprint.

No universal physical default is claimed by this ADR.

Analysis/preview may operate with research values, but physical injection requires fixture-approved values.

### Plan-time segment regularization

Before SubEdgePlan is finalized, the engine validates every segment and every adjacent segment pair.

For segment i:
- plan-space segment length must exceed the conservative plan-time minimum;
- planned candidate_speed_mm_s must be finite/positive;
- planned segment execution time = length / speed must satisfy the minimum;
- q_geom and q_cmd must be finite/positive and inside all other bead bounds.

For adjacent segments i and i+1 define:

Q_i = q_cmd_i * speed_i
Q_next = q_cmd_next * speed_next

in mm3/s.

Require:
- abs(Q_next - Q_i) <= max_adjacent_commanded_volumetric_rate_step_mm3_s;
- abs(width_next - width_i) <= max_adjacent_width_step_mm;
- abs(h_eff_next - h_eff_i) <= max_adjacent_effective_height_step_mm.

### Engine-owned smoothing / merging

If a raw candidate violates these regularity bounds, only the geometry/optimizer layer may repair it before plan finalization.

Allowed pre-plan operations include:
- deterministic merging of near-identical adjacent segments when support/error semantics remain valid;
- adding a longer transition region and recomputing segment-local flow/geometry;
- rejecting the candidate.

Any smoothing/transition geometry becomes normal immutable plan intent and is fully rescored for support and bidirectional surface error.

Postprocess MUST NOT smooth, merge, split, or change segment flow to repair a violation.

### Final quantized execution revalidation

After execution-frame mapping and Orca-compatible quantization, recompute for every emitted segment:
- actual quantized 3D length;
- quantized relative E;
- emitted feedrate / segment time;
- adjacent commanded volumetric-rate step under emitted speeds.

Hard requirements:
- quantized length > 0;
- quantized length >= fixture min_candidate_segment_length_mm;
- nonzero material intent => quantized E > 0;
- emitted segment time >= min_candidate_segment_time_s;
- adjacent Q/width/effective-height transition bounds still pass.

If quantization invalidates regularity, the whole injection attempt is Skipped. Postprocess does not replan.

### Open-path endpoints

First/last candidate segments and candidate seam-gap-adjacent segments use the same minimum-length/time requirements.

Nominal flat axial end-cap modeling does not waive transition/segment regularity.

## Requirements / invariants introduced

- No arbitrarily short printable candidate segments.
- No unbounded adjacent flow/width/height steps in physical mode.
- Transition limits are fixture/calibration evidence, not hidden constants.
- Any repair happens before immutable plan publication and is rescored.
- Postprocess remains validation/serialization only.

## Alternatives considered

- Depend on Orca Pressure Equalizer: rejected because v1 disables it and injected paths bypass normal Orca orchestration.
- Hard-code one global flow-step percentage: rejected without physical evidence.
- Ignore transitions until physical testing: rejected because pathological segment chatter is predictable before hardware.
- Smooth in postprocess: rejected because it would change immutable plan geometry after preview/scoring.

## Safety / quality impact

High for physical bead fidelity and pressure-transient control.

## Compatibility impact

Physical fixtures must define segment-regularity limits. Missing evidence => analysis-only.

## Performance / resource impact

May increase optimizer cost because candidate segmentation/transition regions must be rescored.

## Observability impact

Preview/debug reports:
- minimum planned/emitted segment length;
- minimum segment execution time;
- maximum adjacent commanded volumetric-rate step;
- maximum adjacent width/height step;
- any regularization/rejection reason.

## Test / validation impact

Add:
- quantized zero-length segment -> reject;
- quantized E=0 with nonzero material intent -> reject;
- too-short positive segment -> reject;
- too-short execution time -> reject;
- excessive adjacent Q step -> reject;
- excessive width/height step -> reject;
- deterministic pre-plan merge/transition then full rescoring;
- seam-adjacent short segment handling;
- quantization turns valid plan-time segment into invalid emitted segment -> Skip.

## Migration / rollout

Update Settings/DTO schema in Phase 0.5, but do not invent production values until physical fixture/calibration work.

ADR-0048 remains the nominal bead-solid owner. ADR-0039 remains the extrusion-rate-smoothing gate. This ADR owns candidate segment regularity.

## Rollback / disable condition

Missing/unvalidated physical regularity limits => physical injection disabled.

## Open questions

Future empirical calibration may replace simple adjacent-step limits with a validated pressure/extrusion dynamic model.