# ADR-0045: Require deterministic converged surface-error estimation

Status: Accepted
Date: 2026-10-08

## Context

The project uses E_max, E_rms, E_p95, and signed bias to decide whether a candidate meets tolerance.

Those values depend on numerical sampling of the source surface and finite-bead envelope.

If sampling density is unspecified, identical geometry can be accepted by one implementation and rejected by another, and a coarse sampler can miss a local worst-case error.

Calling a sampled maximum "E_max" without a convergence contract is too strong.

## Decision

Introduce a versioned `ErrorEstimatorConfig` in plugin Settings.

Required values include:
- `initial_error_sample_spacing_mm`;
- `error_refinement_factor` (>1, initially expected to be 2 in research fixtures);
- `error_metric_convergence_mm`;
- `max_error_refinement_levels`;
- closest-point / sign numeric tolerance version.

Algorithm:

1. evaluate the required metrics at the configured initial deterministic sampling resolution;
2. refine the sampling resolution by the configured refinement factor;
3. recompute metrics;
4. require the change in each hard metric used for accept/reject to be <= `error_metric_convergence_mm`;
5. continue until converged or max refinement level is reached;
6. failure to converge makes the candidate non-injectable.

The metric names in UI/docs may remain E_max/E_rms/E_p95 for brevity, but the implementation/report must identify them as the converged result of the versioned estimator, not an analytic global proof.

The estimator configuration participates in PluginSettingsFingerprint.

## Requirements / invariants introduced

- Error acceptance is deterministic for identical inputs/settings.
- Hard tolerance decisions require numerical convergence.
- No implementation may silently choose its own sample spacing.
- Optimizer and final structural-deposition revalidation use compatible estimator semantics.

## Test impact

Add:
- coarse feature missed at first level but found after refinement;
- convergence success;
- non-convergence rejection;
- deterministic metrics under repeated runs;
- tolerance decision stable after final refinement;
- estimator settings fingerprint changes.

## Performance impact

Potentially significant; bounded by max refinement levels and later resource budgets.

## Rollback / disable condition

Non-converged hard metric => no injection.
