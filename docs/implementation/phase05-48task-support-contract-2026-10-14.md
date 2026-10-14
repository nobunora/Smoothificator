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
