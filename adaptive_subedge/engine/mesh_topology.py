"""Exact connected closed-mesh topology, without embedded-solid authority."""
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import (
    IndexedTriangleMesh, MeshTopologyResult, OrientedMeshTopology,
)


class _Cancelled(Exception):
    pass


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _difference(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _connected(adjacency, start, check_cancelled):
    visited = {start}
    pending = [start]
    while pending:
        check_cancelled()
        node = pending.pop()
        for neighbor in sorted(adjacency[node]):
            if neighbor not in visited:
                visited.add(neighbor)
                pending.append(neighbor)
    return len(visited) == len(adjacency)


def prepare_mesh_topology(mesh: IndexedTriangleMesh, *, max_vertices: int,
                          max_triangles: int,
                          cancelled: Callable[[], bool]) -> MeshTopologyResult:
    if type(mesh) is not IndexedTriangleMesh:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact indexed mesh required")
    if (type(max_vertices) is not int or max_vertices <= 0
            or type(max_triangles) is not int or max_triangles <= 0 or not callable(cancelled)):
        raise ContractError(ReasonCode.INVALID_SETTING, "positive mesh limits and callback required")

    def check_cancelled():
        stopped = cancelled()
        if type(stopped) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation must return exact bool")
        if stopped:
            raise _Cancelled

    try:
        check_cancelled()
        if len(mesh.vertices) > max_vertices or len(mesh.triangles) > max_triangles:
            return MeshTopologyResult("incomplete", "resource-limit", None)
        return _prepare(mesh, check_cancelled)
    except _Cancelled:
        return MeshTopologyResult("incomplete", "cancelled", None)


def _prepare(mesh, check_cancelled):
    def rejected(reason):
        return MeshTopologyResult("rejected", reason, None)

    points = []
    lower_bounds = upper_bounds = None
    for vertex in mesh.vertices:
        check_cancelled()
        if type(vertex) is not PrintPoint3:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact PrintPoint3 required")
        point = tuple(Fraction(float(x)) for x in (vertex.x_mm, vertex.y_mm, vertex.z_mm))
        points.append(point)
        if lower_bounds is None:
            lower_bounds, upper_bounds = point, point
        else:
            lower_bounds = tuple(min(a, b) for a, b in zip(lower_bounds, point))
            upper_bounds = tuple(max(a, b) for a, b in zip(upper_bounds, point))
    vertex_faces = [[] for _ in points]
    for face, triangle in enumerate(mesh.triangles):
        check_cancelled()
        if (type(triangle) is not tuple or len(triangle) != 3
                or any(type(i) is not int or not 0 <= i < len(points) for i in triangle)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid indexed triangle")
        for vertex in triangle:
            vertex_faces[vertex].append(face)
    if not points or not mesh.triangles:
        return rejected("empty-mesh")
    for incident in vertex_faces:
        check_cancelled()
        if not incident:
            return rejected("unused-vertex")
    if any(a == b for a, b in zip(lower_bounds, upper_bounds)):
        return rejected("degenerate-bounds")
    for a, b, c in mesh.triangles:
        check_cancelled()
        if len({a, b, c}) != 3 or not any(_cross(_difference(points[b], points[a]),
                                                _difference(points[c], points[a]))):
            return rejected("degenerate-triangle")
    seen = set()
    for triangle in mesh.triangles:
        check_cancelled()
        key = tuple(sorted(triangle))
        if key in seen:
            return rejected("duplicate-triangle")
        seen.add(key)
    edge_faces = {}
    for face, (a, b, c) in enumerate(mesh.triangles):
        check_cancelled()
        for start, end in ((a, b), (b, c), (c, a)):
            check_cancelled()
            key = (min(start, end), max(start, end))
            edge_faces.setdefault(key, []).append((face, start < end))
    ordered_edges = sorted(edge_faces)
    for edge in ordered_edges:
        check_cancelled()
        if len(edge_faces[edge]) != 2:
            return rejected("nonmanifold-edge")
    for edge in ordered_edges:
        check_cancelled()
        if edge_faces[edge][0][1] == edge_faces[edge][1][1]:
            return rejected("inconsistent-winding")
    face_neighbors = [[] for _ in mesh.triangles]
    edges = []
    for a, b in ordered_edges:
        check_cancelled()
        lower, upper = (item[0] for item in edge_faces[a, b])
        face_neighbors[lower].append(upper)
        face_neighbors[upper].append(lower)
        edges.append((a, b, lower, upper))
    if not _connected(face_neighbors, 0, check_cancelled):
        return rejected("disconnected-shell")
    for vertex, incident in enumerate(vertex_faces):
        check_cancelled()
        link = {}
        link_edges = set()
        for face in incident:
            check_cancelled()
            a, b = sorted(i for i in mesh.triangles[face] if i != vertex)
            if (a, b) in link_edges:
                return rejected("nonmanifold-vertex")
            link_edges.add((a, b))
            link.setdefault(a, []).append(b)
            link.setdefault(b, []).append(a)
        for neighbor in sorted(link):
            check_cancelled()
            if len(link[neighbor]) != 2:
                return rejected("nonmanifold-vertex")
        if not _connected(link, min(link), check_cancelled):
            return rejected("nonmanifold-vertex")
    origin = points[0]
    volume_six = Fraction(0)
    for a, b, c in mesh.triangles:
        check_cancelled()
        offset_a, offset_b, offset_c = (_difference(points[i], origin) for i in (a, b, c))
        volume_six += sum(x*y for x, y in zip(offset_a, _cross(offset_b, offset_c)))
    if volume_six == 0:
        return rejected("zero-signed-volume")
    flipped = volume_six < 0
    oriented = []
    for a, b, c in mesh.triangles:
        check_cancelled()
        oriented.append((a, c, b) if flipped else (a, b, c))
    topology = OrientedMeshTopology(mesh, tuple(oriented), tuple(edges),
                                    tuple(tuple(row) for row in vertex_faces), volume_six, flipped)
    check_cancelled()
    return MeshTopologyResult("complete", "prepared", topology)
