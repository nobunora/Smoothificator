# Flat microextrusion matrix — independent blind execution review

Date2026-10-19. Contract: Accepted ADR0072 and `docs/specs/flat-microextrusion-matrix-trial.md`. Scope: `tools/native_microextrusion_matrix.py`, exact-type dispatch in `tools/gui_native_trial_copy.py`, fixture source/mesh owner and directly relevant tests. No primary implementation findings were provided before completion. No implementation source/test edits, GUI or printing.

## Findings

No Critical/High or Medium finding established in this bounded execution review. One Low expected-input validation finding remains for adjudication.

FM-B1 — Low — `freeze_matrix_line` authenticates cells by canonical stringifying hash instead of exact field types. A copy of actual cell01 with `h_cmd_mm` replaced by its identical string `'1/100'` has the same matrix_identity as the expected Fraction, passes the membership check, then raises TypeError at `Fraction('.8')+cell['h_cmd_mm']`. This violates the closed exact-input/stable expected-failure boundary and can bypass callers handling ValueError. Independent direct repro confirms TypeError. It does not admit unsafe output or affect the current internally generated exact cells. Recommended direction: validate exact cell fields/types or compare a strictly typed immutable cell representation before arithmetic; reject malformed values with ValueError. Confidence high.

## Execution and source observations

The adapter is a separate exact recipe type. Ordinary NativeTrialCopyRecipe still follows its historical route; unknown recipe types reject. Commanded clearance and final-volume are kept separate from stadium physical dimensions. E is volume*10mm/filamentarea rounded once to5places, without reapplying host flow ratios. Frozen records expose requested/achieved final volume and relative rounding error; saved profile/candidate/outer-wall speed and volume caps bound feed. Closed25-cell geometry/axes, positive E, fixed1.6retract/1wipe and explicit.45x.2 assumed material envelope are recorded.

Actual original source/mesh/context/profile are interpreted and associated before output. The source evidence rejects insertion before later original deposition, unknown positive material, wrong five-layer Zset, absent label/base regions and extra final-layer deposition outside labels. Those coarse region checks are not alone a continuous physical flatness proof; the separate actual-source fixture review establishes actual25-label rendering and nominal source-top XY coverage and retains the surface-roughness limitation.

Each sample enters via a raised ceiling above original labels, restores source retraction debt, deposits one exact positive segment, applies existing bounded staged retract/reverse wipe, reconciles debt at the raised ceiling and restores anchor XYZ/feed and symbolic E translation. This explicitly distinguishes sample supportfloor.8 from actual saved anchor1.4 (after original G3 hop; labels end1.0) without changing legacy floor validation. The adapter replays generated G1 commands, rejects stationary positive material and checks exact physical-state restoration plus expected total logical-E delta. Acceleration is bounded/restored by the explicit wrapper; actual label/material/tool collision certificates remain separate required artifact gates. No claim of empirically known bead shape or complete OEM suffix execution is introduced.

## Independent actual rebuild and checks

`.venv/Scripts/python.exe -m unittest tests.unit.test_flat_matrix_fixture tests.unit.test_native_microextrusion_matrix -q`:10 PASS,1.114s,exit0.

Loaded the actual artifact recipe through its source-bound builder and independently called `rebuild_native_trial_copy`: anchor byte198905, output215395bytes,25 unique path IDs/25 PATHcomments, added E=.04830mm. Removing the insertion and declared adapter prefix exactly recovers original source bytes. Actual emission-policy identity `f301ea8446bd435b00c665750572d87ccaf0c1c28bd7c1cfb7ac3320c8f55847`. This exercises actual source state, not just scalar numeric fixtures. No package/UI/physical completion claim follows.

Fixture/source-label review is separately recorded in `docs/implementation/flat-matrix-fixture-review-2026-10-19.md`, including genuine saved-mesh association,4246/8488closed oriented mesh, actual5source layers and inspected01..25 sliced-path crops. Full regression and final independent nominal tool/material/state/archive proof remain required. Core review can converge after disposition of FM-B1; no other material finding remains in this bounded pass.


Factual anchor clarification after blind report: actual insertion offset198905 is the final M625 immediately AFTER original G3 raises Z1.0→1.4. Actual inherited XYZ is63.989/69.833/1.4, sample supportfloor remains.8, labels stop1.0, and matrix travel ceiling is1.8 (.4 savedhop above1.4). The earlier accepted design discussion's1.0 was the label layer, not this actual saved anchor. There is no additional original-label-endpoint touching premise; actual source replay/restore uses1.4. This correction changes no implementation/finding disposition.

## FM-B1 reconciliation and closure

FM-B1 disposition: confirmed/fixed. Independent source read verifies closed exact cell keys; exact str/int/Fraction field types; exact tuple/Fraction XY pairs; and membership in the fixed25 conditions before arithmetic. Hash-stringification is no longer the acceptance predicate. Malformed clearance/volume strings, malformed coordinate element and an extra key independently raise expected ValueError. Rate/diameter inputs are exact positive Fractions with128-bit bounds.

`.venv/Scripts/python.exe -m unittest tests.unit.test_native_microextrusion_matrix tests.unit.test_flat_matrix_fixture -q`:11 PASS,.800s,exit0; independent malformed-input script PASS. The earlier actual anchor clarification remains authoritative: original G3 reaches1.4 before M625198905, labeltop1.0/supportfloor.8/matrixceiling1.8, no label-endpoint touching premise. No remaining material finding in this bounded blind execution review. Parent full regression and final actual nominal tool/material/archive/Studio gates remain separate; no further production edits or broad review by this reviewer.
