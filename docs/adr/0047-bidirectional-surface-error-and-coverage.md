# ADR-0047: Use bidirectional surface error so missing material cannot disappear from the metric

Status: Accepted
Date: 2026-10-08

## Context

The earlier error description sampled points on the predicted printed envelope P and measured them against the source-model surface M.

That direction is necessary for detecting overbuild, but it is not sufficient for underfill/coverage.

If an intended source-surface band has little or no predicted material nearby, there may be no corresponding predicted-surface sample q in that region. A purely P -> M metric can therefore report a deceptively small error while an intended surface patch is missing.

Adaptive Sub-Edge is explicitly a surface reconstruction method, so source-surface coverage must be part of the hard tolerance contract.

## Decision

For every target surface region, the v1 ErrorEstimator evaluates two deterministic directions using the same versioned sampling/convergence contract from ADR-0045.

### Predicted -> source

Sample the exposed predicted nominal material envelope P.

Measure signed/normal-aware distance to the intended source boundary M.

This direction is primarily sensitive to:
- overbuild;
- misplaced material;
- predicted surface outside the source.

### Source -> predicted

Sample the intended target source surface/band M.

Measure the distance along the validated material/outward-normal convention, with closest-surface fallback where the normal ray is not numerically resolvable, to the predicted exposed material envelope P.

This direction is primarily sensitive to:
- missing material;
- uncovered terraces;
- seam/gap underfill;
- insufficient surface-band coverage.

## Hard metrics

At minimum retain separate directional summaries:

- E_max_pred_to_src
- E_max_src_to_pred
- E_p95_pred_to_src
- E_p95_src_to_pred
- E_rms_pred_to_src
- E_rms_src_to_pred

Define the public combined hard maximum as:

E_max = max(E_max_pred_to_src, E_max_src_to_pred)

The configured surface tolerance applies to BOTH directional hard errors unless a future ADR explicitly defines asymmetric tolerances.

Signed bias is reported separately with a documented sign convention and MUST NOT replace either directional coverage/error constraint.

## Region of evaluation

Do not score arbitrary hidden/internal bead surfaces.

The estimator operates on the relevant exposed/target surface band associated with the source region and predicted outer material envelope.

Surface classification must be deterministic and use the validated source orientation/material side.

## Empty/missing cases

If the target source band is non-empty but no valid predicted exposed surface exists within the bounded search domain:
- source -> predicted hard error is infeasible / effectively outside tolerance;
- never treat the region as zero error.

If predicted material exists where the target band is empty/outside the intended material boundary, predicted -> source detects overbuild.

## Final G-code revalidation

ADR-0034 FinalStructuralDepositionContext uses the same bidirectional hard-error semantics after final seam/quantization/deposition reconstruction.

Postprocess may accept/reject only; it does not re-optimize.

## Requirements / invariants introduced

- Underfill cannot disappear because the predicted surface lacks samples.
- Public E_max is bidirectional.
- Both directions use ADR-0045 convergence.
- Preview may show the two directional maps separately.
- Tolerance checks are not based solely on signed mean/bias.

## Alternatives considered

- One-sided predicted -> source distance: rejected.
- Unsigned symmetric Hausdorff only: useful but loses directional underfill/overbuild diagnostics.
- Source -> predicted only: misses excess material outside the source.

## Safety / quality impact

Critical for geometry correctness.

## Test impact

Add:
- completely missing target patch -> reject;
- narrow uncovered terrace missed by predicted-only sampling -> source-to-predicted detects it;
- external overbuild -> predicted-to-source detects it;
- seam gap underfill;
- symmetric near-perfect case;
- both directions converge under ADR-0045.

## Rollback / disable condition

Either directional hard metric fails to converge/resolve => non-injectable.
