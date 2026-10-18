# ADR-0046: Gate printable v1 on a known conservative inherited jerk/cornering state

Status: Accepted
Date: 2026-10-08

## Context

ADR-0040 gates inherited acceleration because v1 deliberately does not emit role-specific acceleration commands.

Current Orca G-code generation also selects role-specific jerk/cornering values for extrusion paths.

A SubEdge block inserted later inherits the machine's active cornering state. A high travel/infill jerk can change ringing, pressure transients, and short-segment motion behavior even when feed and acceleration are conservative.

The exact command/semantic representation is firmware-dialect dependent.

## Decision

For the first pinned Bambu fixture family, printable v1 requires a parser-known supported cornering state.

Where the fixture uses classic jerk semantics:
- active XY jerk must be finite and non-negative;
- active jerk <= plugin setting `max_subedge_jerk_mm_s`;
- plugin cap <= the fixture's resolved external-wall jerk limit.

The plugin does not emit or modify jerk in v1.

If the pinned firmware/profile instead uses a different cornering model such as junction deviation, that model is unsupported until a dedicated compatibility contract defines it.

The active cornering state and relevant resolved config participate in execution validation/fingerprints.

## Requirements / invariants introduced

- Candidate feed + acceleration alone are not the complete motion-quality envelope.
- Unknown cornering semantics => Skipped.
- Plugin-owned jerk cap participates in PluginSettingsFingerprint.

## Test impact

Add:
- known conservative jerk accepted;
- high inherited jerk rejected;
- unknown jerk/cornering state rejected;
- jerk cap fingerprint change;
- plugin block leaves jerk state unchanged.

## Rollback / disable condition

Unknown or unsupported cornering semantics => no injection.
