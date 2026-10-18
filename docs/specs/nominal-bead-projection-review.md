# Exact outward projection bounds for nominal bead separation

Repository disposition: validated additive engine geometry API under SPEC 12 /
ADR0048. The independently checked actual source-offset fixture has 341 positive
separating-axis certificates. Reusable math belongs to the existing exact geometry
owner, not copied research scripts. No physical tool shape or contact policy changes.

Add a public projection-bound function to engine/support_cell.py and an immutable
domain result type. Input: ExactNominalTopSegment, a nonzero immutable exact
rational XYZ axis, explicit coordinate/sqrt-bit limits and cancellation. Reject
malformed inputs; resource/cancel outcomes carry no bounds. Use the existing
outward `_sqrt_bounds` owner. Never accept separation using floating arithmetic.

Derivation for the exact existing finite, flat-axial-cap stadium sweep:
let D=dx²+dy², q=(axis_x*dy-axis_y*dx)²/D, f=(width-height)/2, r=height/2.
Its cross-section support extent is f*sqrt(q)+r*sqrt(q+axis_z²).
The centerline endpoints are (x,y,command_z-height/2). Projection extrema are the
min/max endpoint dot products, expanded by an OUTWARD upper bound on the extent.
This is the support function of the same Minkowski segment + horizontal normal
flat + normal/vertical disc. It includes finite end caps and varying structural
command Z; it adds no XY capsule or endpoint volume.

The result bounds the whole solid on an unnormalized axis. Positive separation
of these outward intervals is a sufficient disjointness certificate; overlapping
intervals are inconclusive, never proof of overlap. Do not label an axis-dot
margin as millimetres of head clearance. No automatic physical authorization.

Tests: axis-aligned and oblique projections, reversed endpoints/axis scaling,
vertical and varying-Z extents, exact known cardinal values, rounded support
contribution, malformed/zero axis, resources/cancel. Recompute all 341 actual
nearby certificates through the new owner with source/project/candidate pins;
retain every unknown rather than hiding it. Source state/chronology and full
job/head validation remain caller-owned. No parser, planner, geometry candidate
or old overlap-auditor behavior changes. Independent review required.
