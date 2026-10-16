# Draft: convex-section unscored chord proposals

Status: DRAFT_SPEC. Not implementation authority; no canonical revision is changed.

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
    chord_positions_mm: tuple[float, ...], policy: MeshSectionPolicy,
    max_positions: int, max_vertices: int, max_triangles: int,
    max_mesh_pair_checks: int, max_section_segments: int,
    max_section_pair_checks: int, max_ray_directions: int,
    cancelled: Callable[[], bool]) -> ConvexChordProposalSet
```

All DTOs immutable/frozen/slotted, no defaults. Axis is exact string X or Y.
For X chords, positions are Y coordinates; for Y chords, positions are X.
Require finite binary64 Z, positive finite width/trim, exact mesh/policy/tuple
types, exact positive integer limits and callable exact-bool cancellation.
Geometry/input errors use INVALID_GEOMETRY; policy/limits/callback errors use
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
Do not interpret the positive public MeshSectionPolicy tolerances as zero:
selection of a new explicit proposal algorithm version needs canonical review.

For each CCW edge use its exact interior halfplane a*x+b*y+c>=0. At position s,
an X-directed chord of width w must satisfy, for every edge,
`a*x+b*s+c-abs(b)*w/2>=0`; the Y-directed case is
`a*s+b*y+c-abs(a)*w/2>=0`. This is the minimum over the entire transverse segment,
not a center/corner sampling assumption. Clip the running-coordinate interval
against every inequality. Initialize with the finite section coordinate bounds;
zero coefficient with negative constant makes the interval empty. All arithmetic
and closed interval comparisons are exact Fraction operations.

No interval yields per-position rejected/empty-footprint. Otherwise trim both
ends along the running axis by end_trim_mm. If trimmed lower>=upper, yield
rejected/insufficient-span. A positive span yields ordered exact XY endpoints.
The entire rectangular sweep is inside the closed convex section by halfplane
linearity; this is not a 3D extrusion or surface-error proof.

Validate each positive-span centerline as strictly inside material, using the
same freshly embedded triangle tuple and the existing exact segment-contact and
endpoint-parity owners. Private helpers must accept exact Fraction endpoints;
do not round them through PrintPoint3. Contact produces per-position
rejected/centerline-contact; consistently outside produces rejected/centerline-outside.
Only strictly-inside produces proposed/unscored with both endpoints. Ray exhaustion
or inconsistent classification fails the entire output incomplete with no rows.

## Results, limits and unresolved decisions

Completed set: complete/proposals-evaluated, one row per sorted input position,
possibly all rejected. Proposed rows have exact ordered endpoints; rejected rows
have None endpoints. Global rejection/unknown/cancellation returns an empty tuple,
never a partially usable set. Proposed global rejection reasons include inherited
mesh/section failures, empty-section and nonconvex-section; incomplete reasons
include resource-limit, cancelled, ray-directions-exhausted and
classification-inconsistent. Constructors enforce exact types/matrices only.

Check cancellation before mesh/section phases, every position, each clipping
edge, each contact/parity iteration and final return. Existing mesh pair and
section budgets apply once; max_positions bounds repeated O(F) contact and
O(F*max_ray_directions) endpoint work per chord. No additional hidden retries.

Canonical review must close the proposal algorithm/version selector, precise
global reason matrix, ownership of exact rational private material queries and
how later exposed-band/scoring owners consume these unscored proposals. This
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
