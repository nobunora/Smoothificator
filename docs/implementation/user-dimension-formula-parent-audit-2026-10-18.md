# User-calibrated endpoint dimensions and formula: parent audit

Date: 2026-10-18. Contract: accepted V4 extension of ADR-0071 and `docs/specs/nonlinear-geometric-dimension-taper-trial-review.md`.

## Delivered behavior

The user explicitly selected 0.01 mm when a smaller physically reproducible height could not be established, then requested normal user-configurable minimum endpoint height/width and an editable formula in the plugin. V4 implements that request without redefining the original candidate admission table. Current saved endpoints are height 0.01 mm and equivalent-flow width 0.1 mm; original admission remains layer height 0.2 mm, minimum width 0.21 mm and maximum angle 33.95770549 degrees. Ten-degree plateau and zero overlap remain. The current formula is `1-(6*t**5-15*t**4+10*t**3)`; height and width each interpolate between the original dimension and the user's endpoint with this retention.

The pure parser accepts only bounded rational polynomials in t: arithmetic, division by nonzero constants, nonnegative integer powers up to 12, final/intermediate degree at most 12, 512 characters, 128 AST nodes, depth 24 and 128-bit coefficients. It does not eval/exec Python. Exact endpoints R(0)=1/R(1)=0 are required; evaluated retention clamps to [0,1]. Arbitrary user expressions need not be monotone. Positive grid-aligned minima, height<=width and existing numeric extrusion/position gates remain; the current values are not hardcoded V4 lower limits. Historical V1/V2/V3 policy encodings and semantics are preserved. V4 is a normal user-calibration setting, not a hidden experimental flag.

Original admission/profile validation and numeric replay occur before mapping. Only the two dimension minimum bounds change in the derived emission policy, which the native boundary independently reconstructs. Full ordinary extrusion is recomputed; no older percentage factor is compounded. Source floor, XY paths, original source bytes, profile and all other motion/flow settings remain unchanged. Retraction is 1.6 mm and wipe 1.0 mm. Active G-code XYZ precision is 3 decimals (0.001 mm); E precision is 5 decimals. Decimal representation does not establish hardware resolution or deposited thickness.

## Final artifact and checks

`artifacts/gui-angle0to45-smooth-micro-v1/trial-user-dimensions-v4/angle-0to45-WITH-configurable-micro-dimensions.gcode.3mf`

- Package SHA256: `65e52c884860765e1a88bd2239b114f6b113ab5c0a139675cba83844daf73621`.
- Raw G-code SHA256: `54c2a4fad3ed15fc143b1018e8671100810106a679aa8727b7d1bc75aec822c9`.
- Saved/consumed V4 settings SHA256: `f482321fc9c6f70168cf1b99a818a2bb08d394b978360d1ee922dd9ddfc357f4`.
- 41 paths, 24 groups, all nine plateau paths retain exact original moving E. Actual minimum height 0.010 mm, minimum nominal equivalent width 0.101 mm after lattice/numeric representation. Full supplemental E totals 6.61283 mm filament versus previous 8.75007 mm (about 75.6%). Actual widths/heights are commanded/model quantities, not measured bead dimensions.
- Fresh known-scope tool gate: 2,907 motions, 934,441 pairs, zero known issues, 164 near certificates independently replayed.
- Fresh geometry: all 41 nominal contact/spill receipts, 32,175 future linear pairs, 3 near certificates/6 queries independently replayed, and 820 supplemental pairs. Existing 208 opaque tool entries and four original material unknowns remain explicit; no complete physical or whole-job authority is asserted.
- Independent actual raw E/XYZ/F/state restoration/source recovery/package verification passed. Only G-code and MD5 archive member contents change.
- Authoritative Python 3.12.10 full regression: 1,044 tests passed in 461.889 seconds, exit 0. Sources/tests unchanged during run, protected historical artifacts and log_iotc.txt unchanged. Receipt `artifacts/gui-angle0to45-smooth-micro-v1/final-tests-v1/receipt.json`; log SHA256 `dc3faec0557b470d69a258054977af7490db8271fae32781798c089f76efa1f7`.

## Plugin and desktop evidence

Plugin 0.2.6 installed offline with prior entry backup and unrelated registration preservation. Settings saved/read back through the real plugin storage API and consumed byte-exact by the artifact builder. Actual page JavaScript tested with legacy V3 records and editable formula save/reopen behavior. Parent started the now-closed Orca afresh, but its popup menu was not targetable by the Windows input API, so actual plugin screen interaction remains unverified.

Bambu Studio was launched with the final file. The ordinary settings-compatibility information dialog blocks loading; accessibility exposes OK but the automation reports `coordinate input geometry is unavailable`. Parent requested manual OK before final preview inspection. `studio-preview.png` at that stage is the empty preparation viewport, not successful model preview evidence. No print/send action was performed. Independent artifact checks and the runnable model do not depend on that UI step.

Actual Studio extraction verified at `C:\Users\nobun\AppData\Local\Temp\bamboo_model\Sun_Oct_18\22_37_08#20640#69\Metadata\plate_1.gcode`; SHA256 matches the final raw G-code above. This proves correct file selection/extraction, not completed visual preview.
