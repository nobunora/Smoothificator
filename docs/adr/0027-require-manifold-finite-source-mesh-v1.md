# ADR-0027: Require a finite manifold source mesh for printable v1

Status: Accepted
Date: 2026-09-30

## Context

The v1 engine depends on source geometry for:
- arbitrary-Z plane sections;
- material-side classification;
- surface normals / signed error;
- nesting/support reasoning.

The Orca Python ModelVolume binding exposes:
- `is_manifold()`;
- `mesh_errors_count()`;
- immutable mesh vertices/triangles.

Orca may be able to slice or repair models that are unsuitable for the plugin's independent geometry assumptions.

Trying to reconstruct reliable closed surface bands from an open/non-manifold or numerically invalid mesh would introduce silent ambiguity.

## Decision

Printable v1 requires the one ModelPart source mesh used by the plan to satisfy:
- non-empty vertices/triangles;
- all coordinates finite;
- valid triangle indices;
- `ModelVolume.is_manifold() == true`;
- transformed finite bounding box;
- non-degenerate positive extent;
- centered-frame parity checks from ADR-0012.

`mesh_errors_count()` is recorded as diagnostics. Repaired meshes MAY be used if the bound current ModelVolume mesh is manifold and passes all parity/section tests; the plugin treats the current Print-owned mesh snapshot as authoritative, not the pre-repair file bytes.

Plane-section construction must additionally detect and reject unresolved degeneracies at candidate Z:
- dangling/open contour;
- ambiguous duplicate edge;
- non-closed material boundary where a closed loop is required.

## Requirements / invariants introduced

- Printable geometry never relies on guessed closure/repair inside the plugin.
- Source normals/sign tests are used only after mesh validity gates pass.
- Analysis may report unsupported mesh reasons without injecting.

## Alternatives considered

- Auto-repair in Python: rejected; would diverge from Orca geometry and create a second mesh authority.
- Accept non-manifold and use unsigned distance only: insufficient for material-side centerline placement.

## Safety impact

High for geometric correctness.

## Compatibility impact

Some Orca-sliceable damaged models remain analysis-only.

## Performance / resource impact

One mesh validity scan plus existing section validation.

## Observability impact

Record manifold flag, repaired-error count, vertex/triangle counts, and section failure reason.

## Test / validation impact

Add:
- valid closed mesh;
- open mesh rejection;
- non-manifold edge rejection;
- NaN/Inf rejection;
- degenerate triangle/section case;
- repaired-but-currently-manifold fixture if available.

## Migration / rollout

Add gates to geometry_snapshot and mesh_section.

## Rollback / disable condition

Any unresolved mesh validity/section ambiguity disables injection.

## Open questions

Broader repaired/implicit source support is deferred.

Supersedes: none.
