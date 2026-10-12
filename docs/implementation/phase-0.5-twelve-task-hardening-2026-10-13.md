# Phase 0.5 — Twelve-task bounded hardening and verification — 2026-10-13

Status: IN PROGRESS. This is a primary implementation-and-verification pass, **not an independent blind review**, physical printer release, or completed Phase 0.5 acceptance.

## Immutable baseline and boundaries

- PR #2: `phase-0.5-skeleton-20261013` against `adaptive-subedge-design`, baseline commit `2c375e28188faaa81d85062bde86c854e544dba1`.
- Read `AGENTS.md` first. Source hierarchy: `docs/DOCUMENT_CONTRACT.md`, accepted ADRs, SPECIFICATION/ARCHITECTURE/IMPLEMENTATION, then handoff.
- `docs/AUDIT_REVISION_2026-10-13.md` blob SHA `ed32f47cc541443a52bc6abed289cc86b31d816b`, checked against branch tree: **81/81 exact SHA matches**.
- Legacy `Smoothificator.py` blob `91dd3c1b322a5876f144412f6414ebe86ea3fdce`, `Smoothificator_Adaptive.py` blob `5e26ecffaa41e95bb381fc68ad012ffa690d0565`. These MUST NOT change.
- No Orca live adapter, injector, G-code parser or physical printing permitted. No new unvalidated physical dimensions or universal policy defaults. Schema/safety changes not already authorized by ADR return to adjudication.
- Prior six-task pass achieved 29 Python 3.12 unit tests, but did not establish whole Phase 0.5 readiness or independent review.

## Twelve bounded tasks

1. Reconfirm PR/base, exact manifest, scope, and affected file list. **Completed**.
2. Focused Settings/regularity/tool-profile contract audit, including malformed evidence identities and deeply frozen values.
3. Implement authorized Settings validation corrections and regression tests; run focused CI; **stop and report three-task checkpoint**.
4. Focused source/DTO audit for missing typed invariants, path geometry and stable reasons.
5. Implement minimal DTO validation fixes that do not add new optimizer or geometric behavior.
6. Add focused DTO regression tests, run CI, document checkpoint and **stop/report**.
7. Review canonical array/hash encoding and typed comparisons against ADR-0049/0062/0064, including independent evidence.
8. Implement bounded encoding/validation defect fixes and independent negative/golden test vectors without changing canonical byte grammar.
9. Verify new hash/array cases in CI, review outcomes and **stop/report**.
10. Audit concurrent PlanStore and InjectionAttemptStore lifecycle/eviction/provenance behavior; no runtime hooks.
11. Implement missing in-process edge-case tests or safe fixes inside validated contract; no cross-process lock implementation.
12. Run final CI and repository diff, classify findings, update this record, leave Draft PR #2 unmerged, **stop/report**.

## Known limitations that do not become guessed contracts

- The exact Orca Windows embedded Python/NumPy runtime is not accessible here. Previously audited Orca upstream source pins bundled Python 3.12.13 ABI 312 for the referenced commit; that does not certify a user installation.
- No added tooling dependencies or wheel metadata until the exact target runtime is established.
- A green test suite is only evidence for its enumerated contracts, not approval of physical injection.

## Evidence updates

Tasks 2–12 must be reported using exact commits, CI run IDs, test counts, blocked checks and disposition; never claim unexecuted checks passed.
