# Phase 0.5 — Twelve-task follow-up: identity validation and store eligibility

Status: **Scoped primary review and implementation**, not independent blind review.
Date: 2026-10-13.

## Baseline and precedence

- Implementation Draft PR #2 at `34a361753fddded3c6dfa3a9b90fb3473417a616`, separate Settings Proposed ADR-0066 Draft PR #3 at `5743c86177d653d4e61362a0cf8b09735d00b996`. Both open/unmerged at preflight.
- Read `AGENTS.md` first, `docs/DOCUMENT_CONTRACT.md`, approved handoff, Accepted ADR-0062/0064/0065, architecture and prior Phase 0.5 records.
- Audited manifest `ed32f47cc541443a52bc6abed289cc86b31d816b`: 81/81 expected blob SHAs match the branch tree, 65 ADR source files. Legacy script blobs `91dd3c1b322a5876f144412f6414ebe86ea3fdce` and `5e26ecffaa41e95bb381fc68ad012ffa690d0565` unchanged.
- Existing Python 3.12 tests: 75/75 PASS on prior terminal HEAD; no physical fixture/Orca runtime approval.

## Scoped work items

1. Verify branch, draft PRs, pinned manifest: completed.
2. Review canonical typed identity root and array token exact-key validation plus ADR-0065 PlanStore selection.
3. Record findings and bounded test plan (this record).
4. Enforce exact builtin string keys in typed root/array token validators without changing canonical bytes or schema.
5. Add focused negative/positive canonical tests of subclassed keys and unchanged valid vectors.
6. Run Python 3.12 CI, checkpoint 1.
7. Review PlanStore bounded retention/epoch/generation/selected snapshot semantics against ADR-0065.
8. Add precise tests of eviction-before vs after issuance, stable dedup and isolated store sessions; do not invent attempt binding.
9. Run Python 3.12 CI, checkpoint 2.
10. Review complete DTO field registry/architecture source and distinguish implemented from blocked Settings/Port contracts.
11. Add architecture/regression tests for approved stable DTO fields and runtime-excluded status values; no new DTO meaning.
12. Final CI and diff/PR verification; record dispositions and stop.

## Findings before repair

- **K-01 Medium (confirmed):** `application/serialization.py::validate_root` compares `frozenset(root)` to the required root keys. A dictionary keyed by a `str` subclass whose text matches the names passes this check while `canonical_bytes` rejects subclass map keys. Violates coherent strict typed root validation in Accepted ADR-0062/0064; direct validator should reject it.
- **K-02 Medium (confirmed):** `validate_array_token` similarly uses frozenset equality and accepts noncanonical `str` subclass keys that would fail at the later canonical tree boundary. Requires same exact-key validation.
- **K-03 High-risk contract concern, requires-further-evidence:** `PlanStore.snapshot` issues transferable weak-tracked snapshots, and `eligible` can be called repeatedly on an old snapshot even after eviction. ADR-0065 explicitly preserves an *in-flight attempt* snapshot after eviction but excludes evicted plans for **new** selection. In-process `eligible` has no attempt binding and cannot prove a snapshot belongs to an earlier invocation. Do not change this public lifecycle API without an adjudicated attempt/selection contract; add tests of currently established boundaries and flag the unresolved new-selection association.
- **K-04 config gating:** research-only PluginSettings v1 is incomplete; Proposed ADR-0066 is **not Accepted**, cannot implement v2 or authorize G-code injection. Ports signatures and exact Orca installation remain unverified.

## Verification plan

Only stdlib Python 3.12 GitHub Actions:
`python -m compileall -q adaptive_subedge orca_plugin tests`
`python -m unittest discover -s tests -p 'test_*.py' -v`.

No broad dependency upgrade, new adapter, printer/G-code work, physical default or merge. At completion disclose precise CI/SHA and outstanding independent review/Orca/Settings/Ports gates.

## Tasks 4–6 — typed canonical validators, regression CI

- Task 4: exact builtin string-key validation added to `validate_root` and `validate_array_token`, commit `d705aa62cc39160c489a47fe43b2ff6533a258bd`. Valid canonical byte framing, domain tags and v1 Settings hash unchanged.
- Task 5: two negative/positive tests verify that equal-looking `str`-subclass dictionary keys are rejected immediately by the typed validators while valid exact roots and array tokens remain accepted; commit `1f75df0b8643c0d11bc2bb0a0556e0db6cadd2c7`.
- Task 6: Python 3.12 GitHub Actions [38357681532](https://github.com/nobunora/Smoothificator/actions/runs/38357681532) on `1f75df0b8643c0d11bc2bb0a0556e0db6cadd2c7`: `python -m compileall -q adaptive_subedge orca_plugin tests` **PASS**, `python -m unittest discover -s tests -p 'test_*.py' -v` **77/77 PASS**, 0 failures/errors. K-01/K-02 disposition **confirmed -> resolved** for typed boundary checking.

## Task 7 — ADR-0065 lifecycle audit (primary, bounded)

Reviewed actual `PlanStore.publish/snapshot/reset/eligible`, store tests, ADR-0037 and Accepted ADR-0065. Current implementation is a bounded `OrderedDict` publication index, with a weak registry proving snapshot issuance and an epoch guard. Newer analyzer publications and bounded evictions do not mutate an already captured immutable snapshot.

Existing tests did not independently assert all of: eviction **before a fresh snapshot** makes a plan unavailable, MRU deduplication's effect on bounded eviction, epoch-local generation restart, and no strong retention of discarded snapshots. These are **coverage gaps**, not new ADR-authorized production behavior changes.

The separate K-03 concern remains: a store-issued snapshot may be reused by another caller after eviction; only a future postprocess invocation/attempt association can prove it was captured for an already-running export. It must not be 'fixed' by revoking every old snapshot (which would violate ADR-0065), or by inventing a speculative API in Phase 0.5. Disposition: `requires-further-evidence` for the exact runtime attempt binding. Add only tests for established boundaries now.

## Tasks 7–9 — retained-plan selection checks and second CI checkpoint

- Task 7: source/ADR-0065 review separated confirmed retained-snapshot behavior from the unimplemented postprocess-attempt binding. No unsupported mutation of the `PlanSnapshot` ownership semantics was introduced.
- Task 8: added four unit tests in `tests/unit/test_stores.py`: eviction **before** a fresh selection excludes an old plan; already-held immutable snapshot survives eviction; re-publication of equal plan hash refreshes bounded retention without duplicating semantic candidates; epoch reset starts a new process-local generation scope; weak issuance registry does not strongly hold abandoned snapshots. Commit `1e074e4741ddca11ceecb12d22397035d42dbe57`.
- Task 9: Python 3.12 GitHub Actions [38357838220](https://github.com/nobunora/Smoothificator/actions/runs/38357838220): `python -m compileall -q adaptive_subedge orca_plugin tests` **PASS**; `python -m unittest discover -s tests -p 'test_*.py' -v` **81/81 PASS** (0 failures/errors, 0.126 s logged).
- K-03 remains **requires-further-evidence**: in-flight association must be established by future supported Orca lifecycle and postprocess ID. New snapshots do not resurrect evicted plans; no assertion that a reused old snapshot is a newly valid export.
