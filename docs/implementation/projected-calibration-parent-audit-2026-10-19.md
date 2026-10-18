# User-confirmed projected distance calibration — parent audit

This is the corrected specimen after the user confirmed top-view straight distance. The earlier surface-arclength artifact is historical and superseded for this request. Distance is actual world Y minus the verified zero-degree profile origin, 76.7467788 mm. All placement calculations are tied to the actual saved 3MF profile.

The requested windows remain 6.5–8.5 and 10.5–12.5 mm at approximately +20% nominal material area per length, and 14–16 mm at approximately -10%, with 0.5 mm smooth outer shoulders. A smooth projected-distance transition from 16 to 17 mm reaches commanded height 0.012 mm and equivalent width 0.015 mm; later eligible source rows retain this tiny coherent stadium area. These are commanded/model dimensions, not measured bead dimensions.

New residual families before 16 mm use the old V5 clamped endpoint (height 0.01 mm, width 0.02 mm) as the calibration reference. Their nominal admission seed is never treated as previously emitted material. At projected 16 mm, target area is approximately 0.0001606858347 square mm, smoothly decreasing toward approximately 0.0001490973355 square mm. Ordinary full E is computed from final represented dimensions with the saved ratios; there is no post-hoc E multiplier.

Policy schema 2 includes the explicit coordinate mode and defaults to projected distance. Legacy schema 1 remains surface arclength, retains its exact canonical policy bytes and active native emission identity. The previous 57-path surface artifact was replayed to identical raw bytes and identity as a compatibility check. V1–V5 normal plugin policies/defaults are unchanged. Editable specimen JSON is separate from the installed plugin settings.

The separate research agent and blind reviewer both approved the bounded coordinate change. Independent focused checks passed 87 tests; blind coordinate/boundary review passed 17 focused tests with no finding. The native geometry/profile, unit, namespace and malformed-input fixes from the initial specimen remain in force. Final full-suite v4 is recorded under the preceding spatial artifact root because its runner was prepared there; it covers the corrected frozen source.

Final corrected package: `artifacts/gui-angle0to45-projected-calibration-v1/trial-projected-calibration-v3/angle-0to45-RIGHT-HALF-PROJECTED-DISTANCE.gcode.3mf`.

- Package SHA256: `f6ad14a57eeb150e2ec75ed731c8d4c7c7865d238dec293bc4cf4f2858d01729`, independently checked by parent.
- Raw G-code SHA256: `dc6fd3732b373c58157dcfea545ee39a092f05d6d32712b378eb08279e9928d5`.
- 57 roots in 42 groups, all on the right half. Original left/right structural G-code remains unchanged.
- Independent actual native replay verified all 57 XYZ/E/F/wipe/debt/state records, original source byte recovery, archive G-code/MD5-only changes, and both existing pre-hop anchor routes. Supplemental deposition totals 4.57818 mm filament.
- Fresh tool audit passed in 100.391 seconds: 3,099 motions, 1,431,095 pairs, 57 forming prefixes and zero known issues. Final material geometry passed in 167.891 seconds: 57 contact/spill checks, 32,284 future pairs and 1,596 candidate pairs. Independent certificate replay completed with no findings.
- Final full suite passed all 1,064 tests in 441.017 seconds (runner 443.469 seconds), Python 3.12.10, exit 0. Source/tests and protected prior artifacts remained unchanged. Receipt: `artifacts/gui-angle0to45-spatial-calibration-v1/final-tests-v4/receipt.json`; log SHA256 `c2911bccdd361f5bcad5520919a7fbe88a35c212648499d10c72470a03d54589`.
- Launch of the corrected PROJECTED package in Bambu Studio was requested, but the user stopped Computer Use with physical Escape before preview readback. No further GUI operation was performed. Corrected preview is not visually confirmed; the earlier surface-arclength screenshot is not evidence for this package.

The final comparison plot is generated from corrected projected-distance decisions. The prior arc plot and certificates are not reused as current proof. No printing, sending, merge or release was performed. Whole-original-job and physical-reproduction authority remain outside these scoped checks.
