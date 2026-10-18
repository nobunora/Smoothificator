# Radial rectangle spill independent blind review

Date: 2026-10-18. Independent review against `radial-rectangle-spill-bounds-review.md`; no parent/implementation conclusions consulted. Reviewed the complete new audit function, direct tests, authoritative finite-intersection delegate and actual reproduction recipe/evidence. No source/tests/baseline artifacts changed.

Disposition: no material finding established for the bounded exact parameter-range certificate.

The formula is sufficient throughout each cell: every posed rectangle contains the common horizontal interval `[c1-w0/2-left,c0+w0/2-left]` at the same bottom/top. Intersecting that common rectangle with the finite triangle gives a retained-area lower bound. Every posed rectangle area is at most `w1*(top-bottom)`, so dividing the lower intersection by that maximum area gives a retained-fraction lower bound. Taking one minus and then the maximum over the complete Cartesian partition bounds spill globally. Empty common intervals correctly yield bound1. No endpoint-only acceptance or lateral containment assumption is introduced.

Verified exact rational partition endpoints, immutable report/cells, fixed-center/fixed-width effective bins, finite clipping on every side, positive physical rectangle dimensions, nonnegative ordered radii, exact int/bool input contracts, cell/coordinate-bit limits, early/mid/final cancellation and no global bound on incomplete outcomes. Refinement tightening is justified for nested partitions; arbitrary nonnested bin counts need not be interpreted as monotonic refinement. The implementation does not make that broader claim.

## Checks and actual evidence

Python: repository `.venv` 3.12.10. Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_radial_rectangle_spill tests.unit.test_finite_triangle_intersection -v` — PASS, 10 tests.

Additional read-only probes generated 200 deterministic rational parameter boxes and checked every returned cell at rational boundary/interior points against exact finite intersection. All sampled comparisons satisfied actual spill <= cell bound <= report bound; these checks supplement the whole-cell proof above.

Executed `artifacts/radial-rectangle-spill-review/reproduce.py` with only its two `Path.write_text` calls captured in memory (including Windows newline translation). Generated `whole-range-cells.UNVERIFIED.jsonl` and `whole-range-summary.UNVERIFIED.json` exactly matched existing bytes; no artifact was overwritten. This re-evaluated all 962 certificates / 30,784 cells. Source and candidate/manifest hashes matched. Actual decisions:

| Floor/lane | Whole-range upper spill bound (display) |
|---|---:|
|3.8 outer source-width .42|.4111961220199645|
|3.8 inner source-width .45|.3160289791840106|
|3.2 ring9|.49663343588978237|
|3.2 ring10|.4540376980722843|
|3.2 ring11|.3159687240294638|
|3.2 ring12|.30007930285155304|
|3.2 ring13|.3230550956444422|

All exact bounds are <=1/2, with no incomplete/over-limit certificate. The near-limit ring9 decision uses exact rational comparisons, not rounded displayed decimals. The floor3.8 certificates use whole-lane radius/width boxes; floor3.2 uses each fixed actual E-implied segment width with its outward exact radius enclosure. These reproduce the previous independent research bounds.

## Residuals and authority

This is a sufficient radial rectangle surrogate bound, not an exact maximum, 3D bead-error integral, placement optimum or whole-job acceptance. Callers still own source/frozen-E association, actual geometry/radius enclosure, chronology/contact, packing and configured decisions. Arbitrary caller budgets are explicit bounds, not a fixed wall-clock guarantee. No production gates, geometry selection, physical/runtime flags or print authority changed.
