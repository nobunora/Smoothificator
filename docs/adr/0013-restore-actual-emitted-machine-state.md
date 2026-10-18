# ADR-0013: Restore the actual emitted machine state at the layer-boundary insertion point

Status: Accepted
Date: 2026-09-30

## Context

ADR-0007 selected a Bambu structural-layer boundary and safe-ceiling travel, but described the insertion point as after the upper structural layer transition and restoring the "upper structural state Z".

Audited OrcaSlicer `GCode::change_layer()` does not always emit an immediate physical Z move in normal mode. It may:
- emit/reuse retraction;
- update Orca's internal nominal Z;
- defer lift/Z synchronization until a later travel/extrusion.

Therefore the machine position represented by the final G-code immediately after the layer-change marker may still be at a previous physical Z.

A postprocessor must preserve the emitted file's state, not Orca's internal nominal state.

## Decision

The v1 injection anchor remains the validated supported Bambu structural layer-boundary region, but state preservation is defined entirely from the parsed final G-code.

Immediately before the injected block, capture `SavedMachineState` including at minimum:
- actual emitted X/Y/Z;
- G90/G91 mode;
- M82/M83 mode;
- active tool;
- current relative-E/retraction state;
- current feed rate;
- tracked acceleration/other modal state required by the supported fixture.

For injected travel:
1. start from the actual saved physical state;
2. raise vertically to validated machine-coordinate `Zsafe`;
3. perform all non-extruding XY travel at `Zsafe`;
4. descend vertically to candidate Z;
5. print using the retraction contract in ADR-0018;
6. return at `Zsafe` to the saved X/Y;
7. descend to the saved **actual emitted Z**, not an inferred upper-layer Z;
8. restore all state changed by the plugin;
9. resume original G-code byte-for-byte from the insertion point onward.

The plugin MUST NOT emit or emulate Orca's deferred layer synchronization. The unchanged original G-code remains responsible for it.

## Requirements / invariants introduced

- State restoration is defined by the parsed file, never by nominal layer assumptions.
- Original G-code after the injected block sees the same machine/modal state it would have seen without the plugin.
- Calibration-mode layer blocks are unsupported in v1 and cause injection skip.

## Alternatives considered

- Force machine Z to upper Layer.print_z before resume: rejected; may duplicate/reorder Orca's deferred Z transition.
- Inject after the first upper-layer extrusion: rejected; changes the intended ordering and support surface.

## Safety impact

Critical. Prevents unexpected Z discontinuity or double layer transition after injection.

## Compatibility impact

Requires parser support for the exact supported Bambu layer-boundary state and explicit calibration-mode rejection.

## Performance / resource impact

Negligible beyond parser state tracking.

## Observability impact

Log a compact before/after state digest and restoration result, not raw G-code.

## Test / validation impact

Golden fixtures must include:
- boundary where no immediate Z move was emitted;
- boundary with explicit Z motion if encountered;
- exact state equality before insertion versus after restoration;
- calibration block rejection.

## Migration / rollout

Update ADR-0007 interpretation: its safe-ceiling invariant remains Accepted; its "restore upper structural Z" wording is superseded by this ADR.

## Rollback / disable condition

If actual machine state cannot be reconstructed unambiguously, return Skipped and leave G-code unchanged.

## Open questions

None for the pinned fixture family.

Supersedes: ADR-0007 only for insertion-point/restore-Z semantics.
