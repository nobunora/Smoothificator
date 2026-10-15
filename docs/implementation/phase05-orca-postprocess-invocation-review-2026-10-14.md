# Orca psGCodePostProcess invocation and snapshot/attempt provenance — pinned source review

Date: 2026-10-14
Disposition: **Primary source evidence, partially validated API surface; runtime fixture NOT VERIFIED.**
Source family: `OrcaSlicer/OrcaSlicer` pinned commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873` from this repository's `docs/PLUGIN_REQUIREMENTS.md` prior audit. This file is not a runtime certification and does not grant a new capability.

## Direct GitHub source inspected

| File / Git blob at pinned commit | Source lines | Supported fact |
| --- | --- | --- |
| `src/slic3r/plugin/pluginTypes/slicingPipeline/SlicingPipelinePluginCapability.cpp`; `ed2a6aeecf1eadc525936f35e05ff4029355a2ab` | 35–40, 53–63, 80–90 | `psGCodePostProcess` is a separate export postprocess seam; `ctx.print`/`ctx.object` absent; `ctx.gcode_path`, `ctx.host`, `ctx.output_name` and `ctx.config_value()` available; export/upload may invoke more than once |
| `src/slic3r/plugin/pluginTypes/slicingPipeline/SlicingPipelinePluginCapability.hpp`; `6bad90817fb620741ade3cbaac6688121e4f3443` | 11–30, 39–40 | Context holds opaque working G-code path, host/output name and config fallback; there is **no documented per-invocation ID field**; `execute(ctx)` is callback |
| `src/slic3r/GUI/PostProcessor.cpp`; `4aa498ad7466027f8cf6bef1a2e46a0f1098be28` | 265–299, 334–349 | `run_post_process_plugins` constructs a fresh `SlicingPipelineContext` from path/host/output name/config and invokes each selected `cap->execute(ctx)` under Python GIL; post-processing runs on a G-code working copy, not the original preview mapping |

Exact source URLs:
- https://github.com/OrcaSlicer/OrcaSlicer/blob/7d44b60ae4042b4de8c3844eb9dd2671c2d2d873/src/slic3r/plugin/pluginTypes/slicingPipeline/SlicingPipelinePluginCapability.cpp#L35-L90
- https://github.com/OrcaSlicer/OrcaSlicer/blob/7d44b60ae4042b4de8c3844eb9dd2671c2d2d873/src/slic3r/plugin/pluginTypes/slicingPipeline/SlicingPipelinePluginCapability.hpp#L11-L40
- https://github.com/OrcaSlicer/OrcaSlicer/blob/7d44b60ae4042b4de8c3844eb9dd2671c2d2d873/src/slic3r/GUI/PostProcessor.cpp#L265-L299

## Important positive evidence

- One *entry* to the plugin's `execute(ctx)` for `Step.psGCodePostProcess` is the natural **invocation boundary** at which an application-owned unique `InjectionAttemptId` can be created; it need not be supplied by Orca.
- That entry can snapshot only plans already published into this plugin process-local PlanStore; a genuine fresh analysis publication may be absent on cache-loaded exports.
- Source confirms `ctx.gcode_path` is a working copy and `ctx.config_value()` accesses exported resolved configuration; neither `host` nor `output_name` is proof of a unique invocation or a safe normalized path lock key.
- The accepted ADR-0065 demand for an *atomic pair* of an issued PlanSnapshot and unique attempt identity is an **application-level concurrency contract**; Orca does not provide atomicity across the app's two stores by itself.

## What the source does NOT prove

- No native Orca callback-supplied invocation UUID, PluginSessionEpoch, AnalysisGenerationId or immutable PlanSnapshot owner exists in the inspected context.
- No installed executable/embedded Python/NumPy fixture was run; source behavior may differ by target release.
- No proof that `postprocess` can concurrently invoke two callbacks on the same work file, or that the platform gives exclusive cross-process ownership during precommit.
- No proof that the current app code implements a PlanStore+AttemptStore atomic issue pair. In fact it does not.
- No permission for G-code file IO, rename, physical injection, or motion/clearance claims follows from this source-level review.

## Narrow proposed implementation algorithm for spec adjudication (not implemented)

1. On **each** `execute(ctx)` entry at the pinned `psGCodePostProcess` step, validate it is an allowed invocation; obtain no invented Orca session token.
2. Inside the application concurrency owner, atomically record an independently generated process-local opaque attempt ID and issue exactly one current-epoch immutable eligible PlanSnapshot, with a reversible failure path and fixed lock order. Attempt record remains owned by InjectionAttemptStore and never by PlanStore.
3. Release the PlanStore lock immediately; perform long parser/matcher/validation only later (not Phase 0.5).
4. Explicitly reject stale snapshots, unknown epoch or invalid invocation before any physical output. Do not mistake a new generation for session invalidation or a duplicated plan hash for two distinct plans.
5. Add process-local concurrency tests for pair creation rollback, reset/eviction, duplicate hashes, separated attempts and immutability. A source-backed invocation boundary is **not** an Orca runtime compatibility fixture.

## Required acceptance before source implementation

- Approve exact application call signature/record DTO and lock-order/error rollback policy (proposed ADR-0067 D3/D4).
- Reconcile `PlanStore.snapshot` preview/API use with an attempt-issued executable selection and the no-refresh-after-eviction rule.
- Review with an actual chosen stock Orca executable and fixture before enabling the adapter.
- Keep both Draft PR #2 and this proposal Draft until accepted source/contract revalidation; do not claim Phase 0.5 completed from the source inspection alone.
