# ADR-0060: Make error-scoring domains closed under candidate geometric influence

Status: Accepted
Date: 2026-10-08

## Context

ADR-0050 correctly prevents whole-model nearest-surface matching by restricting correspondence to a local interaction region.

However, a local region that is defined only from the original residual target patch can be too small.

An added finite bead has width, end caps, seam-gap boundaries, and overlap with neighboring structural material. Candidate material may alter the exposed predicted surface outside the original residual patch.

If that changed surface lies outside the scoring domain, the optimizer could improve the target patch while creating unmeasured overbuild or distortion immediately next to it.

This is a false-negative error metric: the candidate affects geometry that the metric never evaluates.

## Decision

Every candidate set must have a deterministic AffectedSurfaceDomain that is closed under the candidate's finite geometric influence.

### Candidate-induced change set

Let:
- P0 = baseline exposed nominal material surface without the candidate set;
- P1 = completed FinalSurfaceEnvelope with the candidate set.

Define the candidate-induced affected material/surface set as the local region where P1 differs from P0, including exposed surfaces created, removed, occluded, or displaced by candidate bead union.

The implementation may compute a conservative superset rather than an exact Boolean symmetric difference, but it MUST NOT compute a subset that can exclude changed exposed material.

### Source correspondence halo

Build the permitted source correspondence domain from:
- the original residual target source patch;
- every source-surface patch within the conservative candidate influence volume;
- a neighborhood expansion sufficient for the configured maximum correspondence distance, quantization uncertainty, and numerical tolerance.

The geometric influence volume must conservatively contain the candidate NominalBeadSolidV1 union plus the configured correspondence neighborhood.

Do not use one arbitrary fixed XY radius when the actual candidate width/end geometry is larger.

### Closure requirement

Hard invariant:

Every exposed predicted surface point whose existence/position can be changed by the candidate must either:
1. have a valid correspondence inside the AffectedSurfaceDomain under ADR-0050 policy; or
2. make the candidate unresolved/non-injectable.

No candidate-generated/modified exposed material may fall outside the scored domain and be silently ignored.

### Neighbor-surface interaction

If candidate influence reaches a neighboring source surface/patch:
- include that neighboring source geometry in the affected correspondence domain when the topology/material-side relationship is unambiguous;
- evaluate whether error there worsens;
- if correspondence becomes ambiguous between competing nearby surfaces, reject the candidate rather than choosing the more favorable surface.

### Bidirectional scoring

ADR-0047 bidirectional metrics apply over the expanded AffectedSurfaceDomain.

Source -> predicted sampling includes:
- the intended residual target patch;
- any neighboring source surface inside the candidate influence domain that could be occluded/overbuilt/undercovered by the candidate.

Predicted -> source sampling includes all candidate-affected exposed predicted surface.

### No hidden collateral regression

A candidate is infeasible if it meets the target-region tolerance but causes any hard metric in the affected neighboring domain to exceed its allowed tolerance or configured regression budget.

Optional optimization cost may permit tiny non-hard regressions only when explicitly configured, fingerprinted, and still inside hard limits.

## Required settings / derived values

SurfaceCorrespondencePolicy gains or derives:
- candidate_influence_expansion_policy_version;
- affected_domain_numeric_tolerance_mm;
- optional max_neighbor_error_regression_mm;
- correspondence/domain convergence version.

Where possible, influence expansion is derived from candidate solid geometry and max_surface_correspondence_distance_mm rather than an unrelated user radius.

All policy values participate in PluginSettingsFingerprint.

## Requirements / invariants introduced

- Error scoring is local but closed under candidate influence.
- Candidate material cannot escape the scored domain.
- Nearby-surface collateral overbuild cannot be hidden by region partitioning.
- Ambiguous neighboring correspondence fails closed.
- Whole-model unrestricted nearest-neighbor matching remains forbidden.

## Alternatives considered

- Score only the originally detected residual patch: rejected because candidate bead width/end effects extend beyond it.
- Score the entire model globally: rejected because opposite/nearby surfaces can create false correspondences and unnecessary cost.
- Ignore neighboring regression if the target patch improves: rejected for dimensional correctness.

## Safety / quality impact

High for geometry correctness. Prevents locally optimized candidates from damaging adjacent surface geometry without being measured.

## Compatibility impact

May reject candidates near close neighboring surfaces that older local scoring would have accepted.

## Performance / resource impact

Requires local BVH/spatial queries and potentially a larger but still bounded scoring domain.

Use candidate-solid bounding volumes to keep the domain local and deterministic.

## Observability impact

Report:
- original target-region id;
- affected source patch ids;
- candidate influence bounds;
- max neighboring error regression;
- ambiguity/rejection reason.

## Test / validation impact

Add:
- candidate improves target but bulges into adjacent coplanar patch -> regression detected;
- candidate near second close surface with ambiguous correspondence -> reject;
- candidate effect entirely inside target patch -> unchanged result;
- wide bead/end cap crossing original patch boundary -> expanded scoring domain;
- influence-domain expansion independent of arbitrary mesh triangle partitioning;
- bidirectional metrics cover every candidate-affected exposed surface.

## Migration / rollout

ADR-0050 remains authoritative for local correspondence rules.

This ADR adds the closure rule that defines how large the local interaction domain must be.

## Rollback / disable condition

If candidate influence cannot be bounded/matched without ambiguity, candidate is non-injectable.

## Open questions

Efficient exact affected-surface extraction may evolve; conservative supersets are acceptable if deterministic and not less safe.