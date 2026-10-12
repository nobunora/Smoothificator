# ADR-0003: Model added material and structural beads together

Status: Accepted
Date: 2026-09-29

## Context
A naive implementation can place geometrically correct intermediate paths but still over-extrude because:
- added beads have finite width/height;
- they overlap lower/upper structural outer-wall beads;
- the next structural layer remains in Orca's original G-code and retains its original extrusion;
- a sub-edge is additional material, not a replacement layer.

Therefore optimizing only centerline Z/XY is insufficient.

## Decision
The optimizer scores the **final combined surface** consisting of:
- lower structural/post-ZAA bead geometry;
- every candidate sub-edge bead;
- upper structural/post-ZAA bead geometry that Orca will still print.

Sub-edge flow is part of the candidate definition.

For a normal non-bridge bead, use Orca's rounded-rectangle cross-section as the initial physical model:

A = h * (w - h * (1 - pi/4))

which is Orca `Flow::mm3_per_mm()` for width w and height h.

A candidate is infeasible if its required geometry/flow cannot be represented within calibrated printable width/height/flow limits.

The engine MUST NOT assume that simply adding a full standard outer-wall bead is correct.

## Flow ownership
The geometry engine determines target bead width/height/volume-per-length assumptions. The G-code emitter only converts the accepted `mm3_per_mm` into filament E.

## Z spacing
Nominal layer interval bounds are only search bounds.

When ZAA creates locally varying structural path heights, support/clearance constraints MUST be evaluated against the local finite-bead envelopes, not only against nominal `Z0` and `Z1`.

## Safety impact
Prevents systematic overfill and invalid clearance assumptions.

## Test impact
Add:
- overlap/overfill regression tests;
- upper-structural-bead inclusion tests;
- Orca Flow formula parity tests;
- infeasible low/high-flow candidate tests once calibration bounds are defined.
