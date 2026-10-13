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

## Verified checkpoints, tasks 4–42

### Tasks 4–6 — ErrorMetrics invariants
- **4** independent finite error-grid and signed-bias boundary tests under existing E_max contract; **5** wrong scalar type/NaN/negative input rejections and valid signed-mean changes reflected in semantic Plan SHA.
- Test file `tests/unit/test_metric_consistency_matrix.py` (4 tests), commit `6d5b4e17bc81deb9e6ce53633e1383b01c719948`.
- **6** Python 3.12 GitHub Actions [38404083070](https://github.com/nobunora/Smoothificator/actions/runs/38404083070): compileall PASS, **153/153 unittest PASS**, 0 failures/errors. No new constraint on `signed_mean_mm` relative to the equal-direction public RMS (not normatively fixed).

### Tasks 7–12 — identity SHA classes and typed comparison
- **7** Reviewed accepted ADR-0062/0064 and `hashing.py`.
- **8** Independently computed SHA256 domain-separated digests for identical payloads across four identity classes.
- **9** Tested typed comparison against distinct semantic values, cross-domain classes and wrong schema/encoding versions.
- **10** Tested streaming ordered byte chunks against an independently computed SHA256 for empty, partitioned and 64-single-byte payloads; rejected noncanonical containers.
- **11** Confirmed two-stage plan identity construction, equal full ID/hash, and supplied valid-shaped-but-wrong digest rejection.
- File `tests/unit/test_identity_domain_matrix_v1.py`, commit `158a3b9eb07024d99b974886a3ab179f75e7caa1`.
- **12** CI [38404273556](https://github.com/nobunora/Smoothificator/actions/runs/38404273556): Python 3.12 compileall PASS, **157/157 unittest PASS**.

### Tasks 13–18 — Settings v1 isolation
- **13** Reviewed accepted Settings identity schema against Proposed ADR-0066; no change to `PluginSettings.schema_version="1"`.
- **14** Tested integer-versus-float value spelling in declared numeric fields produces identical canonical v1 Settings fingerprint.
- **15** Tested builtin-only version/profile/evidence identifiers reject subclass strings.
- **16** Tested `fingerprint_plugin_settings` rejects unapproved research-only nested DTO types and invalid policy/profile replacements.
- **17** Verified exact seven v1 fields, unknown schema versions rejected and physical injection remains explicitly prohibited.
- File `tests/unit/test_settings_identity_isolation_matrix.py`, commit `6fd15fb0d81a291317b0eabdd87e88ed51b53ffa`.
- **18** CI [38404440737](https://github.com/nobunora/Smoothificator/actions/runs/38404440737): Python 3.12 compileall PASS, **161/161 unittest PASS**.

### Tasks 19–24 — canonical array semantic identity
- **19** Reviewed ADR-0062 big-endian framing, logical C-order ownership and typed array digest tokens.
- **20** Tested rank/shape identity distinction for four logically equal-length i64 arrays.
- **21** Tested i64-versus-f64 semantic dtype identity and typed source-geometry reference sensitivity.
- **22** Independently computed signed big-endian 2D negative-i64 SHA256 golden digest and order sensitivity.
- **23** Tested missing/extra/mistyped/truncated array token data fail with typed ContractError.
- File `tests/unit/test_array_semantic_identity_matrix.py`, commit `e2fcd8db440503ada86d69456948a5413c8249a6`.
- **24** CI [38404587559](https://github.com/nobunora/Smoothificator/actions/runs/38404587559): Python 3.12 compileall PASS, **165/165 unittest PASS**.

### Tasks 25–30 — PlanStore concurrency, epochs, fail closed
- **25** Read PlanStore code and Accepted ADR-0065 without claiming actual Orca Export invocation/PlanSnapshot association.
- **26** Tested old snapshot cannot become valid after explicit session reset despite republishing identical semantic plan in the new epoch.
- **27** Verified rejected bad-hash plan never evicts a previous valid entry or advances generation at capacity one.
- **28** Verified 24 simultaneous publications of preview-only versus eligible plans and proper filtering.
- **29** Verified 48 concurrent equal-plan publications allocate distinct generation numbers yet keep exactly one semantic candidate.
- File `tests/unit/test_planstore_interleavings_v1.py`, commit `5720461e158288fb336fd564ebfe0c04a26de683`.
- **30** CI [38404743572](https://github.com/nobunora/Smoothificator/actions/runs/38404743572): Python 3.12 compileall PASS, **169/169 unittest PASS**.

### Tasks 31–36 — InjectionAttemptStore state atomicity
- **31** Reviewed ADR-0037's monotonic immutable records and `execution_status.py`, without implementing filesystem mutation.
- **32** Three concurrent terminal states for one attempt: exactly one winner, no reopening.
- **33** Every nonterminal progress state may fail with stable reason, no success leakage.
- **34** Old snapshot remains a historical immutable record after status transitions.
- **35** Invalid state jumps or reason-bearing forward transitions do not mutate current attempt.
- File `tests/unit/test_attempt_atomic_races_v1.py`, commit `55542fb6080627bf640de60aaf0d1a68140bd77d`.
- **36** CI [38404882812](https://github.com/nobunora/Smoothificator/actions/runs/38404882812): Python 3.12 compileall PASS, **173/173 unittest PASS**.

### Tasks 37–42 — architecture and sole hashing responsibility
- **37** Reviewed AGENTS, ARCHITECTURE dependency direction and current AST static/dynamic import architecture tests.
- **38** Domain package imports point inward and do not depend on app/engine/Orca adapter.
- **39** Application/domain/engine/Ports top-level import graph has no initialization cycle; synthetic cycle rejection is verified.
- **40** Domain/engine/Ports do not import hashlib or hmac; domain-separated SHA256 and typed comparison remain application hashing responsibility.
- **41** Synthetic literal dynamic module imports of forbidden outer layers are detected; current literal imports in domain/engine/Ports are checked.
- File `tests/architecture/test_owner_graph_matrix.py`, commit `15e992df1f0bb7f8312ca9b90106ff30e598d3fe`.
- **42** CI [38405059029](https://github.com/nobunora/Smoothificator/actions/runs/38405059029): Python 3.12 compileall PASS, **177/177 unittest PASS**, 0 failures/errors. Computed or obfuscated dynamic import names are not comprehensively checked.

## Tasks 43–46 — actual end-of-branch provenance and dispositions

- **43** Re-read the final pre-record branch tree `aaa6e69ba9c1b66e463d4c3bd38c4cc3d4b94bd3`, not truncated, confirmed **81/81** manifest blob hashes unchanged, 65 numbered ADRs, both legacy script blobs unchanged: `91dd3c1b322a5876f144412f6414ebe86ea3fdce` and `5e26ecffaa41e95bb381fc68ad012ffa690d0565`.
- **44** Re-read separate Draft PR #3 and `docs/ARCHITECTURE.md` representative Ports signatures and Accepted ADR-0065. Proposed ADR-0066 is **NOT Accepted**; full Settings v2 fields, physical profile/Orca compatibility, actual PlanSnapshot-to-export attempt association and Port function contracts remain **spec-change-required** or **requires-further-evidence**, not solved by these tests.
- **45** Git compare of implementation HEAD against `3e4ea5f11e7374aa202984df8906b698470d6d3c`: eight changed file paths before this final record update, consisting of **seven new test files and this record**. **Zero production Python source or legacy scripts changed**, no new dependency or unreviewed Settings/G-code capability.
- **46** This detailed 48-step evidence ledger committed before final exact-HEAD CI rerun. Task 47 will verify the exact documentation-closure SHA. Task 48 will re-check final PR states, manifest and stop.

## Results / disposition

- **28** new deterministic test functions, from 149 to **177** tests, each four-test block scoped to a primary source/ADR review. Existing valid canonical v1 fingerprints, hash bytes, immutable DTOs, PlanStore and attempt transition code remain unchanged.
- No newly confirmed production defect in this tranche requiring a source change; prior known code cases remain covered. Assertion of a new summary signed-mean-versus-RMS invariant was intentionally **rejected as unsupported** by the separately defined public bidirectional RMS and diagnostic signed-bias semantics.
- **Outstanding (not covered):** full Settings v2 fields/proposal acceptance, Orca export/attempt binding, Ports signature adjudication, actual NumPy endian/layout integration, G-code parser/emitter/atomic commit, physical fixture calibration and independent blind review.
- **Tooling gaps:** Ruff/mypy/pyright and wheel/package build NOT CONFIGURED; no physical printer test performed. A green 177-test suite is not Phase 0.5 completeness or release authorization.
- **Rollback:** delete these regression test and evidence-only files to restore the prior 149-test state; no printer output or hashes would change because no production code changed.

STOP after the user's exact 48 tasks, not a READY_TO_MERGE decision.
