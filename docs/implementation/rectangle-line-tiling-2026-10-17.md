# Updated rectangle constraints and exact line tiling

This record supersedes the dimensions/result in
`tilted-cuboid-rectangles-2026-10-17.md` for the current local review.

User constraints: minimum line width 0.25 mm, maximum line width 0.45 mm,
minimum height 0.05 mm, maximum height equal to configured slicer layer height
minus 10 percent. The fixture source CONFIG_BLOCK has `layer_height = 0.2`,
so the current maximum is exactly 0.18 mm. This is read from the actual source
configuration and multiplied by exact 9/10; it is not a fixed 0.18-mm constant
or a value inferred from the first-layer height. Missing/duplicate/nonpositive
settings and a maximum below the minimum height fail closed.

The maximum width limits each extrusion line, not the logical fill rectangle.
For logical width W, equal-width tiling is possible when an integer n satisfies
`n*0.25 <= W <= n*0.45`. Choose the smallest feasible n and set every line width
to exact `W/n`. Adjacent closed nominal intervals meet exactly and their union
is the rectangle: no padding, gaps or overlap in this rectangular abstraction.
For example, W=1 mm yields three lines of exact width 1/3 mm. W=0.46 mm is
infeasible: one line exceeds 0.45 and two lines are each below 0.25.

`largest_tiled_rectangle` optimizes over the union of n-line feasible-width
intervals; it does not choose an untileable logical width and then violate
minimum line width. For each n, the exact local maximum remains the extrema
of the piecewise quadratic area objective. The best area across all feasible
n is selected, with explicit resource bounds of 256 lines and 256 rectangles.
The greedy sequence of local maxima is not a global packing certificate.

`fill_tiled_section` updates the floor after each logical rectangle and solves
remaining sections again. `split_line_intervals` generates exact equal-width
nominal footprints. The viewer adapter gives all lines in a rectangle a shared
ID, line index/count, exact width, and the same solved height and top Z.

Every line is checked for continuous whole-X contact over its central flat
band before the complete group is admitted. Failed groups are not emitted
partially and cannot support subsequent rectangles. This is still an audit
gate, not a completed 3D support-aware optimizer. Rounded stadium beads do not
fill their entire bounding rectangles; exact nominal interval tiling does not
prove gap-free physical top coverage or safe nozzle motion.
Viewer coordinates/widths are rounded to nine decimal places; exact-tiling
claims refer to the rational plan, not bit-exact coverage by rendered beads.

## Actual tilted fixture

With the revised dimensions, each of the ten interior 2D sections has one
feasible logical rectangle (about 0.28 mm wide and 0.05 mm high); each needs
one line in this particular fixture. This is distinct from the tested wider
cases, where multiple lines are generated. The current nominal 3D whole-path
audit finds a gap for all ten groups, so none is admitted to the viewer.
These are 2D solutions with unresolved 3D reconstruction, not an assertion
that no other full-contact solution exists. No unsupported Custom paths are
shown, and no support-based X clipping is performed.

`artifacts/cuboid-tilt10-review/current-review.json` records the current file,
hashes, configured height/factor, all four limits, logical rectangles, exact
line partitions and failed whole-path contact evidence. The viewer contains
all 6,071 original extrusions and 25 layers. Source paths and model shape are
preserved. The 10-degree tilt is baked into the model before offline slicing.

## Validation

Python 3.12.10; no added dependencies. Tests cover exact line partitions and
boundary widths, non-divisible/infeasible widths, optimization over feasible
line counts, multiple-line actual adapter output on a supported synthetic
terrace, repeated rectangle insertion, configured height changes and malformed
settings. Final checks: compileall PASS; architecture 43 PASS; focused 32 PASS;
full unittest discovery 690 PASS. Logs are `architecture-tests.log`,
`focused-tests.log` and `full-tests.log` under `artifacts/cuboid-tilt10-review/`.
`git diff --check` passes; lint/type tools remain NOT CONFIGURED.

The already open Orca baseline scene and the latest generated baseline have
identical SHA-256 bytes. No new unsupported overlay is presented as valid.

No printing, printer connection, printable authorization, merge or release.
`log_iotc.txt` remains untouched and unstaged. Full-contact 3D reconstruction
and full-surface residual improvement remain unfinished research work.
