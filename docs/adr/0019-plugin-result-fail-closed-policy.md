# ADR-0019: Map expected injection failures to PluginResult.Skipped and preserve valid Orca export

Status: Accepted
Date: 2026-09-30

## Context

Orca's plugin interface exposes:
- Success
- Skipped
- RecoverableError
- FatalError

In audited Orca post-processing code, RecoverableError and FatalError cause the post-processing pipeline to throw and abort/remove the working export.

Most Adaptive Sub-Edge validation failures mean only "do not modify this otherwise valid Orca G-code":
- unsupported profile/config;
- missing/stale plan;
- ambiguous matcher;
- uncertain machine state;
- unsupported calibration/custom code;
- execution-frame mismatch.

Aborting a valid Orca export for these expected conditions is undesirable and conflicts with fail-closed/no-modification semantics.

## Decision

At `psGCodePostProcess`:

### Return Skipped
For every expected unsupported/validation condition where the original working G-code remains untouched.

Examples:
- plan missing/ambiguous/mismatch;
- config fingerprint mismatch;
- unsupported printer/profile/mode;
- parser uncertainty;
- anchor/retraction/frame/quantization validation failure;
- calibration-mode detection;
- already-known non-injectable plan.

### Return Success
Only when:
- injection completed, temp output passed sanity validation, and atomic replacement succeeded; or
- a matching idempotence marker proves the same valid plan was already injected and no change is required.

### RecoverableError
Do not use for routine compatibility or validation failures.

It may be used only if Orca's user-visible retry semantics are explicitly desired and the current compatibility contract verifies the export behavior.

### FatalError
Reserve for a condition where the plugin cannot guarantee integrity of the working file or plugin runtime and aborting the export is safer than continuing.

Top-level capability code catches unexpected exceptions before file commit. If the original file is provably untouched, convert to a stable internal failure record and return Skipped. If integrity cannot be proven, return FatalError.

## Requirements / invariants introduced

- Original file mutation occurs only after all validation and sanity passes.
- Expected failures never destroy a valid Orca export.
- Failure reason codes remain observable through plugin status/logs even when result is Skipped.

## Alternatives considered

- Return RecoverableError for all failures: rejected because Orca aborts export.
- Swallow all exceptions and report Success: rejected; hides plugin failure.

## Safety impact

High. Aligns fail-closed behavior with Orca's actual plugin result semantics.

## Compatibility impact

Tied to audited Orca postprocessor behavior; revalidate on plugin API changes.

## Performance / resource impact

None.

## Observability impact

Every Skipped result carries a stable internal reason/status for preview/reporting.

## Test / validation impact

Integration tests for each result category and working-file preservation.

## Migration / rollout

Capability boundary implements one central exception/result mapper.

## Rollback / disable condition

If Orca changes PluginResult semantics, disable injection until revalidated.

## Open questions

None.

Supersedes: none.
