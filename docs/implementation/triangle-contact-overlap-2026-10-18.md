# Triangle preview contact overlap — 2026-10-18

Historical record: the later user instruction supersedes the signed range and
fixed-height translation behavior below. See
[configurable preview and compensation](configurable-triangle-preview-2026-10-18.md)
for the current 0..30% range and compensated minimum remaining thickness.

The user's placement convention is now an explicit research-preview setting:
0% aligns the added rectangle bottom with the current source layer's command
top Z; positive values penetrate into that layer; negative values leave a gap.
Percentages are relative to each added line's physical thickness h.

```text
bottom_Z = current_layer_top_Z - h * overlap_percent / 100
command_Z = bottom_Z + h
```

For a 0.10-mm line over layer Z=3.00 mm:

| Overlap | Bottom Z | Command/top Z |
| --- | ---: | ---: |
| -5% | 3.005 | 3.105 |
| 0% | 3.000 | 3.100 |
| +5% | 2.995 | 3.095 |

The initial value is 0%. The allowed interval is -10% to +10%, preserving
the user's previous limit of about 10% of physical line thickness for Z
adjustments. This setting belongs to the offline research CLI/manifest;
it does not change production settings schemas or printer profiles.

## Coordinate verification and scope

The previous 39-line version already used command_Z=layer_top_Z+h, so its
nominal bottom was aligned at 0%. The new zero-overlap build preserves that
geometry and makes the convention inspectable. It does not apply a hidden
offset to manufacture a visible contact result.

The pinned renderer snapshot `artifacts/orca-source/ViewerImpl.cpp`, in
`extract_pos_and_or_hwa`, subtracts h/2 from extrusion Z before rendering
the centered cross-section. Consequently command Z is the displayed bead
top, and its lowest centerline point is command_Z-h. The source renderer's
diamond profile has a local upper surface below command Z away from its
crest. Therefore equality to the layer's command top Z is not whole-surface
contact or a physical adhesion certificate. Previously reported gaps remain.

The user-authorized change is implemented in
`tools/build_triangle_rectangle_review.py`: exact placement validation,
`--overlap-percent`, per-line bottom/top/penetration values, adjusted contact
audits, and manifest settings. Widths, physical heights, count and Y placement
come from the existing zero-overlap multiple-rectangle packing solution.

Changing overlap translates each whole bead. It does not reoptimize packing.
Reference packing optimality is explicitly labeled as applying to the
zero-overlap reference only; posed optimality is false for nonzero overlap.
The posed union's triangle error and per-line spill are recomputed by exact
area integration, including penetration below the triangle floor. Any line
exceeding the 50% spill limit causes build rejection. These remain rectangle
model metrics, not rounded-bead surface or printability proof.

## Usage

From `C:/VSC/Smoothificator`:

```powershell
.\.venv\Scripts\python.exe -m tools.build_triangle_rectangle_review --overlap-percent 0
.\.venv\Scripts\python.exe -m tools.build_triangle_rectangle_review --overlap-percent 5
```

Each invocation creates a fresh `*.UNVERIFIED_VIEW_ONLY.gcode` and updates
`artifacts/cuboid-tilt10-review/current-triangle-review.json`. No printer
connection or print action occurs. The currently opened file is the 0% build:

`cuboid-triangle-rectangle-e6d872c40c0d4897807b276a915a14bf.UNVERIFIED_VIEW_ONLY.gcode`.

Its SHA256 is
`d88ddb06f07ea9882cb8ee5a61cb7d1413da4ddd581fd4e7ae57a9109bd4fb97`.
All 39 exact bottom values equal their recorded source layer top Z. Posed
triangle areas equal the reference packing areas exactly at 0%. The original
6,071 extrusion segments and 25 source layers remain, with 39 additions.
The new 0% file was loaded in dedicated Orca; the oblique screenshot
`overlap-zero-orca-preview.png` was captured and inspected. No contact or
print acceptance was inferred from its appearance.

## Validation

Python 3.12.10. Commands use `.venv/Scripts/python.exe`:

```text
-m compileall -q tools/build_triangle_rectangle_review.py tests/unit/test_triangle_rectangle_review.py
-m unittest discover -s tests/architecture -q
-m unittest tests.unit.test_triangle_rectangle_review -q
-m unittest discover -s tests -q
-m tools.build_triangle_rectangle_review --help
```

Architecture: 43 tests passed. Focused: 11 tests passed in 39.504 seconds.
Full suite: all 720 tests passed in 125.258 seconds. `git diff --check`
passed with existing LF/CRLF notices only. CLI +11% was rejected with exit 2.
Tests cover exact zero alignment, signed movement, thickness-relative limits,
invalid values, below-floor area accounting and the actual 39-line +5% scene.
The +5% fixture preserves widths/heights/count and translates every bottom/top
by exactly h/20. All acceptance flags remain false. Logs are
`overlap-architecture-tests.log`, `overlap-focused-tests.log`,
`overlap-full-tests.log` and `overlap-zero-build.log` in the fixture folder.

No dependencies, production code, original slice or unrelated `log_iotc.txt`
were changed. No merge, release, printer connection or print was performed.
