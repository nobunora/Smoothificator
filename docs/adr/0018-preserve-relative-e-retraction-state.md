# ADR-0018: Preserve parsed relative-E retraction state across injected candidate paths

Status: Accepted
Date: 2026-09-30

## Context

Printable v1 uses relative E and disables firmware retraction.

Bambu/Orca layer changes commonly retract before the supported insertion boundary. Retraction may be affected by:
- filament-specific retraction length/speed;
- wipe and split-retraction behavior;
- current already-retracted amount.

Blindly emitting a configured full retract before every candidate can double-retract filament or fail to restore the state expected by unchanged Orca G-code.

## Decision

The parser owns an explicit `RetractionState` for relative-E v1.

At the insertion anchor it MUST determine the actual saved retracted amount from emitted G-code.

Printable v1 requires:
- relative E confirmed;
- firmware retraction disabled;
- saved anchor state is positively retracted and unambiguous;
- resolved restart-extra for ordinary retraction is zero;
- retraction/deretraction speeds are known;
- no unsupported E-reset/custom-code behavior in the candidate block.

For each candidate:
1. begin in the saved retracted state;
2. perform safe-ceiling travel while still retracted;
3. at candidate start, unretract exactly the saved retracted amount at resolved deretraction speed;
4. emit candidate extrusion;
5. retract exactly the same amount at resolved retraction speed;
6. return to safe-ceiling travel still retracted.

After all candidates, leave E/retraction state exactly equal to the saved anchor state. The original Orca G-code performs its own later unretract normally.

The plugin does not reproduce Orca's wipe path for its temporary retract cycle.

## Requirements / invariants introduced

Execution config fingerprint includes resolved values relevant to the supported retraction path, including:
- retract_when_changing_layer / filament override;
- retraction length;
- retraction speed;
- deretraction speed;
- retract restart extra;
- firmware retraction;
- wipe/retract-before-wipe/retract-after-wipe settings that can alter anchor-state formation.

The exact key mapping is centralized and versioned.

## Alternatives considered

- Always retract configured length: rejected due double-retraction risk.
- Do not retract candidate travel: rejected for stringing/ooze and unsafe travel assumptions.
- Reimplement Orca wipe logic: unnecessary for initial additive block and substantially increases scope.

## Safety impact

Critical for extrusion state continuity and nozzle pressure.

## Compatibility impact

Some otherwise valid profiles become analysis-only if anchor retraction cannot be proven.

## Performance / resource impact

Negligible.

## Observability impact

Record saved retracted amount and restoration equality, not raw E history.

## Test / validation impact

Golden cases:
- normal Bambu layer-change retract;
- filament-specific retraction override;
- wipe-enabled source state;
- ambiguous/no-retract rejection;
- exact before/after retraction equality;
- restart-extra nonzero rejection.

## Migration / rollout

Replace generic "establish safe retraction state" wording with this explicit state-machine contract.

## Rollback / disable condition

Any ambiguous retraction state returns Skipped and preserves original G-code.

## Open questions

Support for non-retracted anchors may be added later under a separate ADR.

Supersedes: generic v1 retraction assumptions in ADR-0007.
