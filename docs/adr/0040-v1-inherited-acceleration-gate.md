# ADR-0040: Gate candidate execution on a known conservative inherited acceleration state

Status: Accepted
Date: 2026-10-02

## Context

Adaptive Sub-Edge v1 deliberately avoids emitting new acceleration/jerk/pressure-advance role setup commands.

That keeps postprocess mutation small, but it means candidate extrusion inherits the actual firmware acceleration/modal state present at the insertion anchor.

The insertion anchor is a layer boundary, and the previously active acceleration may come from:
- an external wall;
- inner wall/infill;
- travel;
- another feature.

A high travel/infill acceleration can produce different vibration and pressure transients on a fine surface SubEdge path even if the candidate feed rate itself is conservative.

The previous contract tracked acceleration but did not define an acceptance bound.

## Decision

Printable v1 keeps the "do not emit new acceleration commands" strategy, but adds a strict gate.

At every insertion anchor:
1. the parser must know the active acceleration state for the pinned Bambu/firmware fixture;
2. the effective acceleration governing candidate G1 extrusion must be positive and finite;
3. it must not exceed a fixture-defined `max_subedge_acceleration_mm_s2`;
4. that plugin safety cap must be no greater than the resolved external-wall acceleration limit selected for the exact fixture.

The cap is a plugin-owned safety setting and participates in PluginSettingsFingerprint.

Relevant Orca acceleration configuration and parsed modal state participate in ExecutionConfigFingerprint / final parser validation.

If acceleration state cannot be reconstructed or exceeds the approved cap, injection is Skipped.

## Why not emit M204 in v1

Temporarily changing acceleration and restoring it would be technically possible for some dialects, but would:
- expand the modal-state mutation surface;
- require exact Bambu firmware command semantics;
- interact with mass-load/dynamic acceleration features;
- require more state restoration paths.

Initial v1 instead accepts only anchors where inherited state is already conservative.

## Dynamic acceleration features

Any printer/process feature that changes acceleration dynamically in a way not represented by the supported parser/fixture is non-injectable.

Current fixture acquisition must verify the relevant acceleration commands and limits.

## Requirements / invariants introduced

- Candidate feed speed alone is not considered a sufficient motion-quality bound.
- Active acceleration is part of the saved/validated machine state.
- Plugin does not change acceleration in v1.
- Physical v1 requires an explicit candidate-acceleration upper bound.

## Alternatives considered

- Ignore acceleration: rejected.
- Always emit external-wall M204 then restore: deferred.
- Hard-code one acceleration across Bambu printers: rejected.

## Safety impact

Medium for collision safety; High for surface quality, ringing, and pressure/transient reproducibility.

## Compatibility impact

May reject anchors/profile families whose acceleration state is not parser-visible or conservative.

## Performance / resource impact

Negligible.

## Observability impact

Attempt diagnostics report:
- parsed active acceleration;
- configured candidate maximum;
- margin/result.

## Test / validation impact

Add:
- known conservative acceleration accepted;
- high travel acceleration rejected;
- unknown acceleration rejected;
- zero/non-finite acceleration rejected;
- PluginSettingsFingerprint changes with max_subedge_acceleration;
- saved acceleration unchanged after plugin block.

## Migration / rollout

Update Settings, parser state, fingerprints, Plugin Requirements, Test Strategy, and physical fixture format.

## Rollback / disable condition

Unknown acceleration state => Skipped.

## Open questions

Explicit acceleration control may be introduced later under a dialect-specific ADR.

Supersedes: the permissive interpretation in ADR-0020 that any inherited acceleration state is acceptable.
