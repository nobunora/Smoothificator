# Phase 0.5 — Follow-up Contract Review (2026-10-13)

Scope: primary focused source review of Draft PR #2 against AGENTS, ADR-0062/0064/0065 and current tests. **Not an independent blind review.** Baseline: `685afa6b797a2598418e15719aa73ac9a00a0c15`. Review-only: no source changes in this stage.

## Confirmed findings

### R-01 — Noninjectable plans returned by PlanStore.eligible
- Severity: High (latent boundary violation; injector absent)
- Location: `adaptive_subedge/application/plan_store.py::eligible`
- Evidence: checks only epoch; returns `injectable=False` plans as executable candidates. Current test `test_bounded_dedup_and_old_generation` expects exactly that.
- Violated requirement: ADR-0065 requires a current-epoch, **injectable** candidate.
- Scenario: a preview-only plan becomes an execution candidate in a later injector.
- Repair: retain all plans for preview in `snapshot`; exclude noninjectable plans only from executable `eligible` view. Test both.
- Confidence: High; disposition confirmed -> resolved, source/tests reviewed.

### R-02 — Shallow frozen DTO containers
- Severity: Medium
- Location: `domain/geometry.py::StructuralLoopReference`, `domain/plan.py::InsertionAnchor`, `FinalSurfaceEnvelope`, `ChronologicalSupportEnvelope`, `SubEdgePath.support_dependency_path_ids`.
- Evidence: accepts unvalidated nested elements or list fields (e.g. `FinalSurfaceEnvelope(["a"], ["b"])`); nonstring dependency can throw untyped `TypeError`.
- Violated requirement: immutable, typed domain snapshots, deterministic serialization.
- Scenario: list inside frozen DTO mutates after publication, or invalid nested value reaches hash boundary.
- Repair: strict tuples of nonempty strings/typed PrintPoint3 where applicable; reject invalid nested content with stable ContractError.
- Confidence: High; disposition confirmed -> resolved, source/tests reviewed.

### R-03 — Giant int yields untyped OverflowError
- Severity: Medium
- Location: `domain/settings.py::_nonnegative_finite`, `domain/geometry.py::_finite_mm`, `domain/plan.py::_finite`, `domain/metrics.py`, `application/serialization.py::canonical_array_token`.
- Evidence: `math.isfinite(10**400)` raises OverflowError; several validators call it without guarded conversion.
- Violated requirement: typed expected failures and finite binary64 semantics (AGENTS; ADR-0062).
- Scenario: giant malformed integer escapes as an untyped exception instead of stable ContractError.
- Repair: narrow conversion guard and regression tests for Settings/geometry/metrics/f64 array.
- Confidence: High; disposition confirmed -> resolved, source/tests reviewed.

## Review scope limits

No Orca runtime, printer fixture, NumPy memory-layout parity, optimizer or physical injection checked. No schema or ADR redefinition authorized. Existing 17/17 green tests do not falsify the three findings.

Disposition at review capture: **confirmed defects; repair and CI verification required**.

## Repair reconciliation and post-fix evidence

- R-01: resolved by filtering `PlanStore.eligible()` on explicit `plan.content.injectable is True` while preserving all plans in `snapshot()` for preview. Added `test_preview_only_plans_never_eligible`; old-generation tests use explicit synthetic injectable fixtures.
- R-02: resolved by validating immutable typed nested contents in structural loops, anchors, support references and final/chronological envelopes; invalid mutable or non-string fields reject with `ContractError`. Added `test_rejects_mutable_nested_immutables`.
- R-03: resolved by one domain-owned finite-binary64 predicate in `domain/numeric.py`, reused in Settings/geometry/metrics/plan and canonical f64 arrays. Added `test_huge_ints_fail_with_typed_contract_error` and an oversized-f64 array regression.
- Source implementation fix: `f596405a34c119712e00c472c701e9103775f282`; test update: `bc1c80a586e2b0e7ca7948b456f9d438b153349e`.
- CI: GitHub Actions Python 3.12 `python -m compileall -q adaptive_subedge orca_plugin tests` PASS and `python -m unittest discover -s tests -p 'test_*.py' -v` **20 tests, zero failures/errors, PASS**, source head `bc1c80a586e2b0e7ca7948b456f9d438b153349e`; see https://github.com/nobunora/Smoothificator/actions/runs/38320178003. Push CI https://github.com/nobunora/Smoothificator/actions/runs/38320173714 likewise PASS.
- Final changed-file comparison relative to pre-review head: 11 file paths, all in Phase 0.5 domain/application tests or review report; zero legacy scripts or injector files changed.
- `Spec ready gate` workflow skipped as its `codex-ready` PR label condition was not met. A skipped gate is **not** a PASS, and is not required for the unchanged handoff in this implementation-only PR.

## Final primary review disposition

**R-01/R-02/R-03 confirmed -> resolved for this bounded contract slice.** This is a primary focused review, **not** a separate independent blind review. No physical injection, Orca runtime verification, actual NumPy C/F source-array adapter or full Phase 0.5 completion is claimed. Draft PR remains unmerged pending normal independent implementation review.
