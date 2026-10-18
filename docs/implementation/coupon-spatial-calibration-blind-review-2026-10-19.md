# Specimen spatial calibration — independent blind source review

Date: 2026-10-19. Reviewer: independent planner agent. Scope: Accepted ADR0071 latest specimen amendment, matching handoff, `tools/coupon_spatial_calibration.py`, native optional integration, directly relevant tests. No implementation source/test edits, implementation coordination, GUI or printing. Findings supplied only to parent.

## Disposition

One confirmed Medium source-association finding requires adjudication; one Low malformed-input failure. No Critical/High finding established within this bounded review. Final frozen-source eligibility is pending owner refreeze: source changed during review to add the explicit V5-reference guard. That guard does not itself associate profile coordinates with actual geometry bytes.

## SC-B1 — Medium — Declared geometry hash does not authenticate ruler profile

Location: `NativeCouponCalibration.__post_init__` profile/hash validation and `compose_native_trial_copy` specimen geometry identity comparison.

The descriptor checks the geometry/catalog strings have SHA256 shape, while the native boundary compares only `geometry_sha256` to current context. Neither associates the supplied `placed_profile` coordinates with actual geometry bytes. `catalog_sha256` is not compared to an authoritative catalog. A stale/forged profile with the genuine geometry hash can therefore move every requested ruler band and the residual-tail transition without source/geometry identity rejection.

Independent repro used the genuine-shaped native fixture: build `calibrated_recipe()`, replace only placed-profile Y coordinates by Y−7 while retaining geometry hash, refreeze resulting geometry/plan, and rebuild native copy. Both native copies succeeded against the same original source/project/context. The original path arc was12.29837388mm and shifted-profile arc20.1246118mm; total supplemental E changed .00623→.00061mm. The shipped fixture's geometry ZIP has only a model object/build entry and no mesh, so the current tests cannot establish actual CAD-to-profile association. Tests that reject a different hash string do not exercise this case.

Violated requirement: selected saved placed_top_profile and origin must be source-bound, with actual bands assigned to that profile; forged policies/source identity were specifically within review scope. Confidence: high. Remediation direction: an authoritative geometry/profile extractor or independently validated source-geometry association receipt must establish the supplied profile and placement from pinned bytes before native use. At minimum the actual artifact builder must provide mandatory independently checked association evidence, with a negative shifted-profile case; caller-supplied matching hashes alone are not that evidence. Parent may adjudicate the boundary responsible, but must not claim this source association is already proved by native replay.

## SC-B2 — Low — Bounded malformed JSON leaks RecursionError

Location: `decode_coupon_policy`, direct `json.loads` call.

With the authoritative interpreter, `decode_coupon_policy(b'['*4000+b']'*4000)` is within the10000-byte input limit but raises RecursionError rather than the expected malformed-policy ValueError. This can bypass callers' expected validation-error handling. No valid policy or unsafe path was admitted. Normalize bounded JSON Unicode/parse/recursion errors to a stable expected ValueError and add the nested-array regression. Confidence: high.

## Positive observations and verification

The implementation uses coherent stadium area, recomputes geometry and ordinary full E, and rejects mixing empirical/taper/specimen modes. Reference intents are replayed against their authoritative taper mapping; native emission reconstructs two-minimum HopPolicy adaptation, validates saved profile and source context, rederives actual transformed intents, and checks exact inserted path coverage. Height search is bounded and only increments to solve over-width area. Ordinary nearest-E width rejection is not bypassed. Residual nominal representation is bounded against the uncorrected reference endpoint area. The inactive optional mode preserves the legacy fingerprint path.

Command `.venv/Scripts/python.exe -m unittest tests.unit.test_coupon_spatial_calibration -q`:11 PASS,.237s at initial candidate. Targeted independent profile-shift script demonstrated SC-B1; malformed JSON script demonstrated SC-B2 (recursion limit1000). No broad/full suite was run by this reviewer.

Additional reads beyond the primary source/test packet: `tools/native_smooth_dimensions.py` for reference/admission owner; native user-dimension fixture for immutable source setup; `tests/unit/native_trial_fixture.py` to establish actual fixture geometry contents. No generated/artifact directories were scanned for review context.

## Corrected candidate verification and SC-B3

Original SC-B1 repro is now rejected independently for both Y−7 and Z+1 shifted profiles while retaining declared geometry hash: native calls `verify_coupon_profile` against actual archive bytes and rejects `coupon placed profile differs from actual geometry`. A real mesh fixture replaces the prior no-mesh fixture. SC-B2 nested8000-byte JSON now raises expected ValueError. `.venv/Scripts/python.exe -m unittest tests.unit.test_coupon_spatial_calibration -q`:13 PASS,.358s. These original findings are confirmed fixed in the reviewed candidate.

SC-B3 — Medium — `tools/coupon_profile_association.py` ignores model units. The extractor interprets vertex/translation numbers as millimeters without checking the main or referenced mesh-part model's `unit`. Independent repro adds `unit="inch"` to the genuine mesh fixture main model and keeps all numbers unchanged: `verify_coupon_profile` still accepts the same0..30mm profile. Actual physical model units now differ, so the new association proof is false for this supported-format input. Official [3MF Core model attributes](https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md) define unit as applying to vertices, locations and measurements, default millimeter, with inch among valid values. Confidence high. Smallest bounded remediation: require absent/default or explicit millimeter on both main model and referenced mesh-part root, rejecting other units; no generic unit-conversion implementation is required. Add negative unit regressions. Final clean eligibility remains pending this guard/adjudication; no source edits by reviewer.

SC-B3 unit fix is verified: both model parts now reject explicit non-millimeter units and allow absent/default millimeter only. Original SC-B1/SC-B2 remain fixed. Updated coupon suite14 PASS,.455s.

SC-B4 — Low — Remaining wildcard XML namespace/shape acceptance. The new root-tag check does not constrain the descendants used for association: searches such as `.//{*}vertex`, `.//{*}triangle`, `.//{*}component` accept foreign-namespace or misplaced descendants. Independent repro moved the referenced part's complete mesh/vertices/triangles hierarchy to `urn:unsupported`, preserving its proper core-model root and all numerical attributes. `verify_coupon_profile` still accepted `(0,30)`, even though this part contains no core3MF mesh. This is unsupported/malformed geometry acceptance rather than an actual saved-coupon issue. Confidence high. Smallest remedy is exact core namespace and direct supported hierarchy paths for resource object/components/build item and selected object/mesh vertices/triangles, rejecting unsupported relevant structure. No generic3MF-format support is requested. Bounded translation review found identity-only component transform and build translation applied to all vertices; complete expected-profile vertex set and triangle-coordinate set comparison otherwise establish the supported extruded-coupon shape association.

## Final bounded convergence — 2026-10-19

SC-B1, SC-B2, SC-B3 and SC-B4 are independently verified fixed. Final extractor uses exact CORE namespaces and direct supported one-object/component/mesh/container paths; no wildcard descendant mesh association remains. Both main and referenced model require absent/default or explicit millimeter units. Native always performs actual geometry association before composition. Existing shifted-profile, deep-JSON, foreign-mesh and nonmillimeter negative fixtures pass. No further material finding remains from the completed bounded source/translation/shape/archive review.

Final command `.venv/Scripts/python.exe -m unittest tests.unit.test_coupon_spatial_calibration -q`:14 PASS,.467s,exit0. Frozen SHA256: coupon_profile_association.py `9c0dbe6c83a562c5690cb10f5311ee386bc7d508ba8b2e449f85ee54eb009a93`; coupon_spatial_calibration.py `7ada959e46588c488e6d488eb8add28bf6bc0067d4364083dabcac252f9acdbf`; gui_native_trial_copy.py `d0def74a1a3ad35222c656b02a483cb03458a1e6af93cd2ed2002434dcbdBbaa` (case-insensitive hex); test_coupon_spatial_calibration.py `5d67d88f2fab632b85d52c49026df0af5004e1225035a8898cded4c6497ad8a4`.

Disposition: bounded independent source review converged; eligible for parent full regression on these frozen inputs. This is not a full-suite result, final-artifact clearance proof, physical calibration or permission to print/send. Actual geometry/tool/material/state/archive audits remain distinct required artifact gates.

## Projected-coordinate delta independent review — 2026-10-19

Latest user-confirmed projected-distance amendment reviewed against only the changed calibration policy/target mapping/native identity/test paths. Schema2 defaults to explicit `coordinate='projected'`; calibration distance is exact worldY minus the associated profile's first Y. Arc length remains a separate diagnostic, not the correction coordinate. Residual-mode rows at/before16 use the V5 minimum endpoint dimensions/area, rather than the wider admission seed. The16anchor angle clamps to the V5 maximum, yielding endpoint width/height before negative-window multiplication and16..17 area/height blending. Reference-mode source dimensions remain authoritative. Actualmesh association and earlier fixes are unchanged.

Legacy schema1 omits the newly added coordinate on encoding, injects surface_arc only on decoding, and forbids ambiguous projected schema1. Native historical emission identity removes only the added coordinate before using the original canonical dataclass JSON/hash contract. No new implicit empirical E correction appears. Unknown/missing coordinate settings reject through closed schema/enums.

`.venv/Scripts/python.exe -m unittest tests.unit.test_coupon_spatial_calibration -q`:17 PASS,.418s. Independent enum-malformed/legacy-roundtrip/projected-distance script PASS. Frozen SHA256: calibration `8328bbd6971423901dde469556ad4e4f3d9aa64a0d20c230cbe6ad38c565c2db`; native copy `541749ec5a1ba8f7c7603aae1222a9b264e09a631178a8f89d7b48159be84f52`; coupon tests `5c662835355ab1c18e30c9fe1a50ab422432b7db50b9006e5f5d3c352e043433`.

Disposition: no new material finding; projected-coordinate delta source converged and eligible for parent full regression. Historical actual57-path raw/identity replay is owner-provided artifact evidence; this reviewer independently verified the source canonical compatibility path and fixed policy identity, not a duplicate full artifact rebuild. Replacement actual artifact geometry/tool/material/state/archive proof remains separate. No source/test changes, GUI or printing by reviewer.
