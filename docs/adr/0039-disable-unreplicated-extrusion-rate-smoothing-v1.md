# ADR-0039: Disable Orca extrusion-rate smoothing for printable v1

Status: Accepted
Date: 2026-10-02

## Context

OrcaSlicer has a Pressure Equalizer / extrusion-rate smoothing stage controlled by:

- `max_volumetric_extrusion_rate_slope`;
- `max_volumetric_extrusion_rate_slope_segment_length`;
- `extrusion_rate_smoothing_external_perimeter_only`.

In current Orca source, a positive `max_volumetric_extrusion_rate_slope` enables G-code postprocessing that can subdivide/retime extrusion moves to limit volumetric-flow-rate change.

Adaptive Sub-Edge candidate G-code is inserted later at `psGCodePostProcess` and therefore bypasses Orca's Pressure Equalizer.

If the feature is enabled for the surrounding print, original external walls and injected SubEdge paths would obey different dynamic extrusion-rate behavior.

The current default is 0 (disabled), but supported profiles/user settings may enable it.

## Decision

Printable v1 requires:

`max_volumetric_extrusion_rate_slope == 0`

The setting participates in ExecutionConfigFingerprint.

When nonzero:
- analysis/preview may proceed;
- G-code injection is disabled with a stable reason.

The segment-length and external-only options are fingerprinted/diagnostic as needed, but their values are irrelevant to candidate execution while the main smoothing slope is zero.

## Requirements / invariants introduced

- Injected paths never silently bypass an enabled Orca extrusion-rate smoothing policy.
- v1 does not reproduce Pressure Equalizer behavior.
- Physical benchmark comparisons use the same disabled smoothing state across ZAA-only and ZAA+SubEdge fixtures.

## Alternatives considered

- Reimplement Pressure Equalizer for inserted paths: rejected for v1 scope.
- Use final matched wall feed only: insufficient; Pressure Equalizer controls transitions/history, not just one steady feed.
- Ignore the setting because default is zero: rejected; compatibility must be fail-closed.

## Safety impact

Medium for hardware safety, High for extrusion/transient parity and surface-quality interpretation.

## Compatibility impact

Narrows printable profiles only when this non-default feature is enabled.

## Performance / resource impact

None.

## Observability impact

Preview reports extrusion-rate-smoothing gate status.

## Test / validation impact

Add:
- slope = 0 accepted;
- positive slope rejected;
- fingerprint mismatch if setting changes after planning.

## Migration / rollout

Update ExecutionConfigFingerprint, Plugin Requirements, Test Strategy, and physical fixtures.

## Rollback / disable condition

Unknown smoothing semantics for a supported Orca version => no injection.

## Open questions

Support may be added later with an execution-stage flow-transition model.

Supersedes: none.
