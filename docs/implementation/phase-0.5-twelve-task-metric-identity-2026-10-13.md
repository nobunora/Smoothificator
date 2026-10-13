# Phase 0.5 — Twelve-task metric, dependency and typed outcome review (2026-10-13)

## Preflight (task 1)
- Read AGENTS first, then branch metadata/diff and DOCUMENT_CONTRACT/handoff and relevant accepted ADRs.
- Baseline implementation branch `4b2571c521ae252dc691f3153387d1b0c9a71e54`, PR #2 Draft/unmerged, separate Proposed ADR-0066 PR #3 Draft/unmerged.
- Canonical blob manifest `ed32f47cc541443a52bc6abed289cc86b31d816b`: **81/81 exact Git blob matches**, no legacy script changes.
- Latest prior Python 3.12 focused test run: **96/96 PASS**. This is not full Phase 0.5 readiness or physical safety.

## Task 2 — primary source review findings before edits
- **M-01 Medium, confirmed:** `domain/metrics.py::ErrorMetrics` accepts a finite nonnegative but mathematically impossible `e_rms_mm > e_max_mm` or `e_p95_mm > e_max_mm`. SPECIFICATION §16 and ADR-0050 define E_max as directional maximum, E_p95 as percentile and equal-weight direction RMS; no summary percentile or RMS can exceed the maximum. This is a value-DTO consistency gate, NOT estimator execution or a change to surface sampling.
- **M-02 coverage:** Current `PlanSemanticContent` validates that candidate support points strictly backward in order and down in Z, but no focused positive hash-sensitivity tests assert that candidate order/support dependency changes modify the authoritative plan identity. Add deterministic fixtures only; do not invent geometry constraints or optimizer.
- **M-03 planned later audit:** `PlanSemanticContent.reason` uses `isinstance(reason, str)`, while the registered serializer permits exact builtin string only. A `str` subclass can enter a frozen Plan but fail at canonical hash construction. Confirm against code/ADR-0062 and apply a minimal type fix if still true.
- **Open and unchanged:** Settings v2 ADR-0066 remains Proposed, full execution-config schema/Ports/export snapshot attempt binding need adjudication/Orca fixtures. No v2 schema, Orca live adapter, actual G-code, optimizer or physical injection.

## Twelve-task ledger and focused checks
1. Inspect actual current HEAD/PR status and 81-blob manifest — complete.
2. Audit ErrorMetrics numerical invariants and plan identity coverage — complete.
3. Commit this review-only finding record before production edits.
4. Implement minimal mathematical ErrorMetrics summary consistency checks using existing typed reason codes.
5. Add positive/boundary/negative metric tests and identity regression, not physical estimator.
6. Verify compileall, unittest and record first checkpoint.
7. Audit candidate support/order hash coverage against ADR-0032/0064.
8. Add positive and malformed support/order content hash fixtures, without altering Plan semantics.
9. CI checkpoint and reviewed dispositions.
10. Confirm PlanSemanticContent reason strict-type problem and affected boundary.
11. Minimal fix + regression tests only if confirmed, leave source schema untouched.
12. Final CI/diff/PR status; record exact evidence and stop.

## Quality gates
GitHub Actions Python 3.12 checks:
- `python -m compileall -q adaptive_subedge orca_plugin tests`
- `python -m unittest discover -s tests -p 'test_*.py' -v`

No Ruff/mypy configured, no wheel/package metadata or actual Orca runtime fixture verified. No independent blind review or merge/physical printer action will be claimed. Production changes remain in Domain DTO invariants only, never change valid canonical byte grammar.
