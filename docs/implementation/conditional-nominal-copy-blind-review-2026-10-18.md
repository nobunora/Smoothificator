# Conditional nominal copy independent blind review

Date: 2026-10-18. Scope: tools-only conditional interpreter/copy stage in `conditional-nominal-body-copy-review.md`; no parent primary-review conclusions consulted. No production source, tests, baseline artifacts or printer state changed.

## Finding CBR-1 — Medium: emission policy is not associated with the pinned saved profile

Location: `tools/conditional_nominal_copy.py:218–228` (policy validation/composition), `tools/conditional_nominal_body.py:30` (actual profile resolution).

The assembler checks the requested candidate speed against actual source feed and checks that the supplied policy reproduces the supplied frozen emission. It does not check the policy's source-owned settings against the actual pinned source/project profile. Consequently a caller can replace the filament diameter, re-freeze the same path and regenerate its association, while keeping the actual source/project/profile identities. The assembler accepts the resulting copy.

Independent actual-fixture reproduction changed only the policy filament diameter to 2.85 mm, re-froze the existing path, and called `associate_derived_path` again with the same recipe, original inputs, geometry evidence and matched source lines. `compose_conditional_nominal_copy` accepted it. The first emitted E changed from `33/5000` to `249/100000`, although the saved profile and actual material remained unchanged. A separate synthetic probe also accepted changed diameter and Z hop.

Invariant: a source/profile-associated frozen path must use the declared actual extrusion conversion; merely hashing a new emission alongside the old profile identity does not establish that relationship. SPECIFICATION's commanded-flow equation and the existing `policy_from_slice` owner make filament diameter and saved flow settings meaningful inputs, not arbitrary formatting. This is an offline association/correctness defect; all physical/runtime flags remain false and this finding grants no physical authority.

Remediation direction: validate source-owned HopPolicy fields against `policy_from_slice` resolved from the pinned source/project, allowing explicitly specified conservative speed reductions and caller-owned bounds/precision. If intentional policy overrides are wanted, require a separately adjudicated, explicit override contract/identity rather than accepting them under unchanged saved-profile semantics. Cover diameter/flow, travel/retraction/hop/height/volume policy association as applicable. Confidence: high. Disposition: confirmed; awaiting parent adjudication/fix.

## Verification and negative coverage

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_copy tests.unit.test_conditional_nominal_actual -v` — PASS, 12 tests, Python 3.12.10. No test/source edits.

Independent read-only actual reproduction additionally verified:

- Output bytes exactly equal `single-sample-copy.UNVERIFIED.txt`; output SHA, anchor, association and frozen path exactly match the receipt.
- All 19,551 body-event JSONL records agree with interpreted raw-byte lengths/hashes, event kinds, object scopes and before/after state fingerprints.
- Removing the inserted span reconstructs the complete actual source exactly; strict cycle replay restores the exact saved nominal state.
- Actual source SHA `f917caf88191253f22004d47545daa4e6f78f4b4132d61529101271e4d3ba288`, project SHA `6fe38676704d886a0aa82b1179343629ff612ccb55e2ee534811d1011008e567`, producer SHA `480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba` remain pinned.

Reviewed rejection/state boundaries: actual embedded-profile/source matching; complete-line body boundaries; named immutable declared startup/firmware/object premises; no debt inference from G92; reuse of strict modal/debt arithmetic; exact single-object cancellation scopes; typed M204/M106/M73/M991 effects; unknown/malformed branches, scopes and commands; inherited acceleration and cornering eligibility; reconstruction of anchors and associations; strictly earlier material witnesses; full same-floor source feed cap; unique chronological insertions/path IDs; E/F parity; newline preservation; exact source reconstruction; duplicate marker rejection; separate UNVERIFIED atomic no-replace publication with rebuilt copy. No further material defect established in these bounded checks.

## Limits

The entry state and manufacturer command interpretations remain declared conditional premises. Recipe/geometry evidence is associated evidence, not accepted whole-job geometry. Contact, future volume, planar tool sweeps, support, quality, physical startup/firmware and full-job execution are not certified by this stage. Existing strict/synthetic gates remain separate. Physical/runtime/print authorization remains false.

## CBR-1 follow-up verification

Parent reconciliation confirmed the finding and authorized strict saved-profile policy association. Independently reviewed the correction: the composer now reads the actual current source/project `SlicedProfile`, calls the canonical `policy_from_slice` with explicit caller-owned bounds/precision, and requires exact equality for every source-owned HopPolicy field. Only candidate speed may be reduced; it remains subject to both the profile speed cap and the independently recomputed all-floor source feed cap. The check runs before association/emission acceptance. It does not trust a caller policy fingerprint as the expected model.

Independent actual-fixture probes re-froze and re-associated each changed policy before composing: diameter2.85, hop.001, halved print-flow ratio and halved XY travel speed now all reject with the saved-profile mismatch. Thus the original bypass and the parent's hop variant are closed even with fresh self-consistent frozen emission and association.

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_copy tests.unit.test_conditional_nominal_actual tests.unit.test_supplemental_copy -v` — PASS, 23 tests, 32.539 seconds, Python3.12.10. The actual regression table exercises12 source-owned substitutions (diameter, hop, printable height, XY/Z/retract/deretract feeds, maximum volume, three flow ratios and role-flow flag), each after re-freezing/reassociation; lower candidate speed still composes successfully. Strict-copy regressions pass unchanged.

Independently composed the valid actual sample and compared exact output bytes and output SHA with `artifacts/conditional-nominal-body-review/profile-bound-v2/`; source reconstruction is exact and its receipt explicitly records saved-profile association. No receipt or baseline was overwritten. No new material defect established in this bounded fix review.

Final disposition CBR-1: **confirmed / fixed / independently verified**. Original finding remains part of the record. Conditional state premises and all false physical/runtime/print-authority flags remain unchanged.
