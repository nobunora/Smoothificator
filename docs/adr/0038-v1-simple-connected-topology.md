# ADR-0038: Restrict printable v1 to one connected shell and simple target cross-sections

Status: Accepted
Date: 2026-10-02

## Context

The existing v1 source gate requires:
- one PrintObject;
- one total ModelInstance;
- one positive ModelPart volume;
- finite/manifold/oriented geometry.

A single manifold ModelPart can still contain:
- multiple disconnected closed shells;
- cross-sections with several disjoint outer loops;
- holes/inner loops.

The current Roadmap intentionally defers:
- holes/multiple loops;
- broader topology;
- multi-component matching.

Allowing those shapes implicitly in v1 would create ambiguity in:
- material-side surface-band selection;
- candidate support;
- structural-loop matching;
- seam/gap correspondence;
- final execution-frame references.

## Decision

Printable v1 source geometry MUST contain exactly one connected closed triangle shell after the validated centered transform/orientation view.

For every candidate target interval / required section used by the printable planner:
- the relevant target section is one simple closed outer boundary;
- no inner-hole loop participates in that target interaction region;
- no second disconnected target boundary is present in the same interaction region;
- the section graph has no branch, self-intersection, or ambiguity.

A model may contain geometrically complex curvature, but target topology remains simple.

Unsupported topology is analysis-only and receives a stable reason code.

## Requirements / invariants introduced

- "one ModelPart" is not treated as equivalent to "one connected shell".
- Connected-component count is validated explicitly.
- Target section topology is validated before centerline planning.
- StructuralLoopReference for printable v1 maps to one unambiguous target external loop.

## Alternatives considered

- Allow multiple connected components and rely on final matcher ambiguity checks: rejected; geometry optimizer/support logic would already be ambiguous earlier.
- Support outer + hole loops immediately: deferred by roadmap.
- Auto-select the largest component: rejected; would silently ignore source material.

## Safety impact

High for preventing wrong-surface path generation/matching.

## Compatibility impact

Narrower printable scope; still sufficient for simple calibration coupons and initial proof models.

## Performance / resource impact

One connected-component/topology check.

## Observability impact

Report:
- connected shell count;
- candidate section loop count;
- branch/self-intersection reason.

## Test / validation impact

Add:
- single closed shell accepted;
- two disconnected closed shells reject;
- annulus/hole target section reject;
- two disjoint section loops reject;
- branched/ambiguous section reject;
- simple curved single-loop section accepted.

## Migration / rollout

Update source topology gates, tests, handoff DTO/reason taxonomy, and roadmap language.

## Rollback / disable condition

Unsupported topology => analysis-only / Skipped.

## Open questions

Multiple loops/holes remain a later explicit expansion phase.

Supersedes: any implication that one manifold ModelPart alone fully defines printable v1 topology.
