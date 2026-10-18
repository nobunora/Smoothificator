# Orca side-view floating correction (research only)

This continuation supersedes the pending side-view status in
`true-z-local-migration-2026-10-17.md`. The user dismissed the firewall dialog
and observed a small gap below the 0.14-mm green line in a zoomed side view.
Workspace remains `C:\VSC\Smoothificator`; base is `06d4db8`.

## Cause and bounded correction

The previous exact support-cell audit used the nominal stadium cross-section.
Orca's default libvgcode visualization instead uses a diamond cross-section.
These represent different lower surfaces; a stadium intersection result is
not a diamond contact certificate. Orca also shifts extrusion centers down by
half the recorded height, so command Z is still the top of the displayed bead.

Primary renderer source pinned to `86905a8a20d5887f3b13017e66cd897766334bd3`:

- [ViewerImpl.cpp](https://github.com/SoftFever/OrcaSlicer/blob/86905a8a20d5887f3b13017e66cd897766334bd3/src/libvgcode/src/ViewerImpl.cpp), `extract_pos_and_or_hwa`: subtracts height/2 from extrusion Z.
- [Shaders.hpp](https://github.com/SoftFever/OrcaSlicer/blob/86905a8a20d5887f3b13017e66cd897766334bd3/src/libvgcode/src/Shaders.hpp): half-width/half-height diamond vertices and pointed axial caps.
- [LibVGCodeWrapper.cpp](https://github.com/SoftFever/OrcaSlicer/blob/86905a8a20d5887f3b13017e66cd897766334bd3/src/slic3r/GUI/LibVGCode/LibVGCodeWrapper.cpp): transfers move position, width and height into preview vertices.

Downloaded source snapshots are retained locally under `artifacts/orca-source`.
They support the renderer model investigation, not a physical bead claim.

`top-07` keeps command Z=2.28 mm, Y=127.336335 mm, X=120.3–129.7 mm and
width 0.34 mm. Its research display height changes from 0.14 to 0.19 mm.
The lowest point therefore moves from Z=2.14 to 2.09 mm. No display-Z
projection or hidden coordinate shift was added. The earlier file and plan
remain available for comparison. Height 0.19 increases overlap with lower
material; this is a display hypothesis, not an optimized extrusion path.
The later-layer XY clearance remains approximately 0.018 mm and is not a
nozzle clearance margin.

## Continuous renderer-model evidence

`tools/audit_orca_diamond_contact.py` adds a research-only diamond model.
It reuses the bounded closed-cell subdivision in `audit_top_contact_cells`.
Lower bounds require a whole cell to lie inside one finite source body;
upper bounds include a conservative half-width axial cap extension. Exact
rational arithmetic and outward square-root bounds avoid a point-sampling
certificate. No production engine or injection contract was changed.

`artifacts/geometry-review/orca-diamond-contact.json` records:

- Old 0.14-mm height: a closed witness at X=129.6106–129.6108 mm,
  Y=127.336334–127.336336 mm has source top upper bound approximately
  2.1053997635 mm. The candidate bottom is at least 2.14 mm, so the local
  diamond-model gap is at least 0.0346002365 mm. The bounded broad audit also
  finds gap cells; unresolved cells do not erase this witness.
- New 0.19-mm height: 143 cell queries produce 72 certified leaves, zero gap
  leaves and zero unresolved leaves for the entire 9.4-mm length and central
  0.02-mm strip. The maximum candidate bottom over that strip is
  2.0955882353 mm. Thus the reference diamond geometry intersects lower
  material throughout that strip, including penetration.

This is a certificate for the mathematical reference geometry with source
decimal coordinates. It is not a GPU floating-point error certificate, full
footprint contact, physical adhesion, improved surface error, or chronological
tool-clearance proof. `continuous_contact_verified` in the generator remains
false; the renderer audit never promotes this to an accepted path.

The nominal stadium audit remains separate. Its rounded-edge plane is now
computed from the actual height instead of a hardcoded 0.14-mm assumption.
The HTML warning identifies the current 0.19-mm hypothesis and penetration.

## Native standard Preview evidence

New artifact:
`artifacts/geometry-review/smoothificator-a98153cdfbf640d4bb7cac2fb4981921.UNVERIFIED_VIEW_ONLY.gcode`
and adjacent manifest. It has 12 layers and only `top-07` as Custom.
The SHA-pinned original slice is unchanged and `printable_authorized` is false.

The dedicated relocated Orca opened the new file in standard Preview. We
inspected both a left side view (line cross-section) and a front view (line
length). The visible green profile meets/overlaps the original slice in those
views, with no whole-line floating gap apparent. These screenshots are visual
evidence only, not an independent continuous contact or print-safety test.

- `artifacts/geometry-review/orca-corrected-current.png`: oblique close-up.
- `artifacts/geometry-review/orca-corrected-left-accepted-view.png`: left view;
  "accepted" in the local filename refers only to capturing this view.
- `artifacts/geometry-review/orca-corrected-front-final.png`: full line length
  in front view, current native window left here for user inspection.

Computer Use screenshot capture remained unavailable. Python/Pillow plus
PrintWindow captured the exact dedicated process/window, including when
occluded; images were opened and inspected. Some earlier screen-area grabs
could capture a foreground occluding app, so they are not used as final visual
evidence. Manual and agent inputs briefly conflicted; the window state was
refreshed before further input.

## Changed files and verification

Research tools: `generate_top_surface_candidates.py`,
`audit_top_contact_cells.py`, `audit_orca_diamond_contact.py`,
`render_top_surface_3d_review.py`. Tests: `test_top_surface_candidates.py`,
`test_orca_diamond_contact.py` plus the preceding migration's contact tests.
This record explains the source agreement and limited acceptance criteria.
No production module, printer settings or original source slice was modified.

Python 3.12.10; no dependency added. Lint/type checks remain NOT CONFIGURED.

- `python -m compileall -q tools tests`: PASS.
- `python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 43 PASS.
- `python -m unittest tests.unit.test_top_contact_cells tests.unit.test_orca_diamond_contact tests.unit.test_true_z_orca_review -q`: 20 PASS.
- `python -m unittest tests.unit.test_top_surface_candidates -v`: 4 PASS with local pinned fixtures.
- `python -m unittest discover -s tests -p 'test_*.py' -q`: **651 PASS**, 73.812 s.
- Extracted HTML JavaScript, `node --check -`: PASS.
- `git diff --check`: PASS.
- `python -m tools.audit_top_contact_cells`: PASS for the new height; old 0.14-mm nominal results retained separately.
- `python tools/build_validation_artifacts.py`: PASS for the tracked-source research archive; it does not package these untracked research additions.

Logs: `artifacts/geometry-review/diamond-focused-tests.log`,
`diamond-top-surface-tests.log`, `diamond-full-tests.log`.

The rejected alternative was treating the stadium audit or a screenshot as
proof of the renderer's whole-line contact. Simply lowering command Z would
also move the top below the intended true-Z contour. The chosen height change
retains that contour while exposing more penetration for review. To compare
the old behavior, open the retained old UNVERIFIED_VIEW_ONLY file; no source
or production rollback is required.

No printing, printer connection, printable output, push, merge or release.
Remaining work is shape-error improvement, physical bead feasibility and
chronological nozzle/hotend clearance before any executable-path proposal.
