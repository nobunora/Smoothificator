# Phase 0.5 — Forty-eight bounded regression and contract review tasks — 2026-10-13 (second 48-task tranche)

Status: **Primary review / scoped existing-contract verification only.** No independent blind review, Orca runtime certification, acceptance of Proposed ADR-0066, or physical injection enablement.

## Verified baseline (tasks 1–3)
1. Read `AGENTS.md` before repository source. Branch `phase-0.5-skeleton-20261013`, head `3e4ea5f11e7374aa202984df8906b698470d6d3c`; Draft implementation PR #2 and Proposed ADR #3 both open/unmerged. Compared current PR changed-file metadata against `adaptive-subedge-design`.
2. Revalidated `docs/DOCUMENT_CONTRACT.md`, `docs/specs/adaptive-subedge-v1.md` and canonical handoff, Accepted ADR-0049/0062/0064/0065 and previous task record. 81/81 audited source Git blobs at `ed32f47cc541443a52bc6abed289cc86b31d816b` match the full branch tree. Both legacy Smoothificator scripts retain their original SHA. Previous exact-HEAD CI: Python 3.12 `149/149` PASS.
3. Reviewed `ErrorMetrics`, canonical scalar schema, Plan/Settings/PlanStore/InjectionAttemptStore and architecture tests. The signed bias semantics are diagnostic under ADR-0050 and may not be safely equated to the equal-direction public RMS without a normative contract. **Do not add an unapproved signed-mean-versus-RMS invariant**. The established check `abs(signed_mean_mm) <= e_max_mm` remains. Tests may cover only approved invariants and existing behavior. No production code change is presumed necessary.

## Execution matrix (48 distinct bounded review/test/check actions)

Tasks 4–6: four complementary ErrorMetrics and signed-bias regression vectors, CI and checkpoint evidence.
Tasks 7–12: independently verify typed identity/domain separation, schema/byte/token fail-closed cases; four tests and CI.
Tasks 13–18: review Settings v1 and research-only policy immutable evidence and full declared-fingerprint sensitivity; four tests and CI.
Tasks 19–24: array logical-order, shape, i64/f64 strictness and exact big-endian framing; four vectors and CI.
Tasks 25–30: bounded PlanStore immutable snapshot lifetime, rollback, malformed publications and monotonic generations; four tests and CI.
Tasks 31–36: monotonic attempt state and concurrency/terminal failure modes; four tests and CI.
Tasks 37–42: architecture import boundaries and canonical DTO ownership; four tests and CI.
Tasks 43–48: terminal review/manifest, issues/dispositions, no unapproved API/Settings v2, diff, final exact-HEAD CI and report/stop.

Each block records six meaningful operations (source/contract review, four independently exercised test assertions, CI verification). Only claims backed by source or successful GitHub CI are PASS. Prior regression coverage should not be restated as novel work.

## Invariants and stop gates

- **No modification** of legacy `Smoothificator.py` or `Smoothificator_Adaptive.py`; no changes to physical G-code processing, Orca live adapter, geometry optimizer/estimator implementation, firmware fixture or printer.
- Proposed ADR-0066 remains Proposed on a separate Draft PR; do not extend `PluginSettings.schema_version="1"` or silently alter v1 fingerprint bytes.
- Missing concrete Ports interface signatures and atomic association of PlanSnapshot with actual Orca Export invocation remain **requires-further-evidence**; do not fabricate them.
- Lint static tools/wheel packaging not configured; not permission to install arbitrary dependencies.
- Required checks via existing GitHub Actions on each pushed SHA: `python -m compileall -q adaptive_subedge orca_plugin tests` and `python -m unittest discover -s tests -p 'test_*.py' -v`; record CI failures accurately, retry only with evidence.
- Independent blind review, real NumPy ndarray/embedded Orca, real G-code, physical printer tests **not performed**.
