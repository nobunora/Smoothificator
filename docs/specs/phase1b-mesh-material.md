# Phase 1B exact mesh embedding and point material predicates

Status: SPEC_VALIDATED for bounded exact embedding and point classification.

Independent implementation-lead review checked the contract against actual
topology/section conventions and the independent inside/outside requirement.
Adjacent-pair checks, shared-simplex restrictions, boundary-first classification
and deterministic bounded rays are consistent; no material conflict remains.

Authority: ADR-0030 Closed exact embedding and point classification owns the
two APIs, two result DTOs, exact algorithms and failure/resource precedence.
The indexed-topology subsection remains its prerequisite; ADR-0027 retains
independent Orca/frame requirements.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `7e96ba2c2f77717503fcee1e22e8c6de3ba3501e`

Implement domain/material_side.py, engine/material_side.py and focused private
engine/triangle_intersection.py. Reuse IndexedTriangleMesh, PrintPoint3,
prepare_mesh_topology, its private _cross/_difference exact arithmetic and existing
typed errors. Do not introduce a generic utility owner or external dependency.
Every public query revalidates input geometry, so result DTOs are diagnostic
values rather than reusable permission receipts.

Pair intersections must include coplanar degeneracies, nonparallel point/segment
overlap and adjacent-face overlap beyond the actual shared simplex. Exact source
IDs distinguish adjacency from coincident nonlocal coordinates. Classification
checks exact boundary first, then bounded deterministic ray parity. Ambiguous
ray edge/vertex or coplanar-plane events retry and exhaustion stays incomplete.

Required independent fixtures:

- Tetrahedron/cube and globally reversed/mirrored coordinates: embedding passes;
  interior/exterior/face/edge/vertex classifications and translated coordinates.
- Adjacent triangle pairs intersecting exactly at their common source edge or
  vertex pass; unrelated contact and overlap beyond shared adjacency reject.
- Noncoplanar crossing, coplanar area overlap, coplanar edge/point-only contact,
  parallel disjoint planes, and disjoint coplanar triangles.
- Combinatorial closed manifold with geometric self-intersection rejects even
  though topology passes; zero signed volume retains topology failure precedence.
- First ray through vertex/edge or lying in a face plane retries; later generic
  direction succeeds. Exhaustion does not fabricate inside/outside/boundary.
- Pair preflight before intersection work; exact cap boundary; fresh embedding
  on every classification, malformed values, cancellation in each phase and
  callback exceptions without partial output.
- Independent analytic triangle-intersection and classification fixtures;
  no arbitrary test-provided proof callback.

These APIs establish exact supplied-mesh geometry only. They do not complete
surface-band planning, section quantization stability, Orca provenance/parity,
tool clearance, G-code rewriting or physical release. Review before production.
