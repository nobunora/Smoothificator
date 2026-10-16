# ADR-0030: Validate source-mesh orientation and derive material side topologically

Status: Accepted
Date: 2026-09-30

## Context

Printable v1 requires a closed manifold source mesh for:
- material-side centerline placement;
- surface normals;
- signed error;
- nesting/support reasoning.

A manifold flag alone does not prove that every triangle winding is consistently oriented or that stored/generated normals point outward.

Mirrored transforms can also reverse global orientation.

Orca slicing can often operate from triangle intersections without relying on outward normals, while Adaptive Sub-Edge needs a reliable inside/outside/material-side interpretation.

## Decision

Printable v1 MUST NOT trust source triangle normals blindly.

After centered-frame transformation:

1. validate the triangle mesh is a closed 2-manifold in the required v1 topology;
2. validate orientation consistency across shared edges, or construct a non-mutating consistent orientation view for analysis;
3. determine global outward orientation from topology/signed-volume or an equivalent deterministic closed-mesh test;
4. account for mirrored transforms/determinant sign;
5. derive analysis normals from the validated orientation view;
6. use a deterministic inside/outside test as an independent material-side check for centerline placement and signed error.

The plugin does not write a repaired mesh back to Orca.

If orientation/material-side cannot be resolved unambiguously, the model is analysis-only/non-injectable.

### Closed indexed-topology prerequisite

`indexed_closed_mesh_topology_v1` prepares source adjacency and a non-mutating
orientation view. Success proves combinatorial connected closed 2-manifold
topology and nonzero signed volume only. It does not prove embeddedness, absence
of self-intersection, inside/outside, material side, Orca manifold/parity evidence
or injectability. The positive-volume convention is not "outward validated"
until independent embeddedness/material-side gates also pass.

Exact immutable API (frozen slotted dataclasses, no defaults):

```python
IndexedTriangleMesh(vertices: tuple[PrintPoint3, ...],
                    triangles: tuple[tuple[int, int, int], ...])
OrientedMeshTopology(mesh: IndexedTriangleMesh,
    oriented_triangles: tuple[tuple[int, int, int], ...],
    edges: tuple[tuple[int, int, int, int], ...],
    vertex_faces: tuple[tuple[int, ...], ...],
    input_signed_volume_six_mm3: Fraction, globally_flipped: bool)
MeshTopologyResult(state: str, reason: str,
                   topology: OrientedMeshTopology | None)

prepare_mesh_topology(mesh: IndexedTriangleMesh, *, max_vertices: int,
    max_triangles: int, cancelled: Callable[[], bool]) -> MeshTopologyResult
```

Vertices are already transformed centered PrintObject-space millimeters. Vertex
and face IDs are zero-based input tuple indices. Never weld, reorder, discard
or repair source geometry. Arithmetic uses exact Fraction(float(coordinate)) of
the existing finite binary64 normalization. Mirrored input is already transformed;
do not apply determinant correction again. Each edge row is
`(lower_vertex_id, upper_vertex_id, lower_face_id, upper_face_id)`, sorted
lexicographically. vertex_faces contains sorted incident face IDs for each vertex.
Oriented triangles retain face order and first vertex; a global flip exchanges
second and third indices. The original mesh remains unchanged.

IndexedTriangleMesh construction checks exact outer tuples only. Evaluation
first checks exact mesh type, exact positive integer limits (bool excluded),
callable cancellation, then invokes cancellation. If either tuple count exceeds
its limit, return incomplete/resource-limit before scanning elements. Within
budget require exact PrintPoint3 vertices and exact length-three tuples of exact
integer indices, all in range. Malformed geometry raises INVALID_GEOMETRY;
malformed limits/callback or non-exact-bool callback result raises INVALID_SETTING.
Callback exceptions propagate. No callback supplies geometry evidence.

After type validation perform checks in the following order; the first failing
category determines the reason. Within each category process ascending input
IDs or sorted edges:

1. Reject empty vertex/face tuple: empty-mesh. Reject unused vertices:
   unused-vertex. Require all three transformed bounding-box extents positive:
   degenerate-bounds.
2. Reject repeated triangle indices or exactly zero 3D cross product:
   degenerate-triangle. Reject duplicate unordered vertex triples including
   reversed duplicates: duplicate-triangle.
3. Every undirected edge has exactly two distinct incident faces:
   nonmanifold-edge. The two directed traversals are opposite:
   inconsistent-winding. Reject local winding inconsistency, consistent with
   Gate C fixtures; this slice performs no local reorientation repair.
4. The face graph through shared edges has one connected component:
   disconnected-shell. At each vertex, construct the link graph: nodes are its
   adjacent vertices, and each incident triangle contributes the opposite edge.
   Require one connected cycle, degree two at every node, and no repeated link
   edge: nonmanifold-vertex. Edge incidence alone is insufficient.
5. Compute exact signed six-volume `sum(a dot (b cross c))` over input faces.
   Zero rejects: zero-signed-volume. Positive retains input orientation; negative
   reverses every triangle in the view. Store the original signed nonzero Fraction
   and globally_flipped equal to its negativity. View volume is positive.

Distinct vertex IDs at identical coordinates are not welded or independently
rejected unless they trigger a listed face/topology failure; nonlocal geometric
coincidences belong to the later embeddedness gate. For efficiency the volume
sum may use `(a-o) dot ((b-o) cross (c-o))` with o equal to the first input vertex;
after the closed consistent-edge checks this is exactly the same signed sum.

Return complete/prepared with topology only after all checks finish. Rejections
have state rejected, one of the above reason strings, and no topology.
Interruptions have state incomplete, reason cancelled or resource-limit, and
no topology. Never publish partial adjacency. Result constructors enforce exact
strings and this closed matrix. Topology constructors validate exact mesh/type,
tuple row shapes, index ranges, sorted uniqueness, matching lengths and exact
nonzero Fraction/bool sign agreement. Construction is not an evidence factory:
the engine owns relational validation, revalidates each input mesh on each call,
and never consumes caller-constructed topology as proof.

Check cancellation before each vertex/face/edge iteration, graph visit and volume
iteration, and before returning success. Sorting is bounded by input limits.
Use iterative traversals, O(V+F) adjacency storage and O((V+F) log(V+F)) sorting;
no all-pairs intersection test or recursive graph traversal. Limits are required
computational parameters, not physical defaults. No dependency or Plan/canonical
registration is added. IDs are snapshot-local; later persistence/Plan binding
must associate the source snapshot's identity explicitly.

### Closed exact embedding and point classification

`exact_mesh_embedding_v1` and `exact_mesh_point_parity_v1` add numerical
embedded-surface and material-side predicates to the preceding topology stage.
These predicates concern the supplied centered mesh coordinates only. They do
not establish Orca provenance/frame parity, tolerance/calibration, section
quantization stability, valid toolpaths or injection/physical authority.

Exact public API (frozen slotted result dataclasses, no defaults):

```python
MeshEmbeddingResult(state: str, reason: str)
MeshPointClassification(state: str, reason: str, classification: str | None)

evaluate_mesh_embedding(mesh: IndexedTriangleMesh, *, max_vertices: int,
    max_triangles: int, max_pair_checks: int,
    cancelled: Callable[[], bool]) -> MeshEmbeddingResult

classify_mesh_point(mesh: IndexedTriangleMesh, point: PrintPoint3, *,
    max_vertices: int, max_triangles: int, max_pair_checks: int,
    max_ray_directions: int, cancelled: Callable[[], bool]) -> MeshPointClassification
```

Every public call requires exact mesh/point types and exact positive integer
limits, excluding bool; cancellation must be callable and return exact bool.
Malformed geometry raises INVALID_GEOMETRY; bad limits/callback raise
INVALID_SETTING; callback exceptions propagate. Top-level validation precedes
fresh prepare_mesh_topology. Its resource precedence, failures and cancellation
are retained. Every classification call freshly evaluates embedding before
boundary/ray tests; caller-created results or topology values are never accepted
as proof. Private reuse of the topology produced during that same call is allowed.
Use exact Fraction(float(coordinate)); no epsilon, snapping or float predicate.

For F faces preflight F*(F-1)/2 <= max_pair_checks after successful topology
validation, before pair tests; otherwise incomplete/resource-limit. Test every
face pair in lexicographic input-face-ID order, including adjacent faces. Each
triangle is the closed convex hull of its three exact coordinates. Determine
their complete intersection as follows:

- Nonparallel face planes: slice each triangle by the other's plane. Include
  vertices with exact zero signed distance and strict sign-changing edge
  intersections. Deduplicate exact points. Empty slice means no intersection;
  otherwise its convex hull is a point or segment. Intersect the two intervals
  on their common plane-intersection line, using the axis of greatest absolute
  component of the cross product of face normals (ties X,Y,Z). Reconstruct
  overlap endpoints by exact affine interpolation on a nondegenerate slice;
  if both slices are points, require equality. Preserve point/segment contacts.
- Parallel distinct planes: empty intersection. Coplanar planes: drop the axis
  of greatest absolute normal component (ties X,Y,Z), project both triangles
  injectively into 2D, orient the clipping triangle CCW, and clip the subject
  triangle against its three closed halfplanes using exact rational line
  intersections. Retain degenerate point/segment results rather than rejecting
  zero polygon area. Remove exact duplicate vertices and lift results using
  the shared plane equation. The resulting convex polygon/segment/point is
  the complete intersection; an empty list means no intersection.

Coplanar clipping may equivalently retain 3D points while applying projected
halfplane predicates and interpolate the full 3D endpoints with the same exact
parameter. This is identical to lifting the projected result through the plane.

The allowed intersection is defined exclusively by shared source vertex IDs:
none permits no intersection; one permits only that point; two permit only
that closed source edge. Duplicate faces sharing three IDs were already rejected
by topology. Reject self-intersection if any intersection vertex lies outside
this allowed simplex. Because both intersection and allowed simplex are convex,
this checks the entire intersection, including coplanar area overlap and edge
contact. Exact 3D collinearity plus closed coordinate bounds tests source-edge
membership. Nonlocal coincident coordinates are not source adjacency and reject.
Do not skip adjacent pairs: they may overlap away from the common edge/vertex.

After all pairs pass, embedding returns complete/embedded. This proves an
embedded connected closed triangulated surface in the exact normalized input
coordinates; a positive-volume view now has the outward mathematical orientation.
This is numerical material geometry evidence, not a physical permission token.

For point classification, run embedding first. Then scan all faces for exact
point-on-triangle membership: plane equation zero and projected closed triangle
containment. If any matches, return complete/classified with boundary. Boundary
includes vertices/edges and is distinct from inside; a caller must not silently
treat it as interior clearance.

Otherwise try ray directions d_k=(1,k,k*k) for k=0,...,max_ray_directions-1 in
that order. Integers are exact; no normalization is necessary. For each face use
its plane equation to compute exact ray parameter t. A parallel ray not in the
face plane contributes no hit. A ray lying in any face plane makes the entire
direction ambiguous and retries the next direction, even if the finite triangle
might not be reached; this conservative limitation is explicit. For nonparallel
rays, ignore t<=0. At t>0, strict triangle-interior intersection contributes one
hit; an intersection on an edge or vertex makes the direction ambiguous and
retries. Plane hits outside the triangle do not count. Never infer boundary
merely from an ambiguous ray: boundary was checked independently first.

After a full unambiguous direction, odd hit count returns inside, even returns
outside, both complete/classified. Stop after the first such direction. If every
permitted direction is ambiguous, return incomplete/ray-directions-exhausted
with classification None. No random direction, automatic extra retry or numerical
perturbation is permitted. F*max_ray_directions bounds ray work independently
of the face-pair budget; max_ray_directions is a required computational limit.

Closed result matrices: embedding complete/embedded; rejected with any preceding
topology rejection reason or self-intersection; incomplete/cancelled or
resource-limit. Point results complete/classified with exact string inside,
outside or boundary; rejected with the same rejection reasons; incomplete with
cancelled, resource-limit or ray-directions-exhausted. Noncomplete classification
is always None. Constructors enforce exact strings and these matrices but cannot
certify their caller's computation; only fresh engine evaluation owns proof.

Check cancellation before each triangle-pair test, each face boundary test,
each ray direction and face test, and before any complete return. Existing
topology cancellation remains in force. Interrupted calls publish no partial
classification. Each pair has constant-size exact clipping/slicing work; use
O(V+F) topology storage, O(F²) bounded pair work and O(F*max_ray_directions)
bounded ray work, with iterative traversal. No cross-call proof cache, new
dependency, Orca I/O, filesystem or canonical Plan registration is introduced.

## Requirements / invariants introduced

- ModelVolume.is_manifold() is necessary but not sufficient.
- Surface normals used for signed error are derived from validated orientation.
- Candidate insetting uses validated material side, not arbitrary triangle winding.
- Mirrored model fixtures must produce the same physical material-side interpretation after transformation.

## Alternatives considered

- Trust raw face normals: rejected.
- Auto-repair and replace the source mesh: rejected; would create a second geometry authority.
- Use unsigned error only: insufficient for material-side candidate placement.

## Safety impact

High for avoiding outward/inward inversion of candidate paths.

## Compatibility impact

Some malformed-but-sliceable models remain analysis-only.

## Performance / resource impact

One topology/orientation validation pass plus inside/outside queries already needed by the engine.

## Observability impact

Record:
- orientation consistency result;
- signed-volume/orientation sign;
- mirrored transform indication;
- material-side validation failure reason.

## Test / validation impact

Add:
- outward-oriented closed mesh;
- globally reversed mesh;
- mirrored instance;
- locally inconsistent winding rejection;
- material-side point tests;
- signed-error sign parity.

## Migration / rollout

Add orientation/material-side validation to geometry_snapshot/mesh geometry prerequisites before surface-band planning.

## Rollback / disable condition

Unresolved orientation or material side => no injection.

## Open questions

None for single closed ModelPart v1.

Supersedes: any assumption that manifold status alone proves usable outward normals.
