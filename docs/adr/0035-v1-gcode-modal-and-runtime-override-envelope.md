# ADR-0035: Define the v1 G-code modal and runtime override envelope

Status: Accepted
Date: 2026-10-02

## Context

Adaptive Sub-Edge emits machine commands into an existing modal G-code program.

The current contract already tracks G90/G91, M82/M83, feed, retraction, and actual XYZ, but several modal states can silently change the meaning of injected commands:

- G20/G21 units;
- G90/G91 XYZ positioning;
- M82/M83 extrusion positioning;
- M200 volumetric extrusion mode on firmwares that support it;
- M220 speed-factor override;
- M221 extrusion-factor override;
- G92 coordinate resets.

Audited Bambu common start G-code explicitly resets:
- `M220 S100`;
- `M221 S100`;
- `G90`.

The printable v1 command derivation assumes millimeters, absolute XYZ, relative filament-length E, and no hidden runtime speed/flow multiplier.

A second subtlety is retraction accounting:
`G92 E0` changes the logical E coordinate, but it does NOT physically unretract filament. A parser that resets physical retraction debt on G92 E would be incorrect.

## Decision

Printable v1 requires the following modal state at every injection anchor:

- units = millimeters (G21 semantic state);
- XYZ positioning = absolute (G90);
- E positioning = relative (M83);
- firmware retraction disabled by config;
- volumetric-E mode disabled / not active;
- file-level M220 speed factor = 100%;
- file-level M221 extrusion factor = 100%.

The parser may understand additional modes for diagnostics, but injection is disabled outside this envelope.

## G20/G21

Track units explicitly.

Any anchor in inch mode => Skipped.

## G90/G91

Track XYZ positioning explicitly.

v1 does not temporarily switch a relative-XYZ file into G90 for candidate emission.

Anchor must already be G90 absolute XYZ.

If relevant downstream/original motion changes XYZ mode, the parser may continue to classify it for clearance only, but no plugin block is emitted while the state is unsupported.

## M200 volumetric extrusion

Any active volumetric-E mode in the supported firmware dialect => Skipped.

The plugin emits filament-length relative E, not firmware-volumetric E.

A recognized explicit M200-disable command may be accepted by the pinned compatibility descriptor.

## M220 / M221

Track file-level speed and extrusion overrides.

For physical v1:
- speed override at candidate execution = exactly 100%;
- extrusion override at candidate execution = exactly 100%.

If final G-code changes either override before or inside the candidate execution interval, injection is disabled unless a future ADR explicitly models the multiplier.

Downstream changes inside the physical-clearance horizon must also be parser-visible; if they alter material deposition semantics not modeled by the final structural validator, fail closed.

## G92

Maintain distinct parser state for:
1. logical commanded coordinate origin / E coordinate; and
2. physical filament retraction debt.

### G92 E
Allowed in relative-E supported files when parsed correctly.

It may reset the logical E coordinate for display/compatibility but MUST NOT erase physical retraction debt.

### G92 X/Y/Z
v1 does not support a nontrivial XYZ coordinate-origin remap in the injection context.

If active XYZ G92-origin semantics would make the current execution frame nontrivial/piecewise, or a G92 XYZ appears in the target validation context, injection is disabled.

## Feed F

Feed remains modal.

Every plugin command that changes F is included in SavedMachineState restoration.

The pre-insertion feed must be restored before unchanged Orca G-code resumes.

## External live printer overrides

Offline G-code postprocessing cannot observe a user changing printer speed/flow overrides after the file is sent.

Therefore the physical validation claim is conditional on:
- printer speed override remaining 100%; and
- printer flow override remaining 100%

during the validated print.

Changing runtime speed/flow overrides voids the validated execution envelope.

This limitation must be shown in physical-test instructions/records.

## Requirements / invariants introduced

Parser state explicitly separates:
- units;
- XYZ mode;
- E mode;
- logical E coordinate;
- physical retraction debt;
- M220 factor;
- M221 factor;
- volumetric-E state;
- G92 XYZ-origin state;
- feed.

Injection command generation consumes only a validated supported modal snapshot.

## Alternatives considered

- Temporarily force G90/G21/M83 and restore: rejected for v1; broader modal mutation increases risk.
- Model arbitrary M220/M221 factors: deferred.
- Treat G92 E as retraction reset: rejected as physically wrong.
- Ignore M200 because Bambu normally does not use it: rejected; fail-closed parser should identify semantic mode.

## Safety impact

Critical. Wrong modal interpretation can produce wrong coordinates, speed, or extrusion magnitude.

## Compatibility impact

Narrower but matches the normal audited Bambu start-state family.

## Performance / resource impact

Negligible parser-state additions.

## Observability impact

Attempt diagnostics include a compact modal-state summary and specific unsupported-state reason.

## Test / validation impact

Add:
- G21/G90/M83 accepted;
- G20 reject;
- G91 anchor reject;
- M82 anchor reject;
- M200 volumetric mode reject;
- M220 !=100 reject;
- M221 !=100 reject;
- G92 E does not clear physical retraction debt;
- G92 XYZ target-context reject;
- feed restore equality;
- physical-test record warns that live speed/flow override invalidates validation.

## Migration / rollout

Update parser state schema, plugin requirements, fixtures, and physical-test instructions.

## Rollback / disable condition

Unknown modal state => Skipped.

## Open questions

Support for modeled non-100 M220/M221 or relative XYZ may be added under later ADRs.

Supersedes: any implicit assumption that M83 + parsed XYZ alone completely defines candidate command semantics.
