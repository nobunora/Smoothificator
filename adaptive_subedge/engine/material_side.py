"""Fresh bounded embedding validation and independent exact point parity."""
from fractions import Fraction
from itertools import combinations
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.material_side import MeshEmbeddingResult, MeshPointClassification, MeshSegmentClassification
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from .mesh_topology import prepare_mesh_topology
from .triangle_intersection import _intersection_vertices, _point_on_segment, _point_on_triangle, _ray_hit, _segment_contacts_triangle


class _Stopped(Exception):
    def __init__(self, state, reason):
        self.state, self.reason = state, reason


def _validate(mesh, limits, cancelled):
    if type(mesh) is not IndexedTriangleMesh:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact indexed mesh required")
    if any(type(limit) is not int or limit <= 0 for limit in limits) or not callable(cancelled):
        raise ContractError(ReasonCode.INVALID_SETTING, "positive limits and callback required")


def _cancellation(cancelled):
    def check():
        stopped = cancelled()
        if type(stopped) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation must return exact bool")
        if stopped:
            raise _Stopped("incomplete", "cancelled")
    return check


def _embedding(mesh, max_vertices, max_triangles, max_pairs, cancelled, check):
    result = prepare_mesh_topology(mesh, max_vertices=max_vertices, max_triangles=max_triangles,
                                   cancelled=cancelled)
    if result.state != "complete":
        raise _Stopped(result.state, result.reason)
    count = len(mesh.triangles)
    if count*(count-1)//2 > max_pairs:
        raise _Stopped("incomplete", "resource-limit")
    points = []
    for point in mesh.vertices:
        check()
        points.append(tuple(Fraction(float(x)) for x in (point.x_mm, point.y_mm, point.z_mm)))
    triangles = []
    for face in mesh.triangles:
        check()
        triangles.append(tuple(points[i] for i in face))
    for first, second in combinations(range(count), 2):
        check()
        intersection = _intersection_vertices(triangles[first], triangles[second])
        shared = sorted(set(mesh.triangles[first]) & set(mesh.triangles[second]))
        if not shared:
            allowed = not intersection
        elif len(shared) == 1:
            allowed = all(point == points[shared[0]] for point in intersection)
        else:
            a, b = (points[i] for i in shared)
            allowed = all(_point_on_segment(point, a, b) for point in intersection)
        if not allowed:
            raise _Stopped("rejected", "self-intersection")
    return tuple(triangles), result.topology


def evaluate_mesh_embedding(mesh: IndexedTriangleMesh, *, max_vertices: int,
                            max_triangles: int, max_pair_checks: int,
                            cancelled: Callable[[], bool]) -> MeshEmbeddingResult:
    _validate(mesh, (max_vertices, max_triangles, max_pair_checks), cancelled)
    check = _cancellation(cancelled)
    try:
        _embedding(mesh, max_vertices, max_triangles, max_pair_checks, cancelled, check)
        check()
        return MeshEmbeddingResult("complete", "embedded")
    except _Stopped as stopped:
        return MeshEmbeddingResult(stopped.state, stopped.reason)


def classify_mesh_point(mesh: IndexedTriangleMesh, point: PrintPoint3, *, max_vertices: int,
                        max_triangles: int, max_pair_checks: int, max_ray_directions: int,
                        cancelled: Callable[[], bool]) -> MeshPointClassification:
    if type(point) is not PrintPoint3:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact query point required")
    _validate(mesh, (max_vertices, max_triangles, max_pair_checks, max_ray_directions), cancelled)
    check = _cancellation(cancelled)
    try:
        triangles, _ = _embedding(mesh, max_vertices, max_triangles, max_pair_checks, cancelled, check)
        query = tuple(Fraction(float(x)) for x in (point.x_mm, point.y_mm, point.z_mm))
        classification = _classify_point(triangles, query, max_ray_directions, check)
        return MeshPointClassification("complete", "classified", classification)
    except _Stopped as stopped:
        return MeshPointClassification(stopped.state, stopped.reason, None)


def _classify_point(triangles, query, max_ray_directions, check):
    for triangle in triangles:
        check()
        if _point_on_triangle(query, triangle):
            check()
            return "boundary"
    for k in range(max_ray_directions):
        check()
        hits = 0
        for triangle in triangles:
            check()
            outcome = _ray_hit(query, (1, k, k*k), triangle)
            if outcome == "ambiguous":
                break
            hits += outcome == "hit"
        else:
            check()
            return "inside" if hits % 2 else "outside"
    raise _Stopped("incomplete", "ray-directions-exhausted")


def classify_mesh_segment(mesh: IndexedTriangleMesh, start: PrintPoint3, end: PrintPoint3, *,
                          max_vertices: int, max_triangles: int, max_pair_checks: int,
                          max_ray_directions: int,
                          cancelled: Callable[[], bool]) -> MeshSegmentClassification:
    if type(start) is not PrintPoint3 or type(end) is not PrintPoint3:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact segment endpoints required")
    _validate(mesh, (max_vertices, max_triangles, max_pair_checks, max_ray_directions), cancelled)
    first, last = (tuple(Fraction(float(x)) for x in (p.x_mm, p.y_mm, p.z_mm))
                   for p in (start, end))
    if first == last:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "nonzero normalized segment required")
    check = _cancellation(cancelled)
    try:
        triangles, _ = _embedding(mesh, max_vertices, max_triangles, max_pair_checks, cancelled, check)
        for triangle in triangles:
            check()
            if _segment_contacts_triangle(first, last, triangle):
                check()
                return MeshSegmentClassification("complete", "classified", "boundary-contact")
        check()
        start_side = _classify_point(triangles, first, max_ray_directions, check)
        check()
        end_side = _classify_point(triangles, last, max_ray_directions, check)
        check()
        if start_side != end_side or start_side == "boundary":
            return MeshSegmentClassification("incomplete", "classification-inconsistent", None)
        return MeshSegmentClassification("complete", "classified", "strictly-"+start_side)
    except _Stopped as stopped:
        return MeshSegmentClassification(stopped.state, stopped.reason, None)
