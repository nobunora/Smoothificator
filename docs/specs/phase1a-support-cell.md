# Phase 1A actual nominal-bead support cell query

Status: SPEC_VALIDATED for the bounded actual-bead cell query.

Independent repository review: the implementation lead checked the accepted
chronology, nominal solid and effective-height contracts, existing numeric and
domain types, architecture boundaries and proposed rational interval algorithm.
Flat-cap, rotated, curved-side and partial-obstruction analytic fixtures were
derived independently. Resource-check precedence and exact flat-center bounds
were clarified before implementation. No material conflict remains in this scope.

## Authority and scope

ADR-0044 Closed nominal-bead cell query owns the exact API, four immutable DTOs,
chronology, classification and resource limits. ADR-0048 Explicit source-segment
top query owns the actual swept stadium top and linear structural nozzle locus.
ADR-0058 owns the later adaptive integration/convergence obligation. Manifest:
docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`

Implement domain/support_cell.py and engine/support_cell.py (or existing focused
engine/domain files with identical ownership). Use standard-library Fraction and
isqrt. No dependency, production I/O, mutable cache, arbitrary trusted callback,
Plan publication or canonical registration is introduced. Existing finite numeric
helpers, PrintPoint3, CandidateBeadBounds and typed errors remain unchanged.

## Decisions and evidence

Vertical eligibility resolves the existing h_eff contract without inventing a
physical adhesive-contact or gap model. Flat axial caps imply a rectangular XY
footprint. Actual curved sides and sloped structural/ZAA source loci are queried,
not replaced by flat rectangular patches. Exact affine projection and outward
square-root intervals give whole-cell bounds. Every possible high overlap affects
the upper envelope. A single full source proves coverage; seam-only multi-source
coverage remains unresolved, which is conservative and explicitly incomplete.

Source adapters still must establish normalized coordinates and chronological
ownership. Query success is local nominal arithmetic, not verified Orca geometry,
adaptive support convergence, a printable plan or physical clearance.

## Acceptance

- Exact immutable types, positive cell extents, valid source cross-sections and
  nonzero XY length; malformed fields and invalid chronology reject.
- Independent analytic full/empty, flat-center, curved-side, circle, flat-cap,
  sloped/rotated/reversed fixtures; signed effective-height bounds.
- Partial higher overlap cannot be omitted; seam-only coverage unresolved;
  exact inclusive boundaries and uncertain height classification are correct.
- Subnormal/extreme values avoid float-predicate overflow; precision refinement
  tightens outward bounds; explicit budget overflow is unresolved, never success.
- Unchanged Settings/Plan identities and v1 vectors; no physical success flags.
- Syntax/import, architecture, focused/full regression, independent implementation
  review, package and exact-source CI gates.

## Deferred obligations

No adaptive controller, area integration, contiguous-width metric, general union
coverage proof, spatial acceleration, mesh/Orca adapter, fingerprinted planning
integration, collision or physical gates are completed here. This is a substantive
actual-bead query provider for the later controller, not full Phase1A completion.
