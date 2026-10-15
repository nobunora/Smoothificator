# ADR-0067 (PROPOSED): Complete Phase 0.5 DTO contracts and process-local attempt/snapshot association

**Status: Proposed — NOT ACCEPTED, NOT IMPLEMENTATION AUTHORITY**
Date: 2026-10-14
Design branch: `proposed-phase05-dto-attempt-20261014`
Related: Accepted ADR-0037, 0049, 0061, 0062, 0064, 0065; separate **Proposed** ADR-0066 (Settings v2).
Scope: Phase 0.5 contracts ONLY — no Orca adapter, G-code execution or physical printer authorization.

## Context

The initial Phase 0.5 code on Draft PR #2 contains deterministic immutable Plan DTOs, typed canonical identities, a bounded process-local PlanStore and independent InjectionAttemptStore (204 Python 3.12 tests PASS at source commit `e345b9a9850e0203f1b441d6eb3f2692faa921c3`). It does not yet match all domain/attempt fields listed in ARCHITECTURE §3 / IMPLEMENTATION §13 / ADR-0037, and its separately invoked `PlanStore.snapshot()` and `InjectionAttemptStore.begin()` do not establish one atomic selection-attempt association required by Accepted ADR-0065.

The current canonical `SubEdgePlan` identity root has schema `"1"` and a complete closed byte/field contract. Adding meaning-changing Plan fields under that schema without versioning risks breaking reproducibility. Unsupported Orca session IDs, hardware defaults and platform working-file identities must not be invented to fill this gap.

This ADR is a **review packet** seeking precise remaining decisions. It is not a declaration that new DTO fields, method signatures or terminal statuses are already approved.

## Proposed decisions, with unresolved exact schemas

### D1. Represent a SurfaceBand in immutable domain vocabulary

ARCHITECTURE §3 and IMPLEMENTATION §13 require a SurfaceBand containing:
- target material boundary;
- residual error region;
- support and nesting metadata.

Candidate schema **for review only**:
- `surface_band_id: str` (exact nonempty),
- `target_boundary_reference_ids: tuple[str,...]` (immutable, declared frame/meaning pending),
- `residual_error_region_reference_id: str` (exact nonempty),
- `support_relation_reference_ids: tuple[str,...]` (acyclic temporal meaning pending),
- `nesting_parent_band_id: str | None` (optional, no ambiguous CSG semantics).

**Decisions required:** whether SurfaceBand owns references or geometry, whether a closed outer boundary is a StructuralLoopReference or another topology-aware type, what a residual error region actually contains, and what metadata belongs in final/chronological envelopes instead. Do not add fields to the current plan identity before reviewing the precise schema and version.

### D2. Resolve missing structural loop, candidate and anchor metadata

IMPLEMENTATION §13 lists `StructuralLoopReference` canonical closed geometry, length/bounds/orientation, seam-gap, non-collinear anchors and shape hash. The research DTO currently has loop ID, point tuple, seam-gap and string shape hash. The following need field-level decisions:
- `length_mm` / `bounds_print_space_mm` / winding-orientation + material-side version;
- non-collinear matching anchors and how to identify them without encoding mutable Orca objects;
- `SubEdgeSegment` support-validation metadata; candidate `SubEdgePath` travel/ordering metadata beyond existing `execution_order` and support dependency IDs;
- `InsertionAnchor` exact validated boundary-signature and matching tolerance/profile ownership.

**Required separation:** centered PrintObject print-space geometry and immutable planned intent belong in the plan. Final machine XYZ, final emitted E and mutable postprocess result MUST NOT enter its canonical hash.

**Version gate:** if these semantic fields are added to the canonical plan payload, adjudicate a new typed plan root schema version and full cross-version comparison/migration semantics under ADR-0062/0064; do NOT silently extend the current `subedge-plan` schema `"1"`.

### D3. Include attempt-scoped compatibility and fingerprint validation evidence

Accepted ADR-0037 and IMPLEMENTATION §13 require attempt identity, selected plan hash, working-file identity, status/reason **and** compatibility descriptor, fingerprint validation result, source-file identity result and final disposition.

Current `InjectionAttemptRecord` has only 5 fields. Proposed **for review** to keep one application-owned immutable history:
- `attempt_id`: UUID/opaque unique process-local string, never a plan hash;
- `selected_plan_hash`: optional 64 lowercase hex;
- `source_working_file_identity`: platform-authorized opaque identity, **not** fabricated path-key verification;
- `compatibility_descriptor_id`: validated value or explicit unresolved reason;
- `plugin_settings_validation` and `execution_config_validation`: immutable typed gate outcomes, with versions / identity references and failure code;
- `source_file_identity_validation`: immutable recorded check outcome; size/digest/high-resolution metadata only after actual platform evidence;
- `state`, `reason` and terminal outcome;
- future ADR-0061 commit-lock wait/key evidence is a later execution DTO, not a new Phase 0.5 G-code writer.

**Decisions required:** exact record fields/types, when a gate may be Unknown versus Rejected, whether updates create new record versions under monotonic transition, and which evidence can remain empty in research-only/no-injection mode. Unsupported evidence never becomes a boolean PASS.

### D4. Associate an issued snapshot with one unique postprocess attempt atomically

Accepted ADR-0065 already requires each invocation to atomically snapshot eligible current-epoch plans and a unique InjectionAttemptId, releasing PlanStore lock before long work; ADR-0037 requires attempt-scoped independent mutable status.

**Proposed implementation ownership, subject to source and deadlock review:**
- `PlanStore` remains the **only** owner of publication epoch, bounded retention, candidate list and snapshot issuance. `InjectionAttemptStore` remains the **only** owner of attempt records and monotonic updates.
- An application-level operation representing **one entry** to a supported `psGCodePostProcess` invocation coordinates an atomic `(issued_snapshot, attempt_id)` pair. The operation must not accept caller-supplied untrusted epoch/ID or duplicate existing attempt IDs.
- Mutual lock-order/acquisition and rollback of an unsuccessful pair creation must be specified; no partially associated attempt may become executable.
- A new generation after issuing the pair does not invalidate an in-flight snapshot; eviction after issuance does not mutate it; epoch reset invalidates stale session selections.
- No use of raw code-level newest generation as an eligibility criterion.
- The authoritative attempt record includes a reference/provenance token tying it to the exact issued snapshot. Candidate plan list remains immutable; mutable terminal status stays entirely in InjectionAttemptStore.
- Plan selection requires a distinct later unique structural matcher and two fingerprint checks; **an atomically issued attempt ID is not proof of Orca runtime compatibility or printability**.

**Decisions required:** exact public/private operation signature, lock ordering and coordinator lifetime, whether record creation errors roll back snapshot issuance, how preview-only/candidate-free invocations are recorded, and how reset interleaves with an already-held eligible snapshot.

**External evidence condition:** integration must use a source-verified Orca hook and documented invocation lifecycle, not a guessed Orca session key. Pure-process coordination can be unit-tested in isolation, but integration cannot be certified from those tests alone.

### New pinned Orca source evidence for D4

A direct inspection of the previously audited Orca source commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873` is documented in [the pinned postprocess invocation review](../implementation/phase05-orca-postprocess-invocation-review-2026-10-14.md). `PostProcessor.cpp` constructs `SlicingPipelineContext` and calls `cap->execute(ctx)` for each selected plugin capability. The context exposes a working `gcode_path` and resolved config fallback but no native unique invocation ID. An application-generated unique attempt ID at each supported hook entry is therefore source-consistent, without fabricating a native Orca session identifier. **The application-level atomic snapshot/attempt API and its lock/error rollback design remain unapproved and unimplemented**; installed-target runtime fixture evidence is still missing.

### Pure-process implementation progress (does not accept this ADR)

Draft implementation PR #2 now includes the narrow, already-Accepted ADR-0065 primitive `PlanStore.begin_postprocess_attempt(attempt_store, source_working_file_identity)` at commit `e437c85bed70a828ebdfe4bad3694457b9cc9e58`, with six in-memory rollback/concurrency tests and [Python 3.12 CI 210/210 PASS](https://github.com/nobunora/Smoothificator/actions/runs/38421826772). Under the PlanStore lock it issues only eligible current-epoch candidates alongside a newly created attempt record. This does **not** wire an actual Orca export invocation, determine a real filesystem identity/commit lock, or resolve the richer attempt validation evidence DTO schema. Those D3/D4 points remain **Proposed** and need a separate accepted contract before further implementation.

### D5. Clarify architectural file-tree milestone boundary

ARCHITECTURE §2 lists the eventual engine, ports, adapters, preview and G-code modules. The Phase 0.5 handoff expressly **forbids implementing** source mesh, optimizer, Orca live bindings and G-code parser/emitter.

**Proposed resolution:** treat the Section 2 source tree as a **target architecture** and Phase 0.5 acceptance as ownership/import boundaries, complete *approved* DTOs and the application-level immutable/snapshot lifecycle; only create actual modules required by a reviewed concrete contract, never placeholder G-code or optimizer services. Clarify the handoff before marking the milestone complete.

## Alternatives rejected at proposal stage

- Unversioned change to `PlanSemanticContent` or `PluginSettings` root schema `"1"`.
- Generic free-form DTO metadata or Python repr in canonical identity.
- Storing mutable attempt status on `SubEdgePlan` or deriving attempt identity from `plan_hash`.
- Treating `snapshot()` + `begin()` as atomic without a shared ownership/lock contract.
- Using an imagined Orca export-session ID or reconstructing an evicted plan from G-code.
- Adding no-op placeholder Orca/G-code modules solely to make the listed package tree look complete.

## Specification reviewer checklist

An explicit six-decision approval sequence integrating this proposal with Proposed ADR-0066 is maintained at [Phase 0.5 specification approval checklist](../implementation/phase05-spec-approval-checklist-2026-10-14.md). It requires a separate reviewer disposition on Plan identity versioning, Settings ownership, public DTO semantics, attempt evidence states, snapshot-to-invocation provenance and the Phase 0.5 target package tree. **The checklist is NOT an Accepted ADR and does not authorize schema changes or physical injection.**

## Acceptance gates before any implementation of this proposal

1. Source-review D1–D5 with concrete field types, units, meaning and owner; reconcile relevant Accepted ADRs and canonical SPECIFICATION / IMPLEMENTATION / ARCHITECTURE in a separate approved specification revision.
2. If a schema change is approved, define unique root version and deterministic golden vectors for v1 vs new plan/attempt metadata; keep legacy v1 vectors byte-identical.
3. Restamp the audited manifest/handoff without a circular self-reference; perform a fresh repository review with disposition `validated` for the new scope.
4. Add standalone in-memory snapshot/attempt concurrency and failure-atomicity tests and normal architecture/DTO checks. Never count a research-only matched snapshot as actual Orca postprocess proof.
5. Keep physical injection disabled until actual runtime fixtures, a complete execution config, working-file commit-lock proof and independent blind review pass the later safety gates.

**Final status: PROPOSED.** No changed versioned schema, Python implementation or print capability is authorized by this ADR. Reviewer acceptance and source-backed Orca integration are still required.

## 2026-10-15 requester-approved design directions (not normative field schema)

The requester approved D1–D10: SurfaceBand typed immutable geometry references, separate target/residual/support/nesting relationships, loop canonical geometry/matching anchors in PrintObject coordinates, typed insertion signatures and immutable candidate dependency/order data, distinct Plan schema version for semantic additions preserving v1 bytes, attempt validation UNKNOWN/VALIDATED/REJECTED evidence, immutable monotonic attempt snapshots, already implemented process-local atomic snapshot+attempt issuance with immutable provenance, epoch versus generation separation, and Phase 0.5 source-tree limited to reviewed modules without speculative Orca/G-code/optimizer stubs.

Full decision detail and remaining field-level gate are recorded in `docs/implementation/phase05-spec-approval-checklist-2026-10-14.md` on this branch (commit `b7de60621b8b34ca7513319ec5e9e958d235b584`). In particular, exact references/geometry types, validation transitions, coordinate normalization and schema root still require formal source-of-truth definitions before implementation. Existing process-local issuance is not new work. ADR-0067 remains Proposed, not independently reviewed/Accepted; no live plugin, G-code or physical injection is authorized.
