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

## Tasks 4–6 — Existing fix confirmed, extra boundary coverage

- Task 4: rejected the stale C-04 claim after reading `domain/metrics.py` and `test_coverage_version_requires_immutable_text`; exact typed version checks **already existed**. Review-correction commit `81832e112b00d883de2e5781ed0a0bb7d7d69943`.
- Task 5: added **three additional** tests `tests/unit/test_support_coverage_boundary.py`, commit `a23198e7636bd69385819a6cd0993d094941cbfe`. Cases cover valid closed endpoints 0/1, frozen DTO, invalid/range/nonfinite/huge-int/bool/list ratios, str-subclass version refusal, and canonical int-vs-float normalized field semantics. These test the existing ratio value DTO, not the ADR-0044 geometric support metric.
- Task 6: Python 3.12 GitHub Actions [38362393118](https://github.com/nobunora/Smoothificator/actions/runs/38362393118) passed `python -m compileall -q adaptive_subedge orca_plugin tests` and `python -m unittest discover -s tests -p 'test_*.py' -v`, **87/87 PASS**, no errors or failures, 0.141s reported.
- No production files changed in this block. C-04 disposition **rejected/previously resolved**, not a newly repaired defect.

## Tasks 7–9 — V1 Settings identity field sensitivity and canonical containers

- Task 7: reviewed Accepted ADR-0023/0063 against the *currently declared v1* PluginSettings/ToolClearanceProfile/regularity identity fields; avoided Proposed ADR-0066 additions. Existing golden test covered regularity fields but not every tool-profile field or every top-level v1 parameter.
- Task 8: added `tests/unit/test_v1_settings_field_sensitivity.py` with **three tests**, commit `11bc3c8aa564e7d39f702cf01a8c803929146129`. Each of seven tool-profile fields independently changes the Settings fingerprint; all three existing top-level settings parameters affect it; canonical logical list/tuple inputs normalize equivalently while ordering remains meaningful.
- Task 9: GitHub Actions [38362577309](https://github.com/nobunora/Smoothificator/actions/runs/38362577309), Python 3.12 compileall PASS and **90/90 unittest PASS** (0 failures/errors, 0.070s reported). No v2 owner/defaults introduced. Full Settings fingerprint coverage remains **spec-change-required**.

## Tasks 10–12 — Rejected-operation atomicity under current ADR-0065 API

- Task 10: primary focused audit of `PlanStore.publish`, `PlanStore.snapshot` and `InjectionAttemptStore.begin/transition`. Publication verifies the full content hash **before** assigning generation, and attempts create a validated record before insertion; their rejection atomicity was not explicitly covered by previous tests. Existing ADR-0065 attempt-to-snapshot association gap C-02 remains **requires-further-evidence** and was not silently implemented.
- Task 11: added three regression tests in `tests/unit/test_stores.py`, commit `5aaff4ca0b2976bcd53c44f389bd13b8f392f1c4`. Bad/tampered plan and unregistered DTO publications consume no generation or retained entry; invalid attempt creation leaves the store empty; rejected invalid state transitions preserve the previous immutable record.
- Task 12: GitHub Actions [38362725694](https://github.com/nobunora/Smoothificator/actions/runs/38362725694) Python 3.12 compileall PASS and **93/93 unittest PASS**, 0 failures/errors (0.097 s in log). These are tests for existing fail-closed contracts, not a newly added Atomic Snapshot+Attempt interface.
