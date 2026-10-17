# Phase 1A adaptive actual-bead support controller

Status: SPEC_VALIDATED for the bounded adaptive numerical controller.

Independent implementation-lead review checked existing numeric/settings types,
the actual cell provider, chronology and geometry contracts, outward coordinate
mapping, the rational area Jacobian, width sweep and failure precedence. No
material conflict remains. Once target side falls below the minimum split size,
both later split counts are one; implementation may retain that exact predicate
without growing unused rational powers. This preserves the declared subdivision
semantics while bounding arithmetic. Separate width-sweep code may own the
internal O(N log N) algorithm; no public proof callback is introduced.

Authority: ADR-0058 Closed straight-footprint adaptive controller owns the exact
three DTOs, API, partition, metric, convergence and failure contract. ADR-0044
owns the existing actual-bead cell query and ADR-0048 its nominal solid.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `7e96ba2c2f77717503fcee1e22e8c6de3ba3501e`

Implement domain/support_coverage.py and engine/support_coverage.py. Reuse all
existing settings/source types and engine/support_cell._sqrt_bounds. No arbitrary
geometry callback, new dependency, source parser, Plan identity mutation, I/O or
physical permission is introduced. The sole callback is cancellation.

The canonical Python-like API table in ADR-0058 is normative. The straight
candidate uses exact local t/v cells and conservative outward world AABBs, so
real sloped/curved nominal source beads are queried. It is not a rectangle-only
synthetic oracle. Rotated boundaries and multi-source seams may remain unresolved;
this is an explicit fail-closed limitation. This milestone is a reusable actual
adaptive numerical controller, not complete Phase 1A or the whole plugin.

Focused acceptance fixtures:

- Wide real flat-center source: exact area=1, full width, exact height; two passes.
- Rotated candidate with comfortably covering real source; reverse direction.
- Narrow unsupported slit missed by point sampling: no false success, including
  when area threshold would permit its area but unresolved remains.
- Disconnected lateral intervals: longest union, not summed widths; a narrow
  longitudinal strip controls the minimum. Coincident t/v events and gaps.
- Curved sides and sloped structural sources; partial high overlap prevents
  accepting invalid height. Exact height boundary never widened by tolerance.
- Noninteger refinement factor, preserved proofs, blocked minimum-size splits,
  max-levels=1, success at final allowed pass, cumulative query budget overflow.
- Tiny/huge finite coordinates, outward float conversion, nonrepresentable AABB,
  low sqrt precision and zero normal components. No inward proof conversion.
- Cancellation before first pass and midway: last full snapshot only; bad bool
  and callback exception behavior; source-count resource precedence unchanged.
- Independent hand-derived area/width union fixtures and deterministic repeat.

Run focused tests and existing architecture/support-cell regressions. Verify
source chronology and budgets remain fail-closed. Passing tests establish this
bounded numerical API only, not source-file proof, material calibration, collision
clearance, Orca integration, Plan injectability or physical release readiness.
