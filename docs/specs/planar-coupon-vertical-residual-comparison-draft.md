# Restricted vertical residual on one planar coupon rectangle

Status: SPEC_VALIDATED for this bounded research-only comparison.
Independent specification and read-only repository review against MAIN
`9fb2605` returned `validated` after closing certificate version/budgets,
resource-versus-coverage outcomes, deterministic leaf/query bounds and the
pre-certificate exact-rectangle coordinate-bit preflight. Manifest:
`docs/AUDIT_REVISION_2026-10-16.json`, Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`. This status grants no
printability, same-slice Orca identity or G-code implementation authority.

Canonical basis: `docs/SPECIFICATION.md` at
`docs/AUDIT_REVISION_2026-10-16.json` (manifest Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`). This handoff depends on
the separately `SPEC_VALIDATED` planar-cell top certificate and exact nominal
bead top kernel. ADR-0048 governs bead union; ADR-0047 and ADR-0060 remain
the full surface-error and influence-domain authorities. The number here is
only a **restricted maximum vertical top residual on one rectangle**, never
their `E_max` or a printable tolerance result.

## Question, identity and proposed API

Given one closed XY rectangle inside a source mesh's proven planar top and
one explicit tuple of structural nominal segments, does appending a supplied
tuple of candidate segments strictly reduce the maximum absolute vertical
distance between that plane and the nominal union top **over the same entire
rectangle**? The baseline-plus-candidate query must reuse the exact baseline
segment tuple, not reconstruct a second baseline. A source-mesh identifier
and baseline-slice identifier are copied into the result for traceability;
they are caller assertions, not proof of actual Orca slice identity.

```python
# adaptive_subedge/domain/coupon_residual.py
@dataclass(frozen=True, slots=True)
class VerticalResidualInterval:
    lower_mm: Fraction
    upper_mm: Fraction

@dataclass(frozen=True, slots=True)
class CouponVerticalComparison:
    state: str
    reason: str
    source_mesh_id: str
    baseline_slice_id: str
    rectangle: ExactTopCellXY | None
    target_plane_abc: tuple[Fraction, Fraction, Fraction] | None
    baseline_max_residual: VerticalResidualInterval | None
    augmented_max_residual: VerticalResidualInterval | None
    leaf_count: int

# adaptive_subedge/engine/coupon_residual.py
def compare_planar_coupon_vertical_residual(
    mesh: IndexedTriangleMesh, rectangle: ExactTopCellXY,
    structural_sources: tuple[ExactNominalTopSegment, ...],
    candidate_sources: tuple[ExactNominalTopSegment, ...], *,
    source_mesh_id: str, baseline_slice_id: str,
    max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
    max_cell_vertices: int, max_centroid_tests: int,
    max_facet_clip_tests: int,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    max_refinement_depth: int, max_leaf_cells: int,
    cancelled: Callable[[], bool],
) -> CouponVerticalComparison: ...
```

All DTOs frozen/slotted, exact reason/state/field matrices, no defaults.
Both identity strings are nonblank but cannot authenticate Orca, transform,
profile or G-code provenance. A future same-plan integration must establish
that external binding separately. Structural/candidate source kinds must
match their respective tuples; IDs are unique across both. Require at least
one candidate. Every candidate has constant Z and width>=height>0 through
the exact kernel's DTO. No Settings or printer-specific bounds are inferred.
Preflight exact positive integer budgets (except `max_refinement_depth`,
which may be zero), exact DTO/callback types and source counts before source
element scans. Before constructing the certificate cell or doing any
mesh/facet clipping, check the numerator and denominator `bit_length()` of
**each** of the four exact Fraction rectangle coordinates against
`max_coordinate_bits`. An over-budget rectangle returns
`incomplete/resource-limit` with no rectangle/plane/interval result, after
checking cancellation so `incomplete/cancelled` takes precedence. The
subsequent quadtree midpoint coordinates face the same bit budget through
the exact top kernel; its resource failure propagates immediately.
Callback returns exact bool; exceptions propagate.

## Same-call proof and finite estimator

1. Convert the exact rectangle into the strict CCW canonical four-corner
   polygon `(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)`. Invoke
   `certify_planar_cell_top` on the **same mesh in this call** with its own
   explicit `max_cell_vertices`, centroid, facet-clip, mesh and pair budgets.
   Pass the internally fixed `algorithm_version="planar_cell_top_v1"`;
   callers cannot select a different top-certificate algorithm in this API.
   Do not accept a caller-supplied certificate as proof.
   A failed/rejected/incomplete certificate publishes no intervals. Its
   successful exact target plane is `M(x,y)=a*x+b*y+c` throughout the closed
   rectangle. The certificate does not establish section nesting or Orca
   source-slice correspondence.
2. Evaluate two unions on one shared deterministic quadtree partition:
   baseline `B=structural_sources` and augmented
   `A=structural_sources + candidate_sources`. Every point/cell query uses
   the validated exact nominal top kernel and the same source/bit/sqrt
   budgets. The kernel's maximum rule includes candidate end caps and
   multiple lines; do not add bead heights or choose the lower top.
3. For any closed leaf cell L, query both union top bounds. A leaf is
   certified covered only when **both** return `full-bounded`; a partial
   or absent result is unresolved for coverage. `incomplete/resource-limit`
   (including midpoint bit growth beyond `max_coordinate_bits`) or
   `incomplete/cancelled` from either top query propagates immediately as
   the same comparison incomplete reason, with no further refinement.
   A finite upper envelope
   without whole-cell lower/coverage never bounds the whole-cell residual.
   Refine unresolved leaves within the common depth/leaf limits; if any
   remain at the limit, return `incomplete/coverage-unresolved` with no
   public residual intervals or improvement label.
4. On a covered leaf L, target extrema are the exact min/max of M at its four
   corners. If top across L lies in `[Tlo,Thi]`, a valid upper bound on
   `max_L |M-T|` is the largest of the four endpoint distances
   `|Mmin-Tlo|`, `|Mmin-Thi|`, `|Mmax-Tlo|`, `|Mmax-Thi|`. For a lower bound,
   sample the four corners and center using exact point queries. Each point
   top interval `[plo,phi]` yields the certified residual lower bound
   `distance(M(point),[plo,phi])`, zero when M is inside. The maximum over
   five samples is that leaf's lower bound `L_B(L)` or `L_A(L)`.
   The cell formula is that leaf's upper bound `U_B(L)` or `U_A(L)`.
   A point-query `incomplete` propagates immediately; an absent point makes
   the leaf coverage-unresolved. No sampled
   maximum is treated as a whole-cell upper bound.
5. For each union separately, global residual lower is
   `max_leaf L_B(L)` / `max_leaf L_A(L)`; global upper is
   `max_leaf U_B(L)` / `max_leaf U_A(L)` over the **current leaves**, not
   discarded ancestors. An impossible lower>upper is an internal
   `INVALID_GEOMETRY` failure, never a favorable comparison.
   Use the **same leaves and samples** for B/A. Refine the leaf with greatest
   priority width `max(U_B(L)-L_B(L), U_A(L)-L_A(L))` across the two unions;
   coverage-unresolved leaves take priority over all bounded leaves, then
   ties by exact `(x_min,y_min,x_max,y_max)` ascending. Split at
   exact rational midpoints into four children in fixed SW, SE, NW, NE
   order. `max_leaf_cells` bounds the number of live leaves and
   `max_refinement_depth` bounds each root-to-leaf path. No adaptive random
   probes, float coordinates, hidden recursion or unbounded retry. Cache each
   node's query results and never requery an unchanged leaf. With
   `s <= floor((max_leaf_cells-1)/3)` splits, at most `N=1+4s` nodes are ever
   created. Depth may reduce this count; there is no need to evaluate a
   potentially huge `4**max_refinement_depth` budget expression. Each node
   uses at most two cell and ten point top queries, so total top queries
   are at most `12*N`, plus at most one planar certificate call (zero if
   preflight stops first). Every top query visits at most `max_sources`
   segments.

After every refinement, test the comparison only if all current leaves are
covered. Report `complete/certified-reduction` only when
`A.upper_mm < B.lower_mm`. Report `complete/certified-nonreduction` only when
`A.lower_mm >= B.upper_mm`; equality is no strict improvement. If neither
disjoint relation is certified, keep refining until a depth/leaf budget
prevents the next deterministic split; then return
`complete/interval-overlap` with both honest intervals and no improvement
claim. This result does not suggest whether more refinement might resolve
the overlap. Zero-depth evaluation is valid when the initial rectangle is
fully covered. A false early comparison before coverage of every leaf is
forbidden.

## Failure and cancellation contract

Invalid geometry/identities raise `INVALID_GEOMETRY`; invalid budgets/callback
raise `INVALID_SETTING`. `incomplete` reasons are `cancelled`,
`resource-limit`, `coverage-unresolved`; `rejected` reason is
`target-unresolved`. `complete` reasons are exactly
`certified-reduction`, `certified-nonreduction`, `interval-overlap`.
No incomplete/rejected result carries rectangle/plane/intervals.
`leaf_count` is an exact nonnegative int: zero
before the root is created, otherwise the number of live leaves at the
return boundary for incomplete/rejected/complete results. Completed
comparisons require positive leaf_count, the exact input rectangle,
the certified exact target plane and both ordered residual
intervals; incomplete/rejected results require both intervals None.
Map certificate `incomplete/cancelled` to
comparison `incomplete/cancelled` and `incomplete/resource-limit` to
`incomplete/resource-limit`. Map each certificate rejected reason—
`empty-mesh`, `unused-vertex`, `degenerate-bounds`, `degenerate-triangle`,
`duplicate-triangle`, `nonmanifold-edge`, `inconsistent-winding`,
`disconnected-shell`, `nonmanifold-vertex`, `zero-signed-volume`,
`self-intersection`, `no-top-facing-facet`, `ambiguous-top-plane`,
`above-top-plane`, `uncovered-top`—to `rejected/target-unresolved`.
No other certificate state/reason is accepted. Map any top-query
`incomplete/cancelled` or `incomplete/resource-limit` to the same comparison
incomplete reason immediately, including at points. Only an `absent` or
`unresolved-partial` top outcome may lead to `coverage-unresolved` after
refinement is exhausted. Cancellation is checked before each phase, before/after
every certificate/top query, each leaf and sample, every refinement, and
before/after DTO publication; it overrides expected failure and publishes
no partial result. Query exceptions propagate; no unknown is converted to
zero residual. Budget exhaustion is not a physical reject.

## Acceptance and limits

- A planar closed coupon with one structural line, then one or multiple
  exact-Fraction candidate lines, has intervals enclosing independently
  computed analytical point and cell extrema. Reordering source tuples
  leaves the metric invariant; source kind/ID rules remain enforced.
- A candidate that raises the top into the target plane over the whole
  rectangle yields disjoint intervals and certified reduction. A candidate
  that creates overbuild yields certified nonreduction when intervals
  separate. Equality is not reduction.
- A narrow uncovered strip, flat end-cap gap, or two partial lines whose
  union coverage cannot be proven by the kernel returns coverage-unresolved
  at the refinement limit, not a misleading score.
- Zero-depth and leaf-count boundaries, exact midpoint determinism,
  irrational cap enclosure at differing sqrt precision, and cancellation
  after a prior leaf all preserve fail-closed result shape.
- A rectangle coordinate numerator/denominator exactly at the bit limit
  proceeds to certificate validation; one bit over returns resource-limit
  **before** certificate/clipping. Cancellation at that preflight wins.
- Nonplanar/recessed target, boundary-only higher facet, self-intersecting
  mesh, malformed identity/budgets/source and candidate with width<height
  never publish a reduction.

This is a restricted **vertical top** comparison over an explicitly supplied
rectangle. It omits predicted-side/underfill normal correspondence from
ADR-0047, neighbor/side influence closure from ADR-0060, chronological
support, collision, clearance, target-wide search, Plan ranking, G-code
reconstruction and Orca Preview. It cannot certify a printable improvement
or safe G-code output, even when it reports `certified-reduction`.
