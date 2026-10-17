# Evidence/history schema and repository review

Baselines checked 2026-10-16: PR #5 515c2a9, PR #7 02f7455, PR #8 59e2a05.
No branch was merged. The new handoff is phase05-evidence-history.md.

## Independent schema review

A separate reviewer inspected the exact new normative ADR-0067 section and
handoff against B4/B5/B6 and ADR-0037/0065 without primary findings. Result:
validated for four standalone evidence DTOs and opt-in Attempt history. States,
typed identity versions, unavailable/available separation, no canonical
registration, bounded retention and atomic failure semantics were checked.

Primary follow-up identified stale-ID reuse after eviction under repeated UUID
generation. The contract now appends a store-owned successful issuance sequence
in bounded mode, rejects retained UUID collisions, and never reuses an evicted
full ID. Independent re-review validated this without requiring unbounded
tombstones. Existing legacy ID format remains unchanged.

No numerical/physical proof was inferred. Evidence DTOs cannot certify a real
model or transition runtime validation. Plan v2 projection and proof verifiers
remain excluded and unresolved.

## Read-only repository review

Disposition: validated for this handoff only, before production edits.

Observed path: PlanStore.begin_postprocess_attempt holds PlanStore lock, registers
an immutable snapshot, calls InjectionAttemptStore.begin under AttemptStore lock,
then returns the pair. On begin failure it discards the unexposed snapshot.
AttemptStore alone owns records and monotonic transition. Existing zero-argument
callers and UUID-collision/race tests establish compatibility constraints.

Files inspected: domain/status.py, metrics.py, plan.py, geometry.py and errors.py;
application/execution_status.py and plan_store.py; directly related attempt
state/UUID/atomic-race tests. Existing IdentityReference and directional metrics
are sufficient vocabulary; no new hash domain or geometry algorithm is needed.
No CodebaseMemory server/index was started for this bounded source trace.

Implementation boundary: new domain/analysis_evidence.py, runtime AttemptRevision
in domain/status.py, optional capacities/history inside existing AttemptStore,
and focused tests. Keep all new DTOs outside serializer registry. Prepare all
fallible validation/allocation before record/history replacement, so bounded
eviction cannot partially commit. Preserve PlanStore source and lock ordering.

Verification plan: quality-audit syntax/import and 41 architecture checks first;
focused malformed evidence, retention/UUID/atomic/concurrent tests; unchanged v1
goldens; full suite; clean extracted build; independent implementation review;
exact-SHA Windows CI. Lint/type tooling remains NOT CONFIGURED. New dependency:
none. No source tests had run for the new behavior at the review-only gate.

Both existing Settings handoff and new handoff pin the refreshed manifest.
Only ADR-0067's reviewed additional slice changes among pinned source contracts;
Settings normative requirements remain unchanged. Historical Settings review
remains bounded to its original scope, not blanket approval of this addition.
