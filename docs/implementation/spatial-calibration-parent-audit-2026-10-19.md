# Specimen distance calibration — parent audit

## User clarification supersedes the initial artifact

The user subsequently confirmed **top-view straight/projected distance**, not surface arclength. Therefore the surface-arclength v2 artifact below, although all computational gates passed, is historical and must not be delivered as the requested final model. Corrected coordinate is worldY minus the actual profile origin. The requested windows retain their numeric millimeter ranges; tail transition remains 16–17 mm in the corrected coordinate. Schema 2 explicitly identifies projected distance; historical schema 1 retains surface-arclength semantics. New residual source families before projected 16 mm use the old V5 clamped endpoint reference area, not the untapered nominal admission seed. Corrected artifact regeneration and validation are required. No printing was performed.

User requests approximately 20% more supplemental material at ruler distances 6.5–8.5 and 10.5–12.5 mm, 10% less at 14–16 mm, and small residual deposition beyond 16 mm with modestly higher commanded height and lower material volume. Prior right-half V5 printed specimen remains the reference. New artifact generation only; no printing or sending.

## Adjudicated scope

Repository remains on `codex/true-z-review-handoff`, HEAD `06d4db856708283c44b4476d1d16cb9fd83c14f6`, with substantial pre-existing work. No reset, pull, staging or cleaning. Preserve historical artifacts and unrelated `log_iotc.txt`.

Distance is explicitly assumed to be surface arclength from the zero-degree end, pending any user correction. The saved profile has 20 mm projected length and approximately 22.444 mm surface length. The old 33.9577-degree admission cutoff is approximately 16.0624 mm along the surface, matching the reported disappearance more closely than its approximately 15.1 mm projected position. This correspondence is evidence for an assumption, not a user-confirmed measurement definition.

Accepted ADR-0071 and the nonlinear taper handoff specification now define a separate bounded specimen calibration. Keep legacy V1–V5 settings and installed plugin defaults unchanged. Editable specimen parameters and all reference/source identities must participate in the new policy identity and be independently reconstructed at the native boundary.

Use exact requested gain plateaus with 0.5 mm quintic outer shoulders. Derive ordinary coherent stadium dimensions from requested area; do not patch emitted E or compound historical empirical multipliers. Preserve height first, increase it only when needed to respect the unchanged 0.45 mm maximum width and saved/source upper height bounds. Recalculate all ordinary extrusion and geometry checks.

After surface distance 16 mm, blend to target height 0.012 mm and equivalent width 0.015 mm by 17 mm, maintaining a tiny target to the source's 45-degree end wherever fresh checks allow it. Explicit local minimum emission width 0.012 mm permits this coherent geometry; it does not overwrite the V5 plugin's 0.02 mm setting. The target residual area is approximately 0.0001490973 square mm. Quantization error must be reported, not hidden by direct E rescaling.

The prior angle admission limit explains disappearance independently of volume starvation. Beyond that cutoff, use a separately identified coupon-only root-family admission minimum width 0.14 mm and explicit 45-degree cap. The original 0.21 mm admission elsewhere remains unchanged. Support tolerance, zero downshift, source state, profile and all contact/material/tool checks remain unchanged. Failure to find feasible residual roots must be reported rather than forced.

## Verification status

Research and implementation are assigned to separate GPT-6.1-sol agents; a separate blind source reviewer completed review. Four findings (profile-to-mesh association, malformed JSON recursion normalization, 3MF units, and exact XML mesh namespaces/hierarchy) were confirmed, fixed and independently rechecked. Native composition now verifies the supplied profile against the supported actual placed 3MF vertices and faces; this strengthens the initially proposed builder-only association boundary. It does not establish physical accuracy or generic CAD support. The final blind report records convergence with no remaining material finding.

The first two full-suite attempts were deliberately stopped when source review required fixes; neither is counted as a successful run. Full regression v3 passed all 1,061 tests in 489.631 seconds (runner 492.219 seconds), exit 0, Python 3.12.10. Source/tests were unchanged during the run; previous printed V5 files and protected inputs/log were unchanged. Receipt: `artifacts/gui-angle0to45-spatial-calibration-v1/final-tests-v3/receipt.json`. Log SHA256: `aac5bbe2fee859dbf6207180b827436973e279822d0b37ce7a25437b4dde1fce`.

Independent preliminary checks of all 39 existing paths confirm coherent area and fixed source floor/XY spans. Plateau gains are approximately +19.75 to +20.11 percent and -10.51 to -9.42 percent after dimension quantization. Eighteen additional residual roots pass fresh contact/spill/future-material preparation, giving 57 roots in 42 groups. Their surface arclength range is approximately 16.1298–21.5476 mm; the full model surface extends to 22.444 mm, so continuous supplementation to the exact 45-degree endpoint is not claimed.

Two tail groups at source floors 9.4 and 10.2 mm use the existing native pre-hop insertion route immediately before their original G3 motions. Their source hop does not fit the saved post-hop-wrapper expectation. This explicitly scoped route preserves the original arc and saved hop settings, restores the original state, and requires fresh actual chronological tool checks; it is not a gate relaxation. All other groups retain their existing route. Independent final replay verified these anchors at source byte offsets 242476 and 250326 and exact original arc/state restoration.

Final package: `artifacts/gui-angle0to45-spatial-calibration-v1/trial-spatial-calibration-v2/angle-0to45-RIGHT-HALF-spatial-calibration.gcode.3mf`, SHA256 `a268fe52ae03997736222f06993bcbfec2a7d4f732d6ac8f168a73d400500aed`; raw G-code SHA256 `9bba3482a2cf644fd21734bd396c05ae612f0267cba1137b024d05ba4c0d2ba0`. Parent independently checked package hash. Final native replay independently verified 57 path XYZ/E/F/end-wipe/debt/state records, total supplemental deposition E 4.58553 mm, exact original byte recovery and ZIP G-code/MD5-only member changes.

Bambu Studio opened this package in a new window. The information dialog's inaccessible UI element was dismissed with a targeted Return key; subsequent actual screenshot shows the named new file in Preview with the right-half green Custom paths and original left half visible. Parent zoomed the view and inspected Pillow screenshots; final screenshot `artifacts/gui-angle0to45-spatial-calibration-v1/bambu-spatial-preview-detail.png`. No printing or sending was performed.

Fresh final tool audit passed in 128.140 seconds: 3,099 motions, 1,431,095 pairs, 57 forming prefixes, 240 near certificates, zero known issues. Final material geometry audit and certificate replay remain pending at this update. Computational checks do not establish physical reproduction or whole-original-job authority.
