# ADR-0061: Serialize commits per working file and close the final check-replace race

Status: Accepted
Date: 2026-10-08

## Context

ADR-0037 protects long postprocess attempts with immutable plan snapshots, source digests, plugin-settings rechecks, and a pre-commit source identity check.

One in-process race remains if two postprocess attempts target the same working path concurrently:

1. attempt A validates source S;
2. attempt B validates source S;
3. A performs its final source-identity check -> S unchanged;
4. B performs its final source-identity check -> S unchanged;
5. A atomically replaces S;
6. B atomically replaces the same path using a temp derived from old S.

Both attempts can pass a check that occurs before either replace.

Orca normally uses separate working copies for distinct export/upload flows, but the plugin contract must not depend on that behavior without a same-path concurrency guard.

## Decision

Introduce one process-local WorkingFileCommitLockRegistry owned by the G-code/application execution infrastructure.

### Lock key

Derive a canonical working-file key from:
- normalized/resolved absolute working path under the supported platform contract;
- platform file identity metadata where available.

Symlink/reparse-point/unsupported special-file semantics are rejected unless a platform fixture explicitly supports them.

### Long validation remains parallel

Pass 1 parsing, plan matching, temp generation, and sanity validation may run concurrently for different attempts.

Do NOT hold the per-file commit lock for the entire parse.

### Commit critical section

Immediately before final replacement:

1. acquire the per-working-file commit lock;
2. re-read current PluginSettingsFingerprint;
3. revalidate source path/file identity metadata;
4. recompute/verify the source digest or the strongest required final identity check for the platform contract;
5. re-check idempotence markers/current file state needed for commit;
6. if unchanged, perform the supported atomic replace;
7. publish the attempt COMMITTED outcome/evidence;
8. release the lock.

If current source identity differs from the attempt snapshot:
- the prepared temp output MUST NOT be committed;
- delete/retire the stale temp;
- optionally recognize a now-present identical valid SubEdge plan marker as an already-injected Success only after validating the current file;
- otherwise terminate the attempt as Skipped/stale-source.

### Same-path attempt behavior

Only one attempt may execute the final revalidation + replace critical section for a given working-file key at a time.

Attempts targeting different working files remain independent.

### Cross-process ownership

Initial v1 assumes the Orca working copy is not concurrently modified by another process during the plugin commit critical section.

Each supported platform/fixture must document that working-file ownership assumption.

If the environment cannot provide adequate exclusive ownership, a later compatibility contract must add an OS/file-lock mechanism or injection is disabled.

The plugin MUST NOT claim to solve arbitrary hostile cross-process modification with an in-process mutex alone.

## Requirements / invariants introduced

- Final source identity check and atomic replace are serialized per working file.
- Two same-path attempts cannot both commit from the same old source snapshot.
- Different-file export/upload attempts remain concurrent.
- Attempt records remain independent.
- A stale temp file never overwrites a newer committed source.
- Platform ownership assumptions are explicit compatibility evidence.

## Alternatives considered

- Hold a global plugin lock for every postprocess attempt: rejected; unnecessarily serializes independent files.
- Hold the per-file lock from Pass 1 onward: safe but wastes parallelism and blocks long reads.
- Trust Orca never to reuse a path concurrently: rejected as an undocumented safety dependency.
- Rely only on pre-replace stat/mtime: rejected due check-replace race.

## Safety impact

High for concurrent/repeated export correctness.

## Compatibility impact

Requires deterministic path/file identity support in the platform compatibility layer.

## Performance / resource impact

Very small critical section. Maintain bounded weak/cleanup-capable lock-registry entries to avoid unbounded path-lock growth.

## Observability impact

Attempt record includes:
- working-file lock key digest/opaque id;
- commit-lock wait duration;
- final identity result;
- stale-source/already-injected disposition.

Do not expose sensitive full local paths unnecessarily in user-visible logs.

## Test / validation impact

Add:
- two simultaneous attempts same source/path -> at most one replacement from original snapshot;
- second attempt observes changed source and skips or validates already-injected state;
- simultaneous attempts on different files proceed independently;
- stale temp never overwrites newer output;
- lock registry cleanup/bounds;
- unsupported symlink/special-file path rejected;
- external source modification before lock acquisition detected.

## Migration / rollout

ADR-0037 remains authoritative for attempt-scoped state and source identity. This ADR owns the final same-path commit serialization.

## Rollback / disable condition

Unable to derive/support a safe working-file commit key or platform ownership contract => injection disabled.

## Open questions

Cross-process advisory locking may be added per platform if later workflows require it.