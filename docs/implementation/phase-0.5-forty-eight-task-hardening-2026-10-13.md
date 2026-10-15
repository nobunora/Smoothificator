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

## Checkpoint 1: tasks 1–6

- **1** preflight Draft PR / starting HEAD `eb722777d74f4884476330385fc0daa59e28cd22`; **2** validated 81/81 manifest, Accepted canonical integer grammar; **3** filed review-only finding I-01 and bounded implementation/test plan.
- **4** corrected fallback from 1000-digit to 100-digit decimal chunks in `application/serialization.py`; commit `5d82b444fce87eca46b69172aee5f6479c718691`. The canonical output grammar and normal-size integers are unchanged.
- **5** added 3 tests `tests/unit/test_canonical_int_limit.py`, first commit `94f584257df221cac1cc635a6009962ce1aaf3bc`: 1501-digit nonzero remainder under Python's minimum configured 640-digit limit, small/640-digit identity and restricted-vs-unrestricted typed identity matching.
- **6** first CI [38387279043](https://github.com/nobunora/Smoothificator/actions/runs/38387279043) **FAILED** due a test-only independent vector with 500 instead of 501 middle zeros. Second run [38387348882](https://github.com/nobunora/Smoothificator/actions/runs/38387348882) **FAILED** due duplicated "1" in negative expected token. Both fixtures corrected in commits `7690e7f644f6ebb503b2b226178f1340952e1590` and `571438ab243667be1d789c5c877bf3308b6cdccc`. Final source commit `571438ab243667be1d789c5c877bf3308b6cdccc`, CI [38387410905](https://github.com/nobunora/Smoothificator/actions/runs/38387410905) Python3.12 compileall PASS and **119/119 unittest PASS**. No implementation failure in either first test run; preserve failed-CI evidence. I-01 confirmed -> resolved in approved boundary.

## Eight verified checkpoints; all initial constraints preserved

### Tasks 7–12: geometry numeric/immutable value matrices
- 7 PrintPoint2 finite binary64, exact frozen coordinate and int-to-float canonical parity
- 8 PrintPoint3 all three axes reject nonfinite and wrong scalar types
- 9 StructuralPathSegment exact endpoints, positive bead dimensions, role and layer metadata
- 10 StructuralLoopReference tuple/length/immutable points/identity and seam-gap rejection
- 11 SubEdgeSegment/SubEdgePath positive flow/speed, Z continuity, duplicate dependency and open-polyline checks
- 12 GitHub Actions [38387596818](https://github.com/nobunora/Smoothificator/actions/runs/38387596818): **124/124 PASS**, Python3.12 compileall and unittest. Test commit `d3357079c974599e8811cee73881a4ad504e1aa8`. **No source changes** in this set.

### Tasks 13–18: v1 research Settings & hardware-profile explicit requirements
- 13 ToolRadialKeepOut tip height/positive radius and nonfinite numeric gates
- 14 ToolClearanceProfile ordered/within-height keep-out curve, fixture ID, axial validity
- 15 CandidateSegmentRegularityPolicy min segment length/time, research-only maxima and v1 fingerprint sensitivity
- 16 SurfaceCorrespondencePolicy normal-dot extremal limits and ray policy version sensitivity
- 17 ErrorEstimatorConfig/MeshSectionPolicy refinement and topology numeric/version values
- 18 GitHub Actions [38387728099](https://github.com/nobunora/Smoothificator/actions/runs/38387728099): **129/129 PASS**, Python3.12 compileall and unittest. Test commit `8c989bd470641e40b9bb9c3fc4654532438d2aaa`. No universal physical thresholds/defaults or Settings v2 additions.

### Tasks 19–24: independently derived canonical array framing
- 19 Golden 3D i64 minimum/maximum and fixed signed big-endian SHA-256
- 20 Binary64 negative zero/subnormal and exact network-endian array digest
- 21 Logical row-major equality after conceptual column-major memory traversal; raw storage order not directly hashed
- 22 Invalid signed dtype/boolean dimensions/nonfinite/shape mismatch reject typed
- 23 Exact token four-field schema, noncanonical shape/dtype/digest and extra keys reject
- 24 GitHub Actions [38387857296](https://github.com/nobunora/Smoothificator/actions/runs/38387857296): **134/134 PASS**, Python3.12 compileall and unittest. Test commit `94100865ab91ff56b5fc3203d11ea724b5e1b706`. These are **stdlib golden vectors**, not a test in an actual NumPy/Orca memory-layout adapter.

### Tasks 25–30: bounded process-local PlanStore
- 25 Retained earlier and later generation both eligible, no newest-only rank
- 26 Current-epoch held snapshot survives eviction but reset invalidates it
- 27 Thirty identical Plan hashes retain one semantic candidate with new diagnostic generation
- 28 Copied/forged/cross-store snapshot fails issuance provenance
- 29 Thirty concurrent publications/snapshots remain bounded, self-consistent, duplicate-free
- 30 GitHub Actions [38387956346](https://github.com/nobunora/Smoothificator/actions/runs/38387956346): **139/139 PASS**, Python3.12 compileall and unittest. Test commit `55c9619f57d4578aaa8614f2461c7446974a6f7d`. These prove only process-local semantics; no actual Orca postprocess invocation binding.

### Tasks 31–36: InjectionAttemptStore state-machine failure paths
- 31 Monotonic STARTED→VALIDATED→EMITTED_TEMP→SANITY_PASS→COMMITTED, immutable records
- 32 SKIPPED/FAILED/FATAL require stable reason and are terminal
- 33 Invalid skips/backward/reasoned-forward transitions preserve previous immutable record
- 34 Invalid attempt digest/file identity does not create store entries
- 35 Eighty parallel attempts have unique IDs and independent terminal records
- 36 GitHub Actions [38388067608](https://github.com/nobunora/Smoothificator/actions/runs/38388067608): **144/144 PASS**, Python3.12 compileall and unittest. Test commit `bc257ccb1839b8b521b9ee64795f87b9c3b563de`. No file-system atomic commit or physical emitter was executed.

### Tasks 37–42: literal runtime dynamic-import boundary gaps
- 37 AST detection of `__import__("...")` and `importlib.import_module("...")` with constant string, showing synthetic forbidden outer-layer imports
- 38 Explicit relative `importlib.import_module` package resolution against the same boundary contract
- 39 Scan current domain and engine package for forbidden literal dynamic imports
- 40 Scan current Ports and application package for forbidden literal dynamic imports
- 41 Scan currently present Orca plugin package without fabricating unimplemented adapter directories
- 42 GitHub Actions [38388216272](https://github.com/nobunora/Smoothificator/actions/runs/38388216272): **149/149 PASS**, Python3.12 compileall and unittest. Test commit `f1c65e69eb787f570cc2c3ae58ae1bbec66576c1`. Computed/obfuscated module imports are not covered; no assertion of exhaustive dynamic-import discovery.

### Tasks 43–46: provenance, design gate, diff and record closure
- 43 Rechecked final source tree at `f1c65e69eb787f570cc2c3ae58ae1bbec66576c1`: **81/81** manifest blob entries exact; tree not truncated; 65 accepted/history ADR files unchanged; legacy scripts retain original blob SHAs.
- 44 Read Proposed ADR-0066 source and its field-review packet on Draft PR #3: status **Proposed**, not Accepted, v1 canonical bytes expressly preserved, complete Settings v2 field schema and Orca/fixture evidence still open.
- 45 Compared against starting commit `eb722777d74f4884476330385fc0daa59e28cd22`: nine file paths, only one production module changed (`application/serialization.py`, integer fallback chunk width), seven new regression/architecture test files and this evidence record. No dependency/lock/injector changes or legacy edits.
- 46 This completed detailed ledger. It is a **primary** review record, not an independent blind review.

### Final checks — tasks 47–48
47. Re-run/confirm GitHub Actions on this exact **record-final** commit, not only an earlier code commit.
48. Reconfirm Draft PR #2 and Proposed ADR PR #3 remain open/unmerged; inspect final diff, 81-blob manifest and report final verified head. **STOP at 48**.

## Result and dispositions

- **I-01 confirmed → resolved:** Python minimum int-to-decimal conversion cap no longer breaks a valid arbitrarily large canonical integer when a 1000-digit subcomponent is formatted. Fallback produces the same ADR-0049 bytes using 100-digit subchunks. Large positive/negative vectors and v1 typed hash parity covered under `sys.set_int_max_str_digits(640)`.
- **Explicit test-fixture setbacks (retained evidence):** first new integer test commit had the independent expected zero count off by one; second had a duplicate numeral in negative expected string. GitHub Actions [38387279043](https://github.com/nobunora/Smoothificator/actions/runs/38387279043) and [38387348882](https://github.com/nobunora/Smoothificator/actions/runs/38387348882) FAILED for those test fixture errors. Fixed in commits `7690e7f644f6ebb503b2b226178f1340952e1590` and `571438ab243667be1d789c5c877bf3308b6cdccc`. Then [38387410905](https://github.com/nobunora/Smoothificator/actions/runs/38387410905) **119/119 PASS**. No failed test was silently counted green or removed.
- **Coverage:** 116 starting tests → **149** by task 42; **33** new test methods: 3 integer-fallback and six five-test boundary matrices (geometry, Settings, arrays, PlanStore, AttemptStore, import boundaries).
- **No scope expansion:** v1 PluginSettingsFingerprint, canonical identity root grammar, approved ADR set, resolved Orca configuration ownership, Plan DTO schema, legacy scripts and executable printer behavior unchanged.
- **Design gates remain blocked:** Proposed ADR-0066 is unaccepted; full versioned v2 Settings/fixture limits, exact Ports signatures, unique postprocess attempt ↔ PlanSnapshot binding, installed Orca Python/NumPy native-array tests, independent blind review, source geometry optimizer/estimator, actual G-code and printer validation remain **NOT VERIFIED**. Physical Injection remains **disabled**.
- **Not configured/executed:** Ruff/mypy/pyright, wheel/package build, Orca embedded Windows runtime and any printer/firmware test. CI green is only evidence for the listed contracts. New architecture tests detect **literal** runtime imports only, not arbitrary dynamic evaluation.
- **Rollback:** revert the single production integer-decimal chunk change to restore the old edge-case behavior (not advised) and remove test/evidence commits. There is no physical G-code impact, as no production injector exists.

This record is not permission to merge. PR #2 remains Draft, PR #3 stays Proposed; actual Orca integration must first go through reviewed/sourced lifecycle and Settings schema contracts.
