# Draft: convex-section unscored chord proposals

Status: SUPERSEDED historical draft. The adopted contract is ADR-0005 Closed
unscored convex chord proposal primitive; use phase1b-convex-chord-proposals.md
for implementation. This draft remains non-authoritative.

## Purpose and exclusions

Propose deterministic naturally open centerlines inside a convex mesh section.
ADR-0005 still requires exposed-band construction and finite-bead scoring.
This draft does not establish exposure, support, effective height, full bead-solid
containment, clearance, optimality, Plan feasibility or physical/G-code authority.
It checks a rectangular transverse footprint at the supplied Z only.

## Proposed closed API

```python
ChordProposal(position_mm: Fraction, state: str, reason: str,
    start_xy_mm: tuple[Fraction, Fraction] | None,
    end_xy_mm: tuple[Fraction, Fraction] | None)
ConvexChordProposalSet(state: str, reason: str,
    command_z_mm: Fraction, axis: str, width_mm: Fraction,
    proposals: tuple[ChordProposal, ...])

propose_convex_chords(mesh: IndexedTriangleMesh, command_z_mm: float, *,
    axis: str, width_mm: float, end_trim_mm: float,
    chord_positions_mm: tuple[float, ...], algorithm_version: str,
    max_positions: int, max_vertices: int, max_triangles: int,
    max_mesh_pair_checks: int, max_section_segments: int,
    max_section_pair_checks: int, max_ray_directions: int,
    cancelled: Callable[[], bool]) -> ConvexChordProposalSet
```

All DTOs immutable/frozen/slotted, no defaults. Axis is exact string X or Y.
For X chords, positions are Y coordinates; for Y chords, positions are X.
Require finite binary64 Z, positive finite width/trim, exact mesh/tuple
types, exact positive integer limits and callable exact-bool cancellation.
The exact string algorithm_version must be convex_axis_chords_v1. Unknown values
fail INVALID_SETTING. This research API does not consume MeshSectionPolicy:
its exact symbolic route is owned by this explicit proposed algorithm version,
while existing public section tolerances and stability policy remain unchanged.
Geometry/input errors use INVALID_GEOMETRY; version/limits/callback errors use
INVALID_SETTING. Exceptions from callbacks propagate. Normalize scalars through
float then Fraction. A finite scalar overflowing binary64 is invalid; subsequent
Fraction geometry never converts back to float and cannot silently overflow.

Validate top-level types/scalars/limits, invoke cancellation, then check tuple
length against max_positions before inspecting its elements or doing mesh work.
Oversized malformed tuples yield incomplete/resource-limit. Within budget every
position must satisfy finite binary64 validation. Reject empty position tuples
and duplicate normalized positions (including +0/-0 or int/float aliases) as
INVALID_GEOMETRY; do not silently deduplicate. Sort the validated positions by
exact normalized value. Unsorted caller input is allowed and output is ascending.

## Geometry proposal

Freshly validate embedding/topology once, then construct one exact symbolic
single-plane section in the same call using existing zero-tolerance internal
predicates and the explicit section budgets. No supplied proof result is trusted.
The section must be one simple CCW loop with positive area. Reject a nonconvex
loop by requiring every consecutive exact turn >=0; exact collinear forward
vertices are permitted with the existing simple positive-area requirement.
No convex-hull replacement.
The exact-symbolic route under this new version still needs canonical approval;
this draft cannot authorize changing existing public section behavior.

For each CCW edge use its exact interior halfplane a*x+b*y+c>=0. At position s,
an X-directed chord of width w must satisfy, for every edge,
`a*x+b*s+c-abs(b)*w/2>=0`; the Y-directed case is
`a*s+b*y+c-abs(a)*w/2>=0`. This is the minimum over the entire transverse segment,
not a center/corner sampling assumption. Clip the running-coordinate interval
against every inequality. Initialize with the finite section coordinate bounds;
zero coefficient with negative constant makes the interval empty. All arithmetic
and closed interval comparisons are exact Fraction operations.

An empty interval (lower>upper) yields per-position rejected/empty-footprint,
including during edge traversal. A singleton lower==upper is a closed nonempty
interval and proceeds to trimming, where it becomes insufficient-span.
Otherwise trim both
ends along the running axis by end_trim_mm. If trimmed lower>=upper, yield
rejected/insufficient-span. A positive span yields ordered exact XY endpoints.
The entire rectangular sweep is inside the closed convex section by halfplane
linearity; this is not a 3D extrusion or surface-error proof.

Validate each positive-span centerline as strictly inside material, using the
same freshly embedded triangle tuple and the existing exact segment-contact and
endpoint-parity owners. Private helpers must accept exact Fraction endpoints;
do not round them through PrintPoint3. Extract one private segment-classification
helper in the existing material owner, and delegate the existing public segment
API to it after that API's unchanged fresh validation and normalization. This
helper scans contact before endpoint parity and returns the existing closed
classification or typed stop. It must not accept a caller-created proof DTO.
Contact produces per-position
rejected/centerline-contact; consistently outside produces rejected/centerline-outside.
Only strictly-inside produces proposed/unscored with both endpoints. Ray exhaustion
or inconsistent classification fails the entire output incomplete with no rows.

## Results, limits and unresolved decisions

Completed set: complete/proposals-evaluated, one row per sorted input position,
possibly all rejected. Proposed rows have exact ordered endpoints; rejected rows
have None endpoints. Each endpoint is an exact tuple of two exact Fractions.
The enclosing set enforces strictly increasing running coordinates and fixed
coordinates equal to position_mm; positions are unique and ascending. Exact
string states/reasons and positive exact Fraction width are required.
Global rejection/unknown/cancellation returns an empty tuple, never a partially
usable set. The proposed closed global rejected reasons are empty-mesh,
unused-vertex, degenerate-bounds, degenerate-triangle, duplicate-triangle,
nonmanifold-edge, inconsistent-winding, disconnected-shell, nonmanifold-vertex,
zero-signed-volume, self-intersection, coplanar-facet, ambiguous-join,
non-simple-graph, multiple-loops, zero-area, empty-section, nonconvex-section.
Section empty/no-crossing maps to rejected/empty-section. Global incomplete
reasons are resource-limit, cancelled, ray-directions-exhausted and
classification-inconsistent. The exact route cannot emit predicate-uncertain.
Per-position rows are only proposed/unscored with endpoints, or rejected with
empty-footprint, insufficient-span, centerline-contact or centerline-outside
and None endpoints. Constructors validate shapes, not computation authority.

Check cancellation before mesh/section phases, every position, each clipping
edge, each contact/parity iteration and final return. Existing mesh pair and
section budgets apply once; max_positions bounds repeated O(F) contact and
O(F*max_ray_directions) endpoint work per chord. No additional hidden retries.

Independent draft review identified version selection, singleton intervals,
closed result matrices and shared rational material queries as gaps; the text
above now proposes explicit dispositions. Canonical review must approve these
choices and define how later exposed-band/scoring owners consume the proposals. This
draft neither adds Settings defaults nor registers Plan/identity authority.

Fixtures: X/Y axis parity, sloped convex edges, collinear edges, exact transverse
containment, boundary-aligned centerline rejection, empty/narrow trims, concave
rejection, normalized duplicate positions, malformed oversized tuple precedence,
deterministic ordering, rational endpoints not representable in binary64,
cancellation/unknown discarding all rows, and unchanged existing public APIs.
Analytic cases: in x>=0,y>=0,x+y<=1, X chord at y=1/4, width=1/4 and trim=1/8
has untrimmed x interval [0,5/8] and proposed interval [1/8,1/2]. In the unit
square, width=1/4 at y=1/16 has no admissible footprint despite an inside
centerline. Footprint boundary equality is allowed; centerline must be strictly inside.
