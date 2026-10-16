# Phase 1B indexed mesh topology prerequisite

Status: SPEC_VALIDATED for the bounded indexed-topology prerequisite.

Independent implementation-lead repository review checked the API against existing
source types, architecture boundaries and Gate C fixtures. Local winding rejects,
global view reversal and deferred geometry provenance/material proof are
consistent; no material contradiction remains in this scope.

Authority: ADR-0030 Closed indexed-topology prerequisite owns the exact three
DTOs, API, failure precedence and proof limits. ADR-0027 owns source validity;
ADR-0059 requires canonical source adjacency for later topology-aware sections.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `90490ca791491ab1aef2b5f1bf596bd59015f372`

Implement domain/mesh_topology.py and engine/mesh_topology.py. Reuse PrintPoint3,
finite numeric policy and typed ContractError/ReasonCode. No new dependency,
Orca import, filesystem operation, mutable shared owner or canonical registration.
The caller supplies already-centered geometry; this slice does not certify its
Orca provenance/parity. Edges and vertex-face incidence are reusable sectioner
inputs. This is executable topology validation, not an opaque trust DTO.

Decisions: reject unused vertices and local inconsistent winding; allow a global
non-mutating orientation reversal. Exact rational predicates and volume avoid
hidden epsilon. Vertex links must be single cycles. Positive volume is an
orientation convention, not independent proof of an embedded solid/material side.
Mirrored coordinates are already transformed and receive no second determinant
flip. Source identity, mesh self-intersection/material checks, plane sections,
quantization stability and candidate paths remain later work.

Required fixtures:

- Tetrahedron/cube: exact edges, adjacency, signed volume and unchanged input.
- Globally reversed and mirrored coordinates: positive view volume and stable
  physical coordinate set, with recorded input sign.
- Empty, invalid indices/bools, nonfinite points, repeated-index/collinear faces,
  duplicate/reversed duplicate faces and unused vertices.
- Open edge, more-than-two-face edge, local winding error, disconnected shells,
  pinched/bow-tie vertex links, zero signed volume and planar bounds.
- A self-intersecting combinatorial manifold may pass topology only; no test or
  result may interpret that as embeddedness/material/injection validation.
- Exact threshold limits; oversized malformed tuple returns resource-limit before
  element scan; cancellation before/during each phase returns no partial view;
  malformed callback values reject and callback exceptions propagate.
- Repeatability and large iterative traversal without recursion.

Run focused unit/architecture gates; review constructors separately from engine
relational proof. SPEC_VALIDATED requires implementation-lead repository review.
No GUI/physical/G-code evidence is needed or claimed for this prerequisite.
