# Empirical material correction parent audit

User-approved endpoint: supplementation admission limit, 33.95770549 degrees,
not the 45-degree coupon endpoint. Commanded supplemental deposition volume is
multiplied by `1 - 0.5 * clamp(angle / admission_limit, 0, 1)`.
Actual section angle is used. Nominal paths, XYZ, widths and heights are retained.
Stationary unretraction, debt reconciliation and original source E are not scaled.

Supplemental end retraction is 1.6 mm (previous 0.8); reverse wipe is 1.0 mm
(previous 0.5). Feed caps are unchanged. Source debt is restored individually at
each insertion anchor, not assumed to be uniformly 0.8 mm.

## Artifact and independent evidence

- Package: `artifacts/gui-angle0to45-material-correction-v1/trial-material-correction-v1/angle-0to45-WITH-supplement-EXPERIMENTAL.gcode.3mf`
- Package SHA256: `4cbe701be4ba97132d1a01a96a5e2603e2bebaedcfe187865b4d5d1a166c2b28`.
- Raw G-code SHA256: `30d48e5904f1bcf64191c81bcd0ed6e8d3af789945a6f6776cc05bbf1e146b79`.
- 24 insertion groups, 41 paths; same zero-overlap placements and steep exclusions.
- Actual factors: 0.9253718188 through 0.5078076538. Supplemental filament
  deposition: 10.41243 to 7.82119 mm. No zero-degree path exists in this coupon.
- Independent replay: `trial-material-correction-v1/independent-empirical-package-state-replay.json`.
  All 41 E factors, 24 state restorations and 41 reverse wipes pass. Removing
  insertion spans and the established 92-byte Studio adapter recovers the source
  exactly. Only G-code and uppercase MD5 archive members changed.

## Actual Studio display

Opened the package in Bambu Studio. Its newly extracted file at
`C:/Users/nobun/AppData/Local/Temp/bamboo_model/Sun_Oct_18/20_59_11#39192#69/Metadata/plate_1.gcode`
matches the raw SHA above. Existing Orca-to-Studio setting compatibility information
was dismissed; preview loaded without G-code processing error. Screenshot:
`artifacts/gui-angle0to45-material-correction-v1/studio-final-close.png`.
Custom supplemental lines are visible. No print/send action was performed.
Preview bead dimensions remain nominal; they do not predict corrected physical
bead dimensions or validate contact after empirical flow correction.

## Plugin settings and verification limit

Version 0.2.2 adds persisted endpoint percentages, admission H/minimum width,
retract and wipe settings. The native trial consumes the same canonical settings
document and pins its identity. Settings edits show unsaved state until saved.
The wheel was installed offline using the pinned Orca loader's directory/sidecar
contract without altering other plugins or granting permissions. Receipt:
`artifacts/gui-angle0to45-material-correction-v1/plugin-install-evidence/offline-install-receipt.json`.
The existing Orca process needs a rescan/restart.

Actual Orca settings-window interaction is NOT verified: native screenshot API
returns `SetIsBorderRequired 0x80004002`; refreshed input rejects owned WebView
as a different target, and UIA element indices are unavailable. A documented
activation/refresh/retry did not fix it. No unsupported UI bypass was used.
This trial uses the real shared save/load API in artifact-owned storage, not a
claimed UI export. Tests cover the entrypoint save/reopen and stale-window paths.

## Limits

The correction is empirical commanded volume. Nominal geometry/clearance checks
are references, not proof of actual printed shape, adhesion or whole-job safety.
Existing opaque original motion/material limitations remain. No merge/release.
Full regression receipt and final fresh-wipe audit are retained beside the artifact.

Full regression: Python 3.12.10, **1007 tests PASS**, 547.578 seconds. Source/test
snapshots unchanged throughout; preserved inputs and unrelated log unchanged.
Receipt: `artifacts/gui-angle0to45-material-correction-v1/final-tests-v1/receipt.json`.
Log SHA256: `b0c02f2a0a191bac18fe25e700a7d274f3e3c7b5edcc9f6664ab2748a235ea2b`.

Fresh nominal-reference wipe audit passes: 0 issues across 2907 motions and
934441 pairs, including 41 forming motions. Independent replay validates all
164 near certificates (41 forming + 123 own TOP). The 208 opaque source XYZ
motions remain explicitly outside complete proof. See
`trial-material-correction-v1/tool-pinned.UNVERIFIED.json` and
`nominal-geometry-rebind.UNVERIFIED.json`. The initial audit attempt rejected an
asymmetric artifact pin list; that bookkeeping bug was fixed and the full fresh
audit rerun successfully without changing the package or core sources.
