# Exact finite triangle intersection for posed rectangles

Parent-validated contract: `docs/specs/finite-triangle-intersection-review.md`.
This stage extends only the exact intersection owner and its existing wrapper;
it does not admit outward candidates or expand the packing search domain.

## Changes

- `tools/solve_triangle_rectangle.py`: added authoritative
  `finite_triangle_rectangle_intersection_area` for triangle vertices
  (0,0),(base,0),(base,rise) and arbitrary nondegenerate rational axis rectangles.
  Validate exact Fraction types, positive triangle dimensions and ordered
  rectangle extents. Clip X to [0,base] and Y to [0,rise]; integrate the rising
  triangle portion then the constant clipped rectangle-height portion. Return
  exact zero for disjoint or boundary-only intersection. No floating arithmetic.
- `tools/build_triangle_rectangle_review.py`: existing
  `posed_intersection_area(base,rise,rectangle,bottom)` delegates to the owner,
  preserving its signature. No duplicated area formula remains in that wrapper.
- `tests/unit/test_finite_triangle_intersection.py`: six meaningful tests cover
  all four external sides, floor/negative left, beyond-rise top, whole-triangle
  coverage, disjoint/boundary contact, interior legacy equivalence, malformed
  exact inputs and the actual outward ring25 case. An independent exact
  Sutherland-Hodgman/shoelace oracle validates 120 rational rectangles.

The original `spill_area` optimizer arithmetic remains unchanged in its existing
contained domain. Numeric-intent lateral containment, packing optimizer, source
association, support, parser and physical gates are unchanged. No new dependency
or artifact mutation. Existing dirty work and `log_iotc.txt` preserved.

## Exact actual ring25 evidence

Read original pinned review manifest; shift its radius outward by 1/25 mm,
retain width55449/220000 mm, set physical height9/50 mm and remaining63/500 mm.
Relative source triangle and posed rectangle:

- base549/1000, rise1/5;
- left74131/220000, right589/1000 (right excess1/25);
- bottom-27/500, top63/500.

Legacy extrapolated-half-plane spill:
`45253668587/150685429950` = approximately30.0318807213%.
Finite-triangle spill:
`61993776587/150685429950` = approximately41.1411883734%.
The new owner equals the independent polygon-clipping oracle exactly; the
existing wrapper returns that same finite intersection. This confirms the area
rule for the example but does not bypass current containment or emission gates.

## Executed checks

Required interpreter: `.venv\Scripts\python.exe`, Python3.12.10.

1. `& .\.venv\Scripts\python.exe -m py_compile tools/solve_triangle_rectangle.py tools/build_triangle_rectangle_review.py tests/unit/test_finite_triangle_intersection.py`
   -> PASS, exit0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_finite_triangle_intersection tests.unit.test_triangle_rectangle_review tests.unit.test_executable_ring_intents -q`
   -> PASS,28 tests,exit0 (33.227s).

Parent requested syntax and focused checks while review settles; no full suite,
build, dependency installation or physical printing performed. No commit/push/
merge/release. Ready for parent and independent review before any later domain
expansion. Physical printing remains unauthorized and uncertified.
