# ADR-0014: Represent candidate SubEdge extrusion properties per segment

Status: Accepted
Date: 2026-09-30

## Context

The v1 support model defines effective bead height from local supporting material:

h_eff = z_nozzle - z_support

Even a constant-Z SubEdge centerline may cross a support envelope whose Z varies along the path. One path-wide `height` or `mm3_per_mm` value is therefore not generally consistent with the local finite-bead model.

The final G-code emitter already operates segment-by-segment.

## Decision

Introduce an immutable `SubEdgeSegment` as the authoritative extrusion unit.

Each segment contains at minimum:
- start/end print-space XYZ;
- local support Z or support-height summary;
- effective bead height;
- nominal width;
- geometric `mm3_per_mm`;
- commanded `mm3_per_mm` after Orca-compatible flow modifiers;
- emitted relative-E value after compatibility quantization;
- speed limit/request metadata;
- validation flags/reason if non-injectable.

`SubEdgePath` becomes an ordered collection of `SubEdgeSegment` records plus:
- path id;
- interval/error-region id;
- ordering metadata;
- common travel/seam metadata.

Adjacent segments with equal validated properties may be coalesced only if doing so is behavior-preserving after G-code quantization.

## Requirements / invariants introduced

- No path-wide flow assumption may hide local support-height variation.
- Finite-bead scoring and G-code emission use the same segment-local extrusion intent.
- Preview may summarize path-wide ranges but consumes the same segment records.

## Alternatives considered

- Force support surface to be planar: rejected; unnecessarily restricts ZAA/curved surfaces.
- Use one worst-case path-wide flow: rejected; can create systematic under/over extrusion.

## Safety impact

High. Makes local bead-height and material constraints explicit.

## Compatibility impact

SubEdgePlan schema changes before production implementation begins.

## Performance / resource impact

More plan records; bounded by candidate-segment count and PlanStore limits.

## Observability impact

Report min/max segment effective height and commanded flow per path.

## Test / validation impact

Add:
- varying support-height path;
- segment coalescing equivalence;
- local min-height rejection;
- per-segment E parity.

## Migration / rollout

Implement this schema from Phase 0.5; no migration of production plans is needed because none exist.

## Rollback / disable condition

If support or flow cannot be resolved segment-locally, the candidate is non-injectable.

## Open questions

None.

Supersedes: path-wide extrusion fields in the earlier SubEdgePath draft.


## Partial supersession

ADR-0021 supersedes only the earlier idea that authoritative final emitted E is stored in SubEdgeSegment. Segment-local support/height/geometric/commanded-flow semantics remain Accepted. Final E is derived after machine-frame mapping and XYZ quantization.
