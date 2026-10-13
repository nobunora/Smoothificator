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

## Tasks 4–9 — approved, standalone DTO implementation and CI

- Task 4: `domain/settings.py` adds `SurfaceCorrespondencePolicy` from ADR-0050 with explicit distance, normal alignment, local neighborhood, ray numeric tolerance and versioned fallback policy fields. All caller-supplied, no defaults or geometry algorithms. Commit `7f04c69543bb6c5b6339e5aca97c6366ce8ca987`.
- Task 5: `ErrorEstimatorConfig` from ADR-0045 includes initial error spacing, refinement factor >1, convergence tolerance, maximum refinements, sign/closest-point version and nested immutable correspondence policy. Commit `0b27767be83bd6a4ada7c4fbf83a4815ad7f95c2`.
- Task 6: explicit `serialization._FIELDS` whitelist for these two DTOs and four focused tests for frozen values, canonical determinism, meaningful field mutation, nonfinite/type/range rejection. Commit `2e67f0f52b5db7a184c792b7fde231e68e0d3e76`; Python 3.12 GitHub Actions `38336969467`: compileall PASS, **55/55 tests PASS**.
- Task 7: `MeshSectionPolicy` from ADR-0059: caller-supplied predicate epsilon, coplanar epsilon, join tolerance, quantization geometry tolerance and sampling/convergence policy version. Strict positive finite numerics; no broad vertex exclusion default. Commit `f70d69c824f63ff534bb35a428a74de7c0b96a50`.
- Task 8: registered exact serializer fields and three frozen/canonical/invalid-boundary tests. Commit `2060f0d539c7a9582b9adf64e5b1efc572b50b5a`.
- Task 9: Python 3.12 GitHub Actions `38337106103`: compileall PASS and **58/58 tests PASS** (0 failures/errors). No live Orca adapter, optimizer, physical output or G-code mutation.

## Task 10 — Settings identity/schema integration audit

- `PluginSettings.schema_version` still equals `"1"`, with a closed v1 dataclass and canonical serializer field registry. It does **not** contain these three standalone DTOs.
- ADR-0045/0050/0059 demand estimator/correspondence/section settings take part in the eventual PluginSettingsFingerprint. ADR-0049/0062 require schema/version update when adding identity-affecting semantics. Inserting these fields into current v1 and still claiming v1 identity would silently change the digest contract.
- Disposition: **spec-change-required** for complete settings fingerprint integration. Requires accepted versioned Settings schema decision, canonical specification/handoff restamping and repository review **before** consuming these new DTOs for actual injection. The existence of a research-only value DTO does not satisfy the end-to-end plugin-Settings/Fingerprint requirement.
- Scope boundary is deliberate. No independent Orca runtime compatibility proof is available; no package build, mesh section/estimator implementation, safety calibration, source-geometry correspondence or physical injection is claimed.

## Task 11 — architecture/schema regression suite

- Added `tests/architecture/test_versioned_dto_contracts.py` at commit `37b313bc42a9a9f98280029f0682d57fa6560302`.
- Tests assert three new DTOs have exact explicit canonical `_FIELDS` corresponding to declared dataclass fields; `PluginSettings` v1 still contains its original seven fields and does not silently fingerprint research-only DTOs; physical injection remains rejected with `PHYSICAL_INJECTION_NOT_AUTHORIZED`.
- CI [38337219038](https://github.com/nobunora/Smoothificator/actions/runs/38337219038): Python 3.12 compileall PASS, **61/61 focused tests PASS**, 0 failures/errors. No claim of full optimizer/policy completeness.

## Task 12 — final diff, evidence and stop condition

- Compared implementation branch against base head `5137492697191e50c84e64fc5c3cd8a4fc606d54`. Six changed file paths: `domain/settings.py`, `application/serialization.py`, three new `tests/` files and this implementation review record. No legacy Smoothificator scripts or G-code execution components changed.
- Canonical specification/ADR references remain at the same pinned revision, no unreviewed ADR or hash identity schema modification has been made.
- Focused suite increased from 51 to **61 tests**, all successful in Python 3.12. This is positive bounded code evidence, not evidence of compatibility with actual installed OrcaSlicer or physical machine.
- **Findings dispositions**: missing ADR-0045/0050/0059 immutable value DTO coverage confirmed -> resolved *as standalone research-only DTOs*. Validation and canonical field registry complete for this scope. End-to-end PluginSettingsFingerprint inclusion remains **spec-change-required / unresolved**; it was intentionally not implemented under the existing v1 semantic identity.
- **Not run / not configured**: embedded Orca runtime, actual NumPy array adapter C/F/endian tests, wheel build, fixture calibration, optimizer/mesh section geometry, full static type analyzer and independent implementation/blind review. Physical injection remains forbidden.
- Draft PR #2 stays **open, Draft and unmerged**. Work stopped after the twelve bounded tasks. Next gate is ADR-led PluginSettings fingerprint schema finalization/re-audit, completion of other Phase 0.5 DTO/ports, and genuinely independent reviewer examination; no code merge or print authorization.
