# Phase 0.5 — 48 bounded support-coverage contract and specification-convergence tasks

Date: 2026-10-14. **Status: in progress — primary source review; no independent blind sign-off.**

## Preflight and review-first disposition — steps 1–5

1. Read `AGENTS.md` first, then actual PR metadata/changed-file list. Baseline `phase-0.5-skeleton-20261013` HEAD `130660cfbf0cdff9327c931121b272f9e4dc356c`; PR #2 implementation, PR #3 Proposed ADR-0066, PR #4 Proposed ADR-0067 all Draft/unmerged.
2. Read precedence/handoff and confirmed `docs/AUDIT_REVISION_2026-10-13.md` 81/81 matching exact Git blobs; original Smoothificator legacy code unchanged.
3. Examined source `domain/settings.py`, `domain/metrics.py`, `application/serialization.py`; previous standalone ADR-0043 `CandidateBeadBounds` implementation and 221/221 Python 3.12 successful tests.
4. Reviewed **Accepted ADR-0044 and ADR-0058** directly. ADR-0044 establishes `min_support_area_fraction` and `min_support_contact_width_mm`; ADR-0058 establishes `initial_support_cell_size_mm`, `support_refinement_factor`, `support_metric_convergence_fraction`, `support_width_convergence_mm`, `max_support_refinement_levels`, `minimum_support_cell_size_mm`. Support-query numeric tolerance/version is *required* but its exact field name/units need specification adjudication. Do not invent that field.
5. **Disposition: validated narrowly** for standalone immutable research-only value DTOs holding the precisely named Accepted thresholds/refinement settings, exact canonical field whitelist and negative tests. **NOT validated** for the complete `PluginSettingsV2` fingerprint or physical safety. Preserve the seven-field `PluginSettings` schema 1 and all golden v1 identities. Do not implement support geometry algorithms or decide physical defaults.

## Planned 48 reviewable actions

1–6: preflight, accepted-source review, record validated narrow DTO scope and initial design check.
7–12: immutable `SupportCoverageThresholds` with exactly two ADR-0044 fields, canonical registration, bounds tests, independent vectors and CI checkpoint.
13–18: immutable `SupportRefinementPolicy` with exactly six named ADR-0058 fields, canonical registration, numeric/frozen tests and CI checkpoint.
19–24: conservative metric bound semantics vs measured ratio and remaining required query-tolerance field: bounded static review, test coverage and design PR #3 adjudication.
25–30: all-v1 identity backward compatibility, independent source/typed DTO projection and missing/invalid inputs; CI checkpoint.
31–36: external Orca/PlanStore attempt validation vs published ADR-0065 and missing reference evidence; targeted bounded concurrency/provenance tests, CI.
37–42: architecture field-registry exactness, forbidden imports, proposed DTO ownership and no executable module expansion; tests/CI.
43–48: accepted-source and proposed review reconciliation, manifest/legacy checks, exact final code SHA CI, complete step ledger, both design PRs remain unaccepted, final report/STOP.

## Hard boundaries

- No full Settings v2 schema implementation without Accepted ADR-0066 review, no plan v1 schema changes, no speculative public SurfaceBand/Attempt evidence fields without ADR-0067 acceptance.
- These standalone DTOs **cannot** prove conservative support, convergence, geometry, clearance or fixture qualification. Numeric bounds are caller-supplied research examples, NEVER printer defaults.
- No Orca adapter, G-code parser/injector, actual file mutation, legacy script edits, new dependencies, printer/G-code tests.
- GitHub Actions Python 3.12 compileall/unittest is the only configured relevant source validation; Ruff/mypy/wheel NOT CONFIGURED.
- The primary review owner cannot claim independent approval. Missing ADR decision remains `spec-change-required` even if all tests pass.

## Checkpoint results
To be appended with exact commits and CI logs, including any failure.

## Checkpoints 1–3 — tasks 1–18, accepted support policy fragments
- 1–5: source hierarchy, 81 pinned blob SHA matches, Accepted ADR-0044/0058 and existing value-type ownership reviewed; recorded **validated narrowly** for standalone Settings fragments only.
- 6: implemented frozen `SupportCoverageThresholds` from exactly two ADR-0044 named settings in `domain/settings.py`, commit `397b49b7a719173aceb2ccbb3dd7de880f404737`.
- 7: explicit two-field canonical `_FIELDS` registry, commit `4925e76cd1739bb002df17061a935d71491ce9dc`.
- 8–11: 5 tests in `tests/unit/test_support_thresholds_adr44.py` for [0,1], contact width, invalid types, frozen canonical bytes and v1 fingerprint isolation, commit `655bee5957208df44d22a1db28b5c99dd510e10a`.
- 12: GitHub Actions [38519678974](https://github.com/nobunora/Smoothificator/actions/runs/38519678974), Python 3.12 compileall PASS and **226/226 tests PASS**.
- 13: revalidated exact six new field names in Accepted ADR-0058; no magic support-query tolerance/version identifier invented.
- 14: implemented frozen standalone `SupportRefinementPolicy` without physical defaults, commit `68b895b4e8b8e59e6123213f585d3dc30655983f`.
- 15: exact six-field canonical DTO registry, commit `7757085545fac61c709088b128f4e659cb3165c1`.
- 16–17: five regression tests in `tests/unit/test_support_refinement_adr58.py` for numerical, integer-level, frozen, bytes, v1 Settings isolation; commit `6a833bdd31a7fa9245842b8fe6e8ffc741ea4a4a`.
- 18: GitHub Actions [38519935496](https://github.com/nobunora/Smoothificator/actions/runs/38519935496), Python3.12 compileall PASS, **231/231 tests PASS**.

## Task 19 — next review-only disposition: support result bounds

Accepted ADR-0058 directly names four conservative result fields: `supported_area_fraction_lower_bound` (normalized fraction), `minimum_contiguous_support_width_lower_bound_mm`, `minimum_effective_height_lower_bound_mm`, `maximum_effective_height_upper_bound_mm` (millimeters). Existing `SupportCoverageMetrics(version, required_coverage_ratio, measured_coverage_ratio)` is a *research diagnostic*, not those hard acceptance lower/upper proofs. A standalone immutable `ConservativeSupportBounds` **result vocabulary** is narrowly validated as an explicit container for the four already-named values; it shall never itself make a support decision or claim provenance/convergence, which requires future engine and numeric policy. Any tolerance/version or engine algorithm remains outside this scope.

Field validation may check finite, nonnegative magnitudes, normalized area [0,1] and effective min<=effective max; do not infer a physical contact threshold. Register all fields without touching PluginSettings v1 or plan root semantic bytes. New result DTO must not be used as a full Settings fingerprint.

## Checkpoint 4 — tasks 19–24 complete, conservative support result DTO
- 19: audited Accepted ADR-0058's four exact conservative bound outputs, distinguished them from legacy `SupportCoverageMetrics(required_coverage_ratio, measured_coverage_ratio)` diagnostic and verified standalone result-only semantic scope in a **review-only** pass (above).
- 20: added frozen `ConservativeSupportBounds` with area lower fraction, contiguous-support-width lower bound, min-effective-height lower bound, max-effective-height upper bound; range and typed failures. Commit `50271d395be6c5dcfe425ff0b7902d15cf097e15`.
- 21: registered the four exact fields in the sole canonical serializer registry; commit `f4072509c7a82c009df0390402b6027caec84c01`.
- 22: five tests `tests/unit/test_conservative_support_bounds_adr58.py` for exact schema, immutable values, fractions/dimension bounds, canonical sensitivity and v1 Settings fingerprint exclusion; commit `dd5787d21f9fb81b5fe238d31338703ba0a822ea`.
- 23: updated [Draft PR #3 field-level schema review](https://github.com/nobunora/Smoothificator/blob/proposed-settings-schema-v2-20261013/docs/implementation/settings-v2-schema-adjudication-review-2026-10-13.md) to distinguish support thresholds, adaptive refinement **settings**, conservative bound **outcome**, and unresolved mandatory support-query numeric tolerance/version. Design commit `d3b97de941b6c95e5a4f5985675180eb3daefc58` remains review-only.
- 24: Python 3.12 GitHub Actions [38520143725](https://github.com/nobunora/Smoothificator/actions/runs/38520143725): compileall PASS; **236/236 unittest PASS**, zero failures/errors. No support geometry engine/cell convergence executed.

## Checkpoint 5 — tasks 25–30, v1 schema/no physical mode isolation
- 25: reviewed `PluginSettings(schema_version="1")` seven-field closed projection and ADR-0023/0049 identity ownership; existing research fragments cannot silently enter it.
- 26: architecture test checks `_FIELDS` exactly matches all fields in `SupportCoverageThresholds`, `SupportRefinementPolicy`, `ConservativeSupportBounds` and `CandidateBeadBounds`.
- 27: distinguishes legacy diagnostic `SupportCoverageMetrics(required_coverage_ratio,measured_coverage_ratio)` from the four-conservative-bound hard-result vocabulary (not synonymous or interchangeable).
- 28: verifies instantiating research DTO fragments cannot change authoritative Settings v1 fingerprint and unapproved v2 schema version remains rejected.
- 29: verifies even apparently favorable research thresholds/bounds never satisfy `PluginSettings.require_physical_injection()`; tests `tests/architecture/test_support_contract_isolation.py` commit `5890420c2b92e4f9cf8414a0027ec35e1a81df6a`.
- 30: GitHub Actions [38520370033](https://github.com/nobunora/Smoothificator/actions/runs/38520370033), Python 3.12 compileall PASS and **240/240 unittest PASS**. No v1 schema or physical mode modified.

## Task 31 scoped primary review — in-process attempt/PlanStore risks
Accepted ADR-0037/0065 require atomic per-invocation immutable candidate issuance and unique Attempt ID, bounded store/epoch validity and failure rollback. Source `application/plan_store.py::begin_postprocess_attempt` already handles these under PlanStore->AttemptStore lock order. Existing tests cover preview exclusion, eviction/reset, duplicate UUID refusal and 8-worker issuance; remaining bounded test gap: coordination under **simultaneous publication and issuance**, failed initiation followed by normal initiation without state/epoch corruption, and old-generation retention during concurrent newer publish. Do not change public API or infer actual Orca postprocess association from these pure-process tests.

## Checkpoint 6 — tasks 31–36: retained-plan and issue-pair interleavings
- 31: reviewed PlanStore/InjectionAttemptStore source under Accepted ADR-0037/0065; the in-process atomic pair is under one PlanStore lock, not yet wired to an actual Orca callback.
- 32: new test asserts a preview-only/candidate-free issued snapshot is not retroactively filled when a later injectable plan is published.
- 33: adversarial Event/ThreadPool scheduling tests that `publish` cannot enter PlanStore lock while attempt record creation is paused; previously issued snapshot remains old generation.
- 34: rejected Attempt creation does not retain an externally accessible issued snapshot, change earlier attempt records or invalidate held plans.
- 35: same semantic plan republished under a later generation does not change previously issued Attempt/Plan identity; four tests `tests/unit/test_support_attempt_epoch_matrix.py` commit `0050f0731aef7b8417bcb96d62ef8cb23d16733c`.
- 36: GitHub Actions [38520520186](https://github.com/nobunora/Smoothificator/actions/runs/38520520186), Python 3.12 compileall PASS, **244/244 unittest PASS**. Distinct runtime hook/source-file pairing and G-code precommit checks remain deferred.

## Checkpoint 7 — tasks 37–42, architecture and no premature execution
- 37: re-reviewed AGENTS hard dependency rules, `docs/ARCHITECTURE.md` and the closed `_FIELDS` canonical DTO registry against the new research-only support schema.
- 38: checked standalone support threshold/refinement and conservative bounds DTOs plus CandidateBeadBounds all belong to `adaptive_subedge.domain`, remain frozen and have exact fields in `application/serialization.py`.
- 39: verified no support fields silently enter the existing seven-field `PluginSettings(schema_version="1")` identity.
- 40: AST/import graph checks show no forbidden `domain.settings`/`domain.metrics` outbound imports, including literal dynamic module lookups.
- 41: Phase 0.5 source contains no premature `orca_plugin/gcode`, `orca_plugin/capabilities`, live `orca_plugin/adapters` or optimizer/analyzer implementation from the later phase. Four new tests in `tests/architecture/test_support_phase05_boundary.py`, final corrected commit `5841ba5610c4beaaeede76a8828e87333ec6a485` (initial test created at `7a56b772275aa0197cfbb05e35b1054b6b41b83a`, then repaired a weak assertion).
- 42: Python 3.12 GitHub Actions [38520721561](https://github.com/nobunora/Smoothificator/actions/runs/38520721561): compileall PASS and **248/248 unittest PASS**, 0 errors/failures.

## Checkpoint 8 — tasks 43–48, final audited closure
- 43: read actual pre-final Git source tree, **81/81** canonical manifest Git blobs unchanged, tree not truncated, original legacy script blobs `91dd3c1b322a5876f144412f6414ebe86ea3fdce` and `5e26ecffaa41e95bb381fc68ad012ffa690d0565`.
- 44: independently retrieved PR metadata: implementation [PR #2](https://github.com/nobunora/Smoothificator/pull/2), Settings v2 [PR #3](https://github.com/nobunora/Smoothificator/pull/3), DTO/attempt [PR #4](https://github.com/nobunora/Smoothificator/pull/4) all Draft, open, unmerged. Neither Proposed ADR-0066 nor Proposed ADR-0067 has become Accepted.
- 45: compared implementation HEAD against starting `130660cfbf0cdff9327c931121b272f9e4dc356c`: ten paths: **three production** `domain/settings.py`, `domain/metrics.py`, `application/serialization.py`; **six tests**; this evidence record. No legacy, Orca adapter, G-code processor, dependency, v1 Settings/schema/Plan identity change.
- 46: completed this detailed review ledger, preserving source-verified proofs and open source/fixture decisions. No false claim that a DTO means working support estimator or that all Phase 0.5 acceptance criteria are satisfied.
- 47: verify a new GitHub Actions run at the exact **final evidence-record commit** (not only preceding code SHA); record the actual result in final report.
- 48: reconfirm exact last SHA, tree, 81/81 blobs and all three PR states after that terminal run; then stop.

## All 48 distinct work items and disposition

| # | Completed substantive action |
|---|---|
| 1 | Read AGENTS rules first |
| 2 | PR #2/3/4 baseline state and changed-path review |
| 3 | 81/81 pinned source blobs and two legacy hashes |
| 4 | Compare Accepted ADR-0044/0058 and existing Settings/metric owners |
| 5 | Commit narrow review-only implementation disposition |
| 6 | Implement frozen SupportCoverageThresholds (ADR-0044) |
| 7 | Register exact canonical threshold fields |
| 8 | Test normalized area threshold inclusive boundary |
| 9 | Test contact-width and wrong scalar failure reasons |
| 10 | Test deterministic canonical projection/frozen DTO |
| 11 | Test v1 Settings exclusion and missing-value failure |
| 12 | CI 226/226 PASS |
| 13 | Review six exact ADR-0058 adaptive refinement settings |
| 14 | Implement immutable SupportRefinementPolicy |
| 15 | Register exact six-field canonical projection |
| 16 | Test numeric refinements, budget, finite and cell-size bounds |
| 17 | Test canonical sensitivity and v1 rejection |
| 18 | CI 231/231 PASS |
| 19 | Review conservative result semantics vs legacy diagnostic metric |
| 20 | Implement frozen ConservativeSupportBounds |
| 21 | Register exact four-field result DTO |
| 22 | Test normalized lower bounds, min/max, immutability and semantic sensitivity |
| 23 | Update Proposed ADR-0066 review packet with Settings/result separation |
| 24 | CI 236/236 PASS |
| 25 | Review original seven-field v1 identity scope |
| 26 | Regression check all standalone DTO field registries |
| 27 | Test conservative result vs legacy ratio diagnostic separation |
| 28 | Test original v1 fingerprint remains unchanged |
| 29 | Test favorable research-only support values do not enable physical injection |
| 30 | CI 240/240 PASS |
| 31 | Review bounded PlanStore/AttemptStore publication consistency |
| 32 | Test preview-only/empty issuance vs later publication |
| 33 | Test concurrent publication waits on atomic attempt issuance |
| 34 | Test attempt creation rollback does not affect prior records |
| 35 | Test repeated plan hash generation cannot mutate in-flight snapshot |
| 36 | CI 244/244 PASS |
| 37 | Review architecture and canonical registry ownership |
| 38 | Test all new DTOs immutable, explicitly registered and domain-owned |
| 39 | Test v1 Settings fields remain closed |
| 40 | Test forbidden import/literal dynamic import edges |
| 41 | Test no premature Orca/G-code execution modules |
| 42 | CI 248/248 PASS |
| 43 | Revalidate pinned manifest/legacy blobs |
| 44 | Recheck three Draft proposal/implementation PRs |
| 45 | Check exact Git diff and production scope |
| 46 | This final evidence record |
| 47 | Verify exact-final-commit GitHub Actions |
| 48 | Reconfirm exact final state and STOP |

## Technical outcome and limits
- **Standalone DTOs implemented:** ADR-0044 two-field `SupportCoverageThresholds`, ADR-0058 six-field `SupportRefinementPolicy` and four-field `ConservativeSupportBounds`, with exact canonical serializer field registration. They add no default hardware settings, geometry algorithm, candidate support estimator, acceptance predicate, existing Plan fields or Settings v1 schema changes.
- **Tests:** starting 221, ending 248, **27 new tests** in six new focused modules. All documented CI checkpoints passed Python 3.12 compileall/unittest, but no installed Orca or NumPy ABI was tested.
- **Proposed design PR #3 updated:** the review packet now identifies the three approved-source support DTO groups while noting the **required but unresolved** exact support-query numeric tolerance/version field name, v2 grouping and fixture-dependent safety thresholds. Proposal remains NOT ACCEPTED.
- **Remaining Phase 0.5 blockers:** complete PluginSettings v2 policy/identity schema and fingerprint (Proposed ADR-0066), missing `SurfaceBand`/expanded Plan/Attempt validation DTO semantics and accepted schema versions (Proposed ADR-0067), remaining actual invocation/port ownership review and a complete specification-to-implementation review. This tranche does not declare Phase 0.5 complete.
- **Not performed/not configured:** no external physical calibration, Orca plugin callback runtime test, G-code mutation, optimizer, hardware injection, wheel packaging, Ruff/mypy/pyright or independent blind review. Passing a DTO-only test cannot prove conservative geometric support acceptance.
- **Rollback:** revert isolated DTO and serializer additions and the six new test files; prior v1 fingerprints stay identical throughout the change. Original scripts remain untouched.

**Physical Injection prohibited. Keep PR #2, #3, #4 Draft/unmerged; no merge or physical-print enablement.**
