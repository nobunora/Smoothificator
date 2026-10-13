# Phase 0.5 — Twelve-task bounded metrics and canonical identity hardening (2026-10-13)

**State:** Primary review only; no independent blind review or physical authorization.

## Initial state and evidence — tasks 1–3

1. Read `AGENTS.md` first. Confirmed implementation branch `phase-0.5-skeleton-20261013` at `a7c6c03856aa30e1e170a8826c97db3f1e769b6e`; [Draft PR #2](https://github.com/nobunora/Smoothificator/pull/2) and [Draft PR #3](https://github.com/nobunora/Smoothificator/pull/3) both open/unmerged. Checked diff against `adaptive-subedge-design`.
2. Read `docs/DOCUMENT_CONTRACT.md`, handoff `docs/specs/adaptive-subedge-v1.md`, Accepted ADR-0062/0064 and implementation/review records. Matched 81/81 pinned Git blobs from `docs/AUDIT_REVISION_2026-10-13.md` SHA `ed32f47cc541443a52bc6abed289cc86b31d816b`, 65 ADRs. Legacy blobs: `Smoothificator.py` `91dd3c1b322a5876f144412f6414ebe86ea3fdce`; `Smoothificator_Adaptive.py` `5e26ecffaa41e95bb381fc68ad012ffa690d0565`.
3. This review record precedes any production change. Starting Python 3.12 CI: 105 PASS. Scope is immutable domain DTOs, canonical identity, bounded in-process PlanStore and existing architecture tests. No Orca adapter, G-code injector, new Settings schema, package dependencies or printer actions.

## Primary bounded finding / validated correction

**B-01 (Medium; confirmed):** `adaptive_subedge/domain/metrics.py::ErrorMetrics` currently rejects RMS/p95 > `e_max_mm` but accepts `abs(signed_mean_mm) > e_max_mm`. The signed mean of bounded signed errors must be inside the interval `[-E_max, E_max]`. For the project's bidirectional error summary (SPECIFICATION §16, ADR-0050) this is a DTO consistency condition, not an error-estimator algorithm or new hardware setting. Correct only this value invariant with existing `ContractError(INVALID_GEOMETRY)` and focused valid/invalid tests; preserve valid canonical bytes and schema.

## Exactly twelve scoped work items

1. Current branch/PR state and changed files — completed.
2. Review approved metric, canonical identity and safety boundaries; confirm B-01 — completed.
3. Record primary review, tests and no-go limits — this commit.
4. Implement bounded signed-mean metric invariant without defining estimator algorithms.
5. Test positive/negative out-of-bounds and equality/zero and stable typed reason.
6. Check GitHub Actions Python 3.12, report checkpoint.
7. Review semantic Plan hash field sensitivity for injectable/reason/version/geometry and order against ADR-0064.
8. Add independent focused regression tests for existing identity fields, not new schema semantics.
9. Check GitHub Actions, report checkpoint.
10. Audit canonical typed identity and PlanStore/Attempt fail-closed negative edges and architecture boundary; classify findings honestly.
11. Add focused tests or repair a confirmed in-scope contract defect, never a speculative Orca API.
12. Verify final SHA GitHub CI, exact diff/PR status and manifest; close this record and stop.

## Explicit remaining blockers

Proposed ADR-0066 Settings v2 is not Accepted and may not alter existing `PluginSettingsFingerprint`. A unique export attempt has no supported Orca lifecycle association; exact Port signatures, actual embedded Python/NumPy array behavior, physical fixture, and independent blind review have not been established. Release/Physical Injection remains DISABLED.

## Verification commands

`python -m compileall -q adaptive_subedge orca_plugin tests`

`python -m unittest discover -s tests -p 'test_*.py' -v`

Record exact CI run/commit/log and whether tooling is NOT CONFIGURED rather than asserting execution.

## Tasks 4–6: signed mean invariant and CI

- Task 4: minimal `ErrorMetrics` validation added `abs(signed_mean_mm) <= e_max_mm` to existing RMS/p95 maximum constraint. Commit `3d1b574abfdb79190dc3d280e7a356eebed708e1`, no change in canonical grammar or error-estimator algorithm.
- Task 5: three unit tests added in `tests/unit/test_error_metrics_invariants.py`, commit `630914021b54b619f5337a0f0fc540e2bed80d58`. Positive/negative overflow reject with `INVALID_GEOMETRY`, signed ±E_max and zero remain valid, signed-mean change affects the semantic plan hash.
- Task 6: GitHub Actions Python 3.12 [38377264645](https://github.com/nobunora/Smoothificator/actions/runs/38377264645), SHA `630914021b54b619f5337a0f0fc540e2bed80d58`: `python -m compileall -q adaptive_subedge orca_plugin tests` PASS; `python -m unittest discover -s tests -p 'test_*.py' -v` **108/108 PASS**, 0 errors/failures (0.102 s test-suite log). B-01 confirmed -> resolved for the value DTO only.
