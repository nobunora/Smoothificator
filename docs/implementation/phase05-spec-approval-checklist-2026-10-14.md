# Phase 0.5 contract convergence — specification approval checklist

**Status: REQUEST FOR SPECIFICATION REVIEW, not a sign-off.**
Date: 2026-10-14. This pack is intended to make the minimum remaining decisions explicit, based on Accepted ADR-0037/0049/0062/0064/0065, SPECIFICATION §§16–18, ARCHITECTURE §§2–5, IMPLEMENTATION §§12–13, the handoff acceptance criteria, and pinned Orca source. No identity or executable behavior should be implemented from this pack before approval.

## Dependency order

`D6 Settings v2 (Proposed ADR-0066 in Draft PR #3)` and `D7 Phase-0.5 DTO/attempt contract (Proposed ADR-0067 in Draft PR #4)` require one coherent specification revision. Only after those decisions are Accepted, the team must update the canonical docs and audited manifest, run fresh REPOSITORY_REVIEW, then complete implementation and normal implementation review.

### Decision 1 — version identities; no silent migration

- Proposed: preserve existing `PluginSettings` v1 fields and domain-separated SHA-256 golden bytes exactly.
- Proposed: a full future `PluginSettingsV2` uses root schema `"2"`, DTO `schema_version="2"`, *unchanged* canonical encoding version `"1"` unless byte syntax genuinely changes.
- Proposed: any new semantic `PlanSemanticContent` fields require independent version bump and new golden fixture; do not mix Plan v1 with a new schema under the same identity root.
- **Required review outcome**: choose version IDs, exact root/DTO consistency contract and treatment of retained v1 Plan snapshots when settings change; *do not migrate* by filling missing values.

### Decision 2 — normalized Settings field list and ownership

- Already Accepted: the Settings fingerprint covers every plugin-owned planning/cost/safety policy (SPECIFICATION §17), including tool clearance, candidate regularity, error estimator, surface correspondence, mesh section, width/height/motion bounds, support-coverage thresholds, directional cost and deterministic execution policy.
- Proposed specific fields are in [Settings v2 schema inventory](https://github.com/nobunora/Smoothificator/blob/proposed-settings-schema-v2-20261013/docs/implementation/settings-v2-schema-adjudication-review-2026-10-13.md).
- **Required review outcome**: for every proposed sub-DTO, approve or reject its names, exact types, units, requiredness and validation. In particular decide support-coverage contact/sampling tolerance, jerk dialect, optimizer cost normalization, candidate execution-policy switches and nesting of surface correspondence in estimator.
- **No universal default** for fixture-dependent print safety values. A type-valid number alone does not authorize physical injection. Orca-resolved semantics remain in the separate ExecutionConfigFingerprint.

### Decision 3 — public Domain DTO field schema

- Accepted existence/meaning at high level: SurfaceBand target material boundary, residual error region, support/nesting; StructuralLoopReference geometry/orientation/anchors; immutable candidate support/travel; immutable anchor matching metadata.
- Proposed [ADR-0067 D1–D2](https://github.com/nobunora/Smoothificator/blob/proposed-phase05-dto-attempt-20261014/docs/adr/0067-phase05-domain-dto-and-attempt-snapshot-contract-proposal.md) is a **starting schema**, not a code contract.
- **Required review outcome**: decide whether a SurfaceBand stores *closed geometric objects* or *typed reference identities*, how a residual error region is represented, material-side version, bounds/winding/matching anchors, and whether any are included in the Plan semantic payload. If included, make the plan root schema change explicit with byte vectors and reverse-compatibility rejection.
- Source geometry and print-space units must be independent of live Orca pointers; machine XYZ and final emitted E never enter Plan identity.

### Decision 4 — AttemptRecord immutable validation evidence

- Already Accepted (ADR-0037): attempt ID, selected plan hash, working file identity, immutable chronological state/terminal reason, compatibility descriptor, resolved fingerprint validation and source-file identity validation result.
- Current record implements only the first set; storing unverified or computed results as “PASS” is forbidden.
- **Required review outcome**: exact evidence DTO types, Unknown/Rejected/Validated states, revision/terminal transitions, whether missing evidence on analysis-only `SKIPPED` is legitimate, and compatibility ID/version ownership.
- A first-party UUID can identify an attempt, but source path/file key must follow the accepted working-file commit lock and target platform contract.

### Decision 5 — atomic in-process pairing vs Orca callback integration

- **Already implemented and tested:** Accepted ADR-0065 in-process `PlanStore.begin_postprocess_attempt` issues current-epoch eligible immutable PlanSnapshot and unique STARTED AttemptRecord under PlanStore -> AttemptStore lock order. Collision/rollback and reset/interleaving tests: **216/216 Python 3.12 PASS** on source `4382e122f2584c83a727aa9411bb2b804f4bfba5`.
- Pinned OrcaSlicer source commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873` establishes a `psGCodePostProcess` `cap->execute(ctx)` boundary but no native invocation UUID, so a process-local ID must be created by the application on entry.
- **Required review outcome:** how to bind one record to its issued snapshot via an immutable provenance field, whether pairing method returns a typed envelope versus tuple, and when an invocation becomes SKIPPED if no fresh Plan exists. Also define cancellation/reset, and evidence needed for later actual Orca integration.
- Actual Orca plugin registration, export G-code interpretation, filesystem source-digest checks, same-working-file lock and printer behavior are NOT part of Phase 0.5's approved code scope.

### Decision 6 — Phase 0.5 source-tree acceptance and reviews

- Resolve ARCHITECTURE §2 *target* tree versus handoff's express prohibition on implementing engine/Orca/G-code behavior in Phase 0.5. Proposal: only the domain/application/ports boundaries actually needed by this phase are executable modules, and missing later-phase modules are NOT added as speculative empty stubs.
- **Required review outcome:** accept this limited package-layout interpretation and specify the required Phase 0.5 build/import/architecture checks.
- The repeated primary code audit and 216 contract tests are not independent specification sign-off or release clearance. No reviewer has yet approved [implementation PR #2](https://github.com/nobunora/Smoothificator/pull/2), [Settings ADR PR #3](https://github.com/nobunora/Smoothificator/pull/3) or [DTO ADR PR #4](https://github.com/nobunora/Smoothificator/pull/4).

## Evidence needed for ready-for-implementation disposition

A specification reviewer records one of: **Accepted with exactly defined schemas and migration**, **changes requested (each issue enumerated)**, or **blocked for specific external fixture evidence**.

Only after approved ADRs and normative doc revisions are coherent:
1. Update SPECIFICATION, ARCHITECTURE and IMPLEMENTATION exact field/type/ownership descriptions.
2. Restamp the canonical audit manifest/handoff, preserving v1 golden hashes without self-referential revision hashes.
3. Perform a fresh independent-of-implementation **repository review** validating the changed scope, resulting in `validated` (or return to specification adjudication).
4. Implement reviewed DTOs/settings/status evidence with typed fail-closed negatives and canonical version-specific hash fixtures.
5. Run exact-SHA GitHub Actions plus normal implementation review, verify no unresolved Phase 0.5 Critical/High defects, and leave Physical Injection disabled.

**No sign-off was inferred by the act of writing this document.** Draft proposals do not become Accepted because a user requested completion. This checklist exists to turn the blockers into decisions, not evade the approval gate.


## 2026-10-15 execution of milestone-closure plan (primary triage, NOT approval)

Baseline (verified GitHub metadata): implementation PR #2 head `5dc15d122c2180a5e3e3c99e9d09d2909330d4de`, Settings design PR #3 head `d3b97de941b6c95e5a4f5985675180eb3daefc58`, DTO/attempt design PR #4 head `167ac3994a8d63142fcbede4f6198e2473fbd2ae`; all open/Draft/unmerged. PR #3/#4 have **zero submitted PR reviews** at this audit. This paragraph is source-state evidence, not approval. Source branch PR #2 now has **248** reported contract tests (previous 216 count above is historical); GitHub Actions run 38520932726 succeeded on the exact PR #2 head. No test or CI was rerun by this checklist edit.

### Fixed acceptance classification — no scope relaxation

| Acceptance owner and closure evidence | Phase 0.5 disposition | Required next event |
| --- | --- | --- |
| Immutable DTOs, units, cross-boundary fields (handoff/ARCHITECTURE/IMPLEMENTATION) | **PARTIAL / IN-SCOPE**: accepted-field standalone bead/support DTOs done; SurfaceBand, loop/anchor/path semantics open | Reviewer selects precise typed reference/geometry ownership and plan version in ADR-0067; then implement and test |
| PluginSettingsFingerprint covering **all plugin-owned** settings (SPECIFICATION §17) | **BLOCKED / IN-SCOPE**: existing seven-field v1 is deliberately closed, partial research fragments cannot satisfy it | Reviewer approves exhaustive v2 schema and normalization, including support-query tolerance/version and optimization/motion fields in ADR-0066 |
| Canonical serialization/Plan hash identity (ADR-0049/0062/0064) | **PASS for existing v1 only; NOT for v2** | Preserve independent v1 byte vectors; approve distinct v2 Settings root and new Plan schema only if semantic Plan fields change |
| PlanStore atomic publication/session/attempt issuance (ADR-0065) | **IMPLEMENTED in pure-process scope**: paired issuance, duplicate ID rejection, rollback/concurrency tests | Keep regression gate; do not reimplement or demand live Orca as Phase 0.5 evidence |
| Attempt state and validation evidence (ADR-0037) | **PARTIAL / IN-SCOPE**: unique independent attempts/monotonic state done, typed compatibility/settings/execution/source validation evidence missing | ADR-0067 review chooses immutable evidence states/fields, then implementation and negative tests |
| Architecture/import rules, no premature G-code or physical behavior | **IMPLEMENTED to documented test coverage** | Exact-head import/architecture checks at final verification |
| Orca callback wiring, working-file precommit lock, G-code/mesh/optimizer, printer calibration | **OUT OF PHASE 0.5 IMPLEMENTATION SCOPE** under handoff Non-goals/ADR-0061; interfaces only where explicitly approved | Do not use as completion blockers or create placeholder runtime implementations; later phase needs fixtures |
| Review convergence, zero unresolved Critical/High in approved Phase 0.5 scope | **OPEN / IN-SCOPE** | Separate specification approval, revised canonical manifest/handoff, new repository review, exact-SHA CI and Implementation Review |

### Decisions to close, with explicit options and non-decisions

- **S1 (ADR-0066, blocker):** select complete v2 root/DTO field schema and `schema_version="2"` binding versus an alternate explicit version; preserve canonical encoder byte grammar v1. Reuse supported source-defined fields; do **not** silently insert fragments in v1.
- **S2 (ADR-0066, blocker):** resolve exact support-query tolerance name, dimension, policy version and coupling to ADR-0058 effective-height convergence; motion jerk convention; directional objective normalization; optimizer cost dimensions; execution policy switches. Exact semantics remain unspecified by Accepted ADRs; no safety defaults can be inferred.
- **S3 (ADR-0066, blocker):** require research/physical distinction in typed policy/provenance; leave actual fixture numeric calibration in later physical validation, not a blocker to immutable DTO definitions.
- **D1 (ADR-0067, blocker):** choose SurfaceBand geometry-owning vs typed-reference design with target boundary frame, residual-error representation, support provenance and acyclic nesting rules.
- **D2 (ADR-0067, blocker):** decide loop orientation/material-side/shape identity, insertion matching signature/tolerance and SubEdgePath/Segment support/order metadata, including new Plan root version if identity projection changes.
- **D3 (ADR-0067, blocker):** define Attempt validation evidence as explicit UNKNOWN / VALIDATED / REJECTED (or reviewer-approved equivalent), with reason/provenance and immutable transitions; missing fixture proof must never become VALIDATED.
- **D4 (ADR-0067, largely resolved in process):** retain existing atomic PlanStore->AttemptStore pairing; review only immutable snapshot provenance and how a later adapter uses an actual callback, without pretending it is implemented.
- **D5 (ADR-0067, blocker to interpretation):** confirm that ARCHITECTURE §2 is a target tree, not a Phase 0.5 requirement to add forbidden Orca/G-code/optimizer stubs.

### Approval and execution ownership

Specification owner/reviewer: record an explicit disposition for S1–S3 and D1–D5 (accepted exact contract / changes requested / evidence missing), with accepted ADR text and revised canonical docs. Implementation owner: **only after** `validated` repository review, implement the smallest approved DTO/Settings/Attempt schema changes with independent v1/v2 golden vectors and reject-path tests. Verification owner: run compileall and entire unittest suite at exact resulting SHA, compare diff/manifest, perform normal implementation review and document any unresolved Critical/High. This is a dependency order; neither extra test count nor this primary triage constitutes approval.

**Stop rule:** no speculative v2 serializer root, Plan schema alteration, physical injection, Orca callback, G-code mutation, or PR merge based on this document alone. Maintain SPEC-CHANGE-REQUIRED until formal decisions are recorded.