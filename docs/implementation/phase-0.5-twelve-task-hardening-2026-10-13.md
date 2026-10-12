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

## Task 2/3 — Settings evidence validation and regression check

- Confirmed that `ToolClearanceProfile` allowed mutable/non-string fixture evidence, `CandidateSegmentRegularityPolicy` allowed non-string policy version/evidence, and `PluginSettings` accepted an invalid optional hardware profile object. All are inconsistent with immutable typed Settings/fixture identity semantics.
- Corrected `adaptive_subedge/domain/settings.py` with exact nonempty-string identity validation and exact frozen hardware DTO type checking. No physical defaults, printer modes, or new dependencies introduced.
- Added `test_settings_identity_types_are_strict_and_immutable` with malformed nested values and valid explicit-profile control.
- Commit `6da3fe76bdead3f6e62f75029e8042f5c9b28b41`; GitHub Actions run `38321569623`: Python 3.12 syntax/compileall PASS and **30 tests PASS**, 0 failures/errors.

## Task 4 — Additional domain DTO audit (read-only findings)

- F-11 (Medium): `StructuralPathSegment` does not enforce typed `PrintPoint3` start/end and allows truthy non-string role values, potentially putting a mutable object inside a frozen DTO. Violates immutable cross-boundary vocabulary; repair by exact field-type checking, not geometry redesign.
- F-12 (Medium): `PlanSemanticContent.plugin_version` and `compatibility_descriptor_id` currently accept truthy non-string values such as lists. These enter hash identity and compatibility naming; reject without redefining the identity schema.
- F-13 (Low/Medium): `SubEdgeSegment` accepts subclasses of `PrintPoint2` despite canonical serializer accepting only registered exact DTO types. This mismatch can create a dataclass accepted by domain but rejected in hash serialization. Prefer exact type validation.
- F-14 (not yet fixed): full canonical v1 DTO coverage, `SurfaceBand` and advanced ErrorEstimator/structural metadata remain incomplete by the pre-existing Phase 0.5 partial scope. No invented field schema or policy is authorized in this tranche.

All confirmed findings have source evidence in `domain/geometry.py` / `domain/plan.py` and current serializer exact-type register. No unrelated refactors permitted.

## Task 5/6 — DTO type-fidelity repair and CI

- Resolved F-11/F-12/F-13: StructuralPathSegment now accepts exact PrintPoint3 endpoints and nonempty string role; PlanSemanticContent requires string plugin/compatibility labels; SubEdgeSegment uses exact PrintPoint2 types accepted by the authoritative serializer.
- Source commit `ec6a46c14e7e5b09a04ec587160139c73cf685fc`; new tests commit `06a50e56efed2498a2746a140d3c067402636e95`.
- GitHub Actions run `38321710425`: Python 3.12 compileall PASS, **33/33 unittest PASS**. No modifications to old printer scripts, Orca adapters, or G-code injector.
- Open F-14 remains a future Phase 0.5 contract completeness issue; it has not been silently closed.

## Task 7 — Canonical array/hash boundary audit

- F-15 (Medium/resource risk): `application/serialization.py::canonical_array_token` assembles the *entire* canonical array payload in a growing `bytearray`, then converts it again to `bytes` before hashing. ADR-0062 permits streaming; copying large geometry allocations is avoidable. Hash framing and payload ordering MUST remain byte-for-byte unchanged.
- F-16 (Medium/type boundary): `application/hashing.py` provides typed identity construction, but lacks an explicit validator/comparator for two `IdentityReference` values under an expected identity class and version. ADR-0062 prohibits comparing arbitrary 64-hex values without typed context. Add a single application-owned typed comparison API; do not relax cross-domain checks.
- Independent fixture coverage is incomplete for 2D arrays, canonical type-version rejection, subnormal binary64, and logical C-order normalization after a conceptual F-order traversal. No actual NumPy adapter or installed Orca NumPy compatibility is claimed; no new dependency is authorized here.
- These are implementation hardening changes under ADR-0049/0062/0064, **not** alterations to normative canonical byte framing, domain tags or schema.

## Task 8/9 — Streamed canonical arrays, typed digest comparison, and CI

- Implemented one hash owner `domain_digest_chunks`, streaming the existing binary `ASE_ARRAY_V1` header, dimensions and element values into SHA-256 without materializing a second full array byte copy. Retained exact magic/tag/framing/endianness semantics.
- Added `typed_identities_equal(expected_type, left, right)` to require exact typed versioned IdentityReference objects and reject raw/untyped cross-schema comparisons; the comparison itself is constant-time via `hmac.compare_digest`.
- Source commit `3da322aa039c4a73a4f569796c6748b031581452`, tests commit `c22338826d824f77866f6ba9bf6b1b2898f9ad3e`.
- Independent `hashlib`/`struct` vectors prove multi-dimensional i64 canonical framing, conceptual F-memory-to-C-logical ordering, fixed endianness and subnormal f64 values. Also test incremental chunk SHA parity and wrong identity type/schema rejection. These do **not** prove actual NumPy array integration.
- GitHub Actions run `38321880644`: Python 3.12 compileall PASS, **37 unit tests PASS** (0 errors/failures). No new runtime packages or canonical identity schema changes.

## Task 10 — Attempt-state and concurrent-store audit

- F-17 (Medium, confirmed): `domain/status.py::InjectionAttemptRecord` accepts malformed `selected_plan_hash` strings and non-string/mutable `source_working_file_identity`; it can also be directly constructed with inconsistent terminal reason metadata. The authoritative in-process status store uses this value type, so reject malformed records at the DTO boundary.
- F-18 (Medium, coverage): `InjectionAttemptStore.transition` is protected by a lock but lacks a focused competing-transition test for two simultaneous calls on the same attempt. Test that precisely one transition succeeds and the other fails closed with the stable reason.
- Open risk (requires further evidence): `InjectionAttemptStore` record lifetime/capacity has no explicit bounded retention requirement in the current ADR and schema; do not invent a policy in this tranche. Final postprocess state, file digests and Orca fixture integration are later-phase responsibilities.
- These issues are limited to the existing accepted immutable status/monotonicity contract; adding attempt file-system or G-code behavior is out of scope.
