# ADR-0036: Gate timelapse, wrapping-detection, wipe-tower, and object-cancellation behaviors in printable v1

Status: Accepted
Date: 2026-10-02

## Context

Current Orca/Bambu G-code generation can add layer- or print-level behavior that is not represented by the basic structural toolpath:

- timelapse modes;
- farthest-point timelapse;
- timelapse G-code that may move/retract the toolhead;
- wrapping detection;
- prime/wipe tower paths even for otherwise single-filament cases;
- object-label / exclude-object cancellation commands.

Current Orca main also contains newer farthest-point timelapse paths that were not part of the original 2026-09-29 audit baseline.

Adaptive Sub-Edge inserts extrusion after Orca generated these behaviors.

If an injected block is outside an object-cancellation scope, or if layer timelapse/wipe motion changes retraction/position in an unmodeled way, a valid-looking plan may execute incorrectly.

## Decision

Printable v1 narrows these behaviors.

### Smooth timelapse

Rejected.

Smooth timelapse may require wipe/prime tower and deliberate toolhead movement.

### Traditional timelapse

Allowed only for an exact golden fixture where:
- `timelapse_type` is fingerprinted;
- `time_lapse_gcode` / generated timelapse behavior is known;
- any timelapse commands in the candidate anchor or final clearance horizon are fully parsed;
- retraction/state changes are included in SavedMachineState / chronological ToolClearance validation.

No generic assumption is made that "Traditional" means motion-free.

### Farthest-point timelapse

`farthest_point_timelapse` MUST be disabled for printable v1.

### Wrapping detection

`enable_wrapping_detection` MUST be disabled for printable v1.

Its wipe-tower / layer behavior is not replicated by the current contract.

### Prime / wipe tower

Printable v1 requires no generated prime/wipe tower execution in the target print.

This follows naturally from:
- one filament/tool;
- smooth timelapse off;
- wrapping detection off;
but is also verified from the final fixture/G-code.

### Object cancellation

`exclude_object` MUST be disabled for printable v1.

The injected block does not yet participate in Orca's firmware-specific object-exclusion command contract.

`gcode_label_objects` comments may remain enabled and can be used as supporting matcher evidence, but they do not authorize skip-object semantics.

## ExecutionConfigFingerprint additions

Include:
- timelapse_type;
- farthest_point_timelapse;
- time_lapse_gcode or an equivalent canonical template hash;
- enable_wrapping_detection;
- enable_prime_tower / actual tower-presence semantics required by the pinned source family;
- exclude_object;
- gcode_label_objects for diagnostics/matching.

## Requirements / invariants introduced

- Final G-code parser classifies any allowed traditional timelapse behavior in the relevant window.
- No hidden wipe/prime-tower execution is present in printable v1.
- User object-cancellation semantics are not claimed/supported in v1.
- New Orca timelapse features require explicit compatibility review rather than inheriting support accidentally.

## Alternatives considered

- Support all timelapse modes from the first release: rejected.
- Wrap inserted blocks in object labels/EXCLUDE_OBJECT commands immediately: deferred; firmware-specific semantics need dedicated fixtures.
- Ignore farthest-point timelapse because default is false: rejected; supported profiles can enable it.

## Safety impact

High for machine-state correctness and unexpected motion.

## Compatibility impact

Narrows initial physical profile families.

## Performance / resource impact

None.

## Observability impact

Preview shows exact failed gate: smooth timelapse, farthest-point timelapse, wrapping detection, wipe tower, or exclude-object.

## Test / validation impact

Add:
- smooth timelapse reject;
- traditional fixture with known parser-visible behavior;
- unknown traditional timelapse motion reject;
- farthest_point_timelapse=true reject;
- wrapping detection reject;
- generated wipe tower reject;
- exclude_object=true reject;
- gcode_label_objects alone allowed.

## Migration / rollout

Update config fingerprint, Plugin Requirements, Test Strategy, and fixture acquisition.

## Rollback / disable condition

Unknown generated layer/timelapse/cancellation behavior => Skipped.

## Open questions

Object cancellation support and broader timelapse support are later compatibility features.

Supersedes: any broad wording that "normal non-calibration print" alone covers all layer-level dynamic motion features.
