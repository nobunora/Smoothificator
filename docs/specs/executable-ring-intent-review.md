# Quantization-aware ring intent preparation

Parent repository disposition: **validated for offline immutable research intent
preparation**, after separate investigation of the actual 30-ring fixture.
Canonical sources: SPECIFICATION sections 12–13, 23–24 and ADR-0017. Existing
physical, firmware, support, clearance and PlanStore gates remain unchanged.
Quality-error improvement is deferred by the user; this task addresses executable
numeric representability, not a new shape-improvement optimization.

## Problem and chosen bounded solution

Seven zero-overlap original rational heights round upward at XYZ3 and correctly
fail the existing fixed-height composer contract. Merely changing height fixes
that nominal mismatch but nearest E5 then produces 64 chords below min width.
Do not weaken overlap/width/remaining-height bounds, change nearest E rounding,
drop paths or widen packed rectangles without re-solving their placement.

The investigated solution retains all 30 circle radii and nominal widths:
planner quantizes top Z first and freezes the resulting intended physical
height. Rings2/3 can use every other existing endpoint (96 chords); others can
retain192. This makes all emitted E positive, implied widths legal, and actual
XY3 chord radial deviation below the declared0.002-mm review budget. Implement a
bounded deterministic search rather than special-casing those IDs.

## Inputs / association

Use the pinned original source/placed-project/manifest bytes. Verify source and
project hashes, exact embedded-source association and complete ring/chord graph.
Retain source manifest hash and explicit XYZ/E precision, geometry budget and
setting identities in frozen output. No guessed insertion anchors or physical
authority. Read current user width/remaining-height/overlap from manifest and
maximum height from saved layer-height90% cap. Use authoritative existing flow
arithmetic, not a parallel formula owner.

## Planner behavior

For each ring, first round intended top to the explicit nearest XYZ grid. Derive
new physical h from `(top-floor)/(1-overlap)`; preserve requested overlap in
0..30%. Validate h<=width, remaining minimum, physical min/max, next-layer ceiling
and the original per-rectangle radial spill<=50% contract against its source
triangle. If no legal intended grid height exists, reject the job explicitly;
never silently omit a ring or change overlap. Current zero-overlap fixture has
all30 legal nearest heights.

Try chord counts in descending order over divisors of the original closed
polyline count (>=3), selecting subsets of its existing9decimal endpoints,
including closure. Do not generate a different phase or fresh trigonometric
curve. Quantize XY to explicit grid, reject collapsed/zero-length segments,
and recompute lengths, nominal q_geom/q_cmd, nearest E at explicit precision.
Remove command-flow multipliers from quantized E-derived flow before deriving
effective geometric bead width using existing flow arithmetic. Every segment
must have positive E and width within current user bounds; no epsilon or ceil-E
override. Apply the existing volume-rate cap to actual quantized command flow.

Use exact rational squared-distance comparisons to prove every quantized center
segment remains within the radius±declared radial-deviation band: maximum norm
at endpoints, minimum norm at the clipped projection onto that segment. Floating
sqrt values may be reported as estimates only; acceptance uses squared bounds.
The first largest legal divisor is frozen with unchanged radius/nominal width.
If none is legal, reject with per-ring reasons, preserving all inputs.

## Output / verification

Publish frozen SupplementalPath objects and per-ring source/intent/emitted
diagnostics, plus unverified review JSON. Existing composer executes this intent
unchanged and must replay from synthetic declared anchors in tests; real-source
anchor eligibility remains separate. No original-file mutation or printer I/O.

Tests must distinguish original fixed-height failure, planner height correction,
nearest E min-width failure, deterministic legal divisor selection, exact radial
band rejection, unchanged30 paths/radii/nominal widths, source mismatch/graph
malformation, overlap/minheight/height cap/spill rejection, and positive bounded
emitted widths/flow on the actual full fixture. Use Python3.12.10, focused tests,
architecture, actual artifact receipt. Parent and independent audit follow.
