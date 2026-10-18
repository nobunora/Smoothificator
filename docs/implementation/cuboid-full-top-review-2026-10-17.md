# Cuboid full-top native review

User scope: apply the current research representation over the whole top of a
rectangular cuboid and leave it available for inspection in standard Orca Preview.
This is a full-top placement/display trial, not an accepted printable-path result.

## Fixture and scene

`tools/build_cuboid_top_review.py` generates a closed 20 x 12 x 3 mm cuboid STL
and 3MF, slices it offline using the existing dedicated Orca executable, and
reconstructs the original 956 extrusion segments plus a 59-line Custom overlay.
The 3MF copies the existing fixture's slicer geometry/profile settings, disables
arc fitting, and removes machine/filament template programs for the offline test.
It contains no stale thumbnails from the tilted coupon.

The profile is the copied Bambu A1 mini / 0.20 mm example profile; no physical
printer was connected or selected for execution. Native start/slice controls
are disabled in the opened G-code viewer.

Orca rotates the box 90 degrees while placing it. Its actual sliced top bounds
are X=[119.6,131.6], Y=[80,100] mm. These are measured from the sliced outer
wall centers and recorded widths, checked against the known box dimensions,
and snapped to those exact dimensions at the measured center.

The overlay has 59 X-directed nominal rectangular footprints:

- Original top: Z=3.00 mm; candidate top: Z=3.08 mm.
- Width: 0.34 mm; height: 0.19 mm; bottom at the center: Z=2.89 mm.
- Transverse pitch: exactly 983/2900 mm (approximately 0.338965517 mm).
- First/last half-width edges match the two face boundaries exactly;
  adjacent nominal footprints overlap slightly, so their closed rectangular
  union covers the entire 240 mm² top face under the flat-axial-cap model.

For convenient native inspection, **all baseline and candidate paths receive
the same viewer-only XY translation (-35.6,0) mm**, moving their common center
onto the configured bed center. Z, relative coordinates and extrusion geometry
are preserved. This translation is explicit in the G-code header and manifest;
the original slice file is not modified. It does not define an execution frame.
Orca's pointed display caps can extend slightly beyond the nominal X edges.

A horizontal cuboid has no tilted macro surface to reconstruct. This overlay
deliberately raises the nominal top by 0.08 mm and overlaps existing material.
Full-area contact, local/full-surface improvement and chronological clearance
have not been certified. `printable_authorized`, `continuous_contact_verified`
and `shape_improvement_verified` all remain false. Green means Custom category.

## Reproduction and files

```
.venv\Scripts\python.exe -m tools.build_cuboid_top_review
```

The command regenerates the local fixture, invokes offline slicing, and creates
a unique `UNVERIFIED_VIEW_ONLY.gcode` plus JSON manifest under
`artifacts/cuboid-top-review/`. The manifest contains model/STL/source/viewer
SHA-256 values, all 59 candidate endpoints, coverage bounds, pitch and XY shift.
Only G21/G90/M83/G92/G1 commands are retained in the reconstructed scene;
machine programs, heating, homing and device operations are not copied.

Current native-open file:
`artifacts/cuboid-top-review/cuboid-full-top-d47aea1f4acd43c3989b82bbc0c2dc86.UNVERIFIED_VIEW_ONLY.gcode`.
Model files: `cuboid-20x12x3.stl`, `cuboid-20x12x3.3mf` in that directory.

## Integration findings and verification

The slice uses BBL `FEATURE / LINE_WIDTH / LAYER_HEIGHT / CHANGE_LAYER` tags,
unlike the earlier Generic Marlin fixture's compatibility tags. The source
reader now accepts explicit expected digests and the BBL Z/width aliases while
preserving its original SHA-pinned default. An initial native load classified
compatibility-only output as Undefined and one layer; the final emitter uses
the profile's BBL tags and native Preview recognizes 16 layers and green Custom.
Duplicate wipe-tower XY configuration keys are omitted from viewer config.

A full test run caught a default-argument constant being bound too early for
the existing patched source-identity test. The default digest is now resolved
at call time, retaining the existing fixture contract; no test was weakened.

Python 3.12.10, no dependencies added:

- `python -m compileall -q tools tests`: PASS.
- Architecture/import suite: 43 PASS.
- `python -m unittest tests.unit.test_cuboid_top_review tests.unit.test_layered_preview_overlap_audit -q`: 12 PASS.
- `python -m unittest discover -s tests -p 'test_*.py' -q`: **670 PASS in 76.759 s**.
- `git diff --check`: PASS.

Tests verify closed whole-face coverage, no transverse gaps, digest and motion
mode rejection, retained baseline segment counts, equal XY translation of every
baseline endpoint with unchanged Z, 16-layer representation and allowed commands.
Logs: `focused-tests.log`, `full-tests.log` and `slice-stdout/stderr.log` under
the local review directory. Lint/type tooling remains NOT CONFIGURED.

Dedicated Orca standard Preview was visually inspected. The 59 green lines cover
the visible top; original structural side layers remain visible. The final
view is enlarged with the legend collapsed so it does not obscure the top.
`artifacts/cuboid-top-review/orca-full-top-final.png` is a process-identity-checked
PrintWindow/Pillow capture that was opened and inspected. A wider initial
classified view is retained as `orca-classified.png`. Native layer Z labels may
still show 0.00; generated command Z and manifest are the coordinate evidence.

Orca is intentionally left open for the requested user inspection. No printing,
printer communication, merge or release was performed. No manual file operation
edited/deleted/staged the unrelated `log_iotc.txt`.
