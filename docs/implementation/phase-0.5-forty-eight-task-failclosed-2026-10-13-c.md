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

## Checkpoint 5 — tasks 25–30 COMPLETE
- **25:** reviewed actual PlanStore lock/reset/issuance and Accepted ADR-0065 process-local semantics, without inventing postprocess-attempt association.
- **26:** concurrent resetting, publishing and snapshotting cannot expose mixed-epoch entries; stale epochs return no eligible plans.
- **27:** another PlanStore's cached/issued snapshot cannot substitute for a fresh session publication.
- **28:** rejected invalid plan publication at capacity one does not advance analysis generation or evict valid retained plan.
- **29:** repeated plan-hash publication and bounded eviction produce no duplicate semantic candidates in a deterministic retention sequence. File `tests/unit/test_planstore_reset_races_v2.py`, 4 tests, commit `a452900fba9044d0a33cc37dc9cfc9ec4688a1d3`.
- **30:** Python3.12 GitHub Actions [38410248681](https://github.com/nobunora/Smoothificator/actions/runs/38410248681): compileall PASS, **196/196 unittest PASS**. Only in-process synchronization verified.

## Task 31 — architecture helper audit, pending validation
Current `tests/architecture/test_dynamic_import_boundaries.py::_literal_dynamic_targets` recognizes literal `importlib.import_module(...)` but not the equally explicit `from importlib import import_module as alias; alias(...)` nor `import importlib as alias; alias.import_module(...)`. A forbidden Domain -> Orca imported with those explicit literal aliases may not be covered by the dynamic import gate. This is a test-instrumentation coverage gap, **not** evidence that current production code imports forbidden modules. Resolve only lexical module/function aliases defined by import statements, keep computed names and shadowing limitations explicit, and test synthetic forbidden and allowed cases. No production source/import change.

## Checkpoint 6 — tasks 31–36 COMPLETE
- **31:** reviewed `tests/architecture/test_dynamic_import_boundaries.py`: literal module names reached through `import importlib as alias` and `from importlib import import_module as alias` were not recognized, allowing an architectural test bypass. This is a **test-instrumentation gap**, not proven production import.
- **32:** detection of imported function alias from `importlib` and forbidden domain->Orca in a synthetic AST test.
- **33:** detection of module alias `import importlib as mod` and forbidden Ports->Application.
- **34:** relative importlib function alias resolves explicit `package` into the forbidden full module.
- **35:** computed runtime import strings explicitly **NOT DETECTED** and not falsely claimed; scan currently present domain/engine/Ports/application/Orca package source for direct/alias literal dynamic imports. Test helper modified plus four tests in `tests/architecture/test_dynamic_import_aliases.py`, atomic commit `8470666129cb88f46341812a56837b372224de61`.
- **36:** Python3.12 GitHub Actions [38410560810](https://github.com/nobunora/Smoothificator/actions/runs/38410560810) compileall PASS, **200/200 unittest PASS**, 0 failures/errors. Dynamic import alias detection is a scoped lexical check, not a full Python scope/monkeypatch analysis.

## Checkpoint 7 — tasks 37–42 COMPLETE
- **37:** reviewed ADR-0049/0064 and current canonical DTO ownership registry; `SubEdgePlan`, runtime attempt records and process session metadata must not enter the immutable semantic preimage.
- **38:** confirmed `PlanSemanticContent` projection has exactly its registered semantic fields, excludes plan_id/hash, attempt ID and epoch, and recomputes valid plan hash.
- **39:** confirmed `semantic_tree` rejects derived/runtime `SubEdgePlan`, `InjectionAttemptRecord`, `PublishedPlan` and `PlanSnapshot` DTOs.
- **40:** tested independent attempt transition and PlanStore epoch reset leave the *semantic Plan SHA* unchanged.
- **41:** tested exact registered immutable types; derived `ErrorMetrics` and `IdentityReference` subclasses fail the domain serializer boundary. Four tests added in `tests/architecture/test_semantic_projection_closure_v2.py`, commit `a4f0dcf56d1cf4742233cfa9645051b4e94a966f`.
- **42:** Python3.12 GitHub Actions [38410834575](https://github.com/nobunora/Smoothificator/actions/runs/38410834575) conclusion SUCCESS; compileall PASS, **204/204 unittest PASS** (0 failures/errors, 0.542 s reported).

## Tasks 43–46 — governance, provenance and audit outcome
- **43:** current pre-closure implementation tree `1606f49f9da6d5f347ae70a66d95a320b753a653`, not truncated, **81/81 audited blob SHAs** match, 65 numbered ADR files. Legacy blobs `Smoothificator.py` `91dd3c1b322a5876f144412f6414ebe86ea3fdce` and `Smoothificator_Adaptive.py` `5e26ecffaa41e95bb381fc68ad012ffa690d0565` unchanged.
- **44:** re-read Proposed ADR-0066 on design Draft PR #3. Status remains **Proposed / NOT ACCEPTED**. Complete Settings v2 typed field list, policy weights, migration, physical limits and Orca runtime requirements are unresolved. Accepted ADR-0065 demands postprocess attempt ↔ eligible PlanStore snapshot atomic association; actual Orca invocation proof and Port interface signatures remain **requires-further-evidence**.
- **45:** compared implementation branch to initial `ca7e23a08f965d8bac817ffdf39c31bd3b2205af`: ten changed/added paths at pre-closure head: one production file `application/execution_status.py` (only +2 guard lines), 8 test paths (including one existing architecture test helper) and this evidence record. No legacy changes, new dependencies, physical threshold, G-code handler, Orca adapter, or v1 Settings schema change.
- **46:** this final auditable results ledger. Next check terminal record SHA CI and PR/diff/manifest after this documentation commit.

## All 48 tasks ledger

| Tasks | Executed work / verified outcome |
|---|---|
| 1 | Git branch, two Draft PR states and diff baseline verified |
| 2 | 81 audited blob SHAs and Accepted ADR governance verified |
| 3 | F-01 identified, review-only implementation scope documented |
| 4 | Exact attempt-ID front-door guard added; no raw TypeError from invalid ID |
| 5 | Three wrong/unknown/valid-ID tests and unchanged authoritative record |
| 6 | GitHub Actions **180/180 PASS** |
| 7 | Reviewed terminal Attempt DTO fields, exact identity and stable reasons |
| 8 | Full lowercase SHA and None acceptance tested; invalid hash rejected |
| 9 | Attempt/file ID must be builtin nonempty strings |
| 10 | Terminal reason required and nonterminal reasons forbidden |
| 11 | Frozen AttemptState enum / string alias rejection |
| 12 | GitHub Actions **184/184 PASS** |
| 13 | Rechecked Accepted v1 canonical scalar/root requirements |
| 14 | UTF-8 byte-length vectors including combining/emoji/NUL |
| 15 | Unicode codepoint key sorting/insertion order independence |
| 16 | -0.0 normalization and distinct boolean/integer/float tags |
| 17 | Exact typed root keys/version rejection and independent digest |
| 18 | GitHub Actions **188/188 PASS** |
| 19 | Reviewed research-only Settings and ToolClearance contract |
| 20 | Monotone height but fixture-defined, nonmonotone radial curve |
| 21 | Tool curve tip origin/height upper bound/strict order |
| 22 | Regularity fixture ID changes v1 hash; mutable evidence rejected |
| 23 | Estimator research DTO canonical but cannot impersonate PluginSettings |
| 24 | GitHub Actions **192/192 PASS** |
| 25 | Reviewed ADR-0065 PlanStore epoch + publication guarantees |
| 26 | Simultaneous reset/publication/snapshot cannot mix epochs |
| 27 | Old/cached sessions not eligible in a fresh store |
| 28 | Invalid plan publish does not evict or advance generation |
| 29 | Repeat hash updates preserve bounded unique publication candidates |
| 30 | GitHub Actions **196/196 PASS** |
| 31 | Reviewed literal dynamic import alias test gap |
| 32 | From-imported module loader alias recognized and flagged |
| 33 | Imported importlib module alias recognized and flagged |
| 34 | Relative import alias resolves package and forbidden target |
| 35 | Computed module names explicitly excluded; actual source scan verified |
| 36 | GitHub Actions **200/200 PASS** |
| 37 | Reviewed canonical ownership versus runtime derived DTOs |
| 38 | Exact PlanSemanticContent field whitelist/root identity |
| 39 | Derived/runtime DTOs excluded from semantic preimage |
| 40 | Generation/attempt status changes do not change Plan SHA |
| 41 | Subclassed DTOs rejected from canonical plan payload |
| 42 | GitHub Actions **204/204 PASS** |
| 43 | Final pre-closure audited 81-blob tree and legacy evidence checked |
| 44 | Proposed ADR-0066/Ports/attempt association remain unresolved |
| 45 | Narrow diff reviewed, no legacy/G-code or Settings changes |
| 46 | Complete evidence record and dispositions |
| 47 | Verify exact closure-commit GitHub Actions success |
| 48 | Recheck final SHA, both Draft PRs, manifest, STOP |

## Final technical disposition and limitations
- **F-01 Medium confirmed -> resolved:** `InjectionAttemptStore.transition` now reports stable `ContractError(INVALID_STATE_TRANSITION)` for nonhashable/wrong/empty attempt IDs instead of leaking ordinary TypeError. Existing valid attempt record/transition semantics unchanged.
- **Import alias coverage gap confirmed -> closed for literal lexical aliases only:** `from importlib import import_module as ...` and `import importlib as ...` synthetic forbidden dependencies now covered. Shadowing/computed names are not exhaustively statically resolved; no claim of complete Python import-security proof.
- **Established contracts directly verified, no novel requirement introduced:** immutable attempts, canonical scalar/tree identity, v1 Settings isolation, PlanStore publication/epoch/eviction, semantic content exclusion.
- Total tests **177 -> 204, +27** across seven focused stages. Main code delta is two lines in `application/execution_status.py` plus test-only architecture resolver enhancements and new test files; canonical hash grammar and physical mode unchanged.
- **Still spec-change-required:** complete Settings v2 semantic schema, acceptance of Proposed ADR-0066 and normative canonical handoff/audit restamp. **Requires-further-evidence:** exact Orca postprocess snapshot/attempt binding and supported Port signatures, embedded Orca Python/NumPy and actual fixture.
- **NOT CONFIGURED / NOT PERFORMED:** Ruff/mypy/pyright, wheel/package build, independent blind implementation review, live Orca G-code, source mesh optimizer, physical printer tests. No green CI run authorizes printing or merging.
- Rollback: revert the narrow attempt ID guard and delete test/evidence-only changes; it would restore raw exception exposure for malformed IDs but does not alter G-code output because no production injector exists. Physical Injection remains explicitly prohibited.

**Task 47 CI and task 48 PR/manifest verification must be completed after this documentation commit. Stop after task 48.**
