# Phase 0.5 — Six-step bounded follow-up, contract audit (2026-10-13)

Status: PRIMARY REVIEW, not independent blind review. Baseline branch head: `daf9c108da35ccac4a1666f240e4a0302b150d93`.

## Step 1: scope, evidence and findings

Read `AGENTS.md` first; checked Draft PR #2 and branch diff, the 2026-10-13 audited handoff, document precedence, ADR-0032/0065, `IMPLEMENTATION.md` DTO section, `PlanSemanticContent` and existing store tests.

**F-08, High (latent physical-support invariant):** `PlanSemanticContent.__post_init__` checks duplicate candidate `path_id` but does not check global uniqueness of execution order or validate `support_dependency_path_ids` across all paths. A candidate can therefore depend on a nonexistent, future-order, or same-Z candidate and still be hashed into an immutable Plan. ADR-0032 requires a strict earlier candidate in execution order, with required vertical support only from lower candidate material. Proposed smallest fix: validate metadata at the domain Plan boundary; never infer geometric support from IDs; rejected candidate raises typed `ContractError`. Add positive and negative regression tests for missing/future/same-Z dependencies and valid lower/earlier dependency.

**F-09, Medium:** `PlanSemanticContent` allows duplicate `structural_reference_ids` and `InsertionAnchor.anchor_id` values and anchors referring to absent structural loops. This undermines unique anchor identity later. Proposed conservative validation: unique nonempty structural ids and anchor ids, anchor references contained in declared structural references. If later Orca fixtures contradict this assumption, return to ADR/spec rather than bypass it.

**F-10, Medium (separate task):** `PlanStore.eligible(snapshot)` accepts any caller-constructed `PlanSnapshot` that contains the current public epoch, rather than only a snapshot issued by its own store. Current draft has no G-code injector; nevertheless the ADR-0065 execution-selection contract calls for actually published plans. Evaluate a process-local snapshot provenance gate and stress tests without revoking immutable snapshots after eviction.

Scope constraints: no optimizer, Orca live objects, G-code paths, physical evidence, or numerical geometry policy added. Existing 20-test CI passing does not prove these metadata invariants.

## Step 2 / 3 / 4 / 5 / 6 evidence

To be recorded after implementation and test results. Draft PR must remain unmerged. An unresolved external Orca runtime assumption cannot be silently promoted into compatibility authorization.
