# Phase 1B exact whole-segment material classification

Status: SPEC_VALIDATED for exact whole-segment material classification.

Independent implementation-lead review checked actual API/module boundaries,
closed contact predicates, shared endpoint parity and failure mapping. The
bounded contract has no mathematical or material-ownership conflict.

Authority: ADR-0030 Closed exact whole-segment material classification owns the
API, contact predicates, endpoint proof and closed results. Its embedding and
point-classification subsections remain authoritative prerequisites.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `6daab8f3e35a03cc0cbc7bdda20dbe096d78950b`

Extend domain/material_side.py, engine/material_side.py and
engine/triangle_intersection.py. Extract shared private endpoint classification
from the existing point API while preserving that public API's behavior. No new
dependency, module owner, proof cache, adapter or physical setting is introduced.

The entire closed segment is tested against every source triangle after fresh
embedding. Exact coplanar parameter clipping preserves point/edge contacts.
Only contact-free segments receive endpoint parity classification; both endpoints
must agree. Boundary-contact means any contact, not full boundary containment.
This is mathematical segment inclusion, not finite-width bead or tool clearance.

Required independent fixtures:

- Convex tetra/cube strictly interior and strictly exterior whole segments.
- Concave solid: two strictly inside endpoints whose connecting segment exits
  and re-enters material must return boundary-contact; endpoints alone cannot pass.
  Use the independent nested-cone bipyramid fixture with endpoints
  (+/-5/8,0,1/4), each inside its material side of the central cavity.
- Exterior endpoints crossing material, tangency at vertex/edge, endpoint on
  face, coplanar edge overlap, coplanar face interior, and disjoint coplanar segment.
- Exact plane-crossing and clipping parameter endpoint equality; no epsilon.
- Reversal of segment endpoints, global mesh reversal, mirroring and translation.
- Zero normalized length, bad types/limits/callback; embedding and pair-budget
  failure precede classification; ray exhaustion remains incomplete.
- Cancellation during contact and either endpoint phase; no partial value.
- Defensive classification-inconsistent mapping via a focused private-helper
  fault fixture, without making an arbitrary proof callback part of the API.
- Existing public embedding/point and section-stability regression coverage after
  any shared-helper refactor; fresh embedding once per segment public call.

Passing this slice does not generate a candidate path or authorize G-code. It
supplies a necessary exact containment predicate for later path construction.
