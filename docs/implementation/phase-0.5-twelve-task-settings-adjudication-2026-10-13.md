# Phase 0.5 — Twelve bounded Settings adjudication / contract-verification tasks (2026-10-13)

## Review baseline

- GitHub implementation branch `phase-0.5-skeleton-20261013`, initial head `fd05c0d1cc03ce464b4d4a523fa642d9fc6d7a2d`, Draft PR #2 against `adaptive-subedge-design`.
- Read `AGENTS.md` first, then `docs/DOCUMENT_CONTRACT.md`, approved Phase 0.5 handoff, ARCHITECTURE/IMPLEMENTATION and pertinent Accepted ADRs.
- Baseline SHA manifest `docs/AUDIT_REVISION_2026-10-13.md`, blob `ed32f47cc541443a52bc6abed289cc86b31d816b`: 81/81 tree entries matched; 65 ADRs. Neither legacy Smoothificator script was modified.
- Previous Python 3.12 GitHub Actions: 61 unit/architecture tests PASS. Not Orca runtime compatibility evidence.

## Findings, status

- F-SCHEMA (High for later implementation, documented blocker): existing `PluginSettings` v1 fingerprint covers a seven-field research slice but the Accepted ADR-0045/0050/0059/0063 and canonical SPECIFICATION require materially more optimizer/estimator, mesh-section, bead/flow, clearance and execution policy values. The previously added standalone DTOs are *not* part of v1 PluginSettingsFingerprint.
- F-PORTS (needs design evidence): `docs/ARCHITECTURE.md` enumerates `mesh_section_provider.py`, `plan_repository.py`, `cancellation.py` and only representative `MeshSectionProvider.section(...)`/`PlanRepository.put(...)`/`candidates(...)`. Exact signatures, cancellation propagation, snapshot ownership and adapter concrete mapping are unapproved. Do not invent them on this implementation branch.
- F-COMPAT (safety): do not add fingerprint-affecting fields to existing `schema_version="1"` or backfill default printer/fixture values. Draft a separate **Proposed** settings schema ADR in an adjudication branch. It does not change canonical authority until Accepted and audited.
- Independent implementation/blind review, Orca embedded Python/NumPy, physical printer and G-code execution remain unverified.

## 12-task ordered ledger

1. Confirm current GitHub branch/PR, change list, and exact manifest: completed, 81/81.
2. Analyze missing Settings identity groups, port signatures and precedence; decide scoped boundary: completed, proposed ADR and tests only.
3. Create this implementation/evidence record with tests and stop conditions.
4. Create separate design adjudication branch off audited design baseline.
5. Draft proposed settings schema-v2 ADR (not Accepted); preserve version 1 bytes and forbid invented defaults.
6. Cross-check proposed ADR against canonical specs and open separate Draft design PR, report 3-step checkpoint.
7. Add independent golden fingerprint regression fixtures proving v1 stays unchanged.
8. Add tests for missing/unknown typed schema behavior, separate research DTO projections and no physical injection.
9. Run Python 3.12 GitHub Actions and record exact results, report 3-step checkpoint.
10. Audit architecture/import boundaries and narrow published PlanStore/attempt behavior versus known ADR contracts; record any open gaps without inventing new APIs.
11. Add focused architecture or negative tests for any confirmed existing-contract gap; verify CI.
12. Final compare, manifest, two Draft PR states, record dispositions, deliver report and stop.

## Prohibitions

No Accepted ADR modification without specification review; no schema v1 fingerprint update, production G-code/Orca injection, mesh algorithms, optimizer, wheel metadata, or physical printer interaction. Nothing in a Proposed ADR is authority to implement Settings v2. Do not claim a green unit suite proves Orca or printer safety.

## Commands for focused checks

`python -m compileall -q adaptive_subedge orca_plugin tests`
`python -m unittest discover -s tests -p 'test_*.py' -v`

Run using existing GitHub Actions on the actual pushed SHA and record PASS/FAIL explicitly. Further audit notes appended after each checkpoint.
