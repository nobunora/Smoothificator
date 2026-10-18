# Uniform Z lowering: continuous contact versus buried correction

Superseded by the user's line-relative +/-10% limit. The 0.635-mm drop below
is a rejected historical experiment. Current behavior and verification are in
`line-thickness-z-limit-2026-10-17.md`; the builder now rejects the old drop.

User request: investigate lowering Z uniformly to avoid trimming unsupported
X intervals. Scope remains offline research and standard Orca Preview only.

## Result

Uniformly lowering all ten planned lines by **0.635 mm** satisfies the nominal
stadium and conservative native-diamond **centerline upper-envelope contact**
conditions over the entire original X=[80.3,99.7] mm. No X interval is removed.
Line widths and heights are unchanged: widths approximately 0.283 mm,
heights approximately 0.05 mm, within the user's 0.25..0.45 mm width and
0.05..0.18 mm height limits for this configured 0.20-mm slicer layer height.

This result is **not an accepted interpolation path**. All translated tops
fall below their original flat terrace floors. Remaining rectangular height
above those floors is zero. Certified nominal peak witnesses are roughly
0.585 mm above the translated candidate tops: the experiment is substantially
buried in the reconstructed final-baseline envelope. Small actual bead valleys
may be affected, but full-surface error reduction has not been established.

For some lines the nominal support-height variation is certified to be at
least 0.599609375 mm. A constant-Z line of at most 0.18-mm height cannot both
reach all those valleys and stay above all existing peaks. This rejects a
uniform drop as a useful whole-step fill correction; it is not a proof that
other XY placement, varying Z/height, or other reconstruction is impossible.

Sufficient individual drop bounds (not exact minimum drops):

| Terrace Z mm | Drop sufficient for both centerline models, mm |
| --- | --- |
| 3.0, 4.8 | 0.100586 |
| 3.2 | 0.491211 |
| 3.4, 3.8, 4.2, 4.6 | 0.480469 |
| 3.6, 4.0, 4.4 | 0.633789 |

The common 0.635-mm drop rounds the maximum bound upward and adds 0.001 mm.
The source/model hashes and exact rational bounds are in
`artifacts/cuboid-tilt10-review/uniform-z-contact.json`.

## Continuous proof and its limits

`tools/audit_line_support.py` clips the support region of each horizontal
source bead against the candidate centerline using rational affine predicates.
For nominal stadiums, a requested support level determines the supported
lateral radius. Inner and outer square-root bounds give conservative support
intervals and gap witnesses. Diamond lower bounds use the finite source body;
upper bounds conservatively include pointed-cap axial extensions.

Sorted closed inner intervals must cover the full X domain without gaps.
This quantifies every real X, not a finite set of sampled points. A bisection
finds certified support-floor bounds to about 0.001 mm. Point/interval witnesses
only bound extrema from one side; they never grant continuous contact.
The complete original baseline is retained, including later layers. One
unsupported sub-height gap-infill segment at Z=0.4 mm is omitted from these
top queries because it lies below the entire bounded translation domain.

An early closed-rectangle 0.02-mm-wide search remained unresolved under its
coverage/time budget; that negative attempt is preserved separately as
`uniform-z-strip-attempt.json`. It has not been relabelled as successful.
The interval implementation also exposed artificial gaps of about 5e-41 mm
when exact rational square roots were replaced by inward dyadic bounds at
shared boundaries. Exact rational perfect roots are now retained in this
research adapter. Genuine small gaps still fail; no epsilon-merging is used.
The production support-cell engine was not modified.

**The proven scope is a continuous centerline upper-envelope condition.**
Finite-width contact, actual solid-volume intersection, bead deformation,
chronological nozzle clearance and printable safety are not established.
Viewer coordinates are rounded to nine decimals; mathematical certificates
refer to the exact rational research plan. A visual match is not the proof.

## Implementation and review artifact

- `tools/analyze_uniform_z_contact.py`: source-bound support/drop/burial report.
- `tools/audit_line_support.py`: exact interval coverage and minimum bounds.
- `tools/build_uniform_z_review.py`: separately labelled burial comparison.
- `tools/build_tilted_cuboid_review.py`: share native scene rendering; default
  rectangle candidates and rejection behavior are preserved.
- `tests/unit/test_line_support.py`, `test_uniform_z_contact.py`: exact joins,
  narrow genuine gaps, lower support, source/project hash binding, insufficient
  translation rejection, all-baseline retention, and unchanged rejection flags.

Reproduce analysis and the comparison without re-slicing:

```
.venv\Scripts\python.exe -m tools.analyze_uniform_z_contact
.venv\Scripts\python.exe -m tools.build_uniform_z_review
```

Current comparison manifest:
`artifacts/cuboid-tilt10-review/current-uniform-z-review.json`.
It references the unique `UNVERIFIED_VIEW_ONLY.gcode`, contains ten probes
and all 6,071 baseline extrusions, and keeps printable/useful-interpolation/
shape-improvement/full-footprint-contact flags false. Native green Custom
means a viewer category, not an accepted path. The comparison is left open
alongside the unchanged baseline viewer for user inspection.

No physical print, printer connection, merge, release or operation on
`log_iotc.txt`. No dependencies added; lint/type tooling remains unconfigured.
Final validation results and visual evidence are appended below.

## Final verification

Python 3.12.10: compileall PASS; architecture 43 PASS; focused contact/rectangle
suite 30 PASS; full unittest discovery **700 PASS in 79.109 s**;
`git diff --check` PASS. Logs are the `uniform-z-*-tests.log` files in the
review directory. No safety flag was weakened to obtain these results.

Orca standard Preview is open with
`cuboid-uniform-z-contact-e11f26879c904b2da710b0e6a705cc64.UNVERIFIED_VIEW_ONLY.gcode`.
Native Preview recognizes 35 layers and the Custom category. A selected-process
PrintWindow/Pillow capture was opened and inspected:
`artifacts/cuboid-tilt10-review/orca-uniform-z-final.png`.
The added lines are buried; their presence in a category/scene is not visual
proof of contact or useful interpolation. Full baseline remains visible.
The keyboard camera shortcut did not establish an accepted side-view check;
no side-view or full-width-contact acceptance is claimed.
