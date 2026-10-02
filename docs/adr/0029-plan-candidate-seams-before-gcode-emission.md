# ADR-0029: Make candidate SubEdge seam/gap part of the immutable plan

Status: Accepted
Date: 2026-09-30

## Context

A candidate SubEdge centerline may be a closed contour.

Emitting a mathematically closed extrusion loop without an intentional start/end policy can create a local seam blob/overlap.

Conversely, choosing a seam or clipping a gap only during G-code postprocess would change the material geometry after:
- optimization;
- finite-bead scoring;
- preview.

That violates the immutable-plan/same-preview contract.

## Decision

The geometry engine converts every printable candidate into an explicit **open execution path** before the immutable plan is finalized.

### Naturally open candidate

Preserve its planned endpoints.

### Closed candidate loop

The engine deterministically:
1. canonicalizes loop orientation;
2. selects a seam start from geometry using a versioned deterministic rule independent of machine translation;
3. resolves a candidate seam-gap length from validated plugin/settings policy;
4. clips that material interval from the candidate loop;
5. finite-bead prediction and error scoring use the resulting open path, including the gap.

Initial v1 seam policy SHOULD default to the resolved Orca external-wall seam-gap magnitude as a reference, but it is stored/validated as an explicit plugin plan setting and may be made more conservative through calibration.

The postprocessor MUST NOT move the candidate seam or change its gap to match Orca's structural seam.

## Requirements / invariants introduced

- Preview and injection show/use the same candidate seam/gap.
- `SubEdgePath` is an ordered open polyline at one constant command Z.
- Closed-source-loop metadata may be retained for diagnostics, but executable geometry is already open.
- Candidate seam-gap participates in PluginSettingsFingerprint and plan hash.
- Error metrics include the planned gap.

## Alternatives considered

- Fully close every candidate loop: rejected due seam over-extrusion risk.
- Choose seam at postprocess from final Orca seam: rejected because it changes the immutable plan.
- Require all candidates to be naturally open: rejected because arbitrary-Z contour bands may be closed.

## Safety impact

Medium/high for local material amount and deterministic plan execution.

## Compatibility impact

None beyond explicit seam policy.

## Performance / resource impact

Negligible.

## Observability impact

Preview marks candidate start/end and gap length.

## Test / validation impact

Add:
- deterministic seam selection under cyclic/reversed loop input;
- candidate gap included in surface error;
- translation does not change seam choice;
- short loop where requested gap is invalid -> candidate rejected;
- postprocessor cannot alter planned seam.

## Migration / rollout

Add seam policy/settings and explicit open-path DTO invariant before optimizer implementation.

## Rollback / disable condition

If a valid deterministic seam/gap cannot be produced, the closed candidate is non-injectable.

## Open questions

Future seam alignment/optimization with structural Orca seams may be evaluated separately.

Supersedes: none.
