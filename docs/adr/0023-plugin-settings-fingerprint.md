# ADR-0023: Bind injection to the exact plugin settings used to create the plan

Status: Accepted
Date: 2026-09-30

## Context

ADR-0011 validates Orca/export configuration between `posSimplifyPath` and `psGCodePostProcess`.

Adaptive Sub-Edge also has its own settings that influence the immutable plan, for example:
- surface-error tolerance;
- candidate/optimizer limits;
- minimum effective bead height;
- optional candidate speed cap;
- safety tolerances and compatibility-mode choices.

A stale in-process plan must not be injected after these plugin settings change, even if the Orca full export configuration happens to be unchanged.

Orca source/tests indicate plugin configuration changes normally invalidate slicing, but fail-closed postprocess validation should not rely only on cache invalidation side effects.

## Decision

Define a versioned `PluginSettingsFingerprint` from the complete validated Adaptive Sub-Edge Settings object that can influence:
- plan geometry;
- flow;
- cost/selection;
- injectability/safety;
- execution policy.

At `posSimplifyPath`:
1. validate plugin Settings;
2. canonicalize them;
3. compute `PluginSettingsFingerprint`;
4. store the fingerprint in the immutable SubEdgePlan.

At `psGCodePostProcess`:
1. resolve the plugin's current effective configuration through the capability/config contract;
2. rebuild the same validated Settings object;
3. compute the current fingerprint;
4. require exact equality before candidate-plan matching or mutation.

Any missing/invalid/mismatched plugin setting => `PluginResult.Skipped`.

The PlanStore may proactively invalidate stale candidates when settings change, but the postprocess equality check remains mandatory.

## Requirements / invariants introduced

- SubEdgePlan contains both:
  - `ExecutionConfigFingerprint` for Orca/export semantics;
  - `PluginSettingsFingerprint` for plugin-owned policy.
- Plugin settings canonicalization has one owner in the application/settings boundary.
- Runtime UI changes cannot silently alter an already-created plan.

## Alternatives considered

- Rely only on Orca slice invalidation: rejected as an implicit safety dependency.
- Include plugin settings only indirectly through plan_hash: rejected because postprocess still needs an explicit current-settings equality check.

## Safety impact

High for stale-plan prevention.

## Compatibility impact

None beyond requiring the plugin capability/config API to expose the current effective plugin settings at both hooks.

## Performance / resource impact

Negligible.

## Observability impact

Diagnostics record only the settings fingerprint/hash and validation status, not sensitive/raw user data unless needed.

## Test / validation impact

Add:
- identical settings acceptance;
- tolerance change rejection;
- minimum-bead-height change rejection;
- speed-cap change rejection;
- missing/invalid current setting rejection;
- PlanStore proactive invalidation plus mandatory postprocess check.

## Migration / rollout

Add the fingerprint to the v1 plan schema before implementation.

## Rollback / disable condition

If current plugin settings cannot be resolved at postprocess, injection is disabled.

## Open questions

None.

Supersedes: none.
