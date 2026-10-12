# ADR-0016: Match structural loops independently of seam start and normal seam-gap clipping

Status: Accepted
Date: 2026-09-30

## Context

The geometry analyzer observes simplified extrusion loops at `posSimplifyPath`.

Before final G-code emission, Orca `GCode::extrude_loop()` may:
- choose a seam and split/reorder the closed loop at that seam;
- clip the loop end by configured `seam_gap`;
- subdivide segments during speed/overhang processing;
- emit wipe travel.

The audited Orca default `seam_gap` is 10%, so exact ordered-point hashes from `posSimplifyPath` are not stable final-G-code identifiers.

Scarf/sloped seam and arc fitting remain unsupported by v1.

## Decision

Do not use ordered raw-point equality as the authoritative final-G-code match.

The analyzer stores a `StructuralLoopReference` containing:
- closed simplified loop geometry in print-space;
- length and bounding geometry;
- orientation/winding where reliable;
- stable geometry hash based on canonicalized closed shape;
- representative non-collinear anchor samples;
- expected seam-gap configuration and tolerance.

At postprocess, the matcher reconstructs the positive-E external-wall deposition polyline from the supported final G-code and validates it against the plan reference while allowing:
- cyclic change of starting point;
- seam split;
- collinear subdivision;
- one contiguous missing tail interval consistent with configured seam-gap amount plus G-code quantization tolerance.

It MUST reject:
- multiple unexplained missing intervals;
- geometry outside distance tolerance;
- inconsistent scale/rotation/shear;
- ambiguous matches to more than one structural loop.

Role/comments may strengthen matching but MUST NOT be the only geometric evidence.

## Requirements / invariants introduced

- `seam_gap` and relevant seam-mode settings participate in the execution config fingerprint.
- Scarf/seam-slope remains disabled.
- Arc fitting remains disabled for injectable v1.
- Matcher derives execution-frame translation only from a successfully matched structural geometry reference.

## Alternatives considered

- Require seam_gap=0: rejected because the normal Orca default is 10% and the gap can be modeled safely.
- Match only comments/layer number: rejected as insufficiently specific.
- Match raw path hash: rejected because seam processing changes representation.

## Safety impact

High. Prevents false mismatch and, more importantly, false positive path identity.

## Compatibility impact

Requires a geometry-aware matcher before physical injection.

## Performance / resource impact

Bounded shape matching within the one-object v1 scope.

## Observability impact

Record match error, matched length ratio, expected seam-gap allowance, and number of candidate matches.

## Test / validation impact

Fixtures:
- same loop with rotated start;
- seam-gap clip;
- collinear subdivision;
- translated G-code coordinates;
- wrong geometry rejection;
- ambiguous near-identical loop rejection.

## Migration / rollout

Replace raw-loop fingerprint language in InsertionAnchor/PlanMatcher specifications.

## Rollback / disable condition

Any ambiguous structural-loop match returns Skipped.

## Open questions

More complex multiple-loop/hole disambiguation is deferred.

Supersedes: any earlier requirement implying ordered point-for-point final-G-code loop equality.
