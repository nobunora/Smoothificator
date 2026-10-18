# 0–40-degree exponential top with short-base exclusion

The latest user instructions add a geometric applicability gate and change
the top-angle range from 10–40 degrees to 0–40 degrees. Previous 10–40-degree
inputs/results remain under `artifacts/exponential-top-review/`; this new
fixture lives under `artifacts/exponential-top-0to40-review/`.

## Applicability rule

Before packing or contact auditing, exclude a step when

```text
step_base < minimum_line_width * sqrt(2).
```

The implementation compares exact rational squares:
`step_base^2 >= 2 * minimum_line_width^2`. It never rounds sqrt(2) to decide
applicability. At minimum line width 0.25 mm, the threshold is approximately
0.353553390593274 mm. The configured minimum width controls the threshold;
maximum width and actual selected widths do not replace it.

Excluded steps emit no candidates and retain their complete triangle metadata,
`excluded-short-step-base` status, zero line count and exact threshold square.
They remain in the whole-model error domain. This research exclusion is not
a deposition or nozzle-clearance certificate.

## New surface and parameters

A pure exponential starting at zero would stay zero. Use a shifted exponential
ramp with the requested endpoints:

```text
theta(y) = 40 degrees * (exp(log(4)*y/12 mm) - 1) / 3
z(y) = 3 mm + integral(0..y, tan(theta(s)) ds), y=0..12 mm.
```

The surface is extruded 20 mm along X over a flat Z=0 bottom. Its top starts
at 3 mm and ends near 6.504688 mm. There are 256 mesh panels; actual exported
placement/profile is read back for error evaluation. Slope bins are now
0–5, 5–10, ..., 35–40 degrees. Defaults remain 0.25–0.45-mm widths, 0.08-mm
minimum remaining thickness, 0% overlap and 0.18-mm maximum physical height.
The 0..30% overlap limit and thickness compensation are preserved.

## Actual output and angle errors

Sixteen adjacent-layer step triangles are measured. Five are excluded, with
bases 0.352, 0.330, 0.308, 0.290 and 0.274 mm (floors Z=5.2 through 6.0 mm).
The remaining steps produce 29 lines. All 1,382 original extrusion segments
and 31 original layers remain; the viewer has 59 distinct Z levels.

Vertical MAE against the actual placed mesh, in mm:

| Angle | Original | After length gate (unverified) |
| --- | ---: | ---: |
| 0–5° | 0.040974 | 0.063844 |
| 5–10° | 0.048502 | 0.101906 |
| 10–15° | 0.053075 | 0.095173 |
| 15–20° | 0.051305 | 0.093990 |
| 20–25° | 0.056042 | 0.083331 |
| 25–30° | 0.045431 | 0.068626 |
| 30–35° | 0.044715 | 0.044715 |
| 35–40° | 0.095437 | 0.095437 |

The steep 30–40-degree region gains no additions, so its error is unchanged.
The previously diagnosed half-layer mesh/triangle misalignment still increases
mean error at low/middle angles. This patch does not change the user's triangle
height definition, move its floor, or certify improvement.

Comparison uses the same source-covered mask before/after: 392,973 of 393,216
fine-grid points, about 99.9382%. The 243 empty nominal extrusion columns are
explicitly reported; supplemental full-projection Z=0-bed-reference metrics
also remain available. Both 64x1536 and 128x3072 grids are recorded. Native
Orca's diamond display and nominal stadium metric remain separate models.

## Reproduction and evidence

```powershell
.\.venv\Scripts\python.exe -m tools.build_exponential_top_review
```

Use `--reslice` to regenerate and repin the source. Width, minimum remaining
height and overlap CLI options remain available. The final native file opened
in dedicated Orca is
`exponential-top-94bb43ee5b0542fd980a1f61ae0a8b57.UNVERIFIED_VIEW_ONLY.gcode`.
The capture `orca-preview.png` was opened and inspected. It establishes
loading/display only; no contact acceptance was inferred.

Viewer SHA256:
`2a718317e72456c5f3826425a3d894fcecda6ec70372a7fe5b7fd160e4dab94f`.
Source SHA256:
`6027df311adbcbda574021af89e79dac0daf03bdc32bc3f390b7447ce13d5758`.
Placed model SHA256:
`e5b9aadee2bb3e78727a3fd7af41c691199b9e2df3e1ee6ffdeeadf3f7743c57`.

Artifacts: `current-review.json`, `slice-receipt.json`, `fixture.json`,
`angle-errors.csv`, `angle-errors.json`, `architecture-tests.log`,
`focused-tests.log`, `full-tests.log` in the new fixture directory.

Changes are limited to the research triangle builder, curved fixture, angle
bins, fixture runner and associated tests. Production/injection contracts are
unchanged. Repository disposition: validated for this bounded research change.

Syntax/import checks passed. Architecture: 43 tests passed. Related: 26 tests
passed in 50.000 seconds. Commands use `.venv/Scripts/python.exe`:

Full suite: all 728 tests passed in 139.822 seconds on Python 3.12.10.
`git diff --check` passed with existing LF/CRLF notices only.

```text
-m compileall -q tools tests
-m unittest discover -s tests/architecture -q
-m unittest tests.unit.test_exponential_top_review tests.unit.test_triangle_rectangle_review tests.unit.test_tilted_cuboid_review -q
-m unittest discover -s tests -q
```

Tests cover exact near-threshold decisions, width-dependent exclusion, no
candidate on excluded floors, preserved source extrusions and unchanged
35–40-degree metrics. No new dependencies, printing, connection, merge or
release. `log_iotc.txt` remains unrelated and untouched/unstaged.
