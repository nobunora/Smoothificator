# Revolved exponential top: concentric research preview

## Shape and authorized scope

The user requested the same curved cross-section revolved into a new shape.
The working interpretation is a 360-degree revolution around the vertical Z
axis, giving a low center and higher rim. The previous 0..40-degree profile
is unchanged, with Y replaced by radius r:

```text
theta(r) = 40 degrees * (exp(log(4)*r/12 mm)-1)/3
z(r) = 3 mm + integral(0..r, tan(theta(s)) ds).
```

The model is a solid 24-mm-diameter body over a flat Z=0 bottom. Center top
is Z=3 mm; rim top is approximately Z=6.504688 mm. There are 256 radial panels
and 128 angular sectors: 32,898 vertices and 65,792 triangles in a closed,
consistently oriented shell. The angular polygon radius deficit is at most
about 0.003614 mm. The sanitized offline profile is reused as a package seed,
with a new mesh and center placement (90,90) mm. No physical printing occurs.

## Radial packing and native representation

The source slice is independent of the previous linear fixture and is pinned
by SHA256. Finite flat-cap source footprints are intersected with the +X ray
from the axis to measure adjacent-layer inner radii. Radii are numerical
intersections rounded to 9 decimals; they are not exact whole-circle support
bounds. The flat first terrace has inner radius zero.

Each radial step uses the existing exact-area multiple-rectangle DP with
0.25–0.45-mm widths, minimum remaining height 0.08 mm and maximum physical
height 0.18 mm. The squared short-base gate is retained: base² >= 2*min_width².
Overlap is 0% for this review; 0..30% and h_min=t_min/(1-p) compensation remain
available. Every selected radial rectangle becomes a concentric polygonal
extrusion path with 192 closed chords. At radius12 the chord deficit is below
0.002 mm. All paths carry UNVERIFIED_VIEW_ONLY status.

This is the same **radial cross-section objective**, expanded around the axis.
It is not a proof of optimum annular volume error. Actual source deposition
is not rotationally uniform. A reference-ray boundary and a closed generated
ring do not certify continuous circumferential contact, all-azimuth short-step
eligibility or nozzle clearance. Those flags remain false. This adapter does
not promote source-ray evidence into a whole-ring certificate.

## Current result and limits

The actual source contains 14,937 extrusion segments and 31 layers. Sixteen
radial steps yield four short-base exclusions and 30 concentric additions.
Selected widths are about 0.250884–0.376847 mm; physical heights 0.08–0.18 mm.
There are 5,760 added chords and 60 viewer Z levels. All original extrusion
geometry is retained, while executable print chronology is not retained.

The viewer was opened in dedicated Orca and `orca-preview.png` was captured
and inspected. It shows the bowl-like surface and green concentric Custom
paths over orange original extrusions. Green is a feature color, not validity.

## Angle-bin evaluation against the actual placed mesh

The target height and local slope are computed by barycentric interpolation
and gradients of the exported mesh's actual top triangles. All original and
added nominal stadium segments form the comparison top envelope. The same
source-covered XY sample mask is used before/after, on the actual polygonal
disk footprint. Grids are 256x256 and 512x512 over the 24x24-mm bounding square.
The fine grid has 205,679 source-covered points and 109 explicitly excluded
empty nominal columns inside the mesh footprint (about 99.947% coverage).

Vertical mean absolute errors in mm:

| Local angle | Original | With concentric hypotheses |
| --- | ---: | ---: |
| 0–5° | 0.057020 | 0.076151 |
| 5–10° | 0.049021 | 0.102756 |
| 10–15° | 0.052559 | 0.097486 |
| 15–20° | 0.051016 | 0.097647 |
| 20–25° | 0.057397 | 0.088067 |
| 25–30° | 0.045506 | 0.088909 |
| 30–35° | 0.043903 | 0.040896 |
| 35–40° | 0.099003 | 0.099003 |

The earlier mesh/triangle vertical-alignment issue is still present. Most
low/middle-angle means worsen. The 30–35-degree bin improves slightly; the
35–40-degree bin receives no effective addition and is unchanged. These are
sampled nominal height errors, not physical extrusion or contact certificates.
The renderer uses diamond geometry, so its appearance is a separate check.

## Reproduction and artifacts

```powershell
.\.venv\Scripts\python.exe -m tools.build_revolved_top_review
.\.venv\Scripts\python.exe -m tools.evaluate_revolved_surface
```

The builder supports `--reslice`, `--minimum-width-mm`, `--maximum-width-mm`,
`--minimum-height-mm` and `--overlap-percent`. Invalid dimensions, compensated
height beyond the slicer maximum, overlap outside 0..30%, and >50% individual
rectangle spill are rejected. Original source hashes are checked before build.

New modules: `tools/revolved_exponential_fixture.py`,
`tools/build_revolved_top_review.py`, `tools/evaluate_revolved_surface.py`.
New tests: `tests/unit/test_revolved_top_review.py`. No production code or
dependencies changed. Repository disposition: validated for this offline
research scope, with the geometric limitations above.

Artifacts under `artifacts/revolved-exponential-review/`:

- `revolved-exponential.3mf`, `.stl`, `fixture.json`, `slice-receipt.json`.
- `current-review.json` and
  `revolved-exponential-2900f49a4de04b85b7ba2aaa2b2a031e.UNVERIFIED_VIEW_ONLY.gcode`.
- `angle-errors.csv`, `angle-errors.json`, `evaluation.log`.
- `orca-preview.png`, `build.log`, `architecture-tests.log`,
  `ray-focused-tests.log`, `full-tests.log`.

Source slice SHA256:
`8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95`.
Placed mesh SHA256:
`0f4d85b55a2c3e1f579cc013d722f755a657f17dadb840d8a020792099aa3d61`.
Viewer SHA256:
`20e4e6b8920dbb8bbe4f8bba88ff8f1b68c5c649b2cb61edfe3580b46a93d4ea`.

Syntax/import checks passed; architecture 43 tests passed. New tests cover
oriented closed topology, numerical finite-cap ray intersections, closed
constant-Z rings/chord error, actual triangle interpolation, complete original
segment retention, dimension/spill limits, hash and overlap rejection, and
angle-report sample-mask consistency. Numerical ray endpoints use 1e-12-scale
test tolerances; applicability itself still uses exact rational squared tests.
No contact flag is inferred from numerical tests or screenshots.
Full suite: all 734 tests passed in 168.652 seconds on Python 3.12.10.
`git diff --check` passed with existing LF/CRLF notices only.

No printer connection, print, merge or release. `log_iotc.txt` remains unrelated
and untouched/unstaged. Previous linear/curved fixtures are preserved.
