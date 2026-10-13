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

## Results: tasks 4–6 — specification proposal separated

- Task 4: created `proposed-settings-schema-v2-20261013` from audited design commit `347098214979ff3efb5f669c6e3276c0c262d5a7`, separate from PR #2 and the implementation branch.
- Task 5: added Proposed (NOT Accepted) `docs/adr/0066-plugin-settings-fingerprint-schema-versioning-proposal.md`, commit `7cd5da090a8470165501b32357fffeed942cb927`. Proposes preserving v1 canonical bytes, versioning a later complete PluginSettings identity, no safety defaults, distinct Orca execution fingerprint ownership, no implicit migration, outstanding field schema decisions.
- Task 6: source cross-check of five relevant accepted ADR policy groups, Proposal status, absence of Accepted status, and a single-file git diff; opened **Draft [PR #3](https://github.com/nobunora/Smoothificator/pull/3)** against `adaptive-subedge-design`. Not merged and not authoritative. Full field schema, audit restamp and review still required before any v2 production implementation.

## Results: tasks 7–9 — v1 compatibility regression

- Task 7: added `tests/unit/test_v1_settings_fingerprint_golden.py` in commit `cb3bee8940a61951e870401e747142e5bbc96b45`. Four tests independently reconstruct ADR-0062 v1 tagged-root bytes using a separate test implementation with stdlib hashlib, verify semantic sensitivity of every regularity field and research-only ToolClearanceProfile metadata, and assert schema v2 / physical injection are still rejected.
- Task 8: added two architecture tests in `tests/architecture/test_versioned_dto_contracts.py`, commit `00aae761d230b2ad8339c09e2921b90f5296ccbb`. These verify `fingerprint_plugin_settings` rejects non-PluginSettings DTOs and v2/unknown root versions; v1 still exposes the same seven fields and exact four-field typed identity root.
- Task 9: GitHub Actions `Phase 0.5 contracts`, Python 3.12 run [38340202160](https://github.com/nobunora/Smoothificator/actions/runs/38340202160), head `00aae761d230b2ad8339c09e2921b90f5296ccbb`: `python -m compileall -q adaptive_subedge orca_plugin tests` **PASS** and `python -m unittest discover -s tests -p 'test_*.py' -v` **PASS 67/67**, 0 failures/errors (0.119s in logged test suite). No production Settings or identity change. Baseline test count was 61; added six, now 67.

## Task 10 — bounded import/port contract review

- Checked `docs/ARCHITECTURE.md` dependency direction and stable interface checklist against `tests/architecture/test_boundaries.py`.
- Finding P-01 (Medium, CI coverage): current `_import_forbidden` treats `adaptive_subedge.ports` as unconstrained. It also only forbids engine imports from Orca, but not engine imports from the higher-level `adaptive_subedge.application`; and it does not prohibit Orca adapters from importing UI. These are architectural **test gaps**, not evidenced current production violations.
- `adaptive_subedge/ports/` currently contains only `__init__.py`; no actual mesh_section_provider, plan_repository, or cancellation interfaces. The repository spells representative operation names but not complete signatures; implementing speculative ports now would violate the file/architecture boundary discipline. Record as **requires-further-evidence** until first real adapter/engine call surface exists.
- Decision: add CI import-regression constraints for ports/engine/adapters only. Do not add Port protocol implementations, plugin settings v2 schema, production machinery or Orca runtime code.

## Results: tasks 10–12 — Port/import architecture and final evidence

- Task 10: reviewed `docs/ARCHITECTURE.md` dependency direction, the representative Port interface names, and `tests/architecture/test_boundaries.py`. Confirmed import-test coverage gap P-01 for `adaptive_subedge.ports`, engine -> application and Orca adapter -> UI imports. Current Port method signatures remain **requires-further-evidence**; no speculative protocol/interface was implemented. Primary review only, not independent blind review.
- Task 11: strengthened `_import_forbidden` for these inward-only boundaries and added two tests for synthetic forbidden dependencies, valid domain imports and relative-import normalization; no runtime production modules changed. Commit `f3178c04a552aec2560333c6ea1f73bced3391ae`.
- Task 12: Python 3.12 GitHub Actions [38340339069](https://github.com/nobunora/Smoothificator/actions/runs/38340339069) at source head `f3178c04a552aec2560333c6ea1f73bced3391ae` ran `python -m compileall -q adaptive_subedge orca_plugin tests` **PASS** and `python -m unittest discover -s tests -p 'test_*.py' -v` **69/69 PASS**, zero errors/failures; test runner reported 0.062 s.
- Implementation diff from initial head `fd05c0d1cc03ce464b4d4a523fa642d9fc6d7a2d`: exactly four file paths before final record update (this report, two architecture tests, one focused golden fingerprint unit file); existing `Smoothificator.py`/`Smoothificator_Adaptive.py` and production domain/application modules unchanged.
- Design proposal diff: exactly one Proposed ADR-0066 Markdown file, separate new Draft [PR #3](https://github.com/nobunora/Smoothificator/pull/3) against design branch; no existing Accepted ADRs touched.
- Both PR #2 and PR #3 independently checked: `draft=true`, `merged=false`. PR #3 has not been adjudicated and cannot be taken as an Accepted ADR.
- Findings: F-SCHEMA **spec-change-required**, unresolved pending complete normative v2 field schema and review; F-PORTS **requires-further-evidence**, no unsupported interface implemented; P-01 test gap **confirmed -> resolved** at architecture-test level. No claim of independent review, Orca embedded Python/NumPy ABI, wheel build, G-code execution/optimizer, fixture safety or physical printing.
- Earlier audited 81-blob/65-ADR bundle is unchanged by the implementation PR. The separate Proposed ADR-0066 is intentionally NOT in that manifest and requires re-audit/restamp upon eventual acceptance. Neither branch is ready to merge for production.

## Task-by-task completed ledger

| Task | Action | Outcome |
| --- | --- | --- |
| 1 | Verified existing branch/PR, audited manifest and 65 ADR list | 81/81 exact blob matches |
| 2 | Bounded ownership/schema review of Settings and Ports | F-SCHEMA / F-PORTS isolated |
| 3 | Created 12-task report/test contract | Completed |
| 4 | Created separate design branch from audited source | Completed |
| 5 | Drafted proposed ADR-0066 | Proposed ONLY |
| 6 | Cross-checked ADR and opened separate Draft PR #3 | Completed; no Accepted change |
| 7 | Added independent v1 fingerprint golden reference and sensitivity tests | 4 tests |
| 8 | Tested v1/v2 root isolation and strict schema behavior | 2 tests |
| 9 | Verified CI and recorded checkpoint | 67/67 PASS |
| 10 | Reviewed Port/engine/adapter dependency policy coverage | P-01 confirmed |
| 11 | Strengthened import-boundary CI tests | 2 tests |
| 12 | Verified 69-test CI, both PRs/diff and wrote final dispositions | PASS |

## Rollback and next gate

This iteration changed only test and process-document files on implementation PR #2, plus a single **Proposed** design ADR on a separate draft PR. Reverting those commits restores previous behavior with no printer or G-code effect.

Next required scope: independent design review and *field-by-field* ADR-0066 adjudication; after Accepted approval, update normative documents, manifest and handoff then rerun repository review before implementing full Settings fingerprint. Evidence-backed Port signatures are a separate blocker; do not create generic placeholder interfaces. No printer/G-code injection may be enabled from either Draft PR.

**Stop after these 12 completed tasks.**
