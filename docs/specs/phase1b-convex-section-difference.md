# Exact two-height convex-section difference

Status: SPEC_READY for independent repository review; not yet implementation
authority.

Authority: accepted ADR-0005 exposed-band and nesting research scope, reusing
ADR-0030 embedding and ADR-0059 exact symbolic section machinery. This handoff
adds no Plan, physical/G-code gate, dependency owner or Orca hook; the accepted
ADRs need no change. An independent specification review closed cyclic clipping,
strict cell validation, work bounds and failure precedence. Repository review
is pending. Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`

This closes a planar prerequisite for exposed-band work,
not a SurfaceBandV2 constructor or complete Phase1B implementation.

## Closed proposed API

```python
# adaptive_subedge/domain/section_difference.py
@dataclass(frozen=True, slots=True)
class ConvexSectionDifference:
    state: str
    reason: str
    lower_z_mm: Fraction
    upper_z_mm: Fraction
    lower_section: MeshSectionLoop | None
    upper_section: MeshSectionLoop | None
    cells_xy_mm: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    area_mm2: Fraction | None

# adaptive_subedge/engine/section_difference.py
def derive_convex_section_difference(
    mesh: IndexedTriangleMesh, lower_z_mm: float, upper_z_mm: float, *,
    algorithm_version: str,
    max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
    max_section_segments: int, max_section_pair_checks: int,
    max_clip_vertex_tests: int,
    cancelled: Callable[[], bool],
) -> ConvexSectionDifference: ...
```

Every argument is required. Version is `convex_section_difference_v1`.
Use the existing proposal finite-binary64 scalar policy, excluding bool:
normalize int/float inputs through float then Fraction, require lower_z<upper_z.
Output Z and every coordinate/area are exact Fraction, without float conversion.
Exact mesh type, callable cancellation, positive exact-int budgets and supported
version are checked before work. Invalid geometry/scalars/result shapes raise
INVALID_GEOMETRY; invalid limits/version/cancellation callable raise
INVALID_SETTING. Callback must return exact bool; its exceptions propagate.

## Geometry, ownership and determinism

1. Fresh `_embedding` validates once and supplies triangles/topology. Never accept
   caller-created embedding proof or section DTO as computational authority.
2. Call existing private `_section` twice, first lower then upper, with explicit
   zero predicate/coplanar/join tolerances and unchanged section budgets for each
   call. This proposed version authorizes its exact-symbolic route only; public
   single-plane policy remains unchanged. Require two nonempty simple CCW loops.
   Coplanar facets, ambiguous topology and multiple loops fail closed as usual.
3. Convert the loops to planar polygon sequences while retaining original
   MeshSectionLoop objects in successful output. Reject either nonconvex polygon
   using exact consecutive turns <0. Collinear forward vertices are allowed.
4. Canonicalize working polygons cyclically, including triples spanning the
   last/first boundary: remove consecutive duplicates and a collinear middle
   vertex only when it lies strictly between its two neighbors. Iterate until
   stable, then rotate each positive-area CCW polygon to its lexicographically
   smallest (x,y). Backtracking collinear triples reject instead of being
   silently removed. No duplicate closing endpoint.
   No hull, epsilon, snapping or winding repair. Section validation already
   establishes simplicity; later clipping preserves convexity.
5. Prove upper containment: every canonical upper vertex must satisfy every
   closed lower halfplane `a*x+b*y+c>=0`, where a=-dy,b=dx,c=dy*x0-dx*y0.
   Any negative value rejects `non-nested-sections`. Convexity makes this a whole
   polygon test, not sampled boundary evidence. Boundary equality is allowed.
6. Let remaining=L. Visit canonical upper edges in their canonical cyclic order.
   Split remaining by the edge's exact affine halfplane: emit its positive-area
   outside piece (value<=0), retain its inside piece (value>=0). Intersection
   points use exact rational affine interpolation of opposite-sign endpoints.
   ON endpoints are preserved once; zero-area pieces are discarded. Canonicalize
   each emitted piece as above. Return pieces in edge traversal order, not area
   order. Stop splitting if remaining becomes empty. Never emit remaining U.

Cells represent **the closure of L minus U**, discarding zero-area remnants.
Closed cells may share edges/vertices; their interiors are pairwise disjoint.
They are not literal disjoint closed sets. Their union can include U's boundary,
but cannot include its interior. This avoids falsely representing the open
boundary of set difference with closed polygon DTOs. Equal sections yield no
cells and area zero, not a degenerate polygon. Exact summed cell area must equal
area(L)-area(U); a failed internal consistency check raises INVALID_GEOMETRY and
must not publish a result. Use shoelace/2, never floating-point area.

Determinism applies to geometric cells for equivalent loop rotations and source
triangle permutations; source ID metadata in retained sections may differ.

## Result matrix and resource/cancellation contract

`complete/difference-derived`: both source sections, nonempty canonical cells,
strictly positive area. `complete/empty-difference`: both source sections,
cells=(), area=Fraction(0). Every other disposition has sections=None, cells=(),
area=None, never partially useful geometry. Preserve normalized Z in all states.

Rejected reasons: empty-mesh, unused-vertex, degenerate-bounds,
degenerate-triangle, duplicate-triangle, nonmanifold-edge, inconsistent-winding,
disconnected-shell, nonmanifold-vertex, zero-signed-volume, self-intersection,
coplanar-facet, ambiguous-join, non-simple-graph, multiple-loops, zero-area,
empty-section, nonconvex-section, non-nested-sections.
Incomplete reasons: cancelled, resource-limit. Empty section at either Z maps
to rejected/empty-section. The exact route cannot emit predicate-uncertain.

DTO checks exact types, state/reason matrix, lower<upper, each retained section
Z matching its corresponding input Z, and
completed cell shapes: exact tuples, >=3 pairwise-unique points, positive area,
no collinear/repeated closing vertex, lexicographic first vertex. For every
directed cell edge, every nonincident vertex must lie strictly in its inside
halfplane. Also reject intersections between nonadjacent edges. These exact
checks reject self-crossing star sequences that have positive local turns.
It checks area equals summed cell area; construction alone is no nesting,
embedding or correct-difference proof. Cross-cell overlap remains engine-owned.

Embedding budgets apply once; section budgets apply independently to each
section call. A lower-section failure stops before the upper call; exactly two
calls occur only when the lower section succeeds. After canonicalization let
n=#lower vertices and
m=#upper vertices. Preflight the conservative bound `2*n*m + m*m` against
max_clip_vertex_tests before containment/clipping; exceeding it returns
incomplete/resource-limit without partial polygons. This covers n*m containment
evaluations and at most m*(n+m) remaining-polygon vertex evaluations. Compute
each vertex's plane value once per split and reuse it for both sides. Clipping
creates at most m positive cells, each at most n+m vertices; these sizes also
bound canonicalization/output work. The named budget counts plane evaluations,
not DTO constructor or canonicalization operations. Those have a separate
deterministic worst-case bound O(n^2 + m^2 + m*(n+m)^2), bounded by the two
section-segment limits. No hidden retries or extra section queries.

Check cancellation before each expensive phase, at every embedding/section
checkpoint, every polygon traversal vertex and halfplane test/split vertex,
and immediately before every expected return including propagation/conversion
of a lower or upper section failure, rejection and resource failure.
Cancellation overrides earlier expected failures and removes geometry.
Unexpected errors propagate; no conversion to a successful empty difference.

## Explicit non-claims and next integration boundary

Two-plane containment does not prove continuous nesting between the planes,
top-facing surface orientation throughout the interval, target exposed mesh
facets, support, finite-bead coverage/error, optimal widths, or physical safety.
A middle-height outward bulge may exist even when these two sections nest.
Call the result a two-height planar difference, never a certified exposed band.
No seam, candidate generation, Plan identity, G-code, native viewer, Settings
defaults, source-slice integration or Orca adapter changes are in this unit.
Existing exact-event stability proof has separate obligations and cannot be
silently inferred from two section calls. No new library dependency is needed.

## Independent acceptance cases

- Shrinking square prism/frustum: known lower/upper areas and exact difference;
  independently verify pairwise cell interior non-overlap and area conservation.
- Nested triangles with nonbinary rational intersections; no float round trip.
- Same sections: complete empty result. Shared edge/vertex: correct positive
  pieces with zero-area pieces omitted. Upper outward protrusion: rejection.
- Collinear section triangulation nodes: canonical geometric cells unchanged.
- Wraparound collinear/duplicate vertices canonicalize; backtracking rejects.
- Malformed star-polygon and nonconsecutive-duplicate cell DTOs reject.
- Rotated starting vertices and reordered mesh triangles: geometric cell equality.
- Concave lower or upper sections, horizontal facets and multiple loops reject.
- Exact preflight equality succeeds; one-less budget fails before clipping.
- Cancellation during upper section, containment, splitting and final return
  publishes neither sections nor cells; callback exceptions propagate.
- Middle-height bulge fixture documents that this API still checks only the two
  requested planes and must not be interpreted as continuous nesting evidence.
- Existing topology, section, material and chord API behavior stays unchanged.
