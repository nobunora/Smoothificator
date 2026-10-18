# Correct Z adjustment scale: +/-10 percent of line thickness

User correction: the previous 0.635-mm global drop was far beyond the line
thickness and buried the correction. Start with approximately +/-10 percent
of each actual line thickness. That instruction supersedes the large-drop
display trial; its result must not guide an accepted correction.

## Changes

`tools/analyze_thickness_z_offsets.py` evaluates -10%, -5%, 0%, +5%, +10%
of each line's exact physical height. The height comes from the solved
rectangle, not the configured 0.20-mm default layer height. For a 0.05-mm
line, the maximum absolute adjustment is exactly 0.005 mm. The old 0.635-mm
drop was about 12.7 line heights, or 127 times this adjustment limit.

Both nominal and diamond centerline coverage are audited over the entire
unchanged X interval with exact interval unions. The whole rectangular bead
envelope is also checked against the original target plane. Offsets beyond
the line-relative limit are rejected, rather than used to manufacture contact.
No X clipping, physical-height change, width-limit change or blanket top hatch.

The default `tools.build_uniform_z_review` command now reads the bounded
comparison and emits `cuboid-thickness-z-*.UNVERIFIED_VIEW_ONLY.gcode`.
Its historical large-drop build function has an explicit per-line 10% guard;
replaying the previous 0.635-mm analysis cannot recreate that viewer through
this builder. Previous artifacts remain as historical evidence.

## Result on the actual 10-degree fixture

All ten solved heights are approximately 0.05 mm. For -10%, the offset is
approximately -0.005 mm and 90% of the rectangular height remains above its
original terrace floor (about 0.045 mm). The physical bead thickness stays
unchanged. This is a placement comparison, not certified surface improvement.

| Offset fraction | Within target envelope | Full centerline contact in both models |
| --- | --- | --- |
| -10% | 10/10 | 0/10 |
| -5% | 10/10 | 0/10 |
| 0% | 10/10 | 0/10 |
| +5% | 0/10 | 0/10 |
| +10% | 0/10 | 0/10 |

Positive offsets exceed the conservative rectangular target-plane bound for
these already maximal rectangles and are rejected by the viewer builder.
The selected -10% comparison keeps all ten full-length lines visible as
UNVERIFIED probes. It does not relabel them as valid paths or conceal gaps.
The remaining contact problem must be addressed by geometry/placement changes
within this bounded scale, not by large uniform downward translation.

Artifacts under `artifacts/cuboid-tilt10-review/`:

- `thickness-z-offsets.json`: five cases, exact offsets, source/model bindings,
  envelope checks, analytical gap witnesses and retained-height fractions.
- `current-thickness-z-review.json`: selected -10% native representation and
  SHA-256. Full baseline retained: 6,071 source extrusions plus ten probes.

The old excessive-drop Orca instance is closed and replaced by the bounded
comparison. The independent baseline viewer remains available. Native Custom
green is a category, not a valid-path status. Printing, full bead-width contact,
solid-volume contact, nozzle clearance and global residual improvement remain
unverified. No printer connection, printable authorization, merge or release.
`log_iotc.txt` is untouched and unstaged. No dependency added.

## Verification

Tests include line-relative units (0.005 vs a layer-relative 0.02), inclusive
10% boundaries, excessive-drop rejection, exact 90% height retention, positive
target-envelope rejection, tampered-offset rejection, source/project identity
and retention of every baseline segment. Final results are appended below.

Python 3.12.10: compileall PASS; architecture 43 PASS; focused 13 PASS;
full regression **703 PASS in 86.750 s**; `git diff --check` PASS.
Logs: `thickness-z-architecture-tests.log`, `thickness-z-focused-tests.log`,
`thickness-z-full-tests.log` under the review directory. Lint/type tooling
remains NOT CONFIGURED.

Orca is open with the -10% comparison
`cuboid-thickness-z-77a1a5d7908c45c197412d84cf38b5e6.UNVERIFIED_VIEW_ONLY.gcode`.
Standard Preview recognizes 35 layers and Custom. The dedicated-process
PrintWindow/Pillow capture `orca-thickness-z.png` was opened and inspected.
Visual display confirms loading only, not contact or print acceptance.
