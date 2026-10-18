# Balanced cross-section height research (2026-10-18)

The user's midpoint instruction supersedes the previous inscribed-only
rectangle rule. This is an offline, display-only experiment on the cuboid
rotated 10 degrees about X before Orca slicing. It does not authorize printing.

## Placement and objective

For the increasing target plane M(y), a rectangle over [y-w/2,y+w/2]
previously had its top capped by M(y-w/2). Its inscribed and circumscribed
levels are M(y-w/2) and M(y+w/2); their midpoint is M(y). The new search
requires |top-M(y)| <= h/10. It also independently requires
top = terrace_floor + h*(1+f), |f| <= 0.1. Thus Z adjustment is relative to
the physical bead thickness, not the default layer height.

Width remains 0.25–0.45 mm; height remains 0.05–0.18 mm, with the maximum
read as 90% of the source's configured 0.20-mm layer height. The midpoint
constraint allows some geometry overshoot: both overshoot and shortage
contribute equally to mean absolute error. No signed cancellation is used.

`tools.optimize_top_error` evaluates the maximum of all original source bead
tops and each proposed bead top. Beads use the nominal stadium cross-section,
including rounded sides and flat axial ends. The objective is area-weighted
mean absolute vertical distance to the target plane on a fixed uniform grid.
For this planar target, conversion to plane-normal distance is a constant
factor and preserves the ordering. This differs from maximizing rectangle area.

The search uses widths spaced by 0.01 mm, heights by 0.005 mm, positions by
0.025 mm in the previous ten terrace neighborhoods, and Z fractions -0.1,
-0.05, 0, 0.05, 0.1. It evaluates 82,761 eligible parameter combinations.
Weighted interval scheduling selects nonoverlapping footprints rather than
greedily choosing one line. Disjoint terrace bands are checked explicitly.
The result is optimal only over this finite candidate set and sampled objective;
it is not a continuous global optimum or a general model solver.

## Actual fixture evidence

All 6,071 original extrusion segments and all 25 original layers remain in the
viewer, including later source paths. The evaluation covers the projected
whole top face, with candidates extending X=80.3–99.7 mm. Search resolution
is 64x384; the independent validation is 128x768. Both comparisons use the
same source-evaluable mask. Of 98,304 validation points, 98,171 are evaluable
and 133 have unresolved source coverage. Adding any candidate at an unresolved
sample raises an error; none of these samples is affected by the selected lines.
This is numerical evidence, not a continuous whole-face certificate.

| Configuration | Mean absolute vertical error (mm) |
| --- | ---: |
| Original source | 0.0512212 |
| Previous inscribed placement, -10% Z | 0.0382791 |
| Balanced placement, fixed 0.05-mm height | 0.0347167 |
| Balanced placement, best uniform height 0.075 mm | 0.0322049 |
| Balanced placement, adaptive heights | 0.0290572 |

The adaptive result reduces validation MAE by about 24.1% from the previous
placement. It selects 20 lines, two per terrace: ten at 0.05 mm, seven at
0.095 mm, two at 0.075 mm and one at 0.085 mm. Widths are 0.25–0.29 mm.
Mean shortage falls from 0.0182995 to 0.0072893 mm, while mean excess rises
from 0.0199796 to 0.0217679 mm. Maximum sampled error remains 2.3708163 mm;
the deep remaining valleys and edge errors have not been solved.

Analytic centerline audits still find source contact gaps. Midpoint placement
and mean-error reduction do not establish full-length/full-footprint contact,
nozzle clearance, physical deposition behavior or printability. All acceptance
flags remain false. Green in Orca denotes the Custom category only.

## Reproduction and artifacts

Run with `.venv/Scripts/python.exe`:

```text
-m tools.optimize_top_error
-m tools.build_balanced_error_review
-m unittest tests.unit.test_balanced_error -q
-m unittest discover -s tests/architecture -q
-m unittest discover -s tests -q
```

Artifacts under `artifacts/cuboid-tilt10-review/`:

- `balanced-error-optimization.json`: search, exact dimensions, independent metrics.
- `current-balanced-review.json`: source hashes, analytic gaps, viewer hash/path.
- `cuboid-balanced-error-548ecff7648e458abc2c79bbed1d5d78.UNVERIFIED_VIEW_ONLY.gcode`:
  new native Orca preview, 20 hypotheses and 45 viewer layers.
- `balanced-orca-preview.png`: captured and inspected native side view. It shows
  the original orange staircase and added green beads. Visible gray outlines,
  apparent gaps and rounded geometry are not contact acceptance evidence.
- `balanced-focused-tests.log`, `balanced-architecture-tests.log`,
  `balanced-full-tests.log`: executable validation evidence.

Python 3.12.10 validation: six focused tests passed; 43 architecture tests
passed; all 709 tests passed in 98.780 seconds. `compileall` and
`git diff --check` also passed.

Source slice SHA256:
`80647a2dd843125bf3bed3a22ab1808c09154d55adb7ad5f70063dabb4f538e6`.
Placed project SHA256:
`18b45819cf0a7702d72f84dde73832a13d42b79b40daf7435dc7d54a3baf08bf`.
Viewer SHA256:
`17f4f8cbf4f3114b14ed798bb8441d0fe965eff40e94877dec032f78befbba97`.

The new file was opened in the dedicated local Orca instance. No device
connection, print, merge or release was performed. `log_iotc.txt` is unrelated
and remains untouched and unstaged.
