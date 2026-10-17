# Exact planar top coverage of one convex XY cell

Status: SPEC_VALIDATED for this bounded research-only top certificate.
Independent specification review closed oriented facet selection, exact clip
budgets, degenerate boundary contacts, cancellation and hostile convex-cell
validation. Read-only repository review against MAIN `c2110d5` returned
`validated`: the current `_embedding` supplies exact input-winding triangles
and `topology.oriented_triangles` supplies the outward orientation; the
proposed domain/engine owners preserve existing dependency boundaries.
Manifest: `docs/AUDIT_REVISION_2026-10-16.json`, Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`.

Canonical basis: `docs/SPECIFICATION.md` at
`docs/AUDIT_REVISION_2026-10-16.json` (manifest Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`). ADR-0005 owns exposed
band meaning, ADR-0030 owns oriented embedded mesh evidence, and ADR-0059 owns
section events. This handoff adds only a bounded exact top-graph prerequisite;
it does not override these accepted decisions. It does not consume or amend
the existing section-difference result, which proves two-height planar area
only. A caller may pass one of its cells as input, but that DTO is not proof
of this cell's origin, continuous nesting, or exposure.

## Closed proposed interface

```python
# adaptive_subedge/domain/planar_cell_top.py
@dataclass(frozen=True, slots=True)
class PlanarCellTopCoverage:
    state: str
    reason: str
    cell_xy_mm: tuple[tuple[Fraction, Fraction], ...] | None
    plane_a: Fraction | None
    plane_b: Fraction | None
    plane_c_mm: Fraction | None
    area_mm2: Fraction | None

# adaptive_subedge/engine/planar_cell_top.py
def certify_planar_cell_top(
    mesh: IndexedTriangleMesh,
    cell_xy_mm: tuple[tuple[Fraction, Fraction], ...], *,
    algorithm_version: str,
    max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
    max_cell_vertices: int, max_centroid_tests: int,
    max_facet_clip_tests: int,
    cancelled: Callable[[], bool],
) -> PlanarCellTopCoverage: ...
```

Version is exactly `planar_cell_top_v1`. All arguments required. Cell input
is exact Fraction coordinates (bool/float excluded), three or more vertices,
CCW, strictly convex with positive exact shoelace area, no collinear or
duplicate/closing vertices, and lexicographically smallest vertex first.
Preflight `k <= max_cell_vertices` before examining elements. Then require
pairwise-distinct exact XY points. For each directed edge, every nonincident
vertex must lie **strictly** in its interior halfplane; check cyclic edges,
including the last-to-first wrap. Reject every intersection of nonadjacent
closed edges, including endpoint touch. These exact all-pairs checks exclude
self-crossing star orders that can have positive local turns. The cell
validation costs O(k²) exact predicates after the k preflight and checks
cancellation at each edge, vertex and edge-pair checkpoint. This follows the
existing `ConvexSectionDifference` cell DTO precedent, without accepting that
DTO as proof for this call. No normalization, hull, epsilon, snapping or
winding repair. Malformed mesh/cell
raises `INVALID_GEOMETRY`; malformed version/budgets/callback raises
`INVALID_SETTING`. Budgets are exact positive ints. Callback returns exact
bool; callback exceptions propagate. DTO validates exact types, reason/state
matrix and geometry-null-on-failure, but construction is not a coverage proof.

## Exact proof procedure

1. Check cancellation, then run one fresh `_embedding` validation on the
   supplied mesh using the existing topology and self-intersection budgets.
   Use `topology.oriented_triangles` to index the returned exact
   binary64-to-Fraction vertex coordinates. The returned raw triangle tuple
   follows input order and is not the outward-normal authority. Never trust
   input face winding or a caller-created embedding receipt.
2. Let `C` be the closed convex input cell and `p` its exact vertex average,
   strictly inside C. **First pass:** test p directly against the closed XY
   triangle of every oriented facet with three exact edge-side predicates;
   no cell clipping occurs in this pass. Among upward-facing (`normal_z > 0`)
   nonvertical facets containing p, choose the highest exact facet height.
   If none exists, reject `no-top-facing-facet`. If tied highest facets give
   different planes, reject `ambiguous-top-plane`. The chosen plane is
   `z=a*x+b*y+c`, with exact rational coefficients. A horizontal or sloped
   upward facet is allowed; vertical facets cannot select the plane.
3. **Second pass:** clip each oriented 3D facet **once** against the vertical
   prism over C using exact XY halfplanes. Retain zero-area XY point/segment
   contacts and reuse this clipped piece for both height and coverage tests.
   For **every** facet with nonempty projected intersection with C, compare
   its 3D height to the selected plane throughout that intersection. A
   facet's height difference is affine, so checking every exact clipped 3D
   vertex proves its maximum, including for a vertical facet. Merely testing
   original vertices misses a vertical facet whose original vertices lie
   outside C. If any facet
   reaches strictly above the plane at any point of the closed cell, reject
   `above-top-plane`, **including boundary-only contact**. Facets below may
   remain; they cannot establish target coverage. This deliberately rejects
   some harmless side-boundary contacts rather than certify a false closed
   region.
4. For each upward-facing facet whose plane is exactly the selected plane,
   sum the exact positive XY area of its already-clipped piece; all pieces
   are subsets of C. No second clipping pass is permitted.
   The fresh embedding rejects overlapping coplanar facet interiors except
   valid shared edges. Thus equality of this sum and area(C) proves their
   closed union covers all of C, including its boundary: a missing open
   interior has positive area and a finite closed union covering the interior
   cannot omit boundary limit points. A smaller sum rejects `uncovered-top`;
   a larger sum is `INVALID_GEOMETRY` internal inconsistency, never success.
   Do not count lower upward facets, downward facets or zero-area contacts as
   coverage.

Return `complete/planar-top-covered` with the canonical cell, plane and exact
area only after all checks. This proves the oriented mesh has one selected
top-facing planar graph across this closed XY cell under the strict test
above. It does **not** prove the cell is a real exposed band, continuous
Z-nesting, or an Orca sliced surface. Equivalent triangle permutations yield
the same plane and area; face IDs are not part of the output.

## Resource, cancellation and result matrix

Let F be facet count and k be cell vertex count. After normal mesh/cell count
preflights, require `3*F <= max_centroid_tests` before the direct centroid
pass, and `F*k*(k+3) <= max_facet_clip_tests` before the clip pass. The first
budget counts three exact XY edge-side predicates per facet, including faces
that cannot select the target plane. One exact convex prism clip against k
edges has at most k+3 vertices per step and at most k*(k+3)
vertex-halfplane evaluations per facet (a conservative bound). The second
budget counts only those clip predicates. Process each facet once in the
second pass, retaining only one clipped piece at a time plus exact area and
chosen plane. Degenerate XY projections, including a vertical triangle,
use the same 3D prism clip and budget. No result is returned from a resource
preflight without a final cancellation check. Do not
perform hidden mesh/section queries or unbounded retries. Check cancellation
before each phase, each facet, each edge and vertex test, during result
construction, and immediately before every expected return. Cancellation
overrides an earlier expected rejection/resource stop and publishes no plane.

`incomplete`: `cancelled`, `resource-limit`.
`rejected`: the existing `_embedding` reasons (`empty-mesh`, `unused-vertex`,
`degenerate-bounds`, `degenerate-triangle`, `duplicate-triangle`,
`nonmanifold-edge`, `inconsistent-winding`, `disconnected-shell`,
`nonmanifold-vertex`, `zero-signed-volume`, `self-intersection`) plus
`no-top-facing-facet`, `ambiguous-top-plane`, `above-top-plane`,
`uncovered-top`.
Every incomplete/rejected result has `cell_xy_mm=None`, all plane fields
None, and `area_mm2=None`; no partial geometry is public. Unexpected errors
propagate. Exact input validation errors remain exceptions, not dispositions.

## Independent acceptance cases

- Triangulated sloped top of a closed convex wedge and triangulated horizontal
  top: exact a/b/c and area; triangle permutation leaves output unchanged.
- Two coplanar top facets share an edge through p; tie resolves to the same
  plane. Tessellation vertices on the cell boundary preserve closed coverage.
- A separately valid **closed-manifold** solid with a recessed pocket has a
  cell that spans the top plateau and pocket while p stays on the plateau:
  reject uncovered-top. A cell whose p falls into the pocket may instead
  select the lower plane and reject above-top-plane; neither succeeds.
- Higher nonvertical roof and vertical side/overhang touching **only** a cell
  edge or vertex: reject above-top-plane, not a boundary-tolerant success.
- Bottom and lower upward surfaces beneath a fully covered top do not enter
  its coverage sum; crossed/higher surfaces fail.
- Each centroid/clip budget exactly at its bound succeeds; one-less gives
  resource-limit. Cancellation during clipping, before a returned embedding
  failure, and before final return publishes no geometry.
- Malformed/nonconvex/collinear cell, bool limit, non-bool cancellation and
  degenerate vertical projection exercise their explicit failure paths.

No candidate placement, line-width partition, finite-bead score, support,
clearance, Plan identity, G-code mutation or native Orca comparison is in
scope. Separate validated work must establish those gates before claiming
improvement or physical safety.
