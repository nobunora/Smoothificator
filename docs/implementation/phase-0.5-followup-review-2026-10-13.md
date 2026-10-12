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
- Confidence: High; disposition confirmed, pending fix.

### R-02 — Shallow frozen DTO containers
- Severity: Medium
- Location: `domain/geometry.py::StructuralLoopReference`, `domain/plan.py::InsertionAnchor`, `FinalSurfaceEnvelope`, `ChronologicalSupportEnvelope`, `SubEdgePath.support_dependency_path_ids`.
- Evidence: accepts unvalidated nested elements or list fields (e.g. `FinalSurfaceEnvelope(["a"], ["b"])`); nonstring dependency can throw untyped `TypeError`.
- Violated requirement: immutable, typed domain snapshots, deterministic serialization.
- Scenario: list inside frozen DTO mutates after publication, or invalid nested value reaches hash boundary.
- Repair: strict tuples of nonempty strings/typed PrintPoint3 where applicable; reject invalid nested content with stable ContractError.
- Confidence: High; disposition confirmed, pending fix.

### R-03 — Giant int yields untyped OverflowError
- Severity: Medium
- Location: `domain/settings.py::_nonnegative_finite`, `domain/geometry.py::_finite_mm`, `domain/plan.py::_finite`, `domain/metrics.py`, `application/serialization.py::canonical_array_token`.
- Evidence: `math.isfinite(10**400)` raises OverflowError; several validators call it without guarded conversion.
- Violated requirement: typed expected failures and finite binary64 semantics (AGENTS; ADR-0062).
- Scenario: giant malformed integer escapes as an untyped exception instead of stable ContractError.
- Repair: narrow conversion guard and regression tests for Settings/geometry/metrics/f64 array.
- Confidence: High; disposition confirmed, pending fix.

## Review scope limits

No Orca runtime, printer fixture, NumPy memory-layout parity, optimizer or physical injection checked. No schema or ADR redefinition authorized. Existing 17/17 green tests do not falsify the three findings.

Disposition: **confirmed defects; repair and CI verification required**.
