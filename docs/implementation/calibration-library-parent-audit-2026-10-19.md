# Prepared calibration library parent audit

Date: 2026-10-19. Branch: codex/calibration-matrix-library.
Canonical base: f620b1ef5df2bf4a7ea883bd359a63936d7c465a.
Authority: accepted ADR0073 and SPEC_VALIDATED
`../specs/prepared-calibration-matrix-library.md`. Independent repository review:
minheight_research; separate emission and UI implementers. No dependency added.

Parent owns canonical summaries, ADR inventory and integrated verification.
Emission owner owns finite V2 experiments/offline preparation/assets; UI owner owns
resource bridge/capability/refinement requests/wheel. Independent review precedes
source freeze/full regression. Lint and type tools remain NOT CONFIGURED.

Before changes, source raw V1 SHA256 was verified as
`eba3727f0c32d05ad4d03f681c06c46ae376232b16087c4589be822a5c5154f3`.
All25 raw sample XYZ/E values still match the conditions CSV. Column E per10mm is
.00031/.00062/.00125/.00249/.00499; nominal display width remains .45mm for all25.
This is commanded-volume calibration, not a physical-width prediction.

The old V1 `.gcode.3mf` was externally saved as geometry-only before this task's
snapshot (SHA256790cb445e65adbe5ad96e3a0cd704d939de2b3946c694730b6aee2d3f41b9de5,
no .gcode member). The earlier archive-equality checker therefore fails at its
archive assertion, while raw25-cell checks pass. Preserve this externally saved
archive; use separately named new packages only. The genuine original sliced
source remains SHA2561fd57a23c41dbcc7c6a307f6a4c8e1fc547bacbe3ac3ac3f819d1437edab38ef.

Evidence: `artifacts/calibration-matrix-library-v1/protected-before.json` and
`original-raw-25cell-recheck.json`. The former pins unrelated log_iotc.txt and
historical raw/source/reference packages. No printer submission or merge is in
scope for this task.


## Integrated audit and review reconciliation

All four final ready-v5 raw files were independently parsed against separately
stated axes and fixed conditions:100cells, source prefix/suffix preservation,
XYZ, first2mm/remainder E, full-line E, drawing feed, end retraction/wipe,
start debt recovery and fixed30mm/s ceiling reconciliation all pass. Historical
h_volume raw remains byte-identical. See `independent-commands-receipt.json`.

Primary findings corrected before freeze: rendered JavaScript newline escaping;
unknown-current-profile must not disable geometry-only baseline export; approved
refinement caps; CSV/frozen conditions and ZIP path aliases; export-scope metadata
and bundle provenance; resolution-limit request persistence; explicit fixed
ceiling field shared by catalog/CSV/frozen cells. Independent blind reviewer
additionally identified endpoint narrowing mislabeled as expansion (M1), closed
by an explicit offline-range-review request rather than invented axes. Optional
G-code archive contents now match raw bytes. No unresolved material finding.

Actual ready-v5 bundle SHA256
`c233cccba08587b1e57a99b4608ae8fb4bc5755506fd5a961b377087db777cbc`.
Delivered wheel SHA256
`1ba5353e7090f1c68adadce0559133809a8fe0248f46a6a7ab2d46a1b73bcedc`.
Parent verified all RECORD hashes, package sources against the tree, bundled bytes,
isolated wheel-only import, all4 exact exports and result reopen. Browser operation
verified four real-data tables, selected-cell/proposal/export messages, no-acceptable
cell=null, and actual rendered screenshot. Browser host bridge was a stub.
Windows native Orca was launched and accessibility read succeeded, but Prepare-tab
click failed with `coordinate input geometry is unavailable`. New capability
invocation in the real Orca menu remains unverified. No wheel installation or
printer submission is claimed.

## Historical byte-pin repair

First full run:1103tests,3failures/2errors, all from an unchanged historical recipe
failing at its first documentary SHA pin. Source/test tree stayed unchanged during
that run and all protected files stayed unchanged. Root cause was prior Git
text/checkout normalization:5 pinned Python files were converted LF->CRLF; one
pinned document originally used LF body plus one CRLF final newline. Reconstructing
these newline bytes exactly recovers all6 immutable expected SHA256 values, with
no logical content changes. Independent reviewer reproduced the result.

Six exact paths now have `.gitattributes -text`; the mixed-final-newline document
also declares legitimate `whitespace=cr-at-eol`. Neither hashes, manifest,
reader nor tests were weakened. `git diff --check` passes. Evidence:
`historical-pin-failure.json` and `historical-pin-repair-receipt.json` in the parent
artifact folder. A fresh full run follows the nearest historical suites after
repair; it also snapshots the attributes and pinned report.


## Final verification

Nearest repaired historical suites:6tests PASS in213.790s. Fresh full command
`.venv\Scripts\python.exe -m unittest discover -s tests -v`:1103tests PASS
in429.483s, exit0. Final receipt:
`artifacts/calibration-matrix-library-v1/full-regression-v2/receipt.json`;
logSHA256 `2fad08ea4aea0a7f79d2360f5303ecdd81225edbd8b434f2b323915b7a26be28`.
Source/tests plus pinned attributes/report stayed unchanged during the run;
all7 protected files stayed unchanged. Final focused emission30/architecture45
and plugin27 checks, independent4case100cell/nominal/state/source/archive audit,
actual locked wheel export and browser UI evidence are separately retained.
Default actual unbundled wheel also imports in isolation and honestly returns no
prepared bundle; it was built into a separate artifact folder, preserving the
calibration distribution wheel. No new dependency, printer submission, commit,
push or merge was performed in this task.
