# ADR-0053: Define deterministic mesh-plane section degeneracy handling

Status: Accepted
Date: 2026-10-08

## Context

Adaptive Sub-Edge generates arbitrary-Z target boundaries by intersecting the validated source mesh with horizontal planes.

Triangle-plane intersection becomes numerically/topologically ambiguous when the plane:
- passes exactly through a mesh vertex;
- coincides with a triangle edge;
- coincides with a horizontal triangle/facet;
- lies within floating tolerance of those cases.

Different implementations can produce:
- duplicate segments;
- missing segments;
- open chains;
- branch vertices;
- different loop orientation.

v1 already requires one simple relevant outer boundary, but without a deterministic section policy the same mesh/Z may pass or fail depending on implementation details.

## Decision

Introduce one versioned `MeshSectionPolicy` owned by engine/mesh_section.py.

### Candidate-Z degeneracy bands

Before candidate sectioning, compute source vertex Z values in centered slice-space.

Printable candidate command Z MUST NOT lie within configured:
`mesh_section_vertex_avoidance_mm`
of a source mesh vertex Z or a fully horizontal source facet Z.

The optimizer treats those intervals as forbidden candidate-Z bands rather than silently nudging an already selected candidate.

The setting participates in PluginSettingsFingerprint.

### Triangle classification

For section queries outside forbidden bands:
- classify each triangle vertex strictly above/below the section plane using one versioned numeric tolerance;
- intersect only edges whose endpoint classifications straddle the plane;
- deduplicate shared-edge intersection points using deterministic spatial keys/tolerance;
- reject any unexpected coplanar/ON-plane topology instead of inventing an arbitrary segment.

### Segment assembly

Section segments are assembled into graph components using deterministic endpoint snapping under:
`mesh_section_join_tolerance_mm`.

For printable v1 target interaction:
- every vertex in the relevant section component has degree 2;
- exactly one simple closed outer loop is produced;
- no branch;
- no hole;
- no self-intersection;
- orientation/material side is validated against ADR-0030.

Failure => region analysis-only/non-injectable.

### No silent Z perturbation

The mesh-section implementation MUST NOT change candidate command Z after optimization to escape a degeneracy.

Candidate generation excludes forbidden Z bands before plan finalization.

## Requirements / invariants introduced

- Same mesh + Z + policy => identical section topology.
- Degenerate plane cases fail closed or are avoided before optimization.
- Section tolerances are explicit Settings/fingerprinted.
- No hidden epsilon or library-default snapping.

## Test impact

Add:
- plane through ordinary triangle interiors;
- exact vertex-Z candidate forbidden;
- horizontal-facet Z forbidden;
- near-vertex boundary on both sides of avoidance band;
- duplicate shared-edge intersection deduplication;
- closed simple loop assembly;
- branch/open/self-intersecting section rejection;
- deterministic loop under triangle-order permutation.

## Performance impact

Candidate Z search excludes a finite set of narrow forbidden bands; no material complexity increase.

## Rollback / disable condition

Section topology unresolved => no injection for that region.
