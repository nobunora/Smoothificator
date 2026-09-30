# ADR-0030: Validate source-mesh orientation and derive material side topologically

Status: Accepted
Date: 2026-09-30

## Context

Printable v1 requires a closed manifold source mesh for:
- material-side centerline placement;
- surface normals;
- signed error;
- nesting/support reasoning.

A manifold flag alone does not prove that every triangle winding is consistently oriented or that stored/generated normals point outward.

Mirrored transforms can also reverse global orientation.

Orca slicing can often operate from triangle intersections without relying on outward normals, while Adaptive Sub-Edge needs a reliable inside/outside/material-side interpretation.

## Decision

Printable v1 MUST NOT trust source triangle normals blindly.

After centered-frame transformation:

1. validate the triangle mesh is a closed 2-manifold in the required v1 topology;
2. validate orientation consistency across shared edges, or construct a non-mutating consistent orientation view for analysis;
3. determine global outward orientation from topology/signed-volume or an equivalent deterministic closed-mesh test;
4. account for mirrored transforms/determinant sign;
5. derive analysis normals from the validated orientation view;
6. use a deterministic inside/outside test as an independent material-side check for centerline placement and signed error.

The plugin does not write a repaired mesh back to Orca.

If orientation/material-side cannot be resolved unambiguously, the model is analysis-only/non-injectable.

## Requirements / invariants introduced

- ModelVolume.is_manifold() is necessary but not sufficient.
- Surface normals used for signed error are derived from validated orientation.
- Candidate insetting uses validated material side, not arbitrary triangle winding.
- Mirrored model fixtures must produce the same physical material-side interpretation after transformation.

## Alternatives considered

- Trust raw face normals: rejected.
- Auto-repair and replace the source mesh: rejected; would create a second geometry authority.
- Use unsigned error only: insufficient for material-side candidate placement.

## Safety impact

High for avoiding outward/inward inversion of candidate paths.

## Compatibility impact

Some malformed-but-sliceable models remain analysis-only.

## Performance / resource impact

One topology/orientation validation pass plus inside/outside queries already needed by the engine.

## Observability impact

Record:
- orientation consistency result;
- signed-volume/orientation sign;
- mirrored transform indication;
- material-side validation failure reason.

## Test / validation impact

Add:
- outward-oriented closed mesh;
- globally reversed mesh;
- mirrored instance;
- locally inconsistent winding rejection;
- material-side point tests;
- signed-error sign parity.

## Migration / rollout

Add orientation/material-side validation to geometry_snapshot/mesh geometry prerequisites before surface-band planning.

## Rollback / disable condition

Unresolved orientation or material side => no injection.

## Open questions

None for single closed ModelPart v1.

Supersedes: any assumption that manifold status alone proves usable outward normals.
