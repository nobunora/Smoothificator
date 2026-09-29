# ZAA Integration Strategy

## Role
Orca ZAA/Z Contouring is the low-cost first optimizer. Adaptive Sub-Edge does not replace it.

## Actual baseline
Analysis occurs after Orca path simplification at posSimplifyPath.

The engine consumes the actual 3D extrusion paths. It records whether ZAA is enabled and whether non-planar contouring is observed; it does not assume every path was modified.

## Hybrid flow
baseline structural paths
-> ZAA where eligible
-> path simplification
-> finite-bead final-surface estimate
-> residual error
-> optional Sub-edge optimization

## Different solution spaces
ZAA:
- changes Z of existing paths
- minimal added path/time
- fixed existing topology

Sub-edge:
- can create additional surface contours/material
- independent candidate Z and flow
- higher potential quality ceiling
- costs time/material

## Success criterion
Not "beat ZAA everywhere".

Target:
When ZAA-only remains above tolerance, reduce error materially with less penalty than globally reducing layer height.

## Collision/order
Added non-crossing sub-edges are explicitly printed lower-Z first.

Candidate feasibility is still checked against local post-ZAA finite-bead envelopes because ZAA structural paths may vary in Z.

## Benchmark
1/5/10/15/20/25/30 degree coupons plus smooth slope.
Compare:
- normal
- fine conventional
- ZAA
- ZAA + Sub-edge

Measure error, roughness, time, material and failures.
