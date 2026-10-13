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

## Checkpoint 1 — tasks 4–6 COMPLETE
- **4:** `application/execution_status.py` validates that `attempt_id` is an exact nonempty builtin string *before* the record dictionary lookup. This closes the unhashable-ID raw `TypeError` while preserving existing state machine progression. Commit `8ff28a2b5782e13415922fd3db47746303400e54`.
- **5:** Three focused regression tests `tests/unit/test_attempt_id_boundary.py`, commit `6b3cf56dc48facb5222bf2318c88a489c8ec956c`. Wrong/nonhashable IDs (list/dict/set, subclass string, bytes, None, etc.) and unknown nonempty IDs raise `ContractError(INVALID_STATE_TRANSITION)` without mutation; exact ID still progresses normally.
- **6:** Python 3.12 GitHub Actions [38409368194](https://github.com/nobunora/Smoothificator/actions/runs/38409368194) completed successfully; compileall and `python -m unittest discover -s tests -p 'test_*.py' -v` **180/180 PASS**. F-01 confirmed -> resolved; no printer/output/new schema behavior.

## Checkpoint 2 — tasks 7–12 COMPLETE
- **7:** reviewed immutable `InjectionAttemptRecord` (ADR-0037), including selected SHA, file/attempt identity and terminal reason.
- **8:** invalid/uppercase/truncated selected plan SHA rejects typed; `None` accepted as no selection.
- **9:** wrong or mutable attempt/file identity cannot construct an authoritative record.
- **10:** every SKIPPED/FAILED/FATAL requires `ReasonCode`; nonterminal states forbid terminal reasons.
- **11:** frozen enum `AttemptState` cannot be replaced with string aliases or mutated post-construction. Four test methods in `tests/unit/test_attempt_record_contract_matrix_v2.py`, commit `b61be4c4fb2c1e1ab73d27775d84fb99e87233e2`.
- **12:** Python3.12 GitHub Actions [38409581549](https://github.com/nobunora/Smoothificator/actions/runs/38409581549) complete: `python -m compileall -q adaptive_subedge orca_plugin tests` PASS; `python -m unittest discover -s tests -p 'test_*.py' -v` **184/184 PASS**.

## Checkpoint 3 — tasks 13–18 COMPLETE
- **13:** rechecked Accepted ADR-0049/0062 and exact v1 typed identity root schema.
- **14:** independently verified UTF-8 **byte** length for ASCII, multibyte, combining forms, emoji and embedded NUL strings.
- **15:** independently verified map key ordering by Unicode code points irrespective of insertion order.
- **16:** verified -0.0/+0.0 normalized float identity, with bool/int/float remaining distinct tagged scalars.
- **17:** verified exact four-field root reject-extra/missing/cross-domain/unknown versions plus independent full SHA256 preimage vector. File `tests/unit/test_canonical_unicode_scalar_edges.py`, 4 tests, commit `6948e2502cbc319c435234b25f3d1fa12e3371be`.
- **18:** Python3.12 GitHub Actions [38409806274](https://github.com/nobunora/Smoothificator/actions/runs/38409806274): compileall PASS, **188/188 unittest PASS**, 0 failures/errors.

## Checkpoint 4 — tasks 19–24 COMPLETE
- **19:** reviewed Accepted ADR-0023/0045/0050/0059/0063 hardware/profile/estimator schema boundaries, without claiming printable calibration.
- **20:** keep-out curve radial clearance may vary non-monotonically as fixture-defined; do not invent monotonic-radius rule; frozen profile remains immutable.
- **21:** candidate keep-out heights must start at tool tip, increase strictly and not exceed axial height.
- **22:** regularity policy's fixture evidence identifier changes v1 fingerprint while invalid mutable evidence rejects; zero v1 safety qualification implied.
- **23:** standalone `ErrorEstimatorConfig` canonical projection reacts to declared field changes but is rejected as an undeclared v1 PluginSettings fingerprint. Four tests `tests/unit/test_research_settings_boundary_v2.py`, commit `8e72124e11a8208daaf91c90a33408024287d731`.
- **24:** Python3.12 GitHub Actions [38410037491](https://github.com/nobunora/Smoothificator/actions/runs/38410037491) compileall PASS, **192/192 unittest PASS**.
