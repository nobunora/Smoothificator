# Standalone analysis evidence and bounded Attempt history results

## Scope and behavior

Implemented the reviewed ADR-0067 slice and phase05-evidence-history.md handoff.
Prerequisite schema review and source trace are in evidence-history-review-2026-10-16.md.
No open PR was merged; existing Draft PRs carry the separate specification and
implementation commits.

- New domain/analysis_evidence.py: disjoint available/unavailable time values,
  explicit unknown/converged/failed error evidence and two-direction evidence.
  Missing time is never a numeric zero. Constructors validate shape, not proof.
- Runtime-only AttemptRevision and opt-in max_attempts/max_revisions_per_attempt
  on the existing InjectionAttemptStore. Active attempts cannot be evicted.
  At capacity the oldest-created terminal attempt is evicted; an all-active
  store rejects new work. History numbering remains monotonic after pruning.
- Bounded IDs combine UUID and a successful issuance sequence, so an evicted
  UUID cannot cause an old callback to update a new attempt. Retained collisions
  reject before eviction. Fallible validation/allocation precedes publication.
- Existing zero-argument store behavior and ID format remain unchanged. Its
  retained records remain unbounded; new integrations must choose capacities.

The existing PlanStore atomic issuance code and lock order were preserved.
No duplicate store, speculative runtime ID, canonical evidence registration,
v1 Plan/hash change, external library or physical default was introduced.

## Validation

Windows isolated Python 3.12.10. code-quality-audit procedure follows repository
QUALITY_GATES; lint/type tools remain NOT CONFIGURED, not counted as PASS.

- `python -m compileall -q adaptive_subedge orca_plugin diagnostics tools tests`: PASS.
- `python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `python -m unittest tests.unit.test_analysis_evidence tests.unit.test_attempt_retention -v`: 16 PASS.
- `python -m unittest discover -s tests -p 'test_*.py' -q`: 297 PASS.
- `git diff --check`: PASS.

New tests include malformed/numeric/tag/identity/state combinations, absent time,
distinct directional convergence, canonical rejection, capacity configuration,
revision pruning, terminal eviction order, active capacity, retained collision,
evicted UUID recurrence, stale callback rejection, synthetic allocation failures,
PlanStore failed-issuance rollback and 12 concurrent begins against capacity 3.
Existing v1 goldens and Attempt lifecycle/race tests were unchanged and rerun.

## Independent implementation review

A separate reviewer inspected the source, handoff and directly called PlanStore
boundary without primary findings, and independently executed the 16 focused
tests. Result PASS with no actionable finding in the bounded evidence/history
scope. The reviewer checked proof-vs-shape separation, retention, immutable
snapshots, prepublication allocation, sequence numbering, shared locking and
legacy compatibility. Full suite results above were obtained by the parent.

## Remaining work and practical limits

This is not full InjectionAttemptRecord verification: application-owned proof
validation, compatibility/settings/execution/source-file evidence transitions,
TOCTOU rechecks and their runtime integration remain incomplete. Legacy
AttemptState.VALIDATED is still a state-machine value, not physical authorization.

Full Plan v2 projection, immutable SurfaceBand/loop/anchor references and their
identity/graph validation also remain unfinished. Evidence objects deliberately
cannot be hashed as a current Plan. Actual numerical convergence, machine time,
Orca failure/cancellation tests and physical readiness are not certified.

The installed diagnostic plugin was unchanged. No G-code mutation, printer
connection/send/print, security changes, Release or deletion outside C: occurred.
Rollback is local: remove opt-in integration/new DTO callers before reverting;
no persisted identity migration or external state repair is involved.
