# Nonlinear dimension taper: parent audit

Date: 2026-10-18. Contract: ADR-0071. Final artifact is the V2 trial in `artifacts/gui-angle0to45-smooth-dimensions-v1/trial-smooth-dimensions-v2/`.

## Behavior and limits

The coupon retains its original 0–45 degree geometry and angle admission ceiling 33.95770549 degrees. For each original supplemental root, keep original dimensions through 10 degrees. Above that, let t = clamp((angle - 10)/(ceiling - 10), 0, 1), R = 1 - (6t^5 - 15t^4 + 10t^3). Target height = 0.08 + (original height - 0.08)R; target width = 0.21 + (original width - 0.21)R. Both ends have zero first and second derivatives. This is a trial heuristic, not a physically calibrated optimum. Actual source dimensions vary, so monotone retention is not a claim that all paths' absolute dimensions are monotone.

Bottom planes, centerlines and lengths remain unchanged. Actual top Z follows the new height. Ordinary full cross-section extrusion is recomputed; no old 25% or 50% multiplier is compounded. Retraction 1.6 mm and reverse wipe 1.0 mm are retained. The saved 0.2 mm layer height still binds the strict height cap. Positive minimum dimensions necessarily leave a nonzero endpoint at the admission cutoff. The curve removes intermediate minimum-thickness deletion holes; it cannot eliminate all physical boundary steps or pressure-related excess deposition.

All 41 original roots in 24 groups remain. Nine plateau paths preserve original dimensions and deposition E exactly. Numeric E rounding initially rejected two minimum-width paths. Exhausting ordinary width candidates before a single bounded 0.001 mm expansion resolves these at width 0.211 mm, height 0.08 mm. This expands each side by 0.0005 mm; fresh geometry evidence includes it. Standard numeric admission tolerances were not relaxed. The 39-path V1 intermediate is retained as diagnostic evidence, not the delivered artifact.

## Independent and artifact checks

Separate implementation and research agents reviewed source and replayed all actual angle targets, dimension lattice choices, E values, source recovery, state restoration and package members. Focused nine-suite regression: 55 tests passed. Final authoritative Python 3.12.10 full regression: 1,028 tests passed in 545.230 seconds, exit 0. Source/tests remained unchanged throughout; protected historical inputs and log_iotc.txt also remained unchanged. Receipt: `artifacts/gui-angle0to45-smooth-dimensions-v1/final-tests-v2/receipt.json`; full log SHA256 `829cc41cfaf18f436b8faff6f232a32516d6e73f27bbb56e0300617d68b557c3`.

Final package SHA256: `f1121dfff51564d5b9ccd29ab61279d60125f468595299c7e52d51d257041b41`.
Final raw G-code SHA256: `ebcb6ee6c465646fafaac1a37ec233b9ef7e847874d407ce7308ac9399e2297d`.

Fresh tool audit: 0 issues in its modeled scope, 2,907 motions, 934,441 pairs, 164 near certificates independently replayed using new actual E-derived bead geometry. Fresh geometry audit: all 41 nominal centerline contact and spill checks, 32,175 future linear pairs (6 new projection certificates), and 820 supplemental pairs. Existing unresolved original-job entries remain explicit: 208 opaque XYZ tool entries and 4 material entries. These are scoped computational checks, not a complete physical safety assertion.

Total supplemental moving extrusion changes from original full 10.41243 mm filament to 8.75007 mm (about 84%). This is more than the earlier 25%-plus-deletion trial because all 41 paths remain. Original source bytes are recovered exactly after removing inserted spans and the established metadata adapter prefix. Only G-code and MD5 package members change.

## Studio and plugin evidence

Bambu Studio loaded the final package, and the parent inspected `studio-preview.png`: original paths plus green Custom supplemental paths, without a G-code processing error. The actual Studio extracted `plate_1.gcode` at `Sun_Oct_18/21_49_04#28676#69/Metadata/plate_1.gcode` hashes to the final raw G-code. Subsequent user input changed the window to Device view; no further UI input was issued. The parent did not send or start a print. The later `studio-final-close.png` is a Device-view observation, not preview evidence.

Plugin 0.2.5 was installed offline with a backup and registration receipt. Separate geometric policy storage, settings codec and UI handlers are tested. Running Orca was not restarted, and actual plugin screen save/readback remains unverified. The delivered coupon policy was saved/read back through the settings API; it is not falsely described as a UI export.

The earlier V1 full-test process was intentionally stopped for the precision amendment; it is not counted as a passed run. No merge, release, cleanup of unrelated files, or physical printer action was performed by this work.
