# Phase 0.5 — 48 bounded contract hardening and verification tasks — 2026-10-13

Status: **Primary repository review and limited approved-contract implementation**; not a blind independent review, no physical-injection authorization.

## Baseline and hierarchy — tasks 1–3
1. Read `AGENTS.md` first; verified Draft PR #2 / Proposed ADR Draft PR #3 are open and unmerged. Starting implementation HEAD `eb722777d74f4884476330385fc0daa59e28cd22`. Compared against audited `adaptive-subedge-design`.
2. Verified `docs/DOCUMENT_CONTRACT.md`, handoff `docs/specs/adaptive-subedge-v1.md`, Accepted ADR-0049/0062/0064/0065, ARCHITECTURE/QUALITY_GATES and the previous primary implementation review. Manifest `ed32f47cc541443a52bc6abed289cc86b31d816b`: **81/81** exact Git blob matches; legacy source blob hashes unchanged. Previous Python 3.12 contract suite: **116 PASS**.
3. Confirmed bounded review finding I-01 **Medium**: `_decimal_int_bytes` in `application/serialization.py` falls back to 1000-digit `str(lower)` chunks when native integer conversion is denied by Python's adjustable int-to-decimal cap. Python 3.11+ permits a limit as low as 640 digits; a 1000-digit nonzero remainder triggers another uncaught ValueError and undermines cross-runtime canonical encoding determinism under ADR-0049. Correct the fallback chunk width to remain below Python's minimum supported limit without changing any valid integer bytes. Verify independent large positive/negative integers under a temporarily reduced limit and restore global settings in finally.

## The remaining 45 individually bounded tasks

Tasks 4–6: repair I-01, independently test at minimum interpreter digit limit, verify CI.
Tasks 7–12: audit/tighten finite numeric and Plan DTO boundary handling; negative tests, independent vectors, CI, checkpoint.
Tasks 13–18: review physical profile and regularity Settings v1 research-only validation; regression tests, CI, checkpoint.
Tasks 19–24: review canonical plan hash/identity regression and array framing/normalization; add independent vectors and CI.
Tasks 25–30: review PlanStore bounded lifetime, reset, old-generation snapshots and rejected publication under ADR-0065; concurrency tests and CI.
Tasks 31–36: review InjectionAttemptStore monotonic status/invalid transitions and preservation; tests and CI.
Tasks 37–42: verify all DTO serialization fields, strict architecture dependency enforcement and no production G-code entrypoints; tests, CI.
Tasks 43–48: review unresolved v2 schema and Port runtime blockers, complete formal finding dispositions, full diff, CI on terminal record SHA and final 48-task ledger.

## Source/behavior constraints and tests
- Do not edit legacy `Smoothificator.py` / `Smoothificator_Adaptive.py`, build Orca live adapters, source optimization, G-code parser/injector, filesystem commits or printer paths.
- Settings v2 ADR-0066 is only Proposed on PR #3; no new schema/version, default physical limits or fingerprint migration is allowed.
- No invented Port signatures or assumed installed embedded Orca/NumPy ABI.
- Do not add lint/build dependencies. Ruff/mypy and wheel build NOT CONFIGURED. Independent blind review and printer qualification NOT PERFORMED.
- For each code review unit: inspect targeted source first; source changes only for confirmed established-contract defects; avoid unrelated cleanup.
- CI commands on exact pushed SHA: `python -m compileall -q adaptive_subedge orca_plugin tests`; `python -m unittest discover -s tests -p 'test_*.py' -v`.
- Mark test/verification evidence only when GitHub Actions job logs demonstrate it. A green unit suite is not Phase 0.5 release approval.
- Each checkpoint records six distinct review/implementation/verification results with commit SHA and unresolved gates.

## Checkpoint evidence
Pending tasks 4–48.
