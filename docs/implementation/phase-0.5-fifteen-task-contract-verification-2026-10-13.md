# Phase 0.5 — Fifteen-task bounded contract and regression tranche (2026-10-13)

Status: primary implementation review only; **not** independent blind review or printer authorization.

## Task 1 — Fresh repository baseline

- AGENTS.md read before repo files. Branch `phase-0.5-skeleton-20261013` at `fdaa0302e519a54e5748f23d1c38bffa5c3b47b8`, Draft implementation PR #2 open/unmerged, base `adaptive-subedge-design`.
- Compared changed-file list before target file reads. Audited `docs/AUDIT_REVISION_2026-10-13.md`, SHA `ed32f47cc541443a52bc6abed289cc86b31d816b`: 81/81 exact Git tree blob matches. Both legacy script blobs unchanged.
- Draft design PR #3 at `5743c86177d653d4e61362a0cf8b09735d00b996` is open/unmerged; Proposed ADR-0066 is **not Accepted**. The current implementation PR's source-of-truth contract remains accepted ADRs 0001–0065 and the pinned handoff, regardless of draft v2 design work.
- Latest branch CI is already green with 84 tests on Python 3.12; this is only existing coverage.

## Task 2 — Review and disposition: Phase 0.5 limits

Validated scope: DTO input contracts, canonical v1 binary grammar/hash strictness, Settings v1 research-only value fields, PlanStore/InjectionAttemptStore in-process operations and import-boundary enforcement. No live Orca binding, source optimizer, G-code parser/injector, wheel, printer or physical-fixture tests.

- **C-01 / spec-change-required:** complete Settings v2 fingerprint owner/field validation remains blocked on Proposed ADR-0066 and renewed normative audit/Spec-Validated gate; do not add v2 fields to v1 hash.
- **C-02 / requires-further-evidence:** PlanStore-issued snapshot is not yet atomically associated with a unique export attempt. ADR-0065 requires lifecycle provenance for a postprocess invocation; existing `snapshot()` and `InjectionAttemptStore.begin()` separate APIs cannot establish that association. Do not invent an Orca invocation key or subtly redefine selector lifetime.
- **C-03 / requires-further-evidence:** exact Ports signatures and installed Orca embedded Python/NumPy remain unverified; no placeholders or installation assumptions.
- **C-04 / rejected as stale finding:** this initial hypothesis was falsified by reading current `adaptive_subedge/domain/metrics.py`: the exact builtin-string version check already exists, with `test_coverage_version_requires_immutable_text` in `tests/unit/test_contracts.py`. No source fix is appropriate. The remaining coverage task is a focused regression of numerical ratio boundary values and immutable DTO behavior, **not** the ADR-0044 physical support metric algorithm.

## Task 3 — Review-only outcome and fifteen-task bounded verification plan

Created this evidence record before source changes, with the following independently scoped tasks:

1. Baseline/manifest/PR verification **done**
2. Approved scope and unresolved blockers disposition **done**
3. Record findings and exact scoped test strategy **done**
4. Verify whether coverage-version DTO finding is still present; correct false/stale finding
5. Add missing ratio edge/typed numeric/frozen DTO regressions; do not repeat existing version fix
6. Run Python 3.12 compileall/unittest on task-5 head; report checkpoint
7. Audit v1 Settings fingerprint sensitivity against exact registered schema, not proposed v2
8. Add independent focused v1 hardware/tool-curve sensitivity and canonical tuple/list evidence tests
9. Run CI; report checkpoint
10. Audit PlanStore rejected-publication atomicity and candidate chronology against ADR-0065
11. Add rejected-publish/independent snapshot/state regressions; no new attempt binding API
12. Run CI; report checkpoint
13. Audit canonical encoding edge cases and prohibited package boundaries without changing byte grammar
14. Add targeted negative/golden canonical encoding regression tests and record unresolved review disposition
15. Final CI, compare final diff, reconfirm Draft PR states/legacy scripts; close evidence and stop

### Quality gates

Run on exact pushed SHA via GitHub Actions:
- `python -m compileall -q adaptive_subedge orca_plugin tests`
- `python -m unittest discover -s tests -p 'test_*.py' -v`

Ruff/mypy and wheel build NOT CONFIGURED; physical/runtime fixture NOT VERIFIED. A CI pass is not release authorization.

### Rollback

Only registered DTO validation and tests/review records may change. Reverting affected commits restores previous schema-1 byte behavior for valid inputs; no persistent G-code or printer effect.

## Completion evidence

To be appended after CI/compare; do not label unverified tasks PASS.
