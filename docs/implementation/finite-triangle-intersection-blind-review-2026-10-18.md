# Finite triangle intersection — independent blind review, 2026-10-18

## Independence and result

Reviewed docs/specs/finite-triangle-intersection-review.md, the complete new finite_triangle_rectangle_intersection_area function and existing solver/packing paths in tools/solve_triangle_rectangle.py, the posed_intersection_area wrapper/import in tools/build_triangle_rectangle_review.py, tests/unit/test_finite_triangle_intersection.py, and the retained planner containment guard. Did not consult parent or implementation findings for this corrective stage. Earlier independently established finite-area diagnosis is acknowledged; this report separately verifies the supplied correction. No code/test/artifact changes or printer operations; only this report written.

No actionable material defect found. The bounded exact-area extension satisfies the supplied contract; it does not expand the admitted planner domain or create physical authority.

## Mathematical and integration coverage

The function validates exact Fraction arguments, positive base/rise, and strict rectangle extents before division. It clips X to [0,base] and Y to [0,rise], returning exact zero for empty clipped extents. Over the remaining rectangle it integrates max(0,min(top,slope*x)-bottom): a rising portion between bottom/slope and top/slope, then a flat top-bottom portion. These intervals are correctly intersected with clipped X, so no horizontal extrapolation, negative area or contribution below the floor/beyond rise is admitted. All arithmetic is exact rational; no epsilon, sampling, floating branch or external dependency is involved.

The wrapper preserves signature and delegates to the sole finite-area owner with top=bottom+height. Existing spill_area remains the optimizer's contained-domain integral; neither lattice coordinates nor solver feasibility was broadened. The executable-ring planner still explicitly requires 0<=a<b<=base. Thus the previously diagnosed outward ring remains outside emission admission even though its exact research area can now be evaluated.

All four exterior sides, both negative/positive disjoint rectangles, boundary-only slope/floor/right/rise contact, rectangles covering the whole triangle, negative bottom/left, above-rise top and contained legacy behavior were inspected. Degenerate/reversed extents and nonexact Python numeric/string/bool inputs reject. Exact ring25 clipping reproduces finite spill 61993776587/150685429950 (~41.14119%), versus legacy extrapolation 45253668587/150685429950 (~30.03188%). Both being below50% does not bypass the unchanged planner guard or any geometry/physical gate.

## Executed validation

Exact repository `.venv` Python3.12.10, previously verified in this independent session.

- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_finite_triangle_intersection -v`: exit0, all6 tests pass (0.115 seconds). Includes independent exact polygon clipping/shoelace oracle over240 external rational cases, contained legacy equivalence, malformed input and actual ring25 witness.
- Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -`: exit0. Independently checked500 deterministic rational rectangles over varying triangles, with exact nonnegative/rectangle/triangle area bounds, additivity on independent X and Y half-partitions, and anisotropic scaling by2 in X/3 in Y multiplying area by6.
- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_executable_ring_intents -q`: exit0, all8 tests pass (10.086 seconds), exercising the delegated wrapper against the full unchanged30-ring fixture, composer agreement and retained rejection gates.

## Residuals

This establishes finite ideal-triangle/axis-aligned-rectangle area, not actual nominal rounded-bead area, support, future-layer interaction, signed material side, error-domain completeness or tool clearance. A later lateral-spill search extension requires its own adjudicated placement/search contract and downstream checks; this correction alone authorizes none. Exact Fraction operation cost grows with input integer size; this small pure helper has no independent cancellation/resource contract and introduces no broad search. Parent owns architecture/full regression gates beyond the focused independent checks. No findings require disposition; no printing or production convergence declared.
