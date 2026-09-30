# ADR-0004: Rewrite the ZAA upper outer wall segment-by-segment

Status: Accepted
Date: 2026-09-30

## Context
ADR-0002 established that the original upper outer wall must have its extrusion reduced when intermediate passes are inserted.

Further source audit of ContourZ.cpp shows perimeter ZAA stores varying negative Z offsets along the original outer-wall path. Perimeters are prevented from positive Z adjustment, but may be lowered locally.

Therefore the upper outer wall may be non-planar:
Z_top = Z1 + d(s)

A single h_top = Z1-z_k and one uniform flow multiplier is not correct when d(s) varies.

## Decision
v1 keeps intermediate sub-edge passes at constant command Z per loop, but rewrites the original ZAA upper outer wall **per matched extrusion segment**.

For top-wall segment j:
- determine local/representative absolute top command Z from the matched ZAA G-code/path;
- h_top_j = Z_top_j - z_k;
- require h_top_j >= configured minimum printable height/clearance;
- compute target mm3_per_mm_j using that segment's original width and h_top_j;
- scale/rewrite that segment's relative E accordingly.

If any segment has insufficient remaining height, the candidate schedule is infeasible.

With ZAA disabled and planar upper wall, all h_top_j are identical and this reduces to ADR-0002's uniform case.

## Intermediate passes
Intermediate contours remain one common constant-Z schedule for the whole loop in v1.

This deliberately avoids local z_i(s) while still accommodating a non-planar ZAA top wall.

## Additional v1 eligibility gates
- never refine first printed layer;
- target path must be a simple matched external-wall loop whose G-code extrusion segments can be mapped deterministically;
- bridge-role target segments are rejected;
- target loop must satisfy support overlap checks;
- variable original segment width is allowed only if each segment's width/flow is available and matched; otherwise injection is disabled.

## Alternatives considered
- disable ZAA on outer walls: rejected because project goal is ZAA-first.
- require planar upper wall: rejected because it would remove much of ZAA interaction being studied.
- make all sub-edge Z values vary continuously with s: deferred; that approaches non-planar path generation and greatly complicates injection.

## Safety impact
Prevents local over-extrusion where ZAA lowers the original upper outer wall close to the highest sub-edge.

## Compatibility impact
Plan schema must describe per-segment upper-wall rewrite targets rather than one uniform loop flow.

## Test impact
Add:
- planar upper-wall rewrite case;
- synthetic varying-Z upper-wall segments;
- candidate rejection where min(Z_top_j-z_k) violates minimum;
- per-segment relative-E rewrite golden fixture.

Supersedes:
ADR-0002 only where it implied a uniform top-pass flow; the requirement to redistribute outer-wall extrusion remains.
