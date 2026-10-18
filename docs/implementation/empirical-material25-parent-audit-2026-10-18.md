# 25-percent endpoint and minimum modeled thickness

The user changed the endpoint from 50 to 25 percent and requested removal of
supplemental lines below the minimum thickness. The admission endpoint remains
33.95770549 degrees; the coupon maximum remains 45 degrees. New policy defaults
are 100/25 percent with an explicit 0.08 mm modeled minimum. Retraction/wipe
remain 1.6/1.0 mm; Z downshift remains zero.

The same nominal-width stadium model is used. Actual rounded commanded E is
converted to geometric area using the saved filament diameter and flow
multiplier, then compared to the area needed at 0.08 mm. Exact rational pi
enclosures avoid admitting an under-threshold path through tolerance. A path
must pass every segment. Parent removal cascades to descendants; empty groups
are omitted. Final emission independently rechecks the same command precision
and policy-bound threshold. This is a modeled thickness, not a measured result.

## Result

Exactly 14 of 41 paths remain; 27 are removed. Eight of 24 insertion groups
remain. Independent arithmetic replay checks ALL 41 decisions, not only the
surviving paths. Original-source recovery is byte exact.
Survivor section angles range from 5.06840360 to 18.81477250 degrees; commanded
factors range from approximately 0.8880577281 to 0.5844513293. The formula's
25-percent endpoint remains at the admission limit, even though those steeper
paths do not survive the minimum-thickness filter in this coupon.

- Package: `artifacts/gui-angle0to45-material-correction25-v1/trial-material-correction25-v1/angle-0to45-WITH-supplement-EXPERIMENTAL.gcode.3mf`
- Package SHA256: `e0793e0f500c518ae6cb87254230a0f98ced3ee08dafd5d43d27fd483f250820`.
- Raw SHA256: `cecbac2360b60844f8d1a0df35c3b46654bd8fd77a58929a5603933c29cd4c11`.
- Independent decision receipt: `trial-material-correction25-v1/independent-all41-modeled-thickness-decisions.json`.
- Fresh nominal-reference motion audit: 2583 motions, 285265 pairs, 14 forming
  motions, zero scoped issues. Opaque original operations and actual corrected
  physical shape/contact remain outside complete proof.

Original table quality criteria apply to the prefilter design. User-requested
removal permits reduced coverage/improvement; filtered error is diagnostic and
is not represented as passing the original optimization objective. Contact,
spill and motion gates remain enforced within their stated reference models.

## Actual Bambu Studio verification

Opened a separate Studio window to preserve the user's existing untitled window.
The new extracted `21_16_07#11732#69/Metadata/plate_1.gcode` under the dated
local `bamboo_model/Sun_Oct_18` temp folder matches the raw SHA above. Existing
setting-compatibility information was dismissed; preview loaded without a
G-code processing error. Screenshot: `studio-final-close.png` in the task folder.
No print/send action performed. Preview geometry remains nominal.

## Plugin and compatibility

Schema v2 includes the threshold in its identity. Historical v1 files preserve
their explicit values and no-filter semantics; they are not silently migrated.
Version 0.2.3 adds the threshold field/default25. The owned 0.2.2 installation was
fully backed up and replaced using the pinned local loader contract. Exactly
one owned registration remains, all permissions empty, other entries preserved.
Receipt: `plugin-install-evidence/offline-upgrade-receipt.json` in the task folder.
The running Orca process was not restarted; actual UI readback remains unverified
because of the previously recorded native child-window targeting failure.
This artifact's policy was saved/read back through the real persistence API.

## Verification

Independent focused suites: 43 tests pass. Full regression and final artifact
receipts are stored in the task folder; final results are appended below.
No release, merge, physical printing or unrelated file changes are part of this task.

Fresh reference geometry: 14 contact/spill checks, 14104 future-material pairs,
six near certificates with 12 public projections, and 91 candidate pairs pass.
Independent replay matches all 56 tool certificates and all six material
certificates. The genuine all-empty exercise preserves both source G-code and
archive byte-for-byte, without insertion wrappers or adapter prefix.

Full regression completed: **1016 tests PASS**, Python 3.12.10, 551.080 seconds.
Source/test snapshots and preserved files (including unrelated log) unchanged.
Receipt: `artifacts/gui-angle0to45-material-correction25-v1/final-tests-v1/receipt.json`.
Log SHA256: `169b69f88765f7c40988f2522284dc81ce770952ac86b59086d6e01c90f9fbb2`.

A final artifact-only early threshold guard rejects a policy/table minimum
mismatch even when every E rounds to zero, before creating an output directory.
Independent negative replay passes; the valid recipe still regenerates the exact
final raw SHA. The guard-only builder change has an explicit certificate rebind
record, not a claim that earlier broad geometry audits reran against changed code.
