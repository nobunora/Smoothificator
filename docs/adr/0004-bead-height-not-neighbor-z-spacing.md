# ADR-0004: Minimum 0.08 mm applies to deposited bead height, not neighbor Z difference

Status: Accepted
Date: 2026-09-29

## Context
Earlier drafts incorrectly required adjacent sub-edge Z values to differ by at least 0.08 mm.

Orca ZAA source shows the relevant physical quantity is local extrusion height above the lower support plane. For a layer with nominal height h and ZAA offset dz, Orca emits:
- absolute nozzle Z = nominal_z + dz
- extrusion scale = (h + dz) / h
so the effective local bead height is h + dz.

For a 0.20 mm structural interval, paths at +0.08, +0.115, +0.150, +0.185 mm above the lower support can each have printable bead heights even though neighboring Z differences are smaller than 0.08 mm. Such dense height progression may be necessary on shallow slopes to keep horizontal path spacing near extrusion width.

## Decision
The initial 0.08 mm constraint is **minimum effective deposited bead height above its supporting surface**, not a minimum pairwise Z difference.

For candidate path j:
h_eff,j = z_nozzle,j - z_support,j

Require:
h_min <= h_eff,j <= h_base_max

with h_min initially 0.08 mm for the 0.4 mm nozzle target.

No fixed lower bound is imposed on |z_i-z_j| between different non-crossing paths. Pairwise feasibility is decided by:
- finite bead overlap/overbuild
- nozzle envelope clearance
- support geometry
- path crossing
- machine Z resolution/quantization

## Initial support model
For the first simple nested-slope PoC, candidate paths are supported directly by the lower structural layer surface. The engine computes support height from the predicted lower structural bead envelope rather than blindly using nominal Z.

## Consequence
The optimizer can place multiple nearby-height paths across a shallow terrace, which was impossible under the old pairwise-0.08 rule.

## Test impact
- remove pairwise min-Z-spacing tests
- add minimum effective bead-height tests
- add shallow-slope path-spacing tests
- add nozzle-clearance tests for small neighbor Z differences
