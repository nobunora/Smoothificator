# Adjacent-layer triangle packing preview — 2026-10-18

## Authorized research scope and disposition

The user replaced the single-logical-rectangle approximation with a multiple
rectangle packing problem. Repeated sizes are allowed. The target triangle
height is the actual adjacent slice-layer height; its base is the measured
space between the current and next source-layer edges. Each rectangle must
have width 0.25–0.45 mm, height 0.05 mm to 90% of configured layer height,
and spill outside the triangle no greater than half its own area.

Repository disposition: validated for this offline research fixture/preview.
The owning modules are `tools/solve_triangle_rectangle.py` and
`tools/build_triangle_rectangle_review.py`; no production engine, injection,
plugin contract or safety acceptance semantics change. The previous single
rectangle solver is retained only as an analytic comparison baseline.

## Multiple-rectangle objective and algorithm

For triangle T and union U of selected rectangles, minimize

```text
area(T symmetric_difference U) = area(T) + area(U) - 2*area(T intersection U).
```

This implementation permits independent widths/heights, repeated sizes,
variable count and gaps. All rectangles rest on the current layer's command-Z
floor; their Y interiors are disjoint. It does not optimize overlapping or
stacked rectangles. These are explicit model boundaries, not claims about
general rectangle packing.

Positions are a uniform lattice over the entire triangle base. First solve
with spacing <=0.005 mm, then double the divisions for a nested spacing
<=0.0025 mm. For every feasible endpoint pair [a,b], the optimal rectangle
height is the median triangle height m*(a+b)/2, clamped to the configured
height bounds. Its exact spill area is

```text
O = (max(0,h-m*a)^2 - max(0,h-m*b)^2)/(2*m).
```

Reject O > (b-a)*h/2. With I=(b-a)*h-O, the error improvement is
gain = 2I-(b-a)*h. Dynamic programming chooses either an unfilled cell or
any feasible interval ending at the current position:

```text
best[j] = max(best[j-1], max_i(best[i] + gain(i,j))).
```

Areas, heights, positions, feasibility and comparisons use Fraction arithmetic.
The result is a global optimum over the stated position lattice and rectangle
model, with continuous optimal heights for each interval. It is not a proof
of the continuous-position optimum. Fine-grid error must not exceed the
coarse-grid error because the lattices are nested. Identical rectangles have
no uniqueness restriction.

## Actual tilted-cuboid fixture

The original 20x12x3-mm cuboid was physically tilted +10 degrees around X
before the pinned offline Orca slice. Layer edges are measured at mid-X from
X-directed source beads: edge Y = centerline Y - nominal width/2. Both edge
witnesses must span the entire candidate X interval 80.3–99.7 mm. The upper
source bead height must match the adjacent Z interval. No source-bbox-only
boundary inference or support-driven X clipping is used.

Ten rising adjacent-layer steps qualify, each with height 0.20 mm. The first
base is 0.816 mm; subsequent bases are 1.134 or 1.135 mm. The finite top
edge without a next layer is not invented as a full-height triangle. The
configured layer height is 0.20 mm, so the maximum rectangle height is 0.18 mm.

Result: 39 independent rectangles/lines, three in the first step and four
in each remaining step. Width range is 0.250000–0.252278 mm; physical height
range is 0.050000–0.177974 mm. The Z coordinate is floor+height, with zero
extra Z lowering. The selected widths divide each selected interval exactly.
Unfilled regions remain part of the triangle error objective.

| Cross-section area measure | Sum over ten steps (mm²) |
| --- | ---: |
| Target triangles | 1.102400000 |
| Best single-logical-rectangle approximation error | 0.367466667 |
| Multiple rectangle error, coarse positions | 0.128146021 |
| Multiple rectangle error, fine positions | 0.127083222 |

Fine-grid error is 65.4% lower than the single-rectangle baseline; the remaining
symmetric difference is 11.53% of the target triangles' total area. Maximum
individual spill fraction is approximately 19.615%, below 50%.
These are rectangle-versus-slice-triangle areas, not actual 3D surface metrics.

## Contact and native preview evidence

Every original source extrusion is retained: 6,071 segments and 25 original
layers. The 39 additions give 64 viewer Z levels. This preserves extrusion
geometry, not executable chronological print behavior.

Analytic nominal centerline audits report 10 full-centerline intersections
and 29 proven gap cases. These local intersection results allow penetration
and do not certify full-footprint deposition, nozzle clearance or printability.
All continuous-contact, shape-improvement and print-authorization flags remain
false. The slice-edge triangle is deliberately distinct from the exact mesh
plane: first-step clipping, bead rounding and toolpath placement can make them
differ. Original-mesh alignment is not certified.

The new file was opened in dedicated Orca and its captured side view inspected.
The screenshot shows thicker green Custom lines stepping across the orange
source terraces; apparent floating gaps remain visible. Green denotes a native
feature category, never valid-path acceptance. No physical device was used.

Artifacts in `artifacts/cuboid-tilt10-review/`:

- `current-triangle-review.json`: exact triangles, selected rectangles,
  per-line spill fractions, contact audits, source hashes and viewer receipt.
- `cuboid-triangle-rectangle-002183a75e34497699d877a75edd5c76.UNVERIFIED_VIEW_ONLY.gcode`.
- `triangle-orca-preview.png`: inspected native side-view capture.
- `triangle-packing-summary.json`: numerical comparison above.
- `triangle-build.log`, `triangle-focused-tests.log`,
  `triangle-architecture-tests.log`, `triangle-full-tests.log`.

Viewer SHA256:
`46730a27b32ad3c10b22c5b5861a88227bf036da7fc9cdc61efec889b4e07303`.
Source slice SHA256:
`80647a2dd843125bf3bed3a22ab1808c09154d55adb7ad5f70063dabb4f538e6`.
Placed project SHA256:
`18b45819cf0a7702d72f84dde73832a13d42b79b40daf7435dc7d54a3baf08bf`.

## Validation commands

Use `.venv/Scripts/python.exe`:

```text
-m compileall -q tools/solve_triangle_rectangle.py tools/build_triangle_rectangle_review.py tests/unit/test_triangle_rectangle_review.py
-m unittest discover -s tests/architecture -q
-m unittest tests.unit.test_triangle_rectangle_review -q
-m unittest discover -s tests -q
-m tools.build_triangle_rectangle_review
```

Eight focused tests cover the analytic baseline, dimension caps and untileable
width gap, independent grid integration, repeated sizes, exhaustive small-grid
packing with gaps, nested refinement, malformed/infeasible inputs, per-line
spill limits, pinned real fixture and original segment retention. Syntax/import
checks passed. Lint/type tooling remains unconfigured; no dependency was added.

Python 3.12.10 results: architecture 43 tests passed; focused eight tests passed
in 9.439 seconds; full suite 717 tests passed in 120.440 seconds.
`git diff --check` passed (existing LF/CRLF conversion notices only).

No merge, release, printer connection or print was performed. The unrelated
`log_iotc.txt` was neither changed, deleted nor staged.
