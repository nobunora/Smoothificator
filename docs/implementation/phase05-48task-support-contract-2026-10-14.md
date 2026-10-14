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
