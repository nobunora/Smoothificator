# Research-only nominal structural top query

Status: SPEC_VALIDATED for this bounded nominal-top query only.
Independent specification review closed unbounded exact-rational point input
with an explicit bit-length budget and aligned cancellation promises with the
fixed existing helper. Read-only repository review against MAIN `2257bd1`
returned `validated`: `_segment_top_bounds` already owns the ADR-0048 nominal
geometry, repeated-point corners preserve exact point membership, and
conservative rectangular bounds fit the proposed result matrix. Manifest:
`docs/AUDIT_REVISION_2026-10-16.json`, Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`.

Canonical basis: `docs/SPECIFICATION.md` at the audited revision in
`docs/AUDIT_REVISION_2026-10-16.json` (manifest Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`). ADR-0048 owns the
`NominalBeadSolidV1` stadium sweep, axial caps and union top. This handoff
extends the **existing** `adaptive_subedge/domain/support_cell.py` and
`adaptive_subedge/engine/support_cell.py` owner with a pure research query.
It must call/refactor their `_segment_top_bounds` and `_sqrt_bounds` once as
the authoritative bead math; no second independent stadium formula, flow
model, surface/coverage policy or Settings dependency may be introduced.

## Closed bounded API

```python
# Existing DTOs are reused unchanged:
# SupportCellXY, NominalSupportSegment, SupportCellQueryPolicy

@dataclass(frozen=True, slots=True)
class NominalStructuralTopBounds:
    state: str  # absent | full-bounded | unresolved-partial | incomplete
    reason: str
    top_z_lower_mm: Fraction | None
    top_z_upper_mm: Fraction | None

def query_nominal_structural_top_point(
    x_mm: Fraction, y_mm: Fraction,
    sources: tuple[NominalSupportSegment, ...], *,
    policy: SupportCellQueryPolicy, max_point_coordinate_bits: int,
    cancelled: Callable[[], bool],
) -> NominalStructuralTopBounds: ...

def query_nominal_structural_top_cell(
    cell: SupportCellXY,
    sources: tuple[NominalSupportSegment, ...], *,
    policy: SupportCellQueryPolicy,
    cancelled: Callable[[], bool],
) -> NominalStructuralTopBounds: ...
```

The existing policy version `nominal_bead_cell_bounds_v1` supplies explicit
`sqrt_fraction_bits` (1..4096) and `max_source_segments`. The caller supplies
horizontal straight structural segments with immutable `PrintPoint3`
endpoints, constant start/end Z, finite `width>=height>0`, nonzero XY length,
and `source_kind="structural"`. Reuse the existing DTO validation; reject
nonhorizontal or candidate sources as `INVALID_GEOMETRY`. This mathematical
query makes no assertion about a printer profile, actual Orca flow, source
chronology, or calibrated Settings bounds. Segment IDs must be unique for
unambiguous provenance, but their lexical order must not affect the union.
No positional/effective-height safety policy is read.

Point XY inputs are exact Fraction, including zero and nonbinary rationals.
`max_point_coordinate_bits` is a required exact positive int. Before any
geometric arithmetic or source inspection, require both x/y Fractions to
have numerator and denominator `bit_length()` no larger than that budget;
the numerator's sign does not change its bit length. An over-budget point
returns `incomplete/resource-limit` with no bounds after a cancellation
check. Non-Fraction point inputs raise `INVALID_GEOMETRY`; malformed budget
raises `INVALID_SETTING`. This explicit limit avoids treating arbitrary
precision caller input as bounded merely because source coordinates are
finite binary64.
Cell reuses the existing finite-binary64 axis-aligned positive `SupportCellXY`
rectangle and its four closed corners. Both APIs require exact tuple/policy
and callable cancellation. Callback must return exact bool; exceptions
propagate. Reject malformed policy/callback as `INVALID_SETTING` and malformed
geometry as `INVALID_GEOMETRY`. Before source elements are inspected, compare
tuple length to `policy.max_source_segments`; overflow returns
`incomplete/resource-limit` with no bounds. Empty source tuple is valid and
returns `absent/disjoint`. Check cancellation before expected returns.

## Bounds and coverage semantics

Normalize existing finite segment coordinates to exact `Fraction(float(x))`
once. For each source, call the current `_segment_top_bounds` with four cell
corners, or with the same point repeated as its corner tuple for the point
query; no bead equation is reimplemented. Its horizontal-segment special case
is the ADR-0048 top formula: for path parameter `t` in closed `[0,1]`,
radius `r=h/2`, flat half-width `a=(w-h)/2`, lateral distance `u`, top is Z
when `u<=a`, and `Z-r+sqrt(r²-(u-a)²)` when `a<u<=a+r`. Outside the closed
flat-cap rectangle top is absent. Existing `_sqrt_bounds` outward-encloses
irrational roots as Fractions at the chosen precision. Endpoints/side contacts
are included; zero top contribution must not be lost.

At a point, `_segment_top_bounds` returns either `None` (outside the exact
closed footprint) or lower/upper top bounds, because repeated corners imply
full point coverage. The union top is the maximum across present sources, so
take max of lower bounds and max of upper bounds. Return
`full-bounded/covered-point` with both finite ordered Fractions, or
`absent/disjoint` if none is present. At a cell, a source's `None` means it
provably does not intersect the closed rectangle. Among intersecting sources,
take max of every conservative top upper bound. A conservative **whole-cell**
top lower bound exists when at least one source alone fully covers all four
corners (affine path parameter and lateral cross-coordinate then cover the
entire convex rectangle); take the max lower bound of such sources. Return
`full-bounded/one-segment-covers-cell` with lower/upper. If some source may
intersect but none alone covers, return `unresolved-partial/union-coverage-
unproven` with upper bound and no lower bound; do not infer full coverage
from disjoint or overlapping partial sources. If every source is provably
disjoint, return `absent/disjoint` with neither bound. A cell may contain
covered and uncovered points despite a finite upper bound.

The existing helper's projection interval and lateral-distance interval are
independent conservative extrema. For a partial cell they may overestimate
the actual top or return overlap where none exists; they cannot justify a
lower bound. For a fully covered cell, their independent minima are valid
lower bounds. The existing square-root bounds are outward, so finite
precision widens intervals but never claims exact irrational top. This API
does not label a cell's worst target residual or give a closest-surface
correspondence.

## Result, budget and cancellation

`NominalStructuralTopBounds` is frozen/slotted. Exact state/reason pairs:
`absent/disjoint`, `full-bounded/covered-point`,
`full-bounded/one-segment-covers-cell`,
`unresolved-partial/union-coverage-unproven`,
`incomplete/resource-limit`, `incomplete/cancelled`.
Full-bounded has exact Fraction lower<=upper; unresolved-partial has only an
exact Fraction upper; absent/incomplete have no bounds. Input validation errors
are exceptions and no partial result is returned. Return `cancelled` with no
bounds if callback becomes true before publication, including after a resource
preflight. No source list or result from another call is trusted as evidence.

At most `N=policy.max_source_segments` sources are visited. For each source,
the existing helper evaluates four rectangle corners (one repeated point for
point API), bounded rational arithmetic and a fixed number of integer-square-
root enclosure calls at `policy.sqrt_fraction_bits`. Cancellation is checked
before and after each `_segment_top_bounds` invocation, before each expected
return and after DTO construction. The current helper has no cancellation
hook, so this contract does **not** claim interruption inside its fixed
four-corner arithmetic. The exact point-coordinate bit preflight above,
finite-binary64 segment/cell coordinates and the maximum 4096-bit root
precision bound each invocation; repository review must confirm the resulting
operand-size bound before implementation. No hidden refinement loop, section
query, mesh query, filesystem, Orca or printer call.

## Independent acceptance cases and non-claims

- Interior center, exact outer side, flat axial endpoint and a point just
  outside each boundary for a horizontal segment; test `w=h` circular case.
- Two overlapping segments: union top uses max, not sum or average. Reverse
  input order and source IDs without changing the geometric result.
- Full cell under one segment: finite lower/upper. Two partial segments whose
  union might cover the cell: unresolved-partial, never fabricated lower.
- Distant segment: absent. Partial overlap: finite upper, missing lower.
- Irrational arc-height point: exact rational enclosure, tightened by larger
  `sqrt_fraction_bits`, never an unrounded float presented as proof.
- Count exactly at budget; one above budget. Cancellation before/within source
  traversal and just before return; point numerator/denominator exactly at
  bit limit and one bit over; malformed source/policy/callback. Cancellation
  during a single helper invocation is observed only after that bounded
  invocation completes.
- Existing `query_nominal_support_cell` outputs and support chronology behavior
  remain unchanged.

This is a nominal **top** query only. It neither proves actual material
deposition nor evaluates a source mesh, exposed surface, candidate improvement,
ADR-0047 bidirectional error, ADR-0060 affected domain, support metric,
collision, Plan, safe G-code output or native Orca Preview.
