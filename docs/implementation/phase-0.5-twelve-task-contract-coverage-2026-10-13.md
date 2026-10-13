# Phase 0.5 — Twelve bounded contract-coverage steps — 2026-10-13

Status: PRE-IMPLEMENTATION CONTRACT INVENTORY. Not a release or physical safety approval.

## Base and governance — task 1 complete

- Branch `phase-0.5-skeleton-20261013` / Draft PR #2 at baseline `5137492697191e50c84e64fc5c3cd8a4fc606d54`, based on `adaptive-subedge-design`.
- Read AGENTS first, then documentation precedence and handoff.
- Audited 2026-10-13 manifest SHA `ed32f47cc541443a52bc6abed289cc86b31d816b`: 81/81 blob SHAs match branch tree, 65 tracked ADRs.
- Existing legacy scripts unchanged; G-code integration, native Orca adaptation, optimizer, and physical printing prohibited.
- Existing focused Python 3.12 CI: 51 tests PASS (previous commit), not proof of Phase 0.5 completeness.

## Task 2 — bounded approved contract inventory

Primary ADR sources:
- ADR-0045 (`6dc799f71ff8c003c0f0061967ad54ffc3358261`): versioned ErrorEstimatorConfig; initial spacing, refinement factor >1, convergence tolerance, max refinement levels, closest-point/sign tolerance version.
- ADR-0050 (`437fc444fae43ec55d5cfe716cb09f8d14f9692f`): versioned SurfaceCorrespondencePolicy with maximum search distance, normal-dot lower bound, neighborhood expansion/tolerance, normal ray numeric version/tolerance, closest-point fallback policy version.
- ADR-0059 (`ed8741401e6a58bc1a8b5737f5381624055d69bf`): versioned MeshSectionPolicy with predicate/coplar/join/quantization tolerances and section-stability sampling/convergence policy version.
- Current `domain/settings.py` only defines ToolClearanceProfile, CandidateSegmentRegularityPolicy and partial PluginSettings; these three immutable DTO classes are absent.
- Current `application/serialization.py` declares a closed DTO registry. Any new DTO must have explicit serializable field list and stable units; no fallback `__dict__` serializer.
- **Important revision gate:** inserting these new identities into the existing `PluginSettings` fingerprint under schema version "1" changes its semantic identity. ADR-0049/0062 require schema/version review before such a change. Therefore this tranche creates isolated, typed **research-only value contracts**, not new fields in v1 PluginSettings, not a claimed full fingerprint contract and not a physical injection enabler.

## Twelve-step work boundary

1. Verify branch, manifest, ADR count/legacy hashes (DONE).
2. Source/ADR inventory of missing approved DTO and identity gate (DONE).
3. Record findings and plan tests (this record).
4. Implement standalone versioned SurfaceCorrespondencePolicy value DTO.
5. Implement standalone ErrorEstimatorConfig referencing correspondence policy.
6. Register exact serializer fields and test both DTOs under finite/strict input and hashed deterministic projection; 3-task checkpoint.
7. Implement standalone versioned MeshSectionPolicy per ADR-0059 required numeric values and policy version.
8. Test MeshSectionPolicy validation and explicit serializer bytes/fingerprint sensitivity at research-only identity level.
9. Run focused CI and report 9-task checkpoint.
10. Evaluate PluginSettings v1 fingerprint schema-version implications, runtime gating and remaining Phase 0.5 gaps, with exact evidence. Do not silently mutate v1 fingerprint.
11. Add architectural regression verifying domain dependency purity and DTO serializer field whitelist, plus independent primary review.
12. Final CI and diff, record dispositions, keep PR Draft, stop/report.

## Planned assertions (prior to edits)

- Negative: missing/incorrect versions, NaN/Inf, bool-as-number, invalid ranges, string/list instead of nested typed DTO, mutable evidence/version values all fail `ContractError`.
- Positive: explicit finite research-only values are immutable, canonicalized deterministically regardless of float/int literal notation.
- Identity: separate typed source-geometry identity of registered DTO changes when a semantic field changes, but no production `PluginSettings` or `SubEdgePlan` schema is expanded.
- Compatibility: no numerical tolerances are fabricated as defaults; callers supply research/fixture-reviewed values.
- Exact commands via existing GitHub Actions: `python -m compileall -q adaptive_subedge orca_plugin tests`; `python -m unittest discover -s tests -p 'test_*.py' -v`.
- Do not run physical printing, Orca postprocessor, cross-process G-code writes, or claim independent blind review.

## Open design issue

Full Phase 0.5 Settings/Fingerprint schema versioning remains **spec-change-required before integration**. A separate ADR/updated canonical audit/handoff is needed to finalize the complete normalized Settings fields, not an opportunistic plugin version bump in this code PR.

## Results

To be appended with exact commit and verified test evidence after each 3-task block.
