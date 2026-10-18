# Finite triangle intersection for posed rectangles

User permits a rectangle outside the triangle if its outside area is at most
half the rectangle area. Horizontal containment in the existing packing lattice
is a bounded search choice, not a replacement for that area rule. Independent
research finds the current posed-area formula extrapolates the sloped half-plane
when passed rectangles outside [0,base]. Existing admitted intents remain inside
that domain and are unaffected.

Repository disposition: validated for this tools-only exact area extension.
Implement one authoritative exact Fraction intersection function in
tools/solve_triangle_rectangle.py for triangle vertices (0,0),(base,0),(base,rise)
and any nondegenerate axis-aligned rectangle with arbitrary rational left/right
and bottom/top. Validate positive triangle dimensions, exact types and rectangle
extents; return exact finite intersection area. Clip against both finite
horizontal sides and the floor, not merely the sloped half-plane. No new deps.

Make build_triangle_rectangle_review.posed_intersection_area delegate to that
owner while preserving its signature. Keep the existing packing optimizer and
all numeric-intent containment, source, support and physical gates unchanged in
this stage. Do not silently admit the outward research candidate into emission.

Tests: interior legacy-equivalence, all four external sides, disjoint and
boundary-only contact, covering whole triangle, negative bottom/left, beyond-rise
top, malformed exact inputs; exact rational real ring25 outward example where
old extrapolation reports ~30.03188% but finite spill is ~41.14119%.
Parent and independent review required before any later search-domain expansion.
