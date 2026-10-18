# Exact finite parameter-range spill certificate

Parent repository disposition validated for bounded tools geometry under current
SPEC12 / ADR0048 and finite-triangle-intersection-review.md. The single exact
finite triangle/rectangle intersection owner remains solve_triangle_rectangle.py.
Source-contour proposals can span a radius range and E-implied width range;
endpoint diagnostics alone are not a documented whole-range certificate.

Add a small pure tools-owned exact parameter-range bound function alongside the
existing finite intersection owner (or one focused audit module delegating it).
Inputs: exact finite triangle base/rise, its left world radius, center-radius
lower/upper, width lower/upper, rectangle bottom/top, explicit center/width bin
counts, max cells/coordinate bits and cancellation. Validate immutable exact
values, nonnegative ordered radii, positive ordered widths/heights, exact integer
budgets and exact bool cancellation. Resource/cancel outcomes are incomplete with
no acceptance bound; do not treat sampled endpoints as a fallback.

For each exact center interval [c0,c1] and width interval [w0,w1], every posed
rectangle contains the common horizontal subrectangle
[c1-w0/2-left_radius, c0+w0/2-left_radius] x [bottom,top]. If its horizontal interval
is empty its guaranteed intersection is0; otherwise delegate the authoritative
finite triangle intersection. Divide guaranteed intersection by w1*(top-bottom)
to obtain a lower bound on retained fraction. One minus it bounds spill from
above throughout that entire parameter cell. The maximum over a COMPLETE exact
partition bounds all supplied radii/widths. This is a sufficient bound, not an
exact maximum or optimality proof. Keep exact cell/provenance evidence and counts.

Allow degenerate parameter ranges (fixed center or fixed width) with one effective
interval; retain nondegenerate physical rectangle constraints. Whole-path callers
may tighten by providing a separate fixed E-implied width and exact radius
enclosure for each segment. Caller still owns association, source order, actual
geometry bounds and configured <=50% decision. No physical/print authority.

Test analytic full/absent/partial finite triangle cases, finite-base clipping,
width/radius intervals with exact interior checks, refinement tightening, invalid
types/limits and cancellation. Independently reproduce the floor3.8 decisions
and apply it to the near-limit floor3.2 repacked candidate: report true whole-range
upper bounds and every unresolved/over-limit result. Do not change placement or
the 50% rule to pass. Focused tests, primary and independent review required.
