# ADR-0041: Treat Orca time/material/progress metadata as non-authoritative after SubEdge injection

Status: Accepted
Date: 2026-10-02

## Context

Adaptive Sub-Edge injects extra extrusion and travel at `psGCodePostProcess`, after Orca has already generated:
- standard preview data;
- print-time estimates;
- filament/material statistics;
- progress/timing G-code such as M73 where applicable.

The current v1 postprocessor does not run Orca's time/material estimator again.

Therefore the final modified G-code can take longer and use more filament than Orca's original preview/statistics report.

This is not a geometry or machine-state contradiction, but it is a user-facing correctness issue.

## Decision

v1 MUST explicitly distinguish:

### Orca original estimates
Pre-postprocess estimates from the slicer.
They are not authoritative for a SubEdge-modified file.

### Plugin delta estimates
The immutable plan/attempt record reports:
- added candidate extrusion length/commanded volume;
- added plugin travel distance;
- estimated added time using validated candidate/travel feeds.

### Final actual print
Printer-reported/observed time and material remain the physical truth for benchmarking.

v1 does NOT rewrite M73/progress metadata or Orca material-stat headers.

Preview/UI/documentation must mark Orca time/material/progress as potentially under-reporting the modified file.

Physical benchmark reports MUST use measured/parsed final modified G-code or actual printer results, not pre-postprocess Orca estimates alone.

## Requirements / invariants introduced

- No claim that standard Orca preview time/material includes SubEdge.
- Plugin delta estimates are separate, not written back as if Orca computed them.
- Timelapse/progress compatibility gates remain governed separately by ADR-0036.

## Alternatives considered

- Rewrite all M73 and statistics: deferred; requires full time simulation and firmware-specific semantics.
- Ignore the discrepancy: rejected as misleading.

## Safety impact

Low direct safety impact; Medium user-facing correctness/benchmark integrity impact.

## Compatibility impact

None; limitation is explicit.

## Performance / resource impact

Requires only existing plan delta estimates.

## Observability impact

Preview shows original Orca estimate (when available) and plugin estimated delta separately.

## Test / validation impact

Add:
- plugin delta material/time deterministic;
- UI labels original estimates as pre-postprocess;
- benchmark tooling does not treat original estimate as final.

## Migration / rollout

Update Preview requirements, documentation, and benchmark records.

## Rollback / disable condition

None.

## Open questions

A future version may rewrite progress metadata using a validated final-G-code estimator.

Supersedes: any implication that Orca's standard time/material/progress statistics remain exact after injection.
