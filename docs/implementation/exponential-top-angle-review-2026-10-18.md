# Exponential-angle top: recomputation and angle-bin errors

## Fixture and scope

The user requested a curved top whose angle varies exponentially instead of
the tilted cuboid. The stated working assumption is a 10-to-40-degree slope
angle over Y=0..12 mm, extruded 20 mm along X:

```text
theta(y) = 10 degrees * exp(log(4) * y / 12 mm)
z(y) = 3 mm + integral(0..y, tan(theta(s)) ds)
```

The bottom is flat at Z=0. The analytic top ends at approximately 7.8991354 mm.
The mesh has 256 Y panels, 1,028 vertices and 2,052 triangles, with a closed,
consistently oriented shell. Panelwise Simpson integration is checked against
512 panels. The analytic chord interpolation bound is about 0.00003775 mm;
this is not a complete floating-point or slicing tolerance certificate.
The comparison target is the **actual exported placed mesh**, not the analytic
curve, so Orca placement and vertex serialization are included.

Offline Orca slicing uses the existing sanitized profile, no orientation or
arrangement change, and 0.20-mm layers. Inputs and exported slice/3MF have a
SHA256 receipt. Later runs reject source drift unless explicitly resliced.

The existing multiple-rectangle algorithm is retained: adjacent source-layer
edge separation is the triangle base, adjacent layer Z difference is its rise,
and exact-area DP chooses independent rectangles on nested position lattices.
Widths remain 0.25–0.45 mm, minimum remaining thickness 0.08 mm, maximum physical
height 0.18 mm and overlap 0%. The 0..30% range and overlap compensation remain
available through CLI parameters. This is a research adapter, not production
injection or physical printing.

## Native preview result

The source contains 1,218 extrusion segments and 38 layers. The 23 rising step
triangles produce 35 additions, width 0.250000–0.324198 mm and physical height
0.080000–0.174876 mm. All original extrusion geometry is retained; the viewer
has 73 distinct Z levels. Top regions without an additional source layer are
not invented as full-height step triangles, but remain in the error domain.

The generated file was opened in dedicated Orca. `orca-preview.png` was captured
and inspected. Green is the Custom category, never a valid-path acceptance.
The nominal stadium model used for numerical errors differs from Orca's
diamond display geometry. No camera view establishes deposition/contact safety.

## Error measurement

Measure the vertical height difference between the target mesh and the maximum
nominal stadium top of all original extrusions plus the additions. Compare
before/after at the same points across the entire projected 20x12-mm top face.
Angle bins use the local **actual mesh facet slope**, in 5-degree intervals.
This is height-direction MAE, not closest Euclidean surface distance.

Two independent grids are used: 64x1536 and 128x3072. The primary table uses
the fixed common source-covered mask, with no changed denominator after adding
lines. The fine grid has 392,964 source-covered points out of 393,216 (99.9359%).
The 252 empty nominal extrusion columns are explicitly counted: 134 in 10–15°
and 118 in 35–40°. Twenty-six gain candidate coverage. They are not silently
reclassified into the primary mask. A separate full-projection comparison
uses bed Z=0 for empty columns and is also recorded; it is sensitive to edge
sampling and does not replace the primary comparison. There are no unsupported
source beads in this fixture.

| Local angle | Before MAE mm | After MAE mm | Change | Before max mm | After max mm |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10–15° | 0.05542 | 0.08670 | +56.4% | 2.97079 | 0.15769 |
| 15–20° | 0.05428 | 0.09075 | +67.2% | 0.29954 | 0.17180 |
| 20–25° | 0.05428 | 0.08940 | +64.7% | 0.29965 | 0.19400 |
| 25–30° | 0.04749 | 0.08068 | +69.9% | 0.29930 | 0.21623 |
| 30–35° | 0.04358 | 0.09046 | +107.6% | 0.23950 | 0.23950 |
| 35–40° | 0.07828 | 0.10203 | +30.3% | 0.37784 | 0.37784 |

Every bin's mean error worsens. The area-weighted covered-point mean increases
from 0.05488 to 0.08908 mm. Some deep local valleys improve, as shown by maximum
sampled errors at low angles, but excess material dominates the mean error.
Coarse/fine differences in primary after-MAE are approximately
0.00022–0.00105 mm. These numerical checks do not certify continuous error bounds.
The all-projection/bed-reference comparison also worsens in every bin.

## Cause confirmed against geometry

The triangle objective is optimal for its stated approximation, but that
approximation is vertically misaligned with the actual mesh. For example:

```text
current layer top Z = 3.2 mm
mesh Z - current layer Z at current edge = -0.099987 mm
mesh Z - current layer Z at next edge    = +0.099953 mm
algorithm's assumed triangle interval   = 0 .. +0.20 mm
```

Many interior steps have this approximately half-source-layer offset. The
added beads start at the current command top Z and therefore overfill the
actual target, even though they improve the assumed 0..0.20-mm triangle.
For 15–20°, mean shortage drops from 0.03393 to 0.00147 mm, while mean excess
increases from 0.02036 to 0.08928 mm. This is not explained away as a display
problem or a few missing samples. `step_mesh_alignment` records every step.

No automatic change to the user's triangle definition, layer-top contact
convention, minimum dimensions or overlap has been made to conceal the result.
The next algorithm issue is aligning the residual fill domain with the actual
geometry boundary while preserving the explicit current-layer contact basis.
All physical-contact, shape-improvement and print-authorization flags remain
false. No successful/green valid candidate is asserted.

## Files, reproduction and verification

New source modules:

- `tools/exponential_top_fixture.py`: model authoring and actual placement readback.
- `tools/evaluate_curved_surface.py`: fixed-domain angle-bin comparisons.
- `tools/build_exponential_top_review.py`: offline slice, pin, build and report.

The existing triangle builder and native scene renderer accept this curved
fixture without claiming it is the old 10-degree plane. Existing cuboid behavior
is retained. New tests cover exponential angle/integration, closed oriented
mesh, actual profile/domain checks, over/under errors and fixed missing masks,
actual source retention, adverse measured errors and the half-layer offset.

```powershell
.\.venv\Scripts\python.exe -m tools.build_exponential_top_review
# Explicitly regenerate and repin offline source slice if required:
.\.venv\Scripts\python.exe -m tools.build_exponential_top_review --reslice
```

The same command exposes `--minimum-width-mm`, `--maximum-width-mm`,
`--minimum-height-mm` and `--overlap-percent`; minimum-height compensation and
0..30% bounds are enforced by the shared research builder.

Artifacts under `artifacts/exponential-top-review/`:

- `exponential-angle-top.3mf`, `.stl`, `fixture.json`, `slice-receipt.json`.
- `current-review.json` and
  `exponential-top-1202c6a91dd645a79b30d62ec8dea843.UNVERIFIED_VIEW_ONLY.gcode`.
- `angle-errors.csv`: primary covered-point table, with sample/exclusion counts.
- `angle-errors.json`: both grids, both mask policies, RMS/shortage/excess and alignment.
- `orca-preview.png`: inspected native screenshot.
- `architecture-tests.log`, `focused-tests.log`, `full-tests.log`, `build.log`.

Source slice SHA256:
`51d250b12913c859cdf699eaeba5132d556e628fdf19b192137cae40768f4bf0`.
Placed model SHA256:
`8c0a14a178b37559d242ee26f8b610d7a40be2cc75fbcdd5fd91c40074ec9d6f`.
Viewer SHA256:
`bb607d92e6cbdf990dcd7037e3f88b503886b57c8980c71562913b0cffb8e3a4`.

Syntax/import checks passed. Related tests: 25 passed in 39.793 seconds.
Architecture: 43 tests passed. Full suite: all 727 tests passed in 152.754
seconds on Python 3.12.10. `git diff --check` passed with existing LF/CRLF
notices only. The curve CLI's +31% overlap was rejected with exit code 2.
Commands: `-m unittest discover -s tests/architecture -q`,
`-m unittest tests.unit.test_exponential_top_review tests.unit.test_triangle_rectangle_review tests.unit.test_tilted_cuboid_review -q`,
and `-m unittest discover -s tests -q` with `.venv/Scripts/python.exe`.
No new dependencies. Lint/type tooling remains unconfigured.
No merge, release, printer connection or print occurred. `log_iotc.txt` remains
unrelated and untouched/unstaged; no files were deleted outside C:.
