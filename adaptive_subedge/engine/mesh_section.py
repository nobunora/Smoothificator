"""Topology-keyed exact sections; selected Z and source geometry never change."""
from fractions import Fraction
from itertools import combinations
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.mesh_section import MeshSectionVertex, MeshSectionLoop, MeshSectionResult
from adaptive_subedge.domain.numeric import finite_binary64
from adaptive_subedge.domain.settings import MeshSectionPolicy
from .mesh_topology import prepare_mesh_topology


class _SectionStop(Exception):
    def __init__(self, state, reason):
        self.state, self.reason = state, reason


def _orientation(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def _on_segment(a, b, p):
    return (_orientation(a, b, p) == 0
            and all(min(x, y) <= z <= max(x, y) for x, y, z in zip(a, b, p)))


def _segments_intersect(a, b, c, d):
    sides = (_orientation(a, b, c), _orientation(a, b, d),
             _orientation(c, d, a), _orientation(c, d, b))
    return (sides[0]*sides[1] < 0 and sides[2]*sides[3] < 0
            or _on_segment(a, b, c) or _on_segment(a, b, d)
            or _on_segment(c, d, a) or _on_segment(c, d, b))


def section_mesh_plane(mesh: IndexedTriangleMesh, command_z_mm: float, *,
                       policy: MeshSectionPolicy, max_vertices: int, max_triangles: int,
                       max_section_segments: int, max_pair_checks: int,
                       cancelled: Callable[[], bool]) -> MeshSectionResult:
    if type(mesh) is not IndexedTriangleMesh or not finite_binary64(command_z_mm):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "mesh and finite section Z required")
    if (type(policy) is not MeshSectionPolicy or policy.version != "indexed_plane_section_v1"
            or policy.section_stability_sampling_convergence_version != "unavailable_v1"
            or any(type(x) is not int or x <= 0 for x in
                   (max_vertices, max_triangles, max_section_segments, max_pair_checks))
            or not callable(cancelled)):
        raise ContractError(ReasonCode.INVALID_SETTING, "invalid section policy, limits or callback")
    topology = prepare_mesh_topology(mesh, max_vertices=max_vertices, max_triangles=max_triangles,
                                     cancelled=cancelled)
    if topology.state != "complete":
        return MeshSectionResult(topology.state, topology.reason, None)

    def check_cancelled():
        stopped = cancelled()
        if type(stopped) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation must return exact bool")
        if stopped:
            raise _SectionStop("incomplete", "cancelled")

    try:
        return _section(topology.topology, Fraction(float(command_z_mm)),
                        max_section_segments, max_pair_checks, check_cancelled,
                        coplanar=Fraction(float(policy.coplanar_section_epsilon_mm)),
                        epsilon=Fraction(float(policy.section_predicate_epsilon_mm)),
                        join_tolerance=Fraction(float(policy.mesh_section_join_tolerance_mm)))
    except _SectionStop as stopped:
        return MeshSectionResult(stopped.state, stopped.reason, None)


def _section(topology, z, max_segments, max_pairs, check_cancelled, *,
             coplanar, epsilon, join_tolerance):
    points, distances = [], []
    for vertex in topology.mesh.vertices:
        check_cancelled()
        point = tuple(Fraction(float(x)) for x in (vertex.x_mm, vertex.y_mm, vertex.z_mm))
        points.append(point)
        distances.append(point[2]-z)
    for triangle in topology.mesh.triangles:
        check_cancelled()
        if all(abs(distances[i]) <= coplanar for i in triangle):
            raise _SectionStop("rejected", "coplanar-facet")
    for distance in distances:
        check_cancelled()
        if 0 < abs(distance) <= epsilon:
            raise _SectionStop("incomplete", "predicate-uncertain")
    nodes, segments = {}, set()

    def vertex_node(i):
        return MeshSectionVertex((i,), None, points[i][0], points[i][1])

    def edge_node(a, b):
        a, b = sorted((a, b))
        t = -distances[a] / (distances[b]-distances[a])
        return MeshSectionVertex((a, b), t,
                                 points[a][0]+t*(points[b][0]-points[a][0]),
                                 points[a][1]+t*(points[b][1]-points[a][1]))

    def add_segment(first, second):
        a, b = first.source_vertex_ids, second.source_vertex_ids
        if a == b:
            raise _SectionStop("rejected", "non-simple-graph")
        pair = tuple(sorted((a, b)))
        if pair in segments:
            return
        if len(segments) >= max_segments:
            raise _SectionStop("incomplete", "resource-limit")
        nodes[a], nodes[b] = first, second
        segments.add(pair)

    for a, b, c in topology.mesh.triangles:
        check_cancelled()
        on = [i for i in (a, b, c) if distances[i] == 0]
        if not on:
            crossings = []
            for i, j in ((a, b), (b, c), (c, a)):
                check_cancelled()
                if distances[i]*distances[j] < 0:
                    crossings.append(edge_node(i, j))
            if crossings:
                add_segment(*crossings)
        elif len(on) == 1:
            i, j = (i for i in (a, b, c) if i != on[0])
            if distances[i]*distances[j] < 0:
                add_segment(vertex_node(on[0]), edge_node(i, j))
    for a, b, face0, face1 in topology.edges:
        check_cancelled()
        if distances[a] == distances[b] == 0:
            other0 = next(i for i in topology.mesh.triangles[face0] if i not in (a, b))
            other1 = next(i for i in topology.mesh.triangles[face1] if i not in (a, b))
            if distances[other0]*distances[other1] < 0:
                add_segment(vertex_node(a), vertex_node(b))
    if not segments:
        return MeshSectionResult("empty", "no-crossing", None)
    keys, ordered_segments = sorted(nodes), sorted(segments)
    n, s = len(keys), len(segments)
    if n*(n-1)//2 + s*(s-1)//2 > max_pairs:
        raise _SectionStop("incomplete", "resource-limit")
    xy = {key: (nodes[key].x_mm, nodes[key].y_mm) for key in keys}
    join_squared = join_tolerance**2
    for a, b in combinations(keys, 2):
        check_cancelled()
        if sum((x-y)**2 for x, y in zip(xy[a], xy[b])) <= join_squared:
            raise _SectionStop("rejected", "ambiguous-join")
    neighbors = {key: [] for key in keys}
    for a, b in ordered_segments:
        check_cancelled()
        neighbors[a].append(b)
        neighbors[b].append(a)
    for key in keys:
        check_cancelled()
        if len(neighbors[key]) != 2:
            raise _SectionStop("rejected", "non-simple-graph")
    cycle, seen = [], set()
    previous, current = None, keys[0]
    while current not in seen:
        check_cancelled()
        cycle.append(current)
        seen.add(current)
        following = min(neighbors[current]) if previous is None else next(
            key for key in neighbors[current] if key != previous)
        previous, current = current, following
    if len(cycle) != len(keys):
        raise _SectionStop("rejected", "multiple-loops")
    for (a, b), (c, d) in combinations(ordered_segments, 2):
        check_cancelled()
        common = set((a, b)) & set((c, d))
        if common:
            joint = next(iter(common))
            left = b if a == joint else a
            right = d if c == joint else c
            if (_orientation(xy[left], xy[joint], xy[right]) == 0
                    and sum((x-o)*(y-o) for x, y, o in zip(xy[left], xy[right], xy[joint])) > 0):
                raise _SectionStop("rejected", "self-intersection")
        elif _segments_intersect(xy[a], xy[b], xy[c], xy[d]):
            raise _SectionStop("rejected", "self-intersection")
    twice_area = Fraction(0)
    for a, b in zip(cycle, cycle[1:]+cycle[:1]):
        check_cancelled()
        twice_area += xy[a][0]*xy[b][1]-xy[a][1]*xy[b][0]
    if twice_area == 0:
        raise _SectionStop("rejected", "zero-area")
    if twice_area < 0:
        cycle = cycle[:1]+list(reversed(cycle[1:]))
    loop = MeshSectionLoop(z, tuple(nodes[key] for key in cycle))
    check_cancelled()
    return MeshSectionResult("complete", "section-loop", loop)
