# Tilted cuboid: replace fixed probes with constrained rectangles

Historical milestone. Current dimensions, maximum line width and split-line
behavior are recorded in `rectangle-line-tiling-2026-10-17.md`.

User clarification: interpolate the entire series of stair-step errors after
tilting the model 10 degrees; do not blanket-hatch the top or trim unsupported
pieces from a fixed probe and present the remainder as a solution.

## Previous method and rejected assumptions

The initial experiment placed one fixed 0.34 x 0.19 mm cross-section per riser,
with center top on the target plane and a 0.02 mm XY separation from higher
source footprints. It then clipped X intervals according to central-strip
nominal/diamond support bounds. This neither optimized error fill nor kept
the entire cross-section below the target. The 153-fragment native scene is
superseded. Its green Custom paths are not accepted interpolation results.

## Current research implementation

`tools/solve_step_rectangles.py` solves the maximum-area axis-aligned rectangle
in a section with a flat current floor and an affine rising target. With
target `z=m*y+c`, floor `s`, section `[a,b]`, and rectangle `[l,b]`, it maximizes
`(b-l)*min(h_max,m*l+c-s)` subject to minimum width and height. For any given
height, right alignment maximizes width. The piecewise quadratic objective
is solved exactly with Fractions at endpoints, the quadratic stationary
point, and the maximum-height breakpoint. No sampled grid claims optimality.

After insertion, the section is split into the unchanged left remainder and
the raised-floor right remainder. The largest next rectangle is solved again.
This supports multiple rows and tiers; it is a greedy sequence of exact local
maxima, not a proof of optimal global packing or complete error removal.
Every remaining section is retained. Minimum dimensions can leave residuals.

`tools/build_tilted_cuboid_review.py` now uses this solver in its default path.
Fixed width/height, center-plane placement, artificial 0.02-mm separation and
support-based X clipping have been removed. A 2D rectangle would still need
continuous contact over the whole X length before being displayed. Failed
3D support requires reconstruction rather than emitting trimmed fragments.
There is no claim that this extra gate solves the general 3D support problem.
Nominal contact over a central flat band is not full-width stadium contact.

The 2D staircase adapter uses source command Z as each flat terrace floor and
conservative higher-source XY bounding boxes as section boundaries. **This is
an explicit approximation, not the exact 3D stadium upper envelope.** Its
positive and negative outcomes must not be promoted to general 3D existence
or nonexistence proofs. Full 3D support-aware optimization remains unfinished.
No production engine, injector or printer authorization contract is changed.

## Current fixture result

The actual 20 x 12 x 3 mm mesh is rotated +10 degrees around X before slicing.
Offline Orca uses `--orient 0 --arrange 0 --export-3mf sliced.3mf`; its exported
mesh and build transform establish the real placed target plane, rather than
assuming a plate offset. Original source: 6,071 extrusions, 25 layers.
One 0.4-mm-Z gap-infill segment has width below height; it is retained in the
viewer and excluded from top queries only because its Z ceiling is strictly
below every top-contact plane. No original extrusion geometry is clipped.

Current research defaults, pending optional user clarification:
minimum width 0.34 mm, minimum height 0.08 mm, maximum height 0.32 mm.
These are inherited experimental values, not calibrated printer settings.

For the ten interior flat-terrace sections, the maximum residual at the upper
boundary is approximately 0.100 mm. Across width 0.34 mm, the target rises
approximately `0.34*tan(10deg)=0.059951` mm. The largest height at that minimum
width is consequently approximately 0.040 mm, below 0.08 mm. All ten sections
have no feasible rectangle **in this 2D approximation**. No Custom candidate
is emitted. This does not prove that every actual bead valley lacks a 3D
solution. It does establish why center-plane fixed probes were misleading.

Current manifest: `artifacts/cuboid-tilt10-review/current-review.json`.
It records source/model/viewer hashes, exact target plane, constraints and
each section's maximum feasible height. The current G-code contains the
complete baseline only, with explicit UNVERIFIED_VIEW_ONLY labelling. Original
Orca supports/brim can still be green by native category; green is not validity.

## Verification and limitations

Python 3.12.10. No added dependency. Compileall passes. Architecture 43 tests
and focused 24 tests pass. Tests include analytic global rectangle optimum,
height/width constraints, equality boundaries, multiple supported insertions,
positive-but-infeasible residuals, whole-line support failure without clipping,
actual 10-degree placed mesh, 25-layer retained baseline and source SHA checks.
Final full regression: `python -m unittest discover -s tests -p 'test_*.py' -q`
passes all 682 tests (see `artifacts/cuboid-tilt10-review/full-tests.log`).
Final syntax, architecture and focused checks pass; `git diff --check` passes.

A byte-identity regression found Windows text writes changing LF to CRLF while
the viewer hash described LF. The tilted generator now writes exact ASCII
bytes and verifies the file's actual bytes in the local integration test.
The intermediate opened viewer was preserved; the corrected current viewer
was written under a new unique name.

No print, printer connection, printable output, merge, release or staging of
`log_iotc.txt`. Lint/type tools remain NOT CONFIGURED. The remaining task is an
actual 3D residual/support-constrained solver; the 2D rectangle solver is a
research foundation and must not be reported as that task's completion.

Native Orca is left open with the final baseline-only rectangle-result scene
`cuboid-tilt10-steps-5d8ee7d1a8ef4e48848819a91c6260f6.UNVERIFIED_VIEW_ONLY.gcode`.
Its 25-layer Preview legend contains no Custom category. Original supports
remain green. A process-identity-checked PrintWindow capture was opened and
inspected: `artifacts/cuboid-tilt10-review/orca-rectangle-result.png`.
