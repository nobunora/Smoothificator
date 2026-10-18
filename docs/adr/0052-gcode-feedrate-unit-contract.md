# ADR-0052: Make speed-to-G-code feedrate units explicit

Status: Accepted
Date: 2026-10-08

## Context

Orca process/machine speed settings such as outer_wall_speed, travel_speed, and travel_speed_z are expressed in mm/s.

G-code F values are emitted in mm/min.

Current Orca source explicitly performs:
- extrusion: F = speed * 60;
- XY travel: emit_f(travel_speed * 60);
- Z travel: emit_f(travel_speed_z * 60).

Earlier Adaptive Sub-Edge documents bounded candidate speed in mm/s but did not explicitly define conversion to emitted F.

That omission can produce a catastrophic 60x unit error.

## Decision

Use explicit typed/unit naming throughout:

- candidate_speed_mm_s
- travel_speed_xy_mm_s
- travel_speed_z_mm_s
- feedrate_mm_min

Only the G-code emitter converts:

feedrate_mm_min = speed_mm_s * 60.0

The resulting F value is then formatted/quantized with the pinned Orca formatter contract.

Parser-tracked existing G-code F values are machine feedrate values in mm/min and MUST NOT be compared directly to profile mm/s values without conversion.

When a matched structural G-code feed is used as an upper bound:
- parse F_mm_min;
- convert structural_speed_mm_s = F_mm_min / 60.0;
- apply runtime M220 policy as defined by the modal contract;
- compare only like units.

Retraction/deretraction speeds follow the same explicit conversion contract when emitted as F values.

## Requirements / invariants introduced

- No ambiguous variable named only speed/F across the domain/emitter boundary.
- Profile/config speeds remain mm/s.
- Parsed/emitted G-code F remains mm/min.
- Conversion occurs in one execution adapter owner.
- Unit conversion is tested before physical injection.

## Test impact

Add:
- 50 mm/s -> F3000;
- 5 mm/s Z travel -> F300;
- parsed F1200 -> 20 mm/s;
- retraction speed conversion;
- Orca formatter parity after conversion;
- tests that intentionally fail if a mm/s value is emitted directly as F.

## Rollback / disable condition

Unknown firmware feedrate-unit semantics => no injection.
