# Angle-table trial independent review

Independent report, 2026-10-18. Review-only; no production, test, profile or device changes. Scope: `docs/specs/angle-table-trial-review.md`, native end emission and preview annotation changes, then the independent finite-bin planner. Planner is still being authored; its final freeze and tests remain outstanding. This report does not grant artifact delivery or physical authority.

## Native end emission freeze

Reviewed `tools/native_supplement_end.py`, optional integration in `tools/gui_native_trial_copy.py`, `tools/conditional_preview_annotations.py`, and directly relevant fixtures/tests. Implementer supplied source paths and passing command only; no primary findings were received.

`python -m unittest tests.unit.test_native_supplement_end tests.unit.test_gui_native_trial_copy tests.unit.test_conditional_preview_annotations -q` independently passed 15 tests, exit 0.

Environment correction: the initial unqualified `python` commands used system Python 3.14.7, including the preliminary planner pytest run (5 passed). Those are supplemental observations, not authoritative repository validation. Independently reran `.\.venv\Scripts\python.exe -m unittest tests.unit.test_native_supplement_end tests.unit.test_gui_native_trial_copy tests.unit.test_conditional_preview_annotations -q` with verified Python 3.12.10: 16 tests passed, exit 0, after the owner added a test. Subsequent acceptance uses this venv.

No Critical/High finding established in this bounded emitter review. The end policy replaces the exact old retract, stages stationary and reverse-axis retract, caps coordinated XY and filament speed, restores source debt after the ceiling hop, then relies on complete native replay to reject physical-state or symbolic-E drift. `_text` rejects unrepresentable feed/coordinate/E values rather than silently rounding them. The wipe target stays on the final axis-aligned deposited segment; diagonal/vertical endings reject. Annotation runs after end transformation, changes only comments, selects native `FEATURE: Custom`, and restores the exact prior FEATURE and dimension comments. No TYPE tag removal/suppression is present.

Remaining gate: reversal through freshly deposited material is intentionally new tool motion. Actual artifact chronological/tool-envelope audit must include that move. Unit replay proves state, not physical clearance, pressure behavior, smearing or hardware acceptance. Original source wipes and bytes remain preserved. The opt-in end policy is not part of the original angle-table spec text; parent explicitly adjudicated it for this review, and the final scope record should include its exact parameters and identity.

## Planner preliminary finding (before final freeze)

### AT-1 — Medium — exact policy validation filters out invalid numeric types

Location: `tools/angle_table_trial.py`, `AngleTablePolicy.__post_init__`, initial `numbers` comprehension. Disposition: pending adjudication. Confidence: high.

The comprehension collects only values already satisfying `isinstance(v, Fraction)` and then checks their exact type. A float in a required exact numeric field is therefore omitted from that check. Concrete independently executed counterexamples: `replace(AngleTablePolicy(), epsilon_fraction=0.02)` and `replace(AngleTablePolicy(), minimum_improvement_fraction=0.05)` both construct successfully, retaining float fields. This violates the stated bounded exact policy contract and can promote exact rational objective comparisons to floating arithmetic near epsilon/improvement boundaries. The source must validate every named numeric field before filtering or deriving lattices; include malformed float/bool/integer and oversized-rational cases in focused tests. Do not infer this is the final planner's only issue: final source/test freeze has not yet been reviewed.

Reproduction: Python imported `AngleTablePolicy`, applied the two `dataclasses.replace` calls above, and printed accepted `float Fraction` / `Fraction float`, exit 0. No repository files were mutated by reproduction.

### AT-2 — Medium — physical-height lattice construction bypasses work limits

Location: `AngleTablePolicy.__post_init__` final `self.heights` validation and `heights` property. Disposition: pending adjudication. Confidence: high.

The policy accepts a 128-bit rational grid without bounding `ceil(layer_height_mm/grid_mm)`. Construction then enumerates that entire range before any table cancellation/event checkpoint exists. `AngleTablePolicy(grid_mm=Fraction(1,10**25), maximum_events=1)` passes the existing scalar bounds and enters approximately 2e24 height iterations. Independent reproduction ran that constructor in a fresh child Python process, waited two seconds, observed no completion, then killed and reaped only that child; supervising command exited 0. This defeats the explicit finite-work/cancellation contract and permits severe resource exhaustion before precomputation. Bound lattice size arithmetically before enumerating, and/or derive only overlap-compatible lattice entries under a validated hard work limit. Test rejection of extreme ratios without constructing the lattice.

### AT-3 — Medium — lookup does not revalidate physical heights or table binding

Location: `lookup_angle_table` rectangle revalidation loop and `AngleTable`/`AngleBin` boundary. Disposition: pending adjudication. Confidence: high.

Lookup checks width, spill and improvement but not physical height, exposed height, exact overlap/grid membership, row slope/index binding or policy/source table identity. Public frozen dataclasses can be constructed/replaced with stale members. Independent counterexample constructs default bounds with step .1/max .5 and a row at slope .5 containing root rectangle X=0.19..0.4, Z=-0.075..0.175 (physical height .25 > strict .2 cap). Six copies of that row in an `AngleTable` are accepted by `lookup_angle_table(table, Fraction('.4'), Fraction('.2'))`, returning `validated-finite-bin-member`, error 321/20000. Physical spill and improvement do not imply valid physical height. The later native freezer may reject this member, but the declared validated lookup result violates the spec's independent height/stale-policy acceptance criteria. Validate immutable table structure/binding and every physical/exposed/overlap/grid bound at lookup, or narrow the API so stale data cannot cross this boundary; test the counterexample and policy replacement explicitly.

## Revised planner source verification

AT-1 and AT-2 source fixes are present: every named numeric policy field is now exact-type checked, and the height/grid ratio is arithmetically capped at 10000 before enumeration. AT-3 physical/exposed/overlap/grid checks and exact row ordering/content identity checks are present; the supplied stale/forged-height regressions now reject. Final authoritative focused test result will be recorded after completion.

### AT-4 — Low — malformed zero-slope row is not rejected before division

Location: lookup row shape validation and `scale=base/(rise/row.slope)`. Confidence high; disposition pending. A recomputed content hash is not semantic validation: construct the expected two-row table for slope step/max .5, replace zero row with `AngleBin(Fraction(0), 'selected', valid_member, Fraction(0), 'forged-flat')`, recompute `_table_identity`, and call lookup with base 1/rise .2. Authoritative Python 3.12.10 independently raises `ZeroDivisionError: Fraction(1, 0)`, rather than a stable malformed-table rejection. Validate state/member/reason/baseline consistency and zero-slope flat semantics before arithmetic. Also validate total path count (roots plus uppers), not root-block count alone. No invalid physical path was admitted by this counterexample.

### AT-5 — Medium — fallback alternatives can exceed the epsilon admission limit

Location: build alternative retention loop and lookup alternative selection. Confidence high; disposition pending. The validated spec says admit only error <= best + epsilon * unsupplemented baseline. Builder sorts candidates outside this band after in-band candidates but still retains them; lookup checks only minimum improvement. Independent authoritative reproduction with step .1/max .5/width samples (.301,) builds a genuine table, then lookup at slope .1, alternative index 2 returns `validated-finite-bin-member` for error 453741/10000000, while the row's best-known error + epsilon limit is 335631/10000000. This is not a forged/stale table. Contact-validation fallback must either remain inside the declared epsilon band or require explicit specification adjudication and label the relaxed ranking. A source support rejection does not silently authorize a worse objective member under the present contract.

AT-4 revised source verification: zero-slope row/state consistency and total root+upper path bounds now reject the reported case before division. Strong-reference validation cache is limited to four immutable exact table instances; no id-reuse gap established. The combined authoritative focused command passed 22 tests before this last source amendment; final repetition remains pending.

## External preview evidence

Official Bambu Studio exact tag `v02.08.02.61`: `src/libslic3r/ExtrusionEntity.cpp` 632–633 maps literal Custom to erCustom; `src/libslic3r/GCode/GCodeProcessor.cpp` 43–45 declares native FEATURE, 3014–3020 consumes that role, and 2494–2495 treats Custom time as preparation. The pinned local Orca sources expose the same native role mapping. Source/binary equivalence and actual UI rendering remain separate checks. Custom must not be used to assert unchanged estimates or bypass printer/plate compatibility warnings.

## Current disposition

Emitter bounded source review: no established Critical/High issue; actual artifact audit pending. Planner: review incomplete; AT-1 requires disposition and final source/tests require independent review. Preserve original printer and plate metadata and compatibility notification until a verified separately adjudicated replacement exists.

## Final reusable-owner freeze review

AT-1, AT-2, AT-3 and AT-4: confirmed, fixed and independently source/test verified. AT-5: confirmed under original fallback contract; superseded by the explicit parent-adjudicated v5 feasible-family ranking amendment. Generic lookup success no longer claims epsilon ranking. Independently read v5 `plan_angle_table.py`: it binds every retained precomputed alternative through numeric freeze/contact/material validation, computes the actual formatted feasible-family minimum and epsilon band, then ranks paths/uppers/error/stable alternative index. This matches the amended bounded family; no new geometric optimization is hidden in placement.

The optional native strict-saved-layer-height permission is default false, checks max height strictly below the actual saved height, and uses a bounds-only adapter to preserve the original inherited profile-field validation. Emitter result now fingerprints copy/end/annotation policy. No additional material issue established in that change.

Final authoritative owner-focused command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_angle_table_trial tests.unit.test_native_supplement_end tests.unit.test_gui_native_trial_copy tests.unit.test_conditional_preview_annotations -q`: **23 passed**, exit 0, Python 3.12.10. No unresolved Critical/High or confirmed unresolved Medium finding remains in the reviewed reusable-owner scope. Actual v5 artifacts and fresh geometry/motion/package replay remain required; this paragraph does not close that gate. Earlier preliminary dispositions above are historical review evidence, superseded by this section where explicitly reconciled.

## Actual-artifact independent progress

Independent package/state rebuild passed for v5 output SHA256 `2f606068fa5f8ac4894158cb2eb2eafdb119c36c40da4261edcf56e168f84798`, package `d8bebbe1284705275f292d5835e224d90773c765114a43a8a48675d53dde3801`. Exact source `a6314651032bc7faa8ceda39440a4f5e20ccf5b0bfd615bde3e0e83313bc2f59` recovered after removing all insertion spans. Independently enumerated ZIP members: only G-code and its uppercase MD5 member bytes differ; all metadata bytes preserved. Each insertion contains one native Custom comment per new path (54 new paths, 26 groups); two original Custom comments remain. Receipt: `artifacts/gui-angle0to30-trial-v2/trial-angle-table-v5/independent-package.UNVERIFIED.json`.

Independent duplicate full geometry/tool runs were explicitly stopped by parent coordination to reduce contention with owner audits/regression/rebinding. Both exited 1; no completed geometry/tool result is claimed from those runs. Independently replaying final owner proof receipts remains pending. Independent full v6 retained-family binding/ranking rerun remains active in `planner-angle-table-independent-v6`.

## Latest user tolerance amendment and final v7 evidence

The user subsequently authorized ignoring support inconsistencies up to 0.08 mm under a flattened-support assumption. Reviewed artifact/spec changes confine this to root source-contact query plane = actual bottom minus configurable 0..0.08 mm; child contact, dimensions, overlap, material/tool exclusion and state restoration are unchanged. Positive tolerance claims explicitly deny exact actual-bottom contact. Schema/table-policy/tolerance are fingerprinted, selected groups must match, and the final geometry audit independently recomputes emitted query planes and continuous source coverage. This remains an experimental support assumption, not physical gap filling proof.

The independent full v6 rank/binding rerun completed exit 0 and matched every group and selected group exactly, but is superseded by the tolerance amendment. Its independent receipt labels that limitation. Final v7 rank arithmetic was independently recomputed from every retained feasible score summary: all 26 best errors, epsilon bands, min-path/min-upper/error/index choices and minimum gains match; 50 roots, 13 uppers, all dimensions and X80..100 spans pass. All 50 root claims carry actual-minus-query = .08 and false exact-contact flag. Receipt: `planner-angle-table-v7/independent-rank-bounds.UNVERIFIED.json`; this checks arithmetic, not independent re-execution of every source-feasibility proof.

Direct independent final v7 package verification passed: raw SHA256 `ff2b739734d71fda4761ca4f26c2823adf8a619b46f5e937541d4c0786fcf023`, package `67d16189f56573ec304af8e44f19a063fadda18dc079c9fabb8716a194a047fc`. Original source recovered exactly; only G-code and uppercase MD5 bytes change in the archive; all metadata bytes remain equal. 63 new paths each carry native Custom metadata. Receipt: `trial-angle-table-v7/independent-package.UNVERIFIED.json`. Actual final geometry and tool receipts plus independent near-proof replay remain pending.

## Independent future-material 4061 investigation

The v7 future-material audit initially had no separation certificate for candidate `table_g00_b005_u` versus unchanged original line 4061 using its coarse k/4 YZ axis family. Independently reconstructed both exact material DTOs and queried the unchanged public projection kernel at `(0,1,-2/25)`, with 128-bit outward square-root bounds. Both projections are bounded and original lower minus candidate upper is strictly positive (approximately 0.0005604402966013152 dot units). Therefore this pair is certified strictly separated; the coarse-axis miss was not evidence of collision or a reason to relax material gates. Exact rational bounds/margin and DTOs: `trial-angle-table-v7/independent-future-4061-separation.UNVERIFIED.json`. Proposed witness-axis expansion still requires fresh certificates for every encountered pair and final complete audit.

The later candidate pair `table_g02_b001_r` / `table_g02_b002_r` was independently certified strictly separated at exact public axis `(0,1,1/100)`, positive outward-bound margin approximately 9.927666082843222e-06 dot units; receipt `independent-g02-separation.UNVERIFIED.json`. Reviewed the general cap-derived proposed axis: exact center-height delta and lateral delta after signed flat-half offsets, restricted to parallel constant-YZ X segments. It is routing only. Every accepted separation still requires fresh bounded public projection intervals and strict inequality; no capsule heuristic, contact tolerance or floating calculation substitutes for the certificate.

