# True-Z review continuation in C:\VSC\Smoothificator

Update: the later user side-view feedback and its display correction are
recorded in `true-z-diamond-preview-2026-10-17.md`, superseding the pending
native side-view status below.

Scope: fixture-only diagnostics and display, not production geometry or injection.
Base: `06d4db856708283c44b4476d1d16cb9fd83c14f6`, branch
`codex/true-z-review-handoff`. Draft PR #8 was not merged or released.

## Workspace and source evidence

The destination was initially empty. The old checkout was copied without deleting
the original. `log_iotc.txt` was excluded and the old checkout still reports only
`?? log_iotc.txt`. A new Python 3.12.10 `.venv` was created in the destination.
`git fetch origin`, `git switch codex/true-z-review-handoff`, and
`git pull --ff-only origin codex/true-z-review-handoff` succeeded there.
No CodebaseMemory operation was needed.

The full first copy encountered access-denied files in Orca's bundled Python;
it was stopped, then source and required fixtures were copied successfully
with runtime/cache/source-extract directories excluded from the retry.
The portable Orca executable and its main libraries had already been copied
and could load the review. This is not a claim of a complete relocated Orca
Python/plugin installation. Existing tooling in the old checkout was used only
to capture an image; all new output was saved in the new destination.

The relocated 3MF, STL and original slice SHA-256 values match the constants
in `tools/generate_top_surface_candidates.py`. The original slice remains
`499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e`.

Commands in the new workspace:

```
.venv\Scripts\python.exe -m tools.generate_top_surface_candidates
.venv\Scripts\python.exe -m tools.build_true_z_orca_review --focus --show-unverified
.venv\Scripts\python.exe -m tools.render_top_surface_3d_review
.venv\Scripts\python.exe -m tools.audit_top_contact_cells
```

The new review is
`artifacts/geometry-review/smoothificator-d29299b775e247cd91ebf17e4b8e7e8c.UNVERIFIED_VIEW_ONLY.gcode`
with an adjacent JSON manifest, 12 layers and only `top-07` as Custom.
`printable_authorized` remains false.

## Contact diagnostics

`tools/audit_top_contact_cells.py` uses the existing exact nominal cell query.
It subdivides closed rational rectangles, with finite depth/cell budgets and
an unresolved result when remaining rectangles cannot be certified. This is
continuous area bounding, not a finite point-sampling certificate.

The audit uses the emitted six-decimal candidate coordinates. It separately
tests the flat central 0.20-mm strip at bottom Z=2.14 mm and a 0.001-mm strip
at the positive-Y rounded edge. For the latter it algebraically checks a
conservative bottom lower plane Z=2.198 mm. The stadium's outer edge bottom
rises to Z=2.21 mm; comparing every XY point to Z=2.14 would miss this.

Results and rational witness rectangles are retained in
`artifacts/geometry-review/top-07-contact-cells-height-0.14.json` (the original
`top-07-contact-cells.json` snapshot, retained before the later height change).
At depth 18, the central strip is covered by 820 certified leaves (1,639
queries), with zero gaps and zero unresolved leaves. Thus its full 9.4-mm
length has nominal intersection with lower material, including penetration.
The positive-Y edge audit has 334 gap leaves, 359 reaching the conservative
plane, and 354 unresolved leaves (2,093 queries). Reaching that conservative
plane is not a certificate of edge contact with the actual curved bottom.
The edge has proven local nominal gaps. This does not establish that the
entire bead is levitating: central contact, edge gaps, nominal penetration,
and printer bead deformation are distinct questions. A fully supported,
shape-improving and collision-free additive path is not established.
No candidate is promoted by this audit. Candidate geometry is preserved for
comparison; simply increasing height would introduce more nominal penetration
without establishing better shape or tool clearance.

The HTML legend now explicitly describes verified-contact candidates (currently
zero) and unverified/excluded reference lines. Green Custom in Orca's native
feature palette is only a category color, not evidence of validity.

## Native UI evidence and limitation

The dedicated relocated executable loaded the generated file with
`--datadir C:\VSC\Smoothificator\artifacts\orca-profile <review-file>`.
An attempted `--gcodeviewer` invocation exited without opening a window; it
was replaced by the successful positional-file invocation.
The native Preview shows Custom, `;Z:2.28`, `;HEIGHT:0.14`, and disabled
slice/export controls.

Computer Use screenshot capture failed twice with
`SetIsBorderRequired failed: ... (0x80004002)`. A task-window Pillow capture
was saved and visually inspected at
`artifacts/geometry-review/orca-migrated-loaded.png`.
Windows Defender's firewall permission dialog overlaps the workspace.
The user was asked to cancel it manually; no security permission was changed.
Side-view rotation and acceptance remain pending until that obstruction is
removed. Loading a file and inspecting its metadata are not side-view proof.

## Validation

Python 3.12.10. No dependency was added. Lint and type tooling remain
NOT CONFIGURED for this bounded research change.

- `python -m compileall -q tools tests`: PASS.
- `python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 43 PASS.
- `python -m unittest tests.unit.test_top_contact_cells tests.unit.test_true_z_orca_review -v`: 14 PASS.
- `python -m unittest tests.unit.test_top_surface_candidates -v`: 4 PASS, local pinned fixtures present.
- `python -m unittest discover -s tests -p 'test_*.py' -q`: 645 PASS in 84.558 s; `artifacts/geometry-review/migration-full-tests.log`.
- Extracted generated HTML JavaScript, `node --check -`: PASS.
- `git diff --check`: PASS.
- `python tools/build_validation_artifacts.py`: PASS (tracked-source research archive only; not evidence that these untracked diagnostic additions are packaged).

Focused logs are under `artifacts/geometry-review/`. The new narrow-gap test
initially reached the default subdivision limit without proving the gap; it
now explicitly supplies depth 18 and proves the between-samples gap. Resource
exhaustion separately remains tested as unresolved.

No physical print, printer connection, printable output, commit, push, merge,
or release was performed. The remaining native side-view acceptance and
geometry/shape/tool-clearance gates are open.
