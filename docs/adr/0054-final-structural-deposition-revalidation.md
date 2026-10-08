# ADR-0054: Revalidate candidate support and hard surface constraints against final structural deposition

Status: Accepted
Date: 2026-10-02

## Context

Planning occurs at `posSimplifyPath`, before Orca performs some final G-code representation changes.

Most representation changes are harmless for geometry identity, but normal seam processing is materially relevant:
- final outer-wall seam/start is chosen later;
- `seam_gap` clips a contiguous portion of the structural loop;
- final XYZ is formatter-quantized;
- line subdivision changes;
- final local feed may be modified by cooling/overhang/resonance logic.

The existing matcher already tolerates these representation changes when identifying the correct structural loop.

However, the **planning-time material envelope** can still be optimistic near a structural seam gap.

This matters in two ways:
1. a SubEdge candidate may rely on lower structural material that final G-code does not actually deposit at the seam gap;
2. final completed-surface error/support/collision metrics can differ from the pre-seam planning prediction.

Also, nearby inner-wall or other positive-E structural material can affect support/collision even though only the external surface is the error target.

## Decision

After unique final-G-code structural matching and before file mutation, construct a local `FinalStructuralDepositionContext` from the actual final G-code around every candidate interaction region.

It MUST include, as relevant:
- lower structural external wall;
- upper structural external/ZAA wall;
- nearby positive-E perimeter/material moves within the support/collision interaction distance;
- final seam-gap clipping;
- final quantized XYZ;
- final E/commanded-volume semantics available from the supported parser contract;
- final actual feed rates.

This context is a validation input only. It does not become a second optimizer.

## Final support revalidation

Rebuild the candidate ChronologicalSupportEnvelope using final lower structural deposition geometry.

Candidate support that existed only in the optimistic pre-seam closed-loop model is invalid.

If final seam clipping / quantization removes required support:
- reject the affected candidate set;
- return Skipped;
- do not replan or move the candidate in postprocess.

## Final hard geometry revalidation

The immutable plan stores enough target surface-band/reference geometry to re-evaluate hard execution validity after final structural deposition is known.

At minimum re-check:
- minimum effective bead height;
- support overlap/contact;
- candidate-vs-structural finite-bead overbuild hard limits;
- candidate crossing/clearance invariants affected by final deposition;
- hard requested tolerance if the final structural difference materially changes the candidate region.

Execution-validated metrics MAY be stored in the per-attempt status record, but MUST NOT mutate the immutable plan's predicted metrics.

## Nearby structural material

The planning/validation material context is not limited to the external perimeter when another already-printed positive-E structural path lies within the physical support/collision interaction region.

External perimeter remains the surface-error reference path, but nearby inner/perimeter material may:
- provide real support;
- be a collision obstacle;
- affect bead overlap.

The exact included roles are versioned and tested.

## Final actual feed as a mandatory speed ceiling

Orca may alter final wall feed after path generation through:
- cooling slowdown;
- overhang/local speed processing;
- resonance-related logic;
- other supported final speed transforms.

Therefore candidate speed for printable v1 MUST NOT exceed the minimum relevant **actual matched final-G-code structural external-wall feed** in the target neighborhood, in addition to:
- configured/resolved outer-wall speed;
- filament max-volumetric-speed limit;
- optional lower plugin cap.

If no representative matched final feed can be established, injection is disabled.

## Requirements / invariants introduced

- Planning-time structural envelopes are provisional until final G-code deposition parity validation.
- Seam-gap matching alone is insufficient; support/material validity is rechecked against the actual deposited gap.
- Final validation may accept/reject only; it may not re-optimize.
- External-surface metrics and local support/collision material roles are explicitly separated.
- Final matched wall feed is a mandatory candidate speed upper bound for physical v1.

## Alternatives considered

- Require seam_gap=0: rejected; Orca default is nonzero and seam geometry is already parseable.
- Ignore final seam gap: rejected as unsafe for support.
- Re-run the optimizer in postprocess: rejected; violates immutable-plan contract.
- Model only external wall material: rejected for local support/collision correctness.

## Safety impact

Critical for support validity near structural seams and High for execution-speed parity.

## Compatibility impact

Requires final G-code fixtures that expose the relevant structural deposition and feed semantics.

## Performance / resource impact

Adds local final-deposition reconstruction and finite-bead validation around planned candidates.

Keep it spatially bounded to candidate interaction regions.

## Observability impact

Record:
- planning-vs-final structural length/gap difference;
- support revalidation result;
- execution-validated hard-error summary;
- actual matched wall feed range;
- first rejecting structural feature if any.

## Test / validation impact

Add:
- lower-wall seam gap removes required candidate support -> reject;
- candidate far from seam remains valid;
- upper-wall seam changes final local error -> hard-tolerance revalidation;
- nearby inner wall participates in support/collision context;
- cooling-slowed matched wall feed caps candidate speed;
- no representative final feed -> reject.

## Migration / rollout

Update Specification, Error Model, Implementation, Plugin Requirements, Test Strategy, and Roadmap before geometry/G-code phases.

## Rollback / disable condition

Any inability to reconstruct the required final structural deposition context => Skipped.

## Open questions

Empirical bead geometry remains governed by later physical calibration.

Supersedes: any implication that successful shape matching alone proves planning-time structural material support remains valid.


## Renumbering note

Renumbered from accidental duplicate ADR-0034 during the 2026-10-08 audit. Decision content is otherwise retained.
