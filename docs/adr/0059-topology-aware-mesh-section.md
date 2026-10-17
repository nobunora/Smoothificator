# ADR-0059: Handle mesh-plane topology events directly instead of broad vertex-Z avoidance bands

Status: Accepted
Date: 2026-10-08

## Context

ADR-0053 introduced mesh_section_vertex_avoidance_mm bands around every source vertex Z / horizontal facet Z so candidate planes would avoid ambiguous triangle-plane cases.

That is safe but can become pathologically restrictive.

For a dense tessellated curved mesh, vertex Z values may be separated by very small increments. Positive-width avoidance bands around every vertex can overlap until most or all candidate-Z search space disappears.

This makes a higher-resolution mesh paradoxically less printable by the algorithm even when the underlying physical surface is smooth.

The actual issue is not being near any vertex Z; it is deterministic handling of plane-through-vertex events, plane-along-edge events, coplanar facet patches, and final G-code Z quantization.

## Decision

Printable v1 MUST use a deterministic topology-aware mesh-plane section policy.

Broad positive-width avoidance around every ordinary vertex Z is no longer the primary rule.

### Signed classification

For section plane Z = z0, each transformed vertex gets signed distance d = vertex_z - z0.

Use one versioned section_predicate_epsilon_mm only for numerical ON-plane classification. This epsilon is a numeric predicate tolerance, not a printable exclusion band.

### Canonical intersection identity

Section intersections are keyed by source topology identity where possible:
- interior edge crossing -> canonical source-edge id + interpolation parameter;
- exact source vertex event -> canonical source-vertex id;
- coplanar source edge -> canonical source-edge id.

Duplicate triangle contributions are merged by topology identity before geometric endpoint snapping.

### Vertex-on-plane handling

A source vertex classified ON is not automatically rejected.

Inspect the incident manifold fan:
- if incident non-coplanar faces exist on both sides of the plane, the vertex is a true section event;
- if all incident material lies on one side, it is a tangential touch and does not create a crossing branch by itself;
- ambiguous/inconsistent incident topology => analysis-only.

### Coplanar edge handling

For an edge whose two vertices are ON:
- include it as a section boundary only when adjacent non-coplanar material/topology proves it belongs to the solid-plane boundary;
- tangential duplicate edges are discarded deterministically;
- ambiguous coplanar-edge topology => non-injectable.

### Fully coplanar facet patches

A candidate plane numerically coincident with a connected horizontal/coplanar facet patch is a discrete topology event.

Initial v1 may reject that exact candidate plane under coplanar_section_epsilon_mm, but MUST NOT reject a broad arbitrary band around that Z merely because a horizontal facet exists.

Candidate generation may choose another Z normally.

### Section graph validation

After topology-aware segment generation:
- deduplicate canonical events;
- assemble deterministic graph components;
- printable target component must still satisfy the simple-loop contract: degree 2, one simple closed outer loop, no hole, no branch, no self-intersection, validated material orientation/side.

### Final-Z quantization robustness

The plan is generated before final machine-frame Z quantization.

Therefore printable candidate geometry also requires SectionQuantizationStability.

Define a conservative print-space Z uncertainty for the pinned compatibility descriptor from half the Orca XYZ formatter resolution, execution-frame Z matching tolerance, and numeric section tolerance.

Around candidate command_z_mm, evaluate section stability over this uncertainty interval.

Hard requirement:
- section topology stays the same simple-loop class;
- material side/orientation stays consistent;
- boundary displacement caused by the allowed Z perturbation remains <= configured section_quantization_geometry_tolerance_mm.

This check may use deterministic endpoint/curve sampling with its own convergence rule.

A mere crossing of a source triangle vertex Z is NOT automatically a failure if the physical section remains topologically/geometrically stable.

### No post-plan Z nudging

Postprocess still MUST NOT change candidate command Z to escape a section event.

If final execution quantization lies outside the proven stability interval, injection is Skipped.

### Closed continuous event-partition stability certificate

The `exact_event_partition_v1` certificate proves numerical section-loop
stability over a supplied closed Z interval. It does not prove that this interval
matches an Orca formatter, execution frame or actual machine. Those independent
owners must supply an adequate uncertainty interval before Plan/injection use.

Exact public API (frozen slotted result, no defaults):

```python
SectionStabilityResult(state: str, reason: str,
    z_lower_mm: Fraction, z_upper_mm: Fraction,
    maximum_boundary_displacement_upper_bound_mm: Fraction | None)

certify_section_stability(mesh: IndexedTriangleMesh, command_z_mm: float,
    uncertainty_halfwidth_mm: float, *, policy: MeshSectionPolicy,
    max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
    max_section_segments: int, max_section_pair_checks: int,
    max_section_queries: int, cancelled: Callable[[], bool]) -> SectionStabilityResult
```

Require exact mesh/policy types, finite binary64 command Z, positive finite
binary64 halfwidth, exact positive integer limits (no bool), and callable exact-
bool cancellation. Geometry/query errors use INVALID_GEOMETRY; policy/limit/
callback errors use INVALID_SETTING; callback exceptions propagate. Normalize
query scalars to float then Fraction. Bounds are center +/- halfwidth in exact
rational arithmetic, even if a bound cannot be represented as finite binary64.
policy.version must be indexed_plane_section_v1 and its stability version must
be exact_event_partition_v1. Unknown versions fail INVALID_SETTING. Existing
positive settings remain unchanged; the existing public single-plane API still
requires unavailable_v1 and retains all its current numerical tolerances.

Freshly evaluate exact embedding and topology under ADR-0030 within each call.
Its rejection and incomplete reasons propagate with bound None. Private reuse
of the same call's prepared topology/triangles is permitted; no caller-created
proof DTO or cross-call cache is trusted. The private embedding operation may
return its prepared topology alongside triangles to avoid duplicate validation.

This certificate uses a separate exact-symbolic route through the sectioner's
internal algorithm: rational query Z, exact zero predicate/coplanar/join
tolerances. Do not construct an invalid zero-tolerance MeshSectionPolicy. The
internal section routine may accept explicit Fraction tolerances; the existing
public wrapper passes its configured tolerances unchanged and this route passes
zeros. Exact horizontal facets reject coplanar-facet; distinct topology nodes
at exactly coincident XY still reject ambiguous-join. Exact nonzero separation
needs no arbitrary snapping. This route proves exact normalized-input geometry,
not robustness to unmodeled source-coordinate errors; the caller's uncertainty
interval is the explicit Z perturbation being certified.

Build sorted unique knots from lower bound, center, upper bound and every source
vertex Z within the closed interval. For K knots, preflight 2*K-1 <=
max_section_queries before any section call, else incomplete/resource-limit.
Each exact section call uses max_section_segments and max_section_pair_checks
independently; the query limit bounds total repeated work. Query every knot and
one exact midpoint of every adjacent knot pair in increasing Z order. Any
section rejection/incomplete propagates; an empty result maps to
rejected/non-simple-section. Each successful query must have one simple loop.

At each knot apply an additional event guard: every ON source vertex must occur
as a single-ID vertex of that knot's loop, and every source edge with two ON
endpoints must have two incident third vertices of opposite strict signs.
Otherwise return incomplete/topology-event-unproven. This stronger guard forbids
unrepresented isolated tangencies and same-side ON edges, including at interval
endpoints; it does not automatically reject ordinary crossing vertex events.

Continuity justification: within an open slab no source vertex Z is crossed,
so active edge identities, face segments and graph incidence are fixed, and all
intersection coordinates are affine in Z. At a knot a triangle with no ON
vertices has its ordinary segment limit. With one ON vertex and opposite other
signs it retains a segment; with same-side signs its possible limit is only the
ON point, which the event guard already places on the accepted loop. With two
ON vertices, opposite strict third-vertex signs of incident faces supply the
same edge limit from each adjacent slab. Three ON vertices reject as a facet.
Consequently each adjacent slab's full segment-set limit equals the knot loop;
collapsing segments do not introduce omitted points or components. Fresh
embedding precludes intersections between unrelated faces. A simple midpoint
loop thus certifies the entire open slab's simple-loop class, and guarded knot
loops connect these classes continuously. No geometric sampling assumption or
empirical convergence threshold substitutes for this argument.

For each slab, take the crossing source edges in its midpoint loop. An edge
from a to b has exact XY speed
`(|bx-ax|+|by-ay|)/|bz-az|`; denominator is nonzero in an open slab. Let
`L=1+max(edge XY speeds)` for that slab. The additional one bounds Z displacement.
At equal convex segment parameter, affine endpoints move by at most
L*abs(deltaZ) in 3D L1 norm, hence also Euclidean norm. This correspondence in
both directions bounds symmetric Hausdorff distance between complete slab loops.
Across knots the certified equal limits allow triangle inequality composition.

Because center is a knot, sum L*slab_width from center to the lower bound and
separately to the upper bound. Their maximum B is an exact Fraction upper bound
on the 3D Euclidean symmetric Hausdorff displacement of every loop in the closed
interval from the nominal center loop. Positive partial sums also cover every
intermediate Z. Compare B inclusively to the exact normalized configured
section_quantization_geometry_tolerance_mm. If B <= tolerance, return
complete/stable with B. Otherwise return incomplete/displacement-unproven with
B: an excessive conservative upper bound is not proof of actual instability.

Result matrices: complete/stable with nonnegative exact Fraction B; incomplete
displacement-unproven with nonnegative exact Fraction B; other incomplete reasons
cancelled, resource-limit or topology-event-unproven with None; rejected with
any embedding/section rejection reason or non-simple-section with None. Near-ON
predicate-uncertain cannot occur on the exact-symbolic route. Both interval fields
are always exact Fraction with lower < upper. Constructors enforce exact string
types and this closed matrix, not computation authority. There are no counters,
Plan identity registrations or physical permission fields.

Check cancellation during knot construction, before each section call, each
event vertex/edge guard, each slab edge/sum and before complete return; retain
existing embedding/section iteration checks. Interrupted work returns no partial
bound. Storage and work are bounded by mesh, per-section and total-query limits;
no extra geometric union-comparison stage or unbounded refinement is introduced.

## Required settings

### Closed exact single-plane research section

`indexed_plane_section_v1` is the bounded exact-zero topology-event sectioner.
It returns a simple geometric loop only; material orientation, embeddedness,
source provenance, quantization stability and Plan/injection authority remain
unproven. No source or selected Z mutation is allowed. The independent topology
prerequisite from ADR-0030 is recomputed; caller-constructed topology is not proof.

Exact immutable API (frozen slotted dataclasses; no defaults):

```python
MeshSectionVertex(source_vertex_ids: tuple[int, ...],
    edge_parameter: Fraction | None, x_mm: Fraction, y_mm: Fraction)
MeshSectionLoop(command_z_mm: Fraction, vertices: tuple[MeshSectionVertex, ...])
MeshSectionResult(state: str, reason: str, loop: MeshSectionLoop | None)

section_mesh_plane(mesh: IndexedTriangleMesh, command_z_mm: float, *,
    policy: MeshSectionPolicy, max_vertices: int, max_triangles: int,
    max_section_segments: int, max_pair_checks: int,
    cancelled: Callable[[], bool]) -> MeshSectionResult
```

Reuse exact existing MeshSectionPolicy, with version `indexed_plane_section_v1`
and section_stability_sampling_convergence_version `unavailable_v1`; reject
other versions as INVALID_SETTING. This selects an executable research algorithm,
not a new physical Settings default. All existing positive numeric policy fields
remain required; quantization geometry tolerance is carried but not evaluated.
Mesh type and finite binary64 command Z use INVALID_GEOMETRY; exact positive
integer limits (no bool), policy and callback errors use INVALID_SETTING.
Normalize command Z through float, then Fraction; no geometry float arithmetic.
Validate these top-level inputs, then call prepare_mesh_topology with the supplied
limits/callback. Propagate its rejected/incomplete state and reason with no loop.
Callbacks must return exact bool; exceptions propagate. Cancellation is checked
before every vertex/face/edge/graph iteration, pair check and final success.

For valid topology compute exact d=vertex.z-command_z. First scan all faces:
if all three abs(d)<=coplanar_section_epsilon_mm, reject coplanar-facet. This is
the explicit numerical facet event, not a broad physical forbidden-Z band.
Then classify abs(d)<=section_predicate_epsilon_mm as ON. If any ON distance is
nonzero, return incomplete/predicate-uncertain. This bounded implementation
handles exact-zero events and refuses to manufacture exact intersections from
projected near-plane vertices. It does not exclude candidate search intervals;
later certified epsilon-ON handling may extend availability without changing Z.

At exact ON vertices use source_vertex_ids=(vertex_id,), edge_parameter=None,
and the exact source XY. At a strict sign-changing edge use sorted IDs (a,b),
parameter t=(z0-za)/(zb-za), 0<t<1, and exact linear interpolation of XY from a
to b. Identity is source IDs, before any coordinate comparison. Within a triangle:
no ON vertices yields one segment between its two crossings, or none; one ON
vertex yields a segment to the opposite edge crossing only if the other two
signs differ, otherwise it is a tangential touch and contributes no segment.
Two ON vertices defer their edge to the following adjacency rule. Three ON
vertices were already rejected as a facet event.

For an edge with two ON endpoints, inspect the third vertex of each of its two
incident faces: opposite strict signs include that source edge once; equal
strict signs discard a tangential edge; an ON third vertex rejects coplanar-facet.
Single-vertex incident fans with more than two actual branches are caught by
the graph gate. No tangential isolated vertex creates a graph node. Deduplicate
segments by unordered endpoint topology keys, including repeated contributions;
zero-identity-length segments reject non-simple-graph. Only nodes used by retained
segments enter the graph. If no segments remain, return empty/no-crossing.

Stop incomplete/resource-limit before storing a new unique segment that would
exceed max_section_segments. Sort topology keys lexicographically. For N nodes
and S unique segments, preflight N*(N-1)/2 + S*(S-1)/2 <= max_pair_checks before
any pair test; otherwise return incomplete/resource-limit. First check all node
pairs in sorted-key order: exact squared XY distance <= join_tolerance² between
distinct keys rejects ambiguous-join, including exact coincident coordinates.
Never weld, average or snap them. Then require degree exactly two at every node
(non-simple-graph), and one connected component (multiple-loops).

Check every segment pair in canonical order with exact 2D orientation and closed
interval predicates. Nonadjacent crossing, touching or collinear overlap rejects
self-intersection. Adjacent segments may meet only at their common endpoint;
collinear backtracking/positive-length overlap also rejects self-intersection.
Disjoint collinear segments are allowed. The pair cap is conservative even for
pairs skipped after adjacency classification. No library/default epsilon is used.

Traverse the cycle from its lexicographically least topology key, initially
choosing its lesser neighbor. Compute exact shoelace twice-area; zero rejects
zero-area. Reverse the traversal except its fixed first vertex if area is negative.
The resulting CCW cycle contains >=3 vertices and omits repeated closing endpoint;
closure is implicit. CCW is a planar coordinate convention, not material side.
Output command_z_mm is the exact Fraction of normalized input Z.

Closed result matrix: complete/section-loop with exact MeshSectionLoop;
empty/no-crossing with None; incomplete/cancelled, resource-limit or
predicate-uncertain with None; rejected with None and either an ADR-0030 topology
rejection reason or coplanar-facet, ambiguous-join, non-simple-graph,
multiple-loops, self-intersection, zero-area. Check reason categories in the
order above. No partial graph or loop escapes cancellation/failure.

Vertex constructors require exact Fraction XY, exact tuple IDs containing one
nonnegative exact int or two strictly ascending nonnegative ints, and None or
exact Fraction parameter according to the above role/range. Loop constructors
require exact Fraction Z and an exact tuple of >=3 exact MeshSectionVertex with
unique topology keys. Result constructors enforce the exact-string closed matrix.
These are shape checks; the engine owns all geometric/relation proof, including
CCW, simplicity and mesh association. Snapshot-local IDs are not persistent global
identities. No Plan/root canonical registration is introduced.

Work is O(V+F+N²+S²) with sorting, bounded by explicit mesh/segment/pair limits;
storage is O(V+F+S). Use iterative graph traversal and the existing topology
validator. No geometry dependency, Orca access, filesystem or proof callback.


Versioned MeshSectionPolicy now includes at minimum:
- section_predicate_epsilon_mm;
- coplanar_section_epsilon_mm;
- mesh_section_join_tolerance_mm;
- section_quantization_geometry_tolerance_mm;
- section-stability sampling/convergence version.

These participate in PluginSettingsFingerprint.

The old broad mesh_section_vertex_avoidance_mm setting is deprecated for hard printable acceptance.

## Requirements / invariants introduced

- Dense mesh vertex count alone cannot erase candidate-Z search space.
- Ordinary vertex crossings are handled topologically, not by broad exclusion.
- Exact ambiguous coplanar facet events may still fail closed.
- Final G-code Z quantization cannot silently move a candidate into a materially different section.
- Same mesh + Z + policy => identical section graph.

## Alternatives considered

- Keep large vertex-Z avoidance bands: rejected because mesh tessellation density controls algorithm availability.
- Add a tiny arbitrary fixed avoidance band: still representation-dependent and does not solve quantization stability.
- Auto-nudge final Z after optimization: rejected because it changes immutable plan geometry.

## Safety impact

High. Preserves fail-closed topology handling without making dense, valid meshes unusable.

## Compatibility impact

Candidates previously rejected only due dense vertex-Z bands may become eligible after topology/stability validation.

## Performance / resource impact

Requires mesh adjacency/topology data and section-stability checks. Use cached topology and bounded local queries.

## Observability impact

Report topology event classes, section graph result, quantization stability interval, maximum boundary displacement, and exact coplanar-plane rejection reason.

## Test / validation impact

Add:
- simple plane through one mesh vertex -> stable valid contour;
- tangent vertex touch -> no false branch;
- plane through shared edge -> deterministic contour;
- exact horizontal coplanar patch -> discrete reject;
- dense curved mesh with closely spaced vertex Z -> candidate search remains available;
- coarse and refined tessellations of same analytic surface produce compatible section geometry;
- final Z quantization perturbation with stable topology -> pass;
- perturbation crossing a true topology/material change -> reject.

## Migration / rollout

ADR-0053 remains authoritative for simple-loop graph validation and no post-plan Z mutation.

This ADR supersedes ADR-0053 only for the broad vertex/facet-Z avoidance-band mechanism.

## Rollback / disable condition

Any unresolved topology/coplanar/quantization-stability case => non-injectable.

## Open questions

A robust-predicate library may later replace custom predicates if dependency review demonstrates deterministic parity and acceptable packaging.
