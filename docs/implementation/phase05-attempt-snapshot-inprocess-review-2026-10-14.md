# Phase 0.5 — scoped repository review: atomic in-process attempt + eligible snapshot issuance

Date: 2026-10-14
**Disposition: VALIDATED narrowly for the process-local primitive; NOT VALIDATED for Orca runtime integration or physical printing.**

## Authoritative source and review rules

- AGENTS.md, DOCUMENT_CONTRACT, accepted ADR-0037 (immutable attempt status) and ADR-0065 (process-local PluginSessionEpoch, unique attempt ID and atomically issued eligible snapshot), canonical Phase 0.5 handoff and existing reviewed PlanStore/AttemptStore code.
- Exact source HEAD before this scoped review: `49162d5f286ba14c5defa75e6b6c4bf2ac4ea444`.
- Prior accepted ADR-0065 already **requires** that one postprocess attempt atomically receives a unique `InjectionAttemptId` and retained eligible immutable current-epoch plans, and explicitly forbids treating newest analysis generation as sole eligible.
- Pinned Orca source `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873`: `PostProcessor.cpp` SHA `4aa498ad7466027f8cf6bef1a2e46a0f1098be28` lines 265–299 constructs the callback context and calls `cap->execute(ctx)`; `SlicingPipelinePluginCapability.hpp` SHA `6bad90817fb620741ade3cbaac6688121e4f3443` has no native invocation ID. Application-owned per-call ID is valid; no imaginary Orca session key is required. This **does not** prove target executable or cross-process file ownership.
- Previous 204 Python 3.12 tests PASS, 81/81 audited manifest entries match.

## Bounded code step / ownership

Under `application/plan_store.py` existing PlanStore RLock, add one internal-use method to issue a `PlanSnapshot` containing **only current-epoch injectable retained publications** and generate an `InjectionAttemptRecord(STARTED)` by calling the existing `InjectionAttemptStore.begin(None, source_working_file_identity)`. The caller receives the issued immutable snapshot and unique record as one operation.

PlanStore owns snapshot issuance/epoch and lock; InjectionAttemptStore retains *exclusive* status record ownership. Fixed lock order: PlanStore lock → AttemptStore lock; `execution_status.py` has no path calling PlanStore. The pair operation holds PlanStore lock only for snapshot/record construction, never during G-code parsing. If attempt creation rejects a malformed working-file identity, discard the unexposed issued snapshot, re-raise stable ContractError, preserve all prior status records and PlanStore publication/generation.

No new canonical Plan fields, Settings v2, Orca adapter, matcher, G-code parser/emitter, file operations, or physical enablement. The method does not select a unique match or claim compatibility / executable safety. Selection/matching remains later work and must revalidate both fingerprints and current source file per ADR-0037/0061.

## Exact regression cases before implementation

1. Attempt ID is unique and STARTED; snapshot contains only eligible current epoch, not preview-only.
2. Old retained generation remains in snapshot after a newer publication and/or controlled eviction, but explicit reset invalidates selection.
3. Malformed file identity creates neither a published attempt nor an externally visible issued snapshot.
4. Concurrent calls produce unique IDs, immutable issued snapshots, bounded candidate lists and no partial records.
5. Cross-store/forged snapshot remains ineligible and no attempt status is stored on Plan.
6. Earlier v1 fingerprint/Plan hash golden vectors unchanged.

## Limitations and remaining decisions

The current `PlanStore.snapshot()` remains a general diagnostic/current-epoch capture method and `eligible(snapshot)` remains the bounded in-memory selection predicate. Application tests cannot yet bind this primitive to a *real installed Orca* `execute(ctx)` or prove exclusive working-file ownership and precommit lock safety; those are explicitly later gates. Proposed ADR-0067's richer evidence DTO and complete public orchestration signature remain unresolved. A new internal atomic primitive **does not by itself complete Phase 0.5 or accept ADR-0067**.

Existing module ownership and two-lock ordering were traced; no architecture move or external undocumented identifier is needed for this narrowly established ADR-0065 contract. Source implementation may begin for this **validated narrow scope**. If an unsafe reverse lock order or unapproved schema change becomes necessary, stop and adjudicate before writing.

Verification: GitHub Actions Python 3.12 `python -m compileall -q adaptive_subedge orca_plugin tests` and `python -m unittest discover -s tests -p 'test_*.py' -v`, exact commit and logs, final manifest/diff checks. No configured mypy/Ruff, no printer tests.

## Implementation/CI closure for the VALIDATED in-process primitive

- Application code changed: `adaptive_subedge/application/plan_store.py`; `begin_postprocess_attempt(attempt_store, source_working_file_identity)` issues an immutable **injectable-current-epoch-only** `PlanSnapshot` and `InjectionAttemptRecord(STARTED)` together under the PlanStore RLock. The AttemptStore alone owns the record. Fixed lock order PlanStore -> InjectionAttemptStore.
- An invalid attempt store type rejects with `ContractError(INVALID_STATE_TRANSITION)`. If AttemptStore rejects source identity, the unexposed snapshot is removed from its weak issuance registry and the original error is re-raised; no valid published Plan is evicted and no attempt record is created.
- Source commit `e437c85bed70a828ebdfe4bad3694457b9cc9e58`; six focused `tests/unit/test_attempt_snapshot_issuance.py` tests committed in `7308b6811b7dbd45262567f74e5dc25fcc52893f` cover preview-only exclusion, empty retained set, wrong file identity and store type, immutable old snapshot after eviction but not reset, and eight parallel unique attempts.
- Python 3.12 GitHub Actions [38421826772](https://github.com/nobunora/Smoothificator/actions/runs/38421826772): `python -m compileall -q adaptive_subedge orca_plugin tests` **PASS**, `python -m unittest discover -s tests -p 'test_*.py' -v` **210/210 PASS**, 0 errors/failures.
- **Narrow disposition:** ADR-0065's pure application-process "issue one eligible snapshot + one unique attempt record together" is **implemented and tested**. The actual Orca `execute(ctx)` adapter is still absent and not implied. Neither active full Settings v2, missing public DTOs nor attempt validation-result payload has been approved or filled. Physical injection remains disabled. This progress does **not** mark Phase 0.5 complete.
