# ADR-0026: Keep each v1 SubEdge path at one constant command Z

Status: Accepted
Date: 2026-09-30

## Context

Adaptive Sub-Edge originated as additional intermediate constant-Z surface contours between structural layers.

During generalization to segment-local support/flow, some draft DTO wording allowed the interpretation that one SubEdgePath could itself vary continuously in Z.

That would turn v1 into a new non-planar path generator, overlap substantially with ZAA's solution space, complicate travel/collision validation, and contradict the intended research distinction:
- ZAA varies Z along existing paths;
- Adaptive Sub-Edge adds new intermediate contours at independently optimized heights.

Segment-local support height may vary even when nozzle command Z is constant, so segment-local effective bead height/flow remains necessary.

## Decision

Every printable v1 `SubEdgePath` has one immutable:

`command_z_mm`

All segments in that path share that command Z, subject only to final constant machine-frame translation and Orca-compatible formatter quantization.

Different SubEdgePaths may:
- use the same command Z;
- use different independently optimized command Z values.

A surface band may therefore contain:
- several lateral centerlines at one Z;
- several centerlines at different Z;
- combinations of both.

The engine MUST NOT generate continuously varying-Z candidate paths in v1.

## Requirements / invariants introduced

- `SubEdgePath.command_z_mm` is authoritative.
- `SubEdgeSegment` stores XY endpoints plus local support/effective-height/flow; its plan-space Z equals the parent path's command Z.
- Effective bead height may vary segment-by-segment because support Z varies.
- Candidate ordering can use path command Z plus validated spatial/non-crossing relationships.

## Alternatives considered

- Allow arbitrary 3D candidate polyline: rejected for v1 scope and conceptual overlap with ZAA.
- Require all added paths in one interval to share one Z: rejected; independent path heights are a core feature.

## Safety impact

Simplifies collision/travel reasoning and prevents accidental non-planar candidate generation.

## Compatibility impact

None; constant-Z G1 candidate emission is simpler for supported stock-Orca postprocess.

## Performance / resource impact

Reduces search/execution complexity.

## Observability impact

Preview reports command Z per SubEdgePath and effective-height range per segment.

## Test / validation impact

Add:
- all segments of one path share command Z;
- different paths can share/differ Z;
- attempted varying-Z path construction rejected.

## Migration / rollout

Update DTO/specification/engine interfaces before implementation.

## Rollback / disable condition

None.

## Open questions

Continuously varying-Z added paths would require a future ADR and would be a distinct research extension.

Supersedes: any draft wording that allowed a v1 SubEdgePath to carry an arbitrary Z profile.
