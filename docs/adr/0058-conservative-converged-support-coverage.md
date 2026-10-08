# ADR-0058: Make support-coverage acceptance conservative and converged

Status: Accepted
Date: 2026-10-08

## Context

ADR-0044 defines a deterministic SupportCoverageMetric using the candidate footprint and ChronologicalSupportEnvelope.

However, a fixed sampling grid can produce a false-positive support decision.

Example:
- a narrow unsupported slot exists inside the bead footprint;
- the slot is narrower than the current sample spacing;
- no sample lands inside the slot;
- supported_area_fraction is incorrectly reported as 1.0.

This is unacceptable because support is a hard printability gate, not only a quality estimate.

ADR-0045 already requires convergence for surface-error metrics. Support acceptance needs an equivalent fail-closed numerical contract.

## Decision

Replace any fixed-resolution "sample and trust" support acceptance with a versioned conservative adaptive procedure.

### Support query coordinates

Evaluate support in a deterministic candidate-local footprint frame:
- longitudinal coordinate along the segment;
- lateral coordinate across nominal bead width.

The authoritative support query still uses ChronologicalSupportEnvelope.

### Cell classification

Partition the candidate footprint into deterministic cells.

For each cell classify:

- PROVEN_SUPPORTED:
  the whole cell is conservatively proven to have valid underlying material/contact and effective-height bounds;

- PROVEN_UNSUPPORTED:
  any part required by the conservative cell bound is proven outside support/contact limits;

- UNRESOLVED:
  current geometric/numeric bounds cannot prove either state.

A cell MUST NOT be counted as supported merely because its center/corner samples are supported.

### Adaptive refinement

UNRESOLVED cells are subdivided deterministically.

Required settings:
- initial_support_cell_size_mm;
- support_refinement_factor;
- support_metric_convergence_fraction;
- support_width_convergence_mm;
- max_support_refinement_levels;
- minimum_support_cell_size_mm;
- support-query numeric tolerance/version.

All participate in PluginSettingsFingerprint.

### Conservative lower bounds

Acceptance uses conservative lower bounds:

- supported_area_fraction_lower_bound;
- minimum_contiguous_support_width_lower_bound_mm;
- minimum_effective_height_lower_bound_mm;
- maximum_effective_height_upper_bound_mm.

Unresolved cells at the maximum refinement level are treated as unsupported for hard acceptance.

### Convergence

At each refinement level compute the conservative metrics.

Hard support acceptance requires:
- all hard thresholds satisfied by lower/upper bounds;
- change in supported-area lower bound <= support_metric_convergence_fraction;
- change in contiguous-support-width lower bound <= support_width_convergence_mm;
- effective-height bounds stable within configured numeric tolerance;
- convergence achieved before max level.

Failure to converge => candidate non-injectable.

### Optional exact geometry path

A future/existing exact polygon/solid intersection implementation may replace adaptive subdivision only if it produces equal-or-more-conservative deterministic bounds under the same metric interface and passes parity fixtures.

No implementation may silently switch to a non-conservative point-sampling shortcut.

## Requirements / invariants introduced

- Hard support acceptance cannot depend on lucky sample placement.
- Unresolved fine-scale support is fail-closed.
- Support metric resolution/settings are explicit and fingerprinted.
- Same geometry/settings => identical refinement tree and result.
- Support convergence is distinct from surface-error convergence.

## Alternatives considered

- Fixed dense grid: rejected; no finite fixed grid guarantees detection of smaller unsupported features.
- Count unresolved cells as half supported: rejected for safety.
- Universal exact mesh boolean requirement: deferred; may be expensive and library-dependent.

## Safety impact

High. Prevents numerically missed unsupported gaps from becoming printable candidates.

## Compatibility impact

May reject candidates that older coarse sampling would have accepted.

## Performance / resource impact

Potentially significant near support boundaries. Use deterministic spatial acceleration and bounded refinement.

## Observability impact

Report:
- refinement levels used;
- unresolved area fraction;
- conservative support lower bounds;
- convergence result.

## Test / validation impact

Add:
- unsupported slit smaller than initial sample spacing -> reject;
- supported solid footprint -> converge/pass;
- unresolved boundary at max level -> reject;
- same result under deterministic traversal/order changes;
- parity against exact analytic support geometries;
- convergence threshold boundary tests.

## Migration / rollout

ADR-0044 remains the semantic owner of support metrics; this ADR supersedes any interpretation that a single fixed sampling resolution is sufficient for hard acceptance.

## Rollback / disable condition

Non-converged or unresolved support => non-injectable / Skipped.

## Open questions

Physical support thresholds still require fixture/calibration evidence.
