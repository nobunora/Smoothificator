# ADR-0002: Redistribute outer-wall extrusion across sub-edge passes

Status: Accepted
Date: 2026-09-30

## Context
The prior design treated sub-edges as purely additional material while leaving the original upper structural outer-wall extrusion unchanged.

That is physically inconsistent. Once an intermediate pass raises/supports the outer surface, the vertical gap available to the original upper outer-wall pass is reduced. Leaving its original layer-height flow unchanged can over-extrude and distort the surface.

Upstream Smoothificator already avoids this class of problem by dividing original outer-wall extrusion among smaller-height passes.

Orca Flow::mm3_per_mm models a non-bridge bead cross-section approximately as:

A = h * (w - h * (1 - pi/4))

## Decision
For every refined structural interval [Z0,Z1], Adaptive Sub-Edge v1 MUST treat the outer wall as a **pass schedule**, not as unchanged base wall plus extra material.

Let:
Z0 < z1 < ... < zk < Z1

Command-Z semantics:
- each Z is the nozzle/path command height (top of the nominal deposited pass);
- h1 = z1 - Z0;
- hi = zi - z(i-1);
- h_top = Z1 - zk.

Intermediate passes use their corresponding effective heights. The original outer-wall pass at Z1 remains geometrically at its Orca XY/Z path but its extrusion for the refined target must be adjusted to the remaining h_top.

For fixed width w, initial flow calculation SHOULD match Orca's rounded-rectangle cross-section formula. The optimizer/bead model may later vary width under a separate ADR.

## v1 simplification
v1 refines an entire matched outer-wall loop with one common Z schedule. Segment-local k(s)/z_i(s) is deferred.

This makes original-wall flow adjustment deterministic and avoids partial-loop E rewriting in the first printable implementation.

## Alternatives considered
- additive-only sub-edges: rejected due over-extrusion risk.
- remove original top wall entirely: rejected because it breaks structural-layer semantics and inner-wall integration.
- locally varying flow/height within one loop: deferred due G-code rewrite complexity.

## Safety impact
Major positive impact: avoids systematic excess material and zero/small nozzle gap at the upper structural outer wall.

## Compatibility impact
Injector must modify matched original outer-wall extrusion as well as insert intermediate passes.

For v1, relative extrusion mode is required in target intervals to make local E scaling tractable.

## Test impact
Add:
- volume/flow formula unit tests;
- upper-wall E rescaling golden tests;
- no-subedge plan preserves original E byte-for-byte;
- refined schedule has positive pass heights and correct total ordering.

## Migration
SubEdgePlan schema gains an OuterWallRewrite/WallPassSchedule description.

Supersedes: none.
