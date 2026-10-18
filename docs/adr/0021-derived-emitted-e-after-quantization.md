# ADR-0021: Keep emitted E derived from the immutable plan, not stored as precomputed plan state

Status: Accepted
Date: 2026-09-30

## Context

ADR-0014 initially listed final relative-E after compatibility quantization as a SubEdgeSegment field.

That conflicts with ADR-0009 and ADR-0017.

The immutable SubEdgePlan is created at geometry-analysis time, before:
- final G-code structural matching;
- print-space -> machine-G-code translation;
- final XYZ formatter quantization.

Machine-space XYZ translation itself preserves Euclidean length, but XYZ quantization can slightly change each emitted segment length. Orca-compatible E should therefore be derived from the **quantized emitted segment length**, not frozen from the higher-precision planning geometry.

## Decision

SubEdgePlan / SubEdgeSegment stores execution intent only:
- high-precision print-space start/end geometry;
- local support/effective bead height;
- nominal width;
- geometric_mm3_per_mm;
- commanded_mm3_per_mm before G-code coordinate quantization;
- speed limits/policy;
- ordering/support metadata.

It MUST NOT store the final emitted E as authoritative plan state.

At postprocess, the G-code adapter deterministically derives execution commands:

1. apply validated execution-frame translation;
2. quantize machine XYZ with ADR-0017 semantics;
3. compute actual emitted segment length from quantized XYZ;
4. compute unquantized E from:
   emitted_length * commanded_mm3_per_mm / filament_cross_section;
5. quantize E with ADR-0017 semantics;
6. reconstruct/validate the quantized execution candidate;
7. emit only if all constraints remain valid.

The derivation is pure and deterministic from:
- immutable plan;
- validated execution config fingerprint;
- validated execution-frame translation;
- pinned Orca compatibility descriptor.

## Requirements / invariants introduced

- Preview shows planned geometric/commanded flow, not an invented pre-export E.
- Injector may derive execution commands but may not alter candidate geometry/flow policy.
- Any post-quantization invalidity causes Skipped, never plan mutation.

## Alternatives considered

- Precompute E from high-precision plan length: rejected because XYZ quantization can change emitted length.
- Store machine-space geometry in plan: rejected by ADR-0009 separation.

## Safety impact

High near minimum-height/flow/short-segment limits.

## Compatibility impact

Clarifies plan schema before implementation.

## Performance / resource impact

Negligible.

## Observability impact

Execution diagnostics may record planned length, quantized emitted length, unquantized E, and quantized E summaries.

## Test / validation impact

Add short-segment cases where XYZ quantization changes length and verify deterministic E recomputation.

## Migration / rollout

Remove final emitted-E fields from the plan schema. Update ADR-0014/Specification/Implementation language accordingly.

## Rollback / disable condition

If the execution derivation cannot be reproduced exactly for the pinned compatibility descriptor, injection is disabled.

## Open questions

None.

Supersedes: ADR-0014 only for storage of final emitted E.
