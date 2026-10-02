# ADR-0037: Use attempt-scoped runtime state and pre-commit revalidation

Status: Accepted
Date: 2026-10-02

## Context

A single immutable SubEdgePlan may be used by:
- preview;
- file export;
- network upload;
- repeated exports;
- potentially overlapping postprocess calls on separate working copies.

A single mutable status value keyed only by plan hash is insufficient:
one attempt can overwrite another attempt's result, producing misleading UI/debug state.

Postprocess validation is also multi-pass and potentially long-running.

Between validation and atomic replace:
- plugin settings may change;
- the source working file may be modified unexpectedly;
- a new analysis generation may publish newer plans.

This creates time-of-check/time-of-use (TOCTOU) risks.

## Decision

### Immutable plan publication

PlanStore publishes only fully constructed immutable plans.

No partially built plan is ever visible.

PlanStore assigns a process-local `AnalysisGenerationId` for lifecycle/diagnostic purposes.

Generation id is NOT part of the deterministic plan hash.

### Plan selection snapshot

At the beginning of a postprocess attempt:
1. acquire PlanStore lock;
2. snapshot the candidate immutable plans/status-independent metadata needed for selection;
3. release the lock before long parsing/validation.

The selected plan object remains immutable even if a newer analysis generation is later published.

A newer generation alone does not invalidate an export whose final G-code uniquely matches the snapshotted old plan and whose fingerprints remain valid.

### InjectionAttemptRecord

Every postprocess invocation gets a unique process-local `InjectionAttemptId`.

Store an immutable attempt record containing:
- attempt id;
- plan hash;
- working-file identity;
- start/end status;
- reason;
- compatibility descriptor;
- fingerprint validation result;
- source-file identity result;
- final outcome.

Do NOT store one overwrite-prone mutable status per plan as the sole runtime record.

Preview may derive:
- latest attempt;
- active attempts;
- aggregate plan state
from attempt records.

### Plugin-settings TOCTOU recheck

PluginSettingsFingerprint is checked:
1. at validation start; and
2. immediately before atomic replacement.

If plugin settings changed during processing, abort the attempt and preserve original G-code.

ExecutionConfigFingerprint comes from the export call's final config snapshot and remains tied to that working export, but its plan equality is still validated during Pass 1.

### Source working-file identity

During Pass 1 record a `SourceFileIdentity`:
- byte size;
- high-resolution modification time where supported;
- streaming cryptographic digest;
- platform file identity metadata where practical.

During Pass 2:
- recompute the source digest while copying;
- require equality with Pass 1.

Immediately before atomic replace:
- require source path metadata/identity still matches the validated source snapshot.

Any mismatch => abort before replace.

The plugin does not attempt to merge concurrent external modifications.

### Atomic status transition

An attempt record transitions monotonically:
STARTED -> VALIDATED -> EMITTED_TEMP -> SANITY_PASS -> COMMITTED

or to a terminal:
SKIPPED / FAILED / FATAL.

The durable/observable record is updated atomically under the status-store owner.

## Requirements / invariants introduced

- PlanStore plan data is immutable and atomically published.
- Runtime status is attempt-scoped.
- Multiple export/upload attempts cannot overwrite each other's evidence.
- Plugin settings are revalidated at commit time.
- Original working-file identity is protected across streaming passes.
- A newer plan generation does not silently replace the selected plan mid-attempt.

## Alternatives considered

- One status per plan hash: rejected due concurrent/repeated attempt races.
- Hold PlanStore lock for full G-code parse: rejected; blocks UI/slicing unnecessarily.
- Ignore source-file TOCTOU because Orca normally owns it: rejected for strong atomicity/reproducibility contract.
- Require current generation id unchanged: rejected; an old export can still be valid when uniquely matched to its old immutable plan.

## Safety impact

High for concurrency, reproducibility, and avoiding stale/changed-file commit.

## Compatibility impact

None to Orca API; implementation detail in application/injector infrastructure.

## Performance / resource impact

One streaming digest pass is folded into existing Pass 1 and Pass 2.

Pre-commit metadata check is negligible.

## Observability impact

Attempt-scoped records improve debugging of separate export/upload outcomes.

## Test / validation impact

Add:
- simultaneous attempts on separate working copies;
- one success / one skip preserve separate records;
- plugin settings changed between Pass 1 and commit -> abort;
- source file changed between Pass 1 and Pass 2 -> abort;
- source metadata changed before replace -> abort;
- newer analysis generation published during old export -> old matching attempt remains valid;
- no partially constructed plan visible;
- monotonic attempt-state transitions.

## Migration / rollout

Phase 0.5 domain/application contracts MUST use InjectionAttemptRecord rather than a single mutable plan status as the only runtime status model.

## Rollback / disable condition

Unable to establish source identity / atomic attempt ownership => Skipped or platform unsupported.

## Open questions

Cross-process file locking is not required for initial Orca-owned working-file flow; platform atomic-replace semantics remain fixture-tested.

Supersedes: any design that models runtime execution state only as one mutable PlanExecutionStatus per plan.
