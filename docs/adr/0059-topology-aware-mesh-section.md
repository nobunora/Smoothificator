# ADR-0059: Handle mesh-plane topology events directly instead of broad vertex-Z avoidance bands

Status: Accepted
Date: 2026-10-08

## Context

ADR-0053 introduced mesh_section_vertex_avoidance_mm bands around every source vertex Z / horizontal facet Z so candidate planes would avoid ambiguous triangle-plane cases.

That is safe but can become pathologically restrictive.

For a dense tessellated curved mesh, vertex Z values may be separated by very small increments. Positive-width avoidance bands around every vertex can overlap until most or all candidate-Z search space disappears.

This makes a higher-resolution mesh paradoxically less printable by the algorithm even when the underlying physical surface is smooth.

The actual issue is not being near any vertex Z; it is deterministic handling of plane-through-vertex events, plane-along-edge events, coplanar facet patches, and final G-code Z quantization.

## Decision

Printable v1 MUST use a deterministic topology-aware mesh-plane section policy.

Broad positive-width avoidance around every ordinary vertex Z is no longer the primary rule.

### Signed classification

For section plane Z = z0, each transformed vertex gets signed distance d = vertex_z - z0.

Use one versioned section_predicate_epsilon_mm only for numerical ON-plane classification. This epsilon is a numeric predicate tolerance, not a printable exclusion band.

### Canonical intersection identity

Section intersections are keyed by source topology identity where possible:
- interior edge crossing -> canonical source-edge id + interpolation parameter;
- exact source vertex event -> canonical source-vertex id;
- coplanar source edge -> canonical source-edge id.

Duplicate triangle contributions are merged by topology identity before geometric endpoint snapping.

### Vertex-on-plane handling

A source vertex classified ON is not automatically rejected.

Inspect the incident manifold fan:
- if incident non-coplanar faces exist on both sides of the plane, the vertex is a true section event;
- if all incident material lies on one side, it is a tangential touch and does not create a crossing branch by itself;
- ambiguous/inconsistent incident topology => analysis-only.

### Coplanar edge handling

For an edge whose two vertices are ON:
- include it as a section boundary only when adjacent non-coplanar material/topology proves it belongs to the solid-plane boundary;
- tangential duplicate edges are discarded deterministically;
- ambiguous coplanar-edge topology => non-injectable.

### Fully coplanar facet patches

A candidate plane numerically coincident with a connected horizontal/coplanar facet patch is a discrete topology event.

Initial v1 may reject that exact candidate plane under coplanar_section_epsilon_mm, but MUST NOT reject a broad arbitrary band around that Z merely because a horizontal facet exists.

Candidate generation may choose another Z normally.

### Section graph validation

After topology-aware segment generation:
- deduplicate canonical events;
- assemble deterministic graph components;
- printable target component must still satisfy the simple-loop contract: degree 2, one simple closed outer loop, no hole, no branch, no self-intersection, validated material orientation/side.

### Final-Z quantization robustness

The plan is generated before final machine-frame Z quantization.

Therefore printable candidate geometry also requires SectionQuantizationStability.

Define a conservative print-space Z uncertainty for the pinned compatibility descriptor from half the Orca XYZ formatter resolution, execution-frame Z matching tolerance, and numeric section tolerance.

Around candidate command_z_mm, evaluate section stability over this uncertainty interval.

Hard requirement:
- section topology stays the same simple-loop class;
- material side/orientation stays consistent;
- boundary displacement caused by the allowed Z perturbation remains <= configured section_quantization_geometry_tolerance_mm.

This check may use deterministic endpoint/curve sampling with its own convergence rule.

A mere crossing of a source triangle vertex Z is NOT automatically a failure if the physical section remains topologically/geometrically stable.

### No post-plan Z nudging

Postprocess still MUST NOT change candidate command Z to escape a section event.

If final execution quantization lies outside the proven stability interval, injection is Skipped.

## Required settings

Versioned MeshSectionPolicy now includes at minimum:
- section_predicate_epsilon_mm;
- coplanar_section_epsilon_mm;
- mesh_section_join_tolerance_mm;
- section_quantization_geometry_tolerance_mm;
- section-stability sampling/convergence version.

These participate in PluginSettingsFingerprint.

The old broad mesh_section_vertex_avoidance_mm setting is deprecated for hard printable acceptance.

## Requirements / invariants introduced

- Dense mesh vertex count alone cannot erase candidate-Z search space.
- Ordinary vertex crossings are handled topologically, not by broad exclusion.
- Exact ambiguous coplanar facet events may still fail closed.
- Final G-code Z quantization cannot silently move a candidate into a materially different section.
- Same mesh + Z + policy => identical section graph.

## Alternatives considered

- Keep large vertex-Z avoidance bands: rejected because mesh tessellation density controls algorithm availability.
- Add a tiny arbitrary fixed avoidance band: still representation-dependent and does not solve quantization stability.
- Auto-nudge final Z after optimization: rejected because it changes immutable plan geometry.

## Safety impact

High. Preserves fail-closed topology handling without making dense, valid meshes unusable.

## Compatibility impact

Candidates previously rejected only due dense vertex-Z bands may become eligible after topology/stability validation.

## Performance / resource impact

Requires mesh adjacency/topology data and section-stability checks. Use cached topology and bounded local queries.

## Observability impact

Report topology event classes, section graph result, quantization stability interval, maximum boundary displacement, and exact coplanar-plane rejection reason.

## Test / validation impact

Add:
- simple plane through one mesh vertex -> stable valid contour;
- tangent vertex touch -> no false branch;
- plane through shared edge -> deterministic contour;
- exact horizontal coplanar patch -> discrete reject;
- dense curved mesh with closely spaced vertex Z -> candidate search remains available;
- coarse and refined tessellations of same analytic surface produce compatible section geometry;
- final Z quantization perturbation with stable topology -> pass;
- perturbation crossing a true topology/material change -> reject.

## Migration / rollout

ADR-0053 remains authoritative for simple-loop graph validation and no post-plan Z mutation.

This ADR supersedes ADR-0053 only for the broad vertex/facet-Z avoidance-band mechanism.

## Rollback / disable condition

Any unresolved topology/coplanar/quantization-stability case => non-injectable.

## Open questions

A robust-predicate library may later replace custom predicates if dependency review demonstrates deterministic parity and acceptable packaging.