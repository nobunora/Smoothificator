# Configurable triangle preview and overlap compensation — 2026-10-18

This offline research change implements the user's requested adjustable
minimum width, maximum width and minimum remaining thickness. It also
supersedes the earlier signed -10..+10% overlap policy: the accepted input
range is now **0..30%**, inclusive. Negative or larger values are rejected.
This numerical input cap is not printer/nozzle safety certification.

## Parameters and reproducible current preview

Defaults and the current requested fixture:

- Minimum line width: 0.25 mm.
- Maximum line width: 0.45 mm.
- Minimum thickness remaining above the current layer after overlap: 0.08 mm.
- Overlap: 0%.
- Maximum physical height: 90% of the original slicer layer-height setting,
  currently 0.18 mm. This limit is not increased to accommodate overlap.

```powershell
.\.venv\Scripts\python.exe -m tools.build_triangle_rectangle_review `
  --minimum-width-mm 0.25 --maximum-width-mm 0.45 `
  --minimum-height-mm 0.08 --overlap-percent 0
```

All four options are available on the research generation CLI. They are
recorded in the adjacent JSON manifest; no production printer profile or
production Settings schema is modified. This is not an Orca settings UI.

## Overlap and minimum-height compensation

For required remaining thickness t, overlap fraction p, and physical height h:

```text
analysis_minimum_height = t / (1-p)
bottom_Z = layer_top_Z - h*p
command/top_Z = bottom_Z + h
remaining_height_above_layer = h*(1-p) >= t
```

Simply multiplying t by (1+p) is insufficient: at t=0.08 and p=0.30 it leaves
only 0.0728 mm above the layer. The implemented exact division gives:

| Overlap | Required remaining thickness | Analysis minimum physical height |
| --- | ---: | ---: |
| 0% | 0.08 mm | 0.0800000 mm |
| 5% | 0.08 mm | 0.0842105 mm |
| 30% | 0.08 mm | 0.1142857 mm |

The compensated minimum participates in the multiple-rectangle packing
optimization, so changing overlap can change widths, heights and count.
The builder does not merely translate the old packing. It then applies the
overlap placement, recomputes posed triangle error/spill and contact audits,
and rejects any per-line spill exceeding half the rectangle area. Reference
packing optimality applies to the compensated zero-overlap reference geometry;
nonzero-overlap posed optimality is not claimed.

If the compensated minimum exceeds the unchanged slicer maximum, generation
fails before output. For example, required 0.13 mm at 30% needs 0.185714 mm,
which exceeds 0.18 mm and is rejected. The exact 0.126/0.7=0.18 boundary passes.
Nonpositive dimensions and minimum width above maximum width are rejected.
Selected nominal bead heights greater than their widths are unsupported and
fail closed. Unfillable triangles remain explicit diagnostics.

## Current actual fixture result

On the pinned 10-degree cuboid, 10 steps now produce 29 lines: two on the
first step and three on each subsequent step. Selected widths are approximately
0.272260–0.362500 mm; heights 0.080000–0.175991 mm. Every bottom equals the
recorded current-layer command top Z at 0%. Maximum per-line posed spill is
approximately 15.5863%, below 50%.

The original 6,071 extrusion segments and 25 layers are retained. The artifact
is still display-only; original mesh fit, whole-footprint contact, chronological
tool clearance and printability remain unverified. Appearance from one camera
angle is not a contact certificate.

Current file under `artifacts/cuboid-tilt10-review/`:

`cuboid-triangle-rectangle-8ef054ec06464dbd92fa9b948a5e686e.UNVERIFIED_VIEW_ONLY.gcode`

SHA256: `304ee279130e44730e5976789361f37254a344249831600ee98ad07996dfb841`.
`current-triangle-review.json` records requested and analysis minimum heights,
exact placement and support-audit evidence. The source slice and placed project
retain their existing pinned SHA256 values. No source files or unrelated
`log_iotc.txt` were changed, deleted or staged.

The final 0% file was opened in dedicated Orca. The native oblique capture
`configurable-orca-preview.png` was inspected and shows the thicker green
Custom lines over the original source. This establishes loading/display only.

## Verification

Changed implementation: `tools/build_triangle_rectangle_review.py`.
Changed tests: `tests/unit/test_triangle_rectangle_review.py`.
No dependency, production engine, physical connection or print action added.
Repository disposition: validated for this research adapter's bounded scope.

Commands use `.venv/Scripts/python.exe`:

```text
-m compileall -q tools/build_triangle_rectangle_review.py tests/unit/test_triangle_rectangle_review.py
-m unittest discover -s tests/architecture -q
-m unittest tests.unit.test_triangle_rectangle_review -q
-m unittest discover -s tests -q
```

Focused: 13 tests passed in 22.366 seconds. Tests include invalid dimensions,
exact 0%/30% placement, rejection of negative/over-limit overlap, exact
compensation and its maximum-height boundary, the actual 30% fixture's
remaining thickness/spill, alternate 0.30–0.40-mm widths and 0.10-mm minimum,
and complete original-segment retention for the default actual fixture.
Logs: `configurable-architecture-tests.log`, `configurable-focused-tests.log`,
`configurable-full-tests.log`, `configurable-build.log`.
Architecture: 43 tests passed. Syntax/import checks and `git diff --check`
passed; lint/type tooling remains unconfigured. CLI -1%, 31%, and 0.13-mm
minimum at 30% overlap all rejected before output with exit code 2.
Full suite: all 722 tests passed in 142.120 seconds on Python 3.12.10.

No merge, release or physical printing was performed.
