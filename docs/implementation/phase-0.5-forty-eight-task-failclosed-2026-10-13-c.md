# Phase 0.5 — 48 bounded failure-boundary and contract-verification tasks (third 48-task tranche)

Status: PRIMARY REVIEW and scoped implementation of **existing Accepted contracts only**. No independent blind review or printer/G-code permission.

## Tasks 1–3: initial verification and review-only disposition

1. Read AGENTS.md first. Verified implementation Draft PR #2 on `phase-0.5-skeleton-20261013`, baseline commit `ca7e23a08f965d8bac817ffdf39c31bd3b2205af`; separate Proposed ADR-0066 Draft PR #3 open and unmerged. Inspected compared file list before source.
2. Read DOCUMENT_CONTRACT, handoff, Accepted ADR-0037/0062/0064/0065 and previous implementation reviews. Full 2026-10-13 manifest SHA `ed32f47cc541443a52bc6abed289cc86b31d816b` matched **81/81** pinned Git blobs, 65 ADR files, both legacy script hashes unchanged. Prior CI on exact head **177 tests PASS**.
3. Reviewed `application/execution_status.py::InjectionAttemptStore.transition` and domain `InjectionAttemptRecord`: **F-01 Medium confirmed.** Passing an unhashable `attempt_id` (list/dict/set) reaches `self._records.get(attempt_id)` and leaks ordinary `TypeError` rather than expected `ContractError(INVALID_STATE_TRANSITION)`. Domain already requires exact nonempty builtin `str` attempt identity. Minimal fail-closed front-door check is validated by Accepted ADR-0037 and AGENTS expected-failure policy. No new attempt/Orca identity scheme. This file is the required review-only scope/disposition record before production edit.

## Planned tasks 4–48 (8 checkpoints total, six tasks per checkpoint)

4. Validate exact attempt-id type before dictionary lookup, preserving monotonic state semantics.
5. Add focused malformed-ID and valid-state regression fixtures for the stable reason.
6. Execute compileall and unittest on actual pushed head and document checkpoint.
7–11. Audit immutable `InjectionAttemptRecord` and independent invalid plan-hash/file/state/terminal reason boundaries; add four focused tests of uncovered cases.
12. CI checkpoint.
13–17. Audit canonical identity root/typed digest and version/Unicode exact contracts; four independent negative/positive vectors.
18. CI checkpoint.
19–23. Review `ToolClearanceProfile` and regularity research-only v1 contracts against ADR-0063, add four independently scoped boundary cases and no printer numeric defaults.
24. CI checkpoint.
25–29. Audit PlanStore lock/reset/snapshot issuance provenance and test four deliberately ordered concurrent reset/publication/rejected-op interleavings; no unsupported postprocess attempt association.
30. CI checkpoint.
31–35. Audit AST import-boundary bypass via `from importlib import import_module as alias`; strengthen test-only alias detection if confirmed and add four synthetic/live-file checks; no production imports.
36. CI checkpoint.
37–41. Audit canonical DTO registry and PlanSemanticContent identity exclusion and add four static/dynamic regression cases for established accepted fields.
42. CI checkpoint.
43. Confirm canonical manifest 81/81 and legacy blobs on latest branch tree.
44. Re-review Proposed ADR-0066 status, Settings v2 and Port/Orca blockers.
45. Inspect entire touched diff and safety/physical gates.
46. Complete all individual work ledger and verified CI evidence.
47. Verify exact terminal documentation-closure commit GitHub Actions compileall and unittest.
48. Recheck both Draft PR status, final SHA/manifest and report/STOP.

## Boundaries, commands, validation

- Accepted contract only; no Orca live hooks, mesh optimizer, source processing, G-code matcher/emitter or file IO, physical injection, fixture claims, default hardware limits, unsupported Settings v2 or Ports signatures.
- Normal valid canonical hashes and v1 identity schema remain byte-identical.
- GitHub Actions Python 3.12: `python -m compileall -q adaptive_subedge orca_plugin tests`; `python -m unittest discover -s tests -p 'test_*.py' -v`. Record run ID/conclusion/log.
- No Ruff/mypy or wheel build configured; actual embedded Orca Python/NumPy and independent review unverified.
- Do not claim another step completed merely for writing a plan; every specific test/source check must actually run and be identified in logs.
