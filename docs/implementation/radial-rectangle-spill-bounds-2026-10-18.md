# Exact whole-parameter radial rectangle spill bounds

Implemented parent-validated `docs/specs/radial-rectangle-spill-bounds-review.md`
as a pure tools audit. `tools/audit_radial_rectangle_spill.py` partitions exact
radius/width intervals, constructs the horizontal subrectangle common to every
posed rectangle in each cell, and delegates intersection to the existing single
finite-triangle area owner. The largest cell spill upper bound is available only
after complete coverage. Frozen reports retain all input/resource parameters and
exact cell intervals, common rectangle, retained area, maximum area and bound.
Fixed parameter ranges use one effective bin. Resource/cancellation outcomes are
incomplete with no acceptance bound. Caller owns actual geometry association,
chronology, configured50% decision and all physical validation.

Changed files: the new audit module, `tests/unit/test_radial_rectangle_spill.py`,
this record, and new `artifacts/radial-rectangle-spill-review/` reproduction/evidence.
The finite-area owner itself, conditional-copy files, source, parser, planner,
profiles and prior artifacts are unchanged. No alternate clipping math or sampled
endpoint fallback was introduced.

Actual source SHA256 is pinned to
`fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`.
The reproduction pins both candidate input content hashes and section-manifest
hash, computes exact whole-segment radius enclosures about declared XY90,90 with
128-bit outward square-root bounds, and preserves all exact cell certificates in
`whole-range-cells.UNVERIFIED.jsonl`. Summary and evidence hash are in
`whole-range-summary.UNVERIFIED.json`.

| Floor/lane | Whole-range spill upper bound (display) |
| --- | ---: |
|3.8 inner, entire radius/width range,32center bins|0.4111961220199645|
|3.8 outer, entire radius/width range,32center bins|0.3160289791840106|
|3.2 ring9,192segments ×32center bins, fixed actual E-width per segment|0.49663343588978237|
|3.2 ring10, same partition|0.4540376980722843|
|3.2 ring11, same partition|0.3159687240294638|
|3.2 ring12, same partition|0.30007930285155304|
|3.2 ring13, same partition|0.3230550956444422|

Every decision compares exact fractions to1/2; display floats are not used for
acceptance. All seven complete lane bounds satisfy the declared criterion.
No unresolved/over-limit result is omitted (summary list is empty). These match
the independent prior audit, including near-limit ring9. They are sufficient
upper bounds, not exact maxima,3D bead error or physical tool clearance. Existing
candidate quality limitations and all physical/print-false flags remain.

All commands used required `.venv\Scripts\python.exe`, Python3.12.10:

- `-m py_compile tools/audit_radial_rectangle_spill.py tests/unit/test_radial_rectangle_spill.py artifacts/radial-rectangle-spill-review/reproduce.py`: PASS,exit0.
- `-m unittest discover -s tests/architecture -q`:45PASS,4.205s,exit0.
- `-m unittest tests.unit.test_radial_rectangle_spill tests.unit.test_finite_triangle_intersection -q`:10PASS,0.082s,exit0.
- `artifacts/radial-rectangle-spill-review/reproduce.py`:PASS,exit0; complete actual evidence above.

Tests cover analytic full/absent/partial/finite-clipped cases, exact interior
checks across every radius/width cell, refinement tightening, immutable report,
empty common interval, fixed ranges, invalid types/limits and cancellation before
and during coverage. Full suite held for parent integration/review. No dependency,
printer connection, printing, commit/push/merge/release; unrelated dirty work and
`log_iotc.txt` preserved. New module/tests/evidence ready for primary/blind review.
