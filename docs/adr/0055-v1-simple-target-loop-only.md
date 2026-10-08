# ADR-0055: Restrict printable v1 to one simple target outer boundary per refined region

Status: Accepted
Date: 2026-10-08

## Context

A single ModelPart can still produce:
- several disconnected islands at one Z;
- holes / inner boundaries;
- several external loops with similar geometry.

The current matcher can reject ambiguous final-G-code matches, but the surface-band planner and support/error semantics would otherwise risk silently generalizing v1 beyond the roadmap's intended first proof.

Multiple loops/holes are explicitly a later controlled-expansion area.

## Decision

For printable v1, each refined target region/structural interval must resolve to exactly one simple external material boundary loop:
- no inner hole boundary participating in that target surface band;
- no disconnected competing target island in the refined region;
- no self-intersection;
- exactly one StructuralLoopReference for the target outer boundary.

Other unrelated geometry may exist only when it cannot enter the target-band/matcher/support decision and the one-object/one-volume v1 gates still hold.

If section topology is multi-loop/holed/ambiguous for the target region, analysis may continue but injection is disabled with a stable reason.

## Requirements / invariants introduced

- surface-band planner v1 operates on one simple target outer loop;
- final matcher must identify exactly that reference;
- multiple-loop/hole generalization requires a later ADR and dedicated fixtures.

## Test impact

Add:
- one simple loop accepted;
- annulus/hole target rejected;
- two target islands rejected;
- self-intersecting/ambiguous section rejected;
- unrelated remote geometry cannot silently become a second target.

## Safety impact

High for identity/support correctness.

## Supersedes

Any implication that one ModelPart automatically means one target loop.


## Renumbering note

Renumbered from accidental duplicate ADR-0035 during the 2026-10-08 audit. Decision content is otherwise retained.
