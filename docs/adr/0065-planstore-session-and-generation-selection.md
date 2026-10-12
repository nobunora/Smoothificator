# ADR-0065: Separate current process session from analysis generation for PlanStore selection

Status: Accepted
Date: 2026-10-13

## Context

ADR-0037 permits a snapshotted older analysis generation to complete an export when its exact final G-code matches and both fingerprints remain valid. Some lower-precedence text says only "current-session" plans are injectable, without defining whether that means the **latest analysis generation** or all retained plans from the current process-local plugin session.

Treating "current-session" as "latest generation" would incorrectly reject an already-running valid export. Treating it as "any historically hashed plan" could reuse stale or persisted plans across plugin restarts.

## Decision

### Two distinct scopes

- **PluginSessionEpoch** is the process-local, nonpersistent lifetime of the active PlanStore. It is regenerated on store creation/reset, is never included in `SubEdgePlan` identity, and cannot be recovered from a past process.
- **AnalysisGenerationId** is a process-local identifier assigned for each completed applicable analyzer publication within that epoch. It is not a plan hash and is not an eligibility ranking.
- A **current-session candidate** means a fully published, retained, injectable plan belonging to the active PluginSessionEpoch; it does **not** require the maximum or newest AnalysisGenerationId.
- No persisted plans or plans from another epoch are eligible. An absent current-epoch plan, cache-loaded geometry without a fresh plugin publication, or unknown epoch is Skipped.
- A newly published generation does not implicitly invalidate older retained generations. Explicit source/config incompatibility, controlled eviction, session reset, or validated fingerprint/matching rejection may make them ineligible.

### Selection and state ownership

- The application PlanStore is the single owner of session epoch, publication generation, bounded retained-plan index and eligibility snapshot. Plan immutable content is atomically published.
- Each postprocess invocation atomically snapshots eligible current-epoch plans and a unique `InjectionAttemptId`, then releases the PlanStore lock before long G-code work.
- Selection revalidates current PluginSettingsFingerprint and export ExecutionConfigFingerprint; the final seam-invariant structural matcher must leave **exactly one semantically matching plan identity**. Zero or ambiguous distinct identities => Skipped. Identical plan hashes from repeated generations refer to the same semantic identity and MUST NOT spuriously create two distinct matches.
- The chosen immutable snapshot remains valid during a concurrent newer analyzer publication or bounded eviction. Eviction must not mutate a snapshot already held by an attempt.
- Plan retention policy must be bounded, deterministic, explicit and tested; if a plan was evicted before selection, never reconstruct or guess it from the final file. A fresh current-session analysis is required.
- `InjectionAttemptStore` alone owns attempt records and monotonic transitions. PlanStore MUST NOT own mutable authoritative per-plan injection status. UI derives status from attempt records.

### Later execution and fail-closed

- Initial eligibility does not waive the two fingerprint checks, final source-file revalidation, ADR-0061 working-file commit lock, parser/matcher ambiguity, idempotence or physical-mode gates.
- If the supported Orca lifecycle cannot establish the required process-local publication/selection association in an exact fixture, injection remains disabled for that environment. No invented Orca session identifier is assumed.

## Tests and acceptance

Phase 0.5 tests MUST cover:
1. epoch changes on store reset, with old-epoch plans ineligible;
2. generation monotonically allocated for publications but excluded from plan hash;
3. old and newer retained plans both eligible, with unique semantic hash deduplication;
4. eviction before snapshot blocks selection, eviction after snapshot does not mutate ongoing attempt;
5. cache-loaded/no-current-epoch plan -> no candidates/Skipped contract;
6. parallel publish and snapshot atomicity, bounded capacity, stable enumeration;
7. runtime attempt records independent and monotonic, no single per-plan authoritative status;
8. new-generation publication during existing export does not invalidate the chosen immutable snapshot.

## Supersession

Clarifies ADR-0037's generation semantics and the lower-precedence "current-session" wording; it does not relax executable matching or physical safety gates.
