# Phase 1B continuous section stability over a supplied Z interval

Status: SPEC_VALIDATED for bounded supplied-interval section stability.

Independent implementation-lead review checked the continuous bound proof,
per-triangle event guards and current private section/embedding interfaces.
These are consistent with the bounded numerical scope; no material conflict
remains. The cube fixture explicitly includes moving side-face diagonal nodes.

Authority: ADR-0059 Closed continuous event-partition stability certificate owns
the exact API, event guards, symbolic route and continuous displacement proof.
ADR-0030 owns fresh embedded-mesh prerequisites.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `90490ca791491ab1aef2b5f1bf596bd59015f372`

Implement domain/section_stability.py and engine/section_stability.py. Narrow
private refactoring may expose explicit Fraction section tolerances and return
same-call topology from embedding. Preserve existing public single-plane,
embedding and point-classification behavior and their regression fixtures.

The interval is supplied by a caller, not derived from a claimed Orca capability.
Exact arithmetic handles source vertex events, affine open-slab sections and
their limits. Event guards deliberately fail closed for orphan ON vertices or
same-side ON edges. The 3D L1 accumulated bound certifies continuous Euclidean
Hausdorff displacement, not only finite samples. An excessive bound means
unproven, not proven geometric failure. No dependency or physical defaults.

Required fixtures:

- Unit cube with triangulated side walls: bound equals twice halfwidth, from
  moving side-face diagonal nodes plus the Z contribution. Exact tolerance
  equality passes; smaller tolerance returns displacement-unproven.
- Sloped tetrahedron/pyramid: hand-derived edge speeds and accumulated bounds.
- Ordinary crossing vertex in interval: valid simple event and slab loops pass,
  including collapsing segments and changed source edge IDs.
- Orphan tangent vertex at endpoint, same-side ON edge, horizontal facet,
  topology change, empty slab or multiple loops fail closed.
- Near-vertex Z that public section reports predicate-uncertain can be certified
  by the exact route; public section remains unchanged.
- Exact halfwidth/input normalization, rational midpoint not representable in
  binary64, symbolic zero tolerances without invalid public DTO construction.
- Mesh pair, section pair/segment and total query caps; 2*K-1 preflight boundary;
  cancellation at each phase returns no partial displacement bound.
- Reversal/mirror/translation parity; independent continuous analytic bounds,
  not assertions based only on repeated sampled production calls.

This establishes numerical supplied-interval geometry only. Actual formatter
resolution, frame matching tolerance and interval derivation must still be
verified before this result can contribute to injection eligibility.
