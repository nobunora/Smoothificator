# Fresh 0..45 degree zero-downshift native source preparation

A genuine existing Orca GUI session loaded the new one-coupon geometry project,
sliced with Ctrl+R, saved the actual GUI project with Ctrl+Shift+S and exported
the real sliced G-code 3MF with Ctrl+G. No CLI slicing, send or print occurred.
The geometry input and all old inputs remain immutable. Screenshot capture API
failed with 0x80004002; user-authorized Pillow captures and refreshed accessibility
confirmed filename fields, new 30x20x10.8254 geometry and sliced preview. All input
paths, hashes, byte sizes and GUI provenance are pinned in the new artifact folder.

The GUI recentered the coupon; parent accepted the fresh actual placement rather
than borrowing old transforms or anchors. Actual X is81.4920309..111.4920309 and
Y76.7467788..96.7467788. World bed floor remains0. Source header nominal maxZ is
10.80; 52 printed planes end at10.4, while progress denominator is54. The last two
nominal planes have no printable material. This is a fresh slice, not old7.4 cache.
Consumed effective settings, selected material index2 and full saved settings
SHA256 exactly match the successfully used v9 source settings; no settings or
archive metadata were normalized. `same-used-slice-settings.UNVERIFIED.json`
records the comparison.

The native material profile previously allowed at most one empty terminal plane.
The new actual archive has used range0..51 and EMPTY52..53. The narrowly amended
validator accepts extended tails only with contiguous used/empty ranges, exact
printed progress sequence1..52, one bounded nominal denominator54, 52 CHANGE_LAYER
and exact Z_HEIGHT sequence i*saved/source globalH, and maxZ/H==54. Per-feature
LAYER_HEIGHT is deliberately not conflated with nominal Z: a legitimate internal
bridge is0.4, and float-written feature metadata includes0.200001. Old one-empty
fixtures remain accepted; nonempty tails, gaps, forged denominator, mismatched H,
nonuniform first/late Z and fractional/unreasonable nominal bounds are rejected.
41 focused tests and the actual9374-event trace passed; independent review accepted
the final helper before parent started the full suite.

Fresh catalog:42 actual source intervals,2536 cropped linear material segments,
7 arc bounds and40 eligible source post-hop anchors. Missing anchors9.4/10.2 are
inside configured short-base-excluded intervals. The original-floor witness map
v1 selected too early, before original wipe G1 commands; it is diagnostic only.
Mapv2 proves the complete boundary immediately BEFORE each actual G3 hop, after
all original wipe/mode updates; post-hop offsets and earlier material are unchanged.
The existing native interval whitelist and physical-state gates are not weakened.

All new artifacts are under `artifacts/gui-angle0to45-zero-overlap-v1/`.
No physical authority is inferred from software, geometry or GUI source evidence.


## Final concrete artifact and completed owned gates

`trial-zero-overlap-v2/angle-0to45-WITH-supplement-EXPERIMENTAL.gcode.3mf`
SHA256051d9d0fb1c72a9adfee09c2c91f88b21c6ed41472111c947baeb8ef8fb738aa
contains24 selected intervals and41 single-tier paths;18 steep intervals are
configured-policy-excluded. Every actual bead bottom minus support plane is0;
the independent0.08 contact-query allowance is analysis-only. There are no
children or vertically stacked supplemental paths in this selected job.

Fresh geometry audit exited0:41 paths /24 groups,32175 future linear pairs,
820 candidate pairs all box separated,40 exact public projection queries for20
near future-material certificates,174.766seconds. Fresh causal tool audit exited0:
41 negative-E XY wipes,2902 motions,927756 pairs,2665 native arc pairs all strictly
box separated, zero issues,83.5seconds. No adjacent-candidate allowance is used.
All164 near proofs are123 own-path retract/wipe/lift TOP and41 conservative
forming-prefix TOP certificates. The208 opaque-invalidated-original-XYZ entries
belong to this fresh52-layer source and remain explicit obligations; they are
not equated to the old source's128 entries. Original stationary material and
one width-below-height source segment also remain recorded. Whole-job/physical
flags remain false.

Independent package readback confirms original recovery after24 spans+92-byte
prefix removal, unique ZIP names/order/CRC, closed G-code+uppercase-MD5 changes,
and all configuration member bytes preserved. Parent reports actual GUI loading
without errors and a temporary extracted G-code hash matching7ae4747b0949b25620ec63cf80164cc70257a06408cf27e55f3cb691fcd46d03.
Parent owns the final996-test full regression, reported passed with source pins
stable. No physical print or send was performed by this workflow.
