# ZAA Integration Strategy

## Role
ZAA is the low-cost first optimizer.

Adaptive Sub-Edge addresses only residual error that remains after actual Orca toolpath generation/simplification.

## Hook
Analyze at posSimplifyPath.

This works whether ZAA was active or not and sees geometry after simplify_extrusion_path().

## ZAA data semantics
ContourZ stores path-point Z as offset d, not absolute Z.

Normalize:
z_abs = layer.print_z + d

For non-ironing ZAA, Orca G-code scales extrusion:
q_eff = q_nominal * (h_nominal + d) / h_nominal

Baseline prediction must reproduce both Z and flow behavior.

## Surface-relevant roles
Do not inspect outer walls only.

ZAA also affects exposed top-solid paths; baseline prediction must include exposed roles that define the target slope.

Ironing and scarf/sloped seams are disabled in printable v1 to avoid ambiguous nonzero-Z semantics.

## Solution-space difference
ZAA:
- moves existing paths
- very low added time/material
- existing topology

Adaptive Sub-Edge:
- adds paths/material
- can use many independently positioned heights
- each candidate's physical bead height is determined relative to support
- can fill residual geometric bandwidth that existing paths cannot represent

## Success criterion
Not “beat ZAA everywhere.”

When ZAA remains above tolerance, improve error with less penalty than globally reducing structural layer height.

## Collision/order
Lower-to-higher path ordering is required.

Actual nozzle clearance still uses a finite nozzle envelope; small pairwise Z differences are allowed only when clearance passes.

## Benchmark
Normal / fine layer / ZAA-only / ZAA+SubEdge on:
1/5/10/15/20/25/30 degree coupons and smooth slope.
