# Phase 0.5 — Twelve bounded contract verification tasks — 2026-10-13 (continuation 2)

Status: scoped review / implementation. Primary code review, not independent blind review.

## Input contract and baseline
- Baseline branch head: `0bed44e74aa9a668c5dcaca70579901b1cf67f32`; PR #2 remains Draft against `adaptive-subedge-design`.
- `AGENTS.md` and `docs/DOCUMENT_CONTRACT.md` read; 2026-10-13 audited manifest blob `ed32f47cc541443a52bc6abed289cc86b31d816b`: **81/81** entries matched current tree; 65 ADR documents.
- Handoff blob `b9337971fc077f0c39793b87ecf0293b0b6a6c29` references the audited manifest.
- The legacy scripts must remain unchanged, no Orca live adapter or G-code file mutation, no printer capability, no guessed physical fixtures or package dependencies.
- Baseline focused CI: Python 3.12, 39 tests PASS on the earlier 2026-10-13 tranche. A passing suite is not global safety validation.

## Twelve work items
1. Verify repository head, handoff and 81 pinned blobs; identify the review/test boundaries. **Done**.
2. Focused canonical encoding and value DTO audit: cyclic caller input and invalid version metadata.
3. Correct confirmed fail-closed gaps, add negative tests, run CI; report 3-task checkpoint.
4. Review existing PlanStore/InjectionAttemptStore concurrency, publication and terminal-state tests against ADR-0037/0065.
5. Harden an approved ownership/concurrency edge case and provide deterministic tests, without filesystem or Orca APIs.
6. Verify tests/CI, consolidate findings and report 6-task checkpoint.
7. Audit canonical identity and array boundary independent vectors/invalid schema controls against ADR-0049/0062/0064.
8. Add independently derived positive and negative hash fixtures or smallest permitted correction, without changing canonical grammar.
9. Verify tests/CI and report 9-task checkpoint.
10. Audit architecture test coverage of import restrictions and cycles against AGENTS/ARCHITECTURE.
11. Add focused architecture regression tests and evaluate any uncovered policy violations; no opportunistic refactor.
12. Verify last commit's CI, diff, source hashes, record dispositions and residual gates; report all and stop.

## Initial focused findings
- C-01 (Medium): `SupportCoverageMetrics.version` accepts truthy non-string objects despite an immutable/versioned scalar DTO contract. The owner must reject invalid mutable metadata.
- C-02 (Medium): `canonical_bytes` and `semantic_tree` accept arbitrary caller-controlled lists/mappings but do not convert recursive/cyclic inputs to stable `ContractError`; Python `RecursionError` escapes the expected failure model. Reject without altering canonical bytes of all acyclic values.
- The current Phase 0.5 package remains partial; no claims about actual Orca runtime, NumPy ndarray C/F parity, broad Settings schema, printer G-code, physical calibration or independent blind review.

## Evidence and final results
Pending work items 3–12. Report exact commit SHA, commands, CI run ID, test count, and non-executed checks. 

## Tasks 1–3 completed — manifest and bounded input failures

- Step 1: confirmed Draft PR #2 baseline `0bed44e74aa9a668c5dcaca70579901b1cf67f32`, handoff blob and 81/81 manifest blobs, and no legacy script changes.
- Step 2: confirmed C-01 invalid mutable `SupportCoverageMetrics.version`, C-02 non-typed `RecursionError` from cyclic canonical tree inputs. Disposition: confirmed.
- Step 3: fixed both without changing byte encoding of valid acyclic trees. New wrapper converts recursion to `ContractError`; version requires nonempty string. Commit `a399ac6e6bce301fd440dcfa863fa6ed136a3b67`. Python 3.12 CI run [38333297267](https://github.com/nobunora/Smoothificator/actions/runs/38333297267): compileall PASS; **41/41 tests PASS**. Dispositions: C-01/C-02 confirmed -> resolved in bounded source.

## Tasks 4–6 completed — concurrent stores

- Step 4: reviewed `PlanStore` and `InjectionAttemptStore` against ADR-0037/0065 for session lifetime, issued snapshots, bounded retention, atomic publication and terminal monotonicity. No new material source defect was substantiated within this focused boundary; missing concurrent snapshot/terminal-race coverage was identified as a test gap.
- Step 5: added four focused tests for 24 parallel publications with immutable complete bounded snapshots, rejection of cross-store snapshots, two competing terminal status updates (exactly one wins), and invalid capacity values. This changes no production runtime code. Commit `81e939a792030bbd0da9e4b91ba6444553a1a490`.
- Step 6: Python 3.12 GitHub Actions [38333416210](https://github.com/nobunora/Smoothificator/actions/runs/38333416210): compileall PASS, **45/45 focused tests PASS**, 0 failures/errors, 0.076 s per CI log.
- Concurrency coverage is bounded; no proof of cross-process exclusion, Orca runtime callbacks, or G-code write atomicity is claimed. Original draft remains unmerged.

## Tasks 7–9 completed — canonical identity and cross-runtime integer encoding

- Step 7: reviewed ADR-0049/0062/0064 against `_canonical_bytes` and typed identity API. Confirmed that Python runtime's configurable integer-to-decimal digit limit could leak a `ValueError` for a valid unbounded ADR integer. Also found unhashable identity type labels leaked `TypeError` rather than rejecting via stable schema reason. Both are existing-contract defects, not new byte-grammar requirements.
- Step 8: `serialization.py` now falls back to exact unsigned decimal chunks (1000 digits per chunk, with sign preserved) when Python declines a very large integer conversion; authoritative bytes remain `i` + canonical ASCII decimal + `;`. `hashing.py` and root validation now reject non-string identity classes before dictionary membership. Added 3 tests including 5001-digit positive/negative integer vectors and anchor semantic hash change. Commit `1876ff7ebc142a61e5771fe22e57cdf8f87408cb`.
- Step 9: Python 3.12 GitHub Actions [38333592715](https://github.com/nobunora/Smoothificator/actions/runs/38333592715): `python -m compileall -q adaptive_subedge orca_plugin tests` PASS; `python -m unittest discover -s tests -p 'test_*.py' -v`: **48/48 tests PASS**, 0 failures/errors, 0.039 s recorded. Acyclic existing vectors remain unchanged.
- Cross-platform package/runtime, actual Orca NumPy array handling and independent blind review remain NOT VERIFIED. Valid large integers now produce deterministic bytes regardless of the Python int-to-str limit used for ordinary `str`, but no arbitrary-memory DoS resistance is claimed.

## Task 10 — Architecture/import-boundary test audit

- Current `tests/architecture/test_boundaries.py` inspects `ast.Import` and `ast.ImportFrom.module` strings but does not resolve relative imports with `ImportFrom.level`; `from .. import application` and package imports may escape boundary assertions.
- The current test also does not construct a top-level module dependency graph to reject import-time cycles, although AGENTS/QUALITY_GATES require material import and architecture cycle tests.
- The in-function deferred `serialization.py -> hashing.py` call path is distinct from a Python module initialization cycle: the `hashing.py -> serialization.py` import is top-level, but the reverse is delayed until function execution. The planned focused graph check will classify module-level imports separately; later full architecture/ownership review must still assess this mutual runtime dependency.
- Disposition: **confirmed architecture test coverage gaps**, not evidence that forbidden code currently executes. Planned repair is tests-only and cannot relax runtime boundaries.

## Tasks 10–12 completed — architecture validation and final gate

- Step 10: audited `tests/architecture/test_boundaries.py` against AGENTS, ARCHITECTURE and QUALITY_GATES. The previous AST test ignored relative-import levels and did not test module initialization dependency cycles. These were verification-coverage findings, **not** evidence of new forbidden imports in the current source. Module-level `hashing -> serialization` is acyclic; a separately delayed `serialization -> hashing` call dependency remains a future ownership review item, not a top-level initialization cycle.
- Step 11: added 3 architecture tests resolving absolute and relative `ImportFrom` nodes, demonstrating rejection of synthetic forbidden imports, and checking acyclic *module-level* imports through the package. Code commit `d06a61eedf2d27122ca480c18a3efd5d41a01441`. No production source changes in tasks 10–11.
- Step 12: GitHub Actions `Phase 0.5 contracts` run [38333792305](https://github.com/nobunora/Smoothificator/actions/runs/38333792305) for `d06a61eedf2d27122ca480c18a3efd5d41a01441`: Python 3.12 `python -m compileall -q adaptive_subedge orca_plugin tests` PASS, `python -m unittest discover -s tests -p 'test_*.py' -v` **51 tests PASS** (zero errors/failures, 0.078 s).
- Final Git comparison versus `0bed44e74aa9a668c5dcaca70579901b1cf67f32`: **8 file paths** changed (application hashing + serialization, domain metrics, 4 test files, this record). Both legacy scripts retain exact blobs; no new Orca/G-code injector or print path.
- Git tree at source head `d06a61eedf2d27122ca480c18a3efd5d41a01441` remains fully readable (not truncated); all 81 canonical manifest entries match pinned blob SHAs, 65 ADR files retained.
- Final source review dispositions: C-01/C-02 confirmed -> resolved; identity label / large integer canonical compatibility confirmed -> resolved; concurrency and import-graph items were **test gaps** and are now directly verified in their bounded scope.
- Relative to initial 39 tests, this twelve-task tranche added **12 tests**, reaching 51; no coverage/performance extrapolation beyond these cases.
- **Not independently verified:** Orca embedded Windows Python/NumPy, actual ndarray C/F adapter parity, complete settings/schema/port/surface-band coverage, printer physics, G-code file mutation, package/wheel build, and independent implementation/blind review. Ruff/mypy remain NOT CONFIGURED.
- PR #2 remains Draft, open, and unmerged. The scope is still **partial Phase 0.5 implementation**, not a `READY_TO_MERGE` or physical injection decision. No exact printer fixture limits were invented.

## Task outcome ledger

| Task | Action | Disposition |
| --- | --- | --- |
| 1 | Verify head, handoff and 81 manifest entries | PASS |
| 2 | Audit cyclic identity inputs and coverage version | 2 findings confirmed |
| 3 | Fix both and add tests | 41/41 PASS |
| 4 | Review PlanStore/AttemptStore atomicity | no new material source defect confirmed; test gap |
| 5 | Add four concurrent store/attempt tests | implemented |
| 6 | CI and checkpoint | 45/45 PASS |
| 7 | Review integer hash portability and typed identity labels | two input-boundary issues confirmed |
| 8 | Implement exact integer fallback, strict identity labels, three regression vectors | implemented |
| 9 | CI and checkpoint | 48/48 PASS |
| 10 | Audit architecture import boundary and initialization cycles | test coverage gap |
| 11 | Add three AST/graph tests | implemented |
| 12 | Final CI, diff, manifest check and ledger | 51/51 PASS |

## Next gate

Stop after exactly 12 tasks. Prioritize an **independent** Phase 0.5 implementation review and complete missing approved immutable Settings, support/surface-band model and port contracts in separately reviewable steps. If that work requires a new semantic policy/schema, adjudicate via ADR first. Physical injection remains disabled.
