# Phase 1B exact single-plane research mesh section

Status: SPEC_VALIDATED for the bounded single-plane research section.

Independent implementation-lead review checked the complete contract against
the actual topology API, existing positive policy tolerances and ownership.
Near-ON uncertainty, coplanar precedence, CCW without material authority and
revalidation of source topology are consistent; no material conflict remains.

Authority: ADR-0059 Closed exact single-plane research section owns the exact
API, predicates, topology events, reason precedence and limits. ADR-0030 owns
the revalidated topology prerequisite. ADR-0053 owns remaining simple-loop rules.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `44f3dc7b41b0cb88d197ad041543c7cbc02c9287`

Implement domain/mesh_section.py and engine/mesh_section.py. Reuse PrintPoint3,
IndexedTriangleMesh, prepare_mesh_topology, MeshSectionPolicy and typed errors.
Three DTOs and one section_mesh_plane API are specified in the ADR. No section
provider trust shortcut, dependency, Orca import or Plan identity change.

Independent design choices: exact rational intersections preserve selected Z;
ordinary exact ON vertices and opposite-side coplanar edges are supported;
tangencies contribute no branches; numeric near-ON ambiguity fails incomplete.
Coplanar facet tolerance has precedence. Distinct near topology nodes reject
instead of arbitrary snapping. CCW is not outward/material evidence. Required
pair budget bounds exhaustive exact simplicity/proximity checks. Snapshot-local
IDs remain associated only with the input mesh.

Required fixtures: cube/tetrahedron ordinary cuts and sloping face intersections;
exact ordinary vertex crossing and tangent vertex; plane along shared edge with
opposite-side versus same-side incident material; coplanar facets and separate
numeric tolerances; nonzero epsilon-ON incomplete; outside mesh empty; duplicate
contributions; distinct-key coincident/near nodes; open/branch graph, multiple
loops, self-cross/touch/collinear overlap; exact cycle area and deterministic CCW
start; global input winding reversal/mirroring; limits before allocation/pairs;
malformed types, bad versions and cancellation without partial loop.

Mesh topology invalidity propagates before section work. No test may call the
result quantization-stable, material-validated or injectable. Full epsilon-ON
certification, independent embeddedness/inside-out tests, source adapters, final-Z
stability, band planning and G-code integration remain later gates. This slice
is a real callable source section algorithm and does not complete Phase 1B.
