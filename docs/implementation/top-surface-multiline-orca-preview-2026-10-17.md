# Top-surface multi-line Orca Preview probe

Disposition: bounded native visual display PASS; executable candidate FAIL.
This record supersedes the underside
single-line candidate in the earlier layered viewer *for future research*.

The fixed-hash offline generic Marlin slice of `offline-coupon.3mf` remained
SHA-256 `499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e`.
The ignored research builder `artifacts/build_orca_layered_overlay_probe.py`
reconstructed the same 669 baseline extrusions on 15 layers. It selected only
the 18 `Top surface` source segments at each of Z=2.2 and 2.4 mm; no underside
segment was used to generate a candidate. Direct segment-by-segment midpoint
pairing collapsed to one horizontal line, so the builder interpolated the
coupon's top-surface centerline envelope at true Z=2.3 mm and covered its
2.674-mm Y span with seven parallel paths. Their display width is 0.4 mm and
centerline pitch is 0.379 mm. These values bound a visual rectangular fill,
not a certified footprint of the actual model.

The new display-only viewer file is
`artifacts/layered-viewer/smoothificator-0f17b22cd4744c848b2e427bae9bf4bc.VIEW_ONLY.gcode`,
SHA-256 `ad6344db331bf324098d4f52a1a99e240d0a57637383d126f6a29fc666d05025`.
Its adjacent JSON records the source digest, 18+18 source top-surface line
numbers, each of the seven display centerlines, the true Z=2.3 mm and the
projected viewer Z=2.4 mm, with support and printable flags false. A bounded
check confirmed 15 viewer layers, 669 original segments, seven `Custom` tags
only on the Z=2.4 mm layer, positive pitch no greater than width, and an
unchanged source digest.

The dedicated Orca viewer opened this representation in standard Preview.
At layer 12 / Z=2.4 mm, the red original top-surface hatch and seven green
Custom lines appear together. A targeted Python Pillow/pywin32 window capture
is at `artifacts/layered-viewer/orca-top-multiline-final.png` (2560x1400,
SHA-256 `d20c6fc7302bfe9a1ae28b26666c292795ccbb881a1b2e668c883a4a2025d5974`).
The layer slider and disabled slice/export controls are visible. The original
G-code was not modified; no printer connection or output operation occurred.

This is not a shape-preservation result. The top-surface envelope can include
points outside the mesh, and viewer projection puts true Z=2.3-mm candidates
on the existing Z=2.4-mm layer. Minimum/maximum bead-width policy, structural
support, collisions and exact affected-surface error are not proven. The
positive-E VIEW_ONLY file must not be printed. Production integration awaits
the top-only, multi-path specification and its geometry/output gates.

## Executable-candidate audit after user review

The displayed Z=2.4 mm is not the proposed Z=2.3 mm. The seven paths also
overlap already scheduled Z=2.4 mm structural extrusion footprints. Closest
centerline distances to an original path, in ascending candidate Y order, are
0, 0, 0, 0, 0, 0.1645 and 0.1885 mm. The corresponding nominal footprint
clearances after subtracting half the two recorded widths are all negative:
-0.4068 mm for the first five (Top surface), -0.2605 mm for the sixth
(Inner wall), and -0.2115 mm for the seventh (Outer wall). The source G-code
line numbers for the nearest paths include 1357/1354/1350, 1330 and 1339.
The first five each geometrically cross 14-15 original top-surface centerlines.
At the prior Z=2.2 mm layer, five of the seven candidates likewise intersect
14-15 top-surface centerlines. These are direct defects of the additive
viewer geometry, not merely missing hardware tolerances.

Consequently none of the seven may be converted into an executable insertion.
The dedicated invalid viewer was closed, the source remains unchanged, and no
modified printable G-code was published. A future plan must use true candidate
Z, account for the material and motion on both adjacent layers, prove an
actual reduction in full top-surface error, and validate the chronological
nozzle/hotend clearance before any G-code mutation. Existing research Settings
v2 deliberately raises `PHYSICAL_INJECTION_NOT_AUTHORIZED` when injection is
requested; there is no production injector in this checkout.

`tools/audit_layered_preview_overlap.py` now reproduces this fixture audit
read-only. It SHA-pins the original source, parses its recorded extrusion
segments, measures horizontal candidate-to-structural centerline distance,
subtracts both nominal half-widths, and returns `rejected` with seven negative
clearances and `printable_authorized: false`. The manifest's candidate and
per-layer counts must agree, so a missing segment cannot silently pass this
screen. It measures the displayed layer only: actual-Z adjacent-layer and
chronological nozzle/hotend clearance remain unverified. Python 3.12.10
compile/import, 43 architecture tests, eight focused audit tests and the
627-test full suite passed. No G-code writer or physical injection flag was
enabled.

## True-Z 3D review and bead-height correction

The initial seven-line envelope fill is superseded for review. A pinned 3MF
build transform plus the pinned Orca plate offset now produces top-face
isocontours at their actual XYZ coordinates. Five 0.4-mm-wide review lines
at Z=2.22, 2.26, 2.30, 2.34 and 2.38 mm lie on the transformed upward top
face. The first two avoid the higher-layer XY footprint but their minimum
sampled effective bead heights above the Z=2.20-mm source material are only
0.02 and 0.06 mm, below the 0.08-mm research/fixture minimum. They were
removed from the focused Orca viewer. The last three have heights 0.10,
0.14 and 0.18 mm but overlap higher-layer structural footprints; they too
are excluded.

A bounded width/Z search found one *review-only* alternative at Z=2.28 mm,
Y=127.336335 mm, X=120.3–129.7 mm and width 0.30 mm. Its sampled lower
support top is Z=2.20 mm across 21 X positions and three Y offsets; the
sampled effective height is 0.08 mm. Its nearest later-layer XY footprint
clearance is 0.038 mm. That tiny clearance is not a physical tool margin;
the 0.30-mm minimum width is also not yet validated against an actual
printer/profile. It is a geometry-review hypothesis, not a printable path.

`tools/generate_top_surface_candidates.py` records six mesh-clipped true-Z
lines, their rejection reasons and source hashes in an ignored local JSON.
`tools/build_true_z_orca_review.py --focus` reconstructs the original
slice through Z=2.20 mm and adds only the Z=2.28-mm Custom review line,
with viewer bead height 0.08 mm. The original source slice remains unchanged.
The focused VIEW_ONLY file has 12 display layers, an adjacent manifest with
`printable_authorized: false`, and no machine setup, homing or heater commands.
Dedicated Orca loaded it in standard Preview and displayed a separate
Custom category and the `;Z:2.28` / `;HEIGHT:0.08` commands. A window
capture is at `artifacts/geometry-review/orca-bonded-review-loaded.png`.
The user additionally inspected the earlier Z=2.22/2.26 side view and
reported those lines floating, consistent with the computed subminimum
heights.

`tools/render_top_surface_3d_review.py` also generated an offline,
self-contained 3D canvas comparison showing the transformed top face,
original slice, one hypothesis and five excluded reference lines. Its
JavaScript passed `node --check`; browser visual acceptance was unavailable
because the local file URL was blocked by the browser security policy.
No shape-error improvement, full-area support, width feasibility or
chronological tool clearance is established.

## Exact lower-bead check after side-view feedback

The user inspected the focused Z=2.28-mm Custom line and reported that it
still floats and appears to have nearly zero thickness. The line is not
zero-volume: its 9.4-mm length, 0.30-mm width and 0.08-mm nominal height
give a rounded-rectangle cross-section of 0.022626548 mm² and volume
0.21268955 mm³. With the source's 1.75-mm filament diameter, the viewer's
synthetic `E` increment is about 0.088426 mm. Orca's coarse filament-length
and mass labels can therefore show 0.00 without implying zero geometry.

The earlier sampled support check used source-line XY footprints and treated
all points within a width as having the full source top Z=2.20 mm. That was
insufficient. An exact nominal top query against the pinned source bead
heights, at 95 positions along the candidate and the center plus both width
edges, found a conservative lower top of Z=2.161310 mm. A nominal 0.08-mm
bead commanded at Z=2.28 has its bottom at Z=2.20 mm, leaving up to about
0.03869 mm of nominal gap. This accounts for the visible floating sections.

The generator now marks this sixth line `nominal-support-valley`; the Orca
viewer builder refuses to display it as an accepted Custom candidate. The
other five lines already failed minimum height or higher-layer footprint
checks, so this pinned unchanged-source coupon currently has **no accepted
additive review line**. The previously opened focused VIEW_ONLY artifact is
superseded and must not be treated as an improved or printable slice. This
check is still sampled and nominal; it does not certify continuous support,
printer tolerances, or collision clearance. Correctly supported geometry
requires a new candidate construction and a separate validation pass.

An independent code review also found that the 95-by-3-point nominal probe
cannot prove continuous contact or exclude a narrow material intrusion
between samples. The generator therefore never promotes a line solely from
that sampled check: otherwise plausible lines are marked
`continuous-contact-unverified`. The VIEW_ONLY builder requires an explicit
continuous-contact result and consistent bead-height metadata before it can
show a green candidate. No such certificate is produced by this research
generator, and no printable G-code path is enabled.
