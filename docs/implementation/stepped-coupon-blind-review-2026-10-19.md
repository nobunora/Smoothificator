# Stepped layer-angle coupon — independent implementation review

Date2026-10-19. Role: independent blind source reviewer. Contract: Accepted ADR0071/current focused handoff `docs/specs/stepped-layer-angle-coupon.md` and parent actual-source/serialization adjudications. Scope is the frozen deterministic constructor/whole-mesh association/schema3 reference-angle/native identity delta. No production source/test edits, GUI or printing.

Disposition: CONVERGED for bounded core implementation review; no confirmed material finding. Eligible for continued parent full regression on these frozen inputs. Final source-catalog/family/contact/material/tool/state/archive artifact proofs remain separate and were not inferred from the core unit suite.

## Source observations

The constructor has a closed schema for fixed supported main/ruler geometry, a bounded exact placement translation, and separately identified input-v1/orca-f32-v1 serialization modes. It preserves the accepted flat1.8/vertical lead-in, one-degree facets, terminal45degree guard/1mm plateau and physical5degree rail tabs. Whole-mesh association regenerates every known vertex and triangle and checks exact ordered actual mesh, translated placement and the complete serialized working-boundary profile. It returns the main30mm working bounds rather than the extra rail bounds. Existing archive/mm/CORE/direct-hierarchy checks stay authoritative; legacy pure-extrusion validation remains unchanged.

The roundtrip owner models import9decimal coordinates as binary32, binary32 bounding-box center, binary32 subtraction and9-significant-digit local/transform output. All serialized roof boundary stations are included, rather than only unsplit angle knots. The mode participates in frozen fixture/recipe identity. Actual installed-Orca529-coordinate equivalence is parent/research-provided independent runtime evidence; this review confirms the implementation matches that adjudicated transformation, not a newly performed GUI export.

Schema3 is explicitly reference_angle and requires a pinned reference-geometry SHA256 plus typed stepped fixture. Calibration distance uses the quantized actual source section angle times20/45, not localY, desired integer labels or surface arc. Reference section metadata must match the authoritative V5 nominal mapping; residual classification/rise/short-base rules remain. Tail anchor maps16reference-mm to36degrees, clamps the previous V5 endpoint and keeps coherent stadium-area/height mapping with ordinary numeric refreeze. Raw E multiplication is not introduced.

Legacy policy schemas1/2 omit the new reference-geometry field, and native legacy emission canonicalization omits the newly added stepped_fixture/reference_geometry fields plus schema1 coordinate as appropriate. Closed enums/schema fields and exact old formula behavior remain. Unsupported serialization/unit/namespace/changed ruler/changed face/placement/profile inputs reject; core mutation does not optimize geometry or invoke GUI.

## Checks

Authoritative `.venv/Scripts/python.exe -m unittest tests.unit.test_stepped_coupon_fixture tests.unit.test_coupon_spatial_calibration tests.unit.test_native_user_dimensions tests.unit.test_gui_native_trial_copy -q`:33 PASS,2.677s,exit0. Initial command additionally named nonexistent `test_native_late_width_tail`, producing one import error; corrected command above passed all actual selected modules. No full suite was run by this reviewer.

The five stepped tests exercise full supported mesh association, tampered ruler/face/unit rejection, actual-angle mapping/codec legacy distinction and binary32 coordinate reconstruction. Existing calibration/native tests exercise prior profile/namespace/units/JSON fixes, coherent ordinary-E geometry, source restoration and inactive-mode compatibility. These are software/source evidence, not physical readability or printability proof.

## Frozen SHA256

- `tools/stepped_coupon_fixture.py`: `f99e0cb01bf4d0fdeb94f22905997afcaae50659dac997b717494b0b1b964e37`
- `tools/coupon_profile_association.py`: `b05591a9a0a3709bdd4ac928e0efab18d3b1d3aeec81756aa2d2ad3794e16d41`
- `tools/coupon_spatial_calibration.py`: `94cb424c30a52cdf9addb7b4d92de6cfbcb7f722a51fc2e4b2f17a9b2e4b4697`
- `tools/gui_native_trial_copy.py`: `c128d82a28c1c31d9c82c166538c857dd6017dafbd8e109466c416a1fc958b77`
- `tests/unit/test_stepped_coupon_fixture.py`: `416c087a75ed932dda0e671e5ec43e86a506514c1c87ac635e0bd935a2abe70a`

## Post-blind parent finding reconciliation

After the blind report completed, parent disclosed a confirmed malformed-version defect: schema_version string/None/list reached `<3` and leaked TypeError. Disposition: confirmed, fixed. Independent review verifies an exact-int guard now precedes schema-derived membership/ordered comparisons; bool is rejected as well. New regressions cover `'3'`,None,[],True and expect stable ValueError. `.venv/Scripts/python.exe -m unittest tests.unit.test_stepped_coupon_fixture tests.unit.test_coupon_spatial_calibration -q`:22 PASS,2.003s,exit0. No broader rereview or source/test edits by reviewer. Core convergence remains clean and parent fullv2 may proceed; actual artifact gates remain separate.

## Deferred artifact-only exact-error branch bound

Read-only review of `artifacts/layer-angle-0to45-coupon-v1/bind_ledger_roots_v5.py`: for a fully validated feasible incumbent error B and fixed per-floor epsilon=baseline_error*.02, any candidate's exact formatted error E>B+epsilon cannot improve the final feasible minimum B*<=B and cannot be eligible under E<=B*+epsilon. Thus expensive contact/material checks may be omitted for that candidate without changing the selected result. Equality must remain evaluated; without a feasible incumbent no pruning is justified. Sorting by exact formatted error and original member index permits stopping past the bound after the first feasible incumbent. Preserve original tie breaking/min-path selection.

The score must use the identical actual numeric freeze as binding: same saved HopPolicy/XYZ span/floor/rectangle height/top/roundedY+grid phase; width=Fraction(str(frozen.physical_width_mm[0])); same posed rectangles/base/rise/floor_union_error. Raw pre-table error is insufficient. Recompute/assert score equality at full binding; mismatch or incomplete/cancel/resource failure aborts. Report candidates skipped by the mathematical bound separately from failed/feasible candidates; do not claim their unknown contact feasibility was tested.

Status: DEFERRED, not implemented or used in this trial. Parent selected v6's narrower per-floor pure memoization of repeated source-filter work; no core or algorithmic gate change was made by this reviewer. This note is mathematical review, not a measured performance result.
