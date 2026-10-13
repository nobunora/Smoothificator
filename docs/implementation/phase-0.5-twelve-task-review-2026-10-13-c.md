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
