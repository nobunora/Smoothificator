# Zero physical downshift and 0..45-degree preview: parent audit

Scope: user-requested physical overlap zero and extension of the same coupon
to expose the configured no-supplement region. No print/send, merge or release.
The existing working tree and unrelated log_iotc.txt are preserved.

## Specification decisions

- Actual old root lowering was 30 percent of physical line height, not a
  uniform 0.08 mm. Set overlap to zero: root bottom equals source terrace
  top, and upper bottom equals its completed parent's top.
- Retain the independently approved 0.08 mm nominal support-query tolerance;
  it is an analysis premise and never an emitted Z shift.
- Retain the user's explicit base < sqrt(2) * minimum-width exclusion.
  At H=0.2 mm and minimum width 0.21 mm its configured boundary is
  33.9577054886 degrees. It is a conservative admission policy, not proof
  that all rectangles beyond that angle are physically impossible.
- A fingerprinted 0.01 mm physical-height candidate lattice plus the strict
  saved-height endpoint bounds table construction. At zero overlap and
  H=0.2, heights are 0.08..0.19 and 0.199 mm. Coordinate grid remains 0.001.
- Preserve the same 30 by 20 mm coupon, base 2 mm, original placement and
  saved settings; change its maximum angle from 30 to 45 degrees.

## Independent review and boundary correction

The researcher reproduced a missing exact admission check: actual slope
0.675 failed the user's short-base rule but could use selected bin 0.67.
Parent directed the owner to enforce the exact constant-time base check in
the authoritative lookup before selecting a table bin, with boundary tests.
This adds no per-location optimization and does not loosen a gate.

The first full regression run was intentionally stopped at 295.485 seconds
for that correction; it is INCOMPLETE, never PASS. Receipt and explanation:
artifacts/gui-angle0to30-trial-v3/final-tests-zero-overlap-v1/.
The source/test snapshot was unchanged during that incomplete run and all
preserved input hashes, including log_iotc.txt, matched.

Before the correction, 45 architecture checks passed and both owner and
independent reviewer ran 8 focused table tests successfully. Final corrected
regression and actual artifact acceptance are recorded below when complete.

## Genuine new slice and terminal empty planes

Orca GUI loaded the geometry-only project, sliced with Ctrl+R, saved the
actual project and exported the sliced archive. Saved settings bytes remain
SHA256 33df726ee13a5f6458106abd9de1553d456b7e7f6a264b480582da1ab969a482.
The GUI recentered XY; actual placed geometry is pinned and all catalog,
anchors and inset endpoints were derived anew. The new nominal mesh height
is 10.825424006 mm. Genuine source has 52 printed planes ending at Z10.4,
54 nominal planes with max_z_height10.8, and two empty terminal usage planes.

The material-profile reader now admits that narrow case only with consistent
progress sequence/denominator, printed count, CHANGE_LAYER count, source and
saved global layer height, nominal max Z, and exact actual Z_HEIGHT sequence.
Per-feature LAYER_HEIGHT is not a uniform plane-height invariant: the genuine
source contains bridge thickness0.4 and float-rounded0.200001 tags, preserved.
Nonempty material beyond printed layers, missing used layers and malformed
extended metadata reject. Independent review accepted the corrected helper.
The second full run was intentionally INCOMPLETE for this change; its receipt
and explanation are in final-tests-zero-overlap-v2, not claimed as PASS.

## Final artifact and independent acceptance

Artifact root: artifacts/gui-angle0to45-zero-overlap-v1/.
Final package: trial-zero-overlap-v2/angle-0to45-WITH-supplement-EXPERIMENTAL.gcode.3mf.
Package SHA256: 051d9d0fb1c72a9adfee09c2c91f88b21c6ed41472111c947baeb8ef8fb738aa.
Raw SHA256: 7ae4747b0949b25620ec63cf80164cc70257a06408cf27e55f3cb691fcd46d03.
Plans SHA256: 6c930b32a6caef31a3f829671485785ba546018296d76b0a4b28efffcced7a44.

There are 24 selected terraces, 41 single-tier paths, no upper paths, and
18 configured steep skips. Last selected average terrace angle33.427445deg;
first skipped34.045937deg. All actual formatted-E bead bottoms equal the
original terrace support plane. Actual selected heights0.08..0.18; configured
strict cap remains0.199, not a restored90-percent cap. Taller retained options
were dominated in the table objective. Root query tolerance0.08 remains
explicitly separate from emitted placement. Both end margins remain>=5mm.

Independent raw-table/Fraction replay matches every final intent without
calling the optimizer. Independent source recovery removes24 insertion spans
and the92-byte native-preview adapter prefix to obtain the original exactly.
Archive changes are only G-code and its MD5; saved config bytes match. Reduced
Studio-native state comparison finds zero mismatches at2556 original moving
extrusion vertices. Fresh actual-material near replay reproduces all20
certificates with40 public projection queries; no old30-degree proof reuse.

Parent opened the final package in existing Bambu Studio using computer-use,
dismissed the known settings-compatibility information dialog, and inspected
Pillow captures. No G-code processing error occurred. Current extracted
Metadata/plate_1.gcode under15_58_12#38960#251 has the exact final raw hash.
The side view was enlarged; screenshot studio-zero-overlap-final-side.png.
The actual-E cross-section zero-overlap-angle45-cross-section-v2.png was
visually inspected and clearly shows the steep unsupplemented region.
No print/send was performed. Compatibility preset mappings are still shown
by Studio; original sliced commands and saved configuration remain unchanged.

## Final regression

Python3.12.10, full unittest discovery: 996 tests PASS in534.803seconds,
exit0, source/test hashes stable throughout. All preserved original inputs
and unrelated log_iotc.txt remain unchanged. Receipt:
artifacts/gui-angle0to30-trial-v3/final-tests-zero-overlap-v3/receipt.json.
Log SHA256: 723d6fbb48587be44922b421aeeeca0c5e55f128d77f1691655ca43892cb283c.
Focused table9, material-related41, independent profile/trace/copy/end/Studio34,
and architecture45 checks also passed. No dependencies added; lint/type tools
remain unconfigured for this task. This is an experimental preview artifact,
not physical validation of the provisional tool model or unresolved OEM moves.

## Final tool audit completion

Fresh tool audit found zero issues in its known-motion scope: 2902 motions,
927756 pairs, 2665 native-arc pairs strictly separated, 41 forming moves and
41 negative-E wipes. No adjacent-terrace exception was used. Independent
review reproduced all164 public certificates (41 forming TOP,123 own TOP),
all41 material-availability/wipe sequences, and24 cycle XYZ/feed/debt/
acceleration restores. The fresh original-source ledger contains208 opaque
XYZ-invalidated entries; it was independently re-derived and matches exactly.
The report correctly remains overall incomplete for opaque execution,
stationary material and unverified physical/CAD behavior. No physical safety
claim is inferred from the zero known-scope issues or GUI rendering.
