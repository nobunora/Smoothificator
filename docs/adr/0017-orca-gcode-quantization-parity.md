# ADR-0017: Reproduce Orca G-code quantization before final injection validation

Status: Accepted
Date: 2026-09-30

## Context

The candidate engine operates in floating-point millimeters and volumetric values.

Audited OrcaSlicer `GCodeFormatter` at commit `789f848694b955d293ca6b277d1c8046aa6f7436` emits:
- XYZ/F with 3 decimal digits;
- E with 5 decimal digits;
- rounding through C++ `std::round`.

Python's built-in `round()` uses different tie behavior and MUST NOT be assumed equivalent.

A candidate that is valid before quantization may violate minimum effective bead height, clearance, or extrusion-volume assumptions after export rounding.

## Decision

Create one compatibility-owned Orca G-code quantizer.

For the audited source family:
- XYZ/F resolution = 0.001;
- E resolution = 0.00001;
- midpoint behavior matches C++ `std::round` (half away from zero), not Python bankers rounding.

The optimizer may use higher precision internally.

Before a plan is injectable:
1. transform candidate coordinates into the validated machine execution frame;
2. quantize XYZ and E exactly as the supported Orca formatter would;
3. reconstruct the quantized candidate geometry/extrusion;
4. rerun all execution-critical constraints that quantization can affect;
5. reject the plan if quantization changes validity or exceeds configured error budget.

Emitter output MUST use the same quantizer; it MUST NOT format with unrelated Python defaults.

## Requirements / invariants introduced

Quantization constants are part of the pinned Orca compatibility descriptor, not arbitrary user settings.

An Orca upgrade that changes formatter precision requires compatibility revalidation.

## Alternatives considered

- Python round/format directly: rejected because tie semantics differ.
- Ignore sub-micron/micron rounding: rejected because v1 candidate heights can be close to hard physical bounds.

## Safety impact

High near Z/flow limits and important for deterministic matching.

## Compatibility impact

Pins formatter semantics to the supported Orca source family.

## Performance / resource impact

Negligible.

## Observability impact

Diagnostics may report pre/post quantization min bead height and maximum coordinate delta.

## Test / validation impact

Add:
- positive/negative half-tie cases;
- XYZ 3-digit parity;
- E 5-digit parity;
- candidate valid pre-quantization but invalid post-quantization rejection.

## Migration / rollout

All G-code emitter formatting goes through the compatibility quantizer.

## Rollback / disable condition

Unknown formatter semantics for a new Orca version => injection disabled.

## Open questions

None for current source family.

Supersedes: none.
