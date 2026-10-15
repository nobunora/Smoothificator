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

## Task 7 — ADR-0064 plan identity field sensitivity audit

Reviewed `domain/plan.py::PlanSemanticContent`, `SubEdgeSegment`, prior identity and dependency tests, and Accepted ADR-0064. The existing tests already cover support/order, anchor, metric RMS/mean and PluginSettings v1 changes. Missing focused field-sensitivity cases include: `injectable`/reason/plugin version/compatibility descriptor, semantic volume/time totals, per-segment requested speed/commanded flow/width, and source/execution typed reference digests.

These are **test coverage gaps**, not a confirmed omission from the serializer registry. The source `_FIELDS[PlanSemanticContent]` and `_FIELDS[SubEdgeSegment]` list these fields. Add regression fixtures using only valid immutable DTO values and `dataclasses.replace`; no schema addition or geometry policy change.

## Tasks 7–9: ADR-0064 semantic field sensitivity

- Task 7: primary audit of existing PlanSemanticContent/SubEdgeSegment registration and earlier tests. Found **missing regression coverage**, not missing serializer fields, for plugin metadata/injectability/reason, volume/time summaries, candidate segment flow/width/speed/seam, and typed source/execution/settings references.
- Task 8: created `tests/unit/test_plan_semantic_field_sensitivity.py` with four tests using valid frozen DTOs and `dataclasses.replace`, commit `57f341bdd4ce84163ad2af165fa394a186fe92fd`. Every independently modified declared semantic field family changes the Plan SHA-256 while baseline identity is stable.
- Task 9: GitHub Actions Python 3.12 [38377471111](https://github.com/nobunora/Smoothificator/actions/runs/38377471111) on `57f341bdd4ce84163ad2af165fa394a186fe92fd`: compileall **PASS**, unittest **112/112 PASS**, 0 errors/failures (0.080s in log).

## Task 10 — SubEdgePlan identity type audit

**B-02 (Medium, confirmed):** `domain/plan.py::SubEdgePlan.__post_init__` uses `isinstance(self.content, PlanSemanticContent)`, allowing subclasses of the declared content DTO even though `create_plan` requires exact `PlanSemanticContent`. The constructor also checks `plan_hash` as exact `str` but only compares `plan_id` for equality, permitting an equal-valued `str` subclass ID. These are inconsistent with the canonical exact-type registered schema and typed identity contract in Accepted ADR-0064. A directly constructed frozen `SubEdgePlan` can pass early checks then fail at publishing/verification, or have noncanonical ID type.

Confirmed disposition: change only SubEdgePlan construction checks to require exact PlanSemanticContent and exact builtin `str` plan_id, retain authoritative hash equality and existing 64-hex validation. Add subclass-negative tests plus an ordinary plan-positive regression. This does not recompute content hash inside domain, which remains the application/hashing owner; `verify_plan` continues recomputation.

## Tasks 10–12: derived identity DTO construction and final checks

- Task 10: **B-02 Medium confirmed**. `SubEdgePlan.__post_init__` checked `isinstance(content, PlanSemanticContent)` while application `create_plan` accepts only the exact frozen registered type; a subclassed content DTO could construct a Plan, then fail publication/verification. The constructor also permitted a `str` subclass as an equal-valued derived `plan_id`. Both violate the exact canonical DTO/identity value-type boundary, while no hash recomputation belongs inside domain.
- Task 11: `domain/plan.py` now requires exact `PlanSemanticContent`, exact `str` for `plan_hash` **and** `plan_id`, and still enforces full equal lowercase 64-hex authoritative identity. New `tests/unit/test_subedge_plan_construction.py`: four cases for ordinary plan verification, rejection of PlanSemanticContent subtype and plan-ID string subtype, and retained explicit hash mismatch rejection by `verify_plan`. One atomic source/test commit `ed510550cfcb78374d9b02277f25671c498239be`.
- Task 12: GitHub Actions [38377685837](https://github.com/nobunora/Smoothificator/actions/runs/38377685837) for source commit `ed510550cfcb78374d9b02277f25671c498239be`: Python 3.12 compileall PASS; `python -m unittest discover -s tests -p 'test_*.py' -v` **116/116 PASS**, no failures/errors (0.141s test log). Reconfirm after this record commit on exact final HEAD.

## Final 12-task ledger

| Step | Work | Outcome |
| --- | --- | --- |
| 1 | Read AGENTS, branch/PR, changed files, canonical 81-blob set | PASS |
| 2 | Review signed error mean and canonical identities | B-01 confirmed |
| 3 | Commit reviewed scope and verification plan | complete |
| 4 | Enforce signed mean error within max absolute error | source repair |
| 5 | Three numerical error/recomputed identity regressions | +3 |
| 6 | CI checkpoint | 108/108 PASS |
| 7 | Audit plan field-level semantic SHA sensitivity | missing test coverage |
| 8 | Four field-family hash-sensitivity tests | +4 |
| 9 | CI checkpoint | 112/112 PASS |
| 10 | Review SubEdgePlan content/ID strict-type handling | B-02 confirmed |
| 11 | Enforce exact DTO/string identity types and four regressions | +4 |
| 12 | Verify CI, Git diff, PR status, manifest; close evidence | 116/116 PASS on source |

## Primary dispositions and risk boundaries

- **B-01 confirmed -> resolved:** signed-mean bound in ErrorMetrics; a value-type invariant, not the bidirectionally converged error-estimator algorithm. Normal schema and hash bytes unchanged.
- **B-02 confirmed -> resolved:** exact registered frozen content type and authoritative plan_id builtin string at Plan construction, avoiding deferred failures.
- **Field sensitivity coverage gap -> verified:** plugin metadata/injectability/reason, volumes/time, segment width/flow/speed/seam and typed identities affect semantic Plan SHA as defined in ADR-0064. The `injectable=True` test fixture is only an immutable plan identity fixture and does not enable any physical injector.
- Starting 105 tests and ending **116 tests**, +11. Six changed/added paths relative to `a7c6c03856aa30e1e170a8826c97db3f1e769b6e`: `domain/metrics.py`, `domain/plan.py`, `tests/unit/test_error_metrics_invariants.py`, `tests/unit/test_plan_semantic_field_sensitivity.py`, `tests/unit/test_subedge_plan_construction.py`, and this record. No legacy code or Orca/physical execution paths changed.
- Draft implementation PR #2 and Proposed ADR-0066 Draft PR #3 remain unmerged. Pinned 81 canonical docs/ADRs unchanged.
- **Still blocked/NOT VERIFIED:** complete PluginSettings v2 schema (Proposed ADR-0066 not Accepted), association of an immutable PlanSnapshot with unique actual Orca export attempt, concrete Ports signatures, embedded Orca Python/NumPy ndarray C/F/endianness fixture, G-code postprocess, physical printing and independent blind review. Ruff/mypy and wheel build remain NOT CONFIGURED.
- Existing compileall/unittest success is contract-specific evidence, not READY_TO_MERGE or printer release permission. Physical Injection remains forbidden.
- Rollback reverses only the two invariant checks and their tests; it would admit malformed DTOs but cannot change printer output because no production injector exists.

**Stop after exactly twelve tasks.**
