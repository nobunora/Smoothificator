# ADR-0057: Treat Orca time/cooling/progress metadata as pre-injection estimates in v1

Status: Accepted
Date: 2026-10-08
Supersedes: ADR-0041

## Context

Adaptive Sub-Edge injects G-code at psGCodePostProcess, after Orca has already generated and processed the original print.

Orca has already applied features such as:
- layer cooling / slowdown decisions;
- fan scheduling;
- time estimation;
- progress/time placeholders or metadata;
- filament-usage summaries.

Injected SubEdge paths add motion, extrusion, and elapsed time after those calculations.

Therefore original Orca estimates and cooling decisions cannot be assumed to describe the postprocessed print exactly.

## Decision

Printable v1 does NOT attempt to rerun Orca's full CoolingBuffer/time-estimation pipeline or rewrite every progress/material metadata field.

Instead:

1. The plugin computes and reports its own deterministic added-path estimates:
   - added geometric/commanded material;
   - added path/travel length;
   - estimated added execution time under the plugin's own motion assumptions.

2. Orca/Bambu original total-time, progress, and filament-usage metadata are treated as **pre-injection estimates** and may be stale after injection.

3. Those original metadata values MUST NOT be used as safety-critical inputs for plugin validation.

4. Physical validation records actual print time and observed thermal/surface behavior.

5. The initial physical fixture must document cooling/fan/min-layer-time settings, because the added dwell/extrusion time can change real thermal conditions even when original fan commands remain unchanged.

6. The plugin does not silently modify fan/temperature/cooling commands in v1.

## Requirements / invariants introduced

- Preview/status labels plugin-added time/material separately from Orca original estimates.
- No claim that Orca's displayed remaining/total time remains exact after injection.
- Cooling/thermal differences are an empirical physical-validation item.
- If a future target machine uses progress/time metadata as a safety-critical execution control, that machine/profile is unsupported until a dedicated compatibility ADR exists.

## Test impact

Add:
- added-time/material estimate determinism;
- original metadata bytes preserved under ADR-0031;
- fixture records show stale-metadata warning/diagnostic;
- physical benchmark compares predicted added time with measured added time.

## Safety impact

Medium for direct motion safety; High for avoiding misleading quality/progress claims.

## Open questions

A later native-Orca integration or dedicated metadata-rewrite phase may recompute selected estimates.


## Renumbering note

Renumbered from accidental duplicate ADR-0037 during the 2026-10-08 audit. Decision content is otherwise retained.
