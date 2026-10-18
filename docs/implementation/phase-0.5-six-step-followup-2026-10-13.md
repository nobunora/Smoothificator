# Phase 0.5 — Six-step bounded follow-up, contract audit (2026-10-13)

Status: PRIMARY REVIEW, not independent blind review. Baseline branch head: `daf9c108da35ccac4a1666f240e4a0302b150d93`.

## Step 1: scope, evidence and findings

Read `AGENTS.md` first; checked Draft PR #2 and branch diff, the 2026-10-13 audited handoff, document precedence, ADR-0032/0065, `IMPLEMENTATION.md` DTO section, `PlanSemanticContent` and existing store tests.

**F-08, High (latent physical-support invariant):** `PlanSemanticContent.__post_init__` checks duplicate candidate `path_id` but does not check global uniqueness of execution order or validate `support_dependency_path_ids` across all paths. A candidate can therefore depend on a nonexistent, future-order, or same-Z candidate and still be hashed into an immutable Plan. ADR-0032 requires a strict earlier candidate in execution order, with required vertical support only from lower candidate material. Proposed smallest fix: validate metadata at the domain Plan boundary; never infer geometric support from IDs; rejected candidate raises typed `ContractError`. Add positive and negative regression tests for missing/future/same-Z dependencies and valid lower/earlier dependency.

**F-09, Medium:** `PlanSemanticContent` allows duplicate `structural_reference_ids` and `InsertionAnchor.anchor_id` values and anchors referring to absent structural loops. This undermines unique anchor identity later. Proposed conservative validation: unique nonempty structural ids and anchor ids, anchor references contained in declared structural references. If later Orca fixtures contradict this assumption, return to ADR/spec rather than bypass it.

**F-10, Medium (separate task):** `PlanStore.eligible(snapshot)` accepts any caller-constructed `PlanSnapshot` that contains the current public epoch, rather than only a snapshot issued by its own store. Current draft has no G-code injector; nevertheless the ADR-0065 execution-selection contract calls for actually published plans. Evaluate a process-local snapshot provenance gate and stress tests without revoking immutable snapshots after eviction.

Scope constraints: no optimizer, Orca live objects, G-code paths, physical evidence, or numerical geometry policy added. Existing 20-test CI passing does not prove these metadata invariants.

## Step 2 — Frozen candidate support metadata (completed)

- `adaptive_subedge/domain/plan.py`: verifies unique execution order and structural/anchor identities; every candidate support dependency must resolve to a candidate whose execution order and command Z are both strictly lower. Same-Z required support and missing/future dependencies produce typed `ContractError`. Engine contact/geometry proof remains a later step.
- `tests/unit/test_plan_dependencies.py`: seven test cases, including positive earlier-lower support and failures for missing/future/same-Z/duplicate metadata.
- Code commit: `5f0d35c6247f9b0ab40b9227c2c63fbaf59de3cf`.

## Step 3 — First verification checkpoint (completed)

- GitHub Actions `Phase 0.5 contracts`: https://github.com/nobunora/Smoothificator/actions/runs/38320789224
- Python 3.12 `python -m compileall -q adaptive_subedge orca_plugin tests`: PASS.
- Python 3.12 `python -m unittest discover -s tests -p 'test_*.py' -v`: **27 tests, 0 failures/errors, PASS**.
- Compared to previous 20 tests: +7 targeted metadata cases.

## Step 4 — Pinned upstream Orca runtime source verification (completed as source-only check)

Pinned external source ref: `OrcaSlicer/OrcaSlicer` commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873` (2026-10-08 project baseline).

- `CMakeLists.txt` lines 990–992 set bundled Python version `3.12.13` and ABI `312`: https://github.com/OrcaSlicer/OrcaSlicer/blob/7d44b60ae4042b4de8c3844eb9dd2671c2d2d873/CMakeLists.txt
- `src/slic3r/plugin/PluginLoader.cpp` lines 441–471 use bundled `uv` to install declared packages into the plugin package target, with explicit errors if bundled executables are unavailable: https://github.com/OrcaSlicer/OrcaSlicer/blob/7d44b60ae4042b4de8c3844eb9dd2671c2d2d873/src/slic3r/plugin/PluginLoader.cpp
- The same file lines 653–659 rejects side-loaded `.py` missing required PEP 723 `name` metadata; this does not apply as a claim of an installed plugin's runtime.
- Official Orca plugin docs describe declaring NumPy in PEP 723 dependencies for mesh accessor APIs. NumPy is not demonstrated to be preinstalled; no particular installed NumPy version/ABI was measured.
- **Scope classification:** source configuration is VERIFIED at the pinned commit; actual target Windows Orca executable/interpreter, installed NumPy, plugin loading, API binding, wheel compatibility and printer hardware are **NOT VERIFIED**. No package metadata or dependency was added. Unverified runtime => **no physical injection / no compatibility claim**.

## Step 5 — Provenance of PlanStore snapshots and concurrency stress (completed)

**F-10 confirmed:** the old `eligible()` trusted a caller-constructed snapshot as long as its epoch matched, contrary to the ADR-0065 published-plan selection principle. It could admit a Plan never published by that store.

- `adaptive_subedge/application/plan_store.py`: identity-based weak issuance registry (`WeakSet`) for `PlanSnapshot`, with `eq=False, weakref_slot=True`. Only snapshots actually issued by the same store pass `eligible()`. A retained issued snapshot survives bounded eviction; explicit reset revokes it.
- `tests/unit/test_stores.py`: checks a fabricated/copied snapshot is rejected, genuine snapshot remains usable after eviction, reset revokes old snapshot, and 60 parallel attempts have unique IDs and independent terminal states.
- No serializer/plan identity schema change and no persistence/OS lock introduced.
- Code commit: `5d058d84129eb5f8233c40238dcaa9ce2af167a8`.

## Step 6 — Final CI, bounded review, and completion criteria

- Source GitHub Actions run https://github.com/nobunora/Smoothificator/actions/runs/38320947120: Python 3.12 compileall PASS and **29 unittest tests PASS** in 0.046 s (0 failures/errors).
- Compared to six-step baseline (20 tests), +9 targeted tests: support metadata (+7), snapshot issuance and concurrent attempt identity (+2).
- GitHub compare from `daf9c108da35ccac4a1666f240e4a0302b150d93` to source commit `5d058d84129eb5f8233c40238dcaa9ce2af167a8`: only domain Plan, PlanStore, two tests and this record; no legacy Smoothificator code, Orca adapter, G-code parser/emitter/injector or machine state mutation.
- Primary focused assessment: F-08/F-09/F-10 **confirmed -> resolved for this in-memory Phase 0.5 slice**. This is **not** an independent blind review and cannot authorize injection.
- Remaining: approved Phase 0.5 schema still incomplete for full optimizer/error/Settings fields, runtime integration untested, true NumPy C/F layout and platform ABI untested, no release readiness. Lint/type analyzers NOT CONFIGURED; no wheel build.
- Draft PR #2 remains open/unmerged; no change to `Smoothificator.py` or `Smoothificator_Adaptive.py`.

## Exit / continuation gate

Six bounded tasks completed, stop here. The next review should independently examine whether candidate support/order data models and session snapshots meet the entire accepted ADR set before completing remaining DTO/Settings scope. Any new schema/safety semantics must return to specification adjudication. No printer G-code may be injected.

