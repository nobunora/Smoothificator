"""Bounded exact top-graph certificate over one caller-supplied convex cell."""
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.planar_cell_top import PlanarCellTopCoverage

from .material_side import _Stopped, _cancellation, _embedding, _validate


def _turn(a, b, p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def _on_segment(a, b, p):
    return (_turn(a, b, p) == 0
            and min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def _intersects(a, b, c, d):
    first, second = _turn(a, b, c), _turn(a, b, d)
    third, fourth = _turn(c, d, a), _turn(c, d, b)
    return ((first*second < 0 and third*fourth < 0)
            or _on_segment(a, b, c) or _on_segment(a, b, d)
            or _on_segment(c, d, a) or _on_segment(c, d, b))


def _cell_area(cell, max_cell_vertices, check):
    if type(cell) is not tuple or len(cell) > max_cell_vertices:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "bounded cell tuple required")
    if len(cell) < 3:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "cell needs three vertices")
    for point in cell:
        check()
        if (type(point) is not tuple or len(point) != 2
                or any(type(v) is not Fraction for v in point)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact cell points required")
    if len(set(cell)) != len(cell) or cell[0] != min(cell):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "unique canonical cell required")
    area2 = Fraction(0)
    for i, a in enumerate(cell):
        check()
        b = cell[(i+1) % len(cell)]
        area2 += a[0]*b[1]-a[1]*b[0]
        for j, point in enumerate(cell):
            check()
            if j not in (i, (i+1) % len(cell)) and _turn(a, b, point) <= 0:
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "strict convexity required")
        for j in range(i+1, len(cell)):
            check()
            if j != (i+1) % len(cell) and (j+1) % len(cell) != i:
                if _intersects(a, b, cell[j], cell[(j+1) % len(cell)]):
                    raise ContractError(ReasonCode.INVALID_GEOMETRY, "cell edges intersect")
    if area2 <= 0:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "positive CCW cell required")
    return area2/2


def _plane(triangle):
    a, b, c = triangle
    ux, uy, uz = (b[i]-a[i] for i in range(3))
    vx, vy, vz = (c[i]-a[i] for i in range(3))
    nx, ny, nz = uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx
    if nz <= 0:
        return None
    slope_x, slope_y = -nx/nz, -ny/nz
    return slope_x, slope_y, a[2]-slope_x*a[0]-slope_y*a[1]


def _clip(triangle, cell, check):
    piece = triangle
    for i, a in enumerate(cell):
        check()
        b = cell[(i+1) % len(cell)]
        distances = []
        for point in piece:
            check()
            distances.append(_turn(a, b, point))
        clipped = []
        for j, point in enumerate(piece):
            check()
            previous = piece[j-1]
            before, current = distances[j-1], distances[j]
            if before*current < 0:
                ratio = before/(before-current)
                clipped.append(tuple(previous[d]+ratio*(point[d]-previous[d])
                                     for d in range(3)))
            if current >= 0:
                clipped.append(point)
        piece = tuple(clipped)
        if not piece:
            break
    return piece


def _area(piece, check):
    doubled = Fraction(0)
    for i, point in enumerate(piece):
        check()
        following = piece[(i+1) % len(piece)]
        doubled += point[0]*following[1]-point[1]*following[0]
    return abs(doubled)/2


def certify_planar_cell_top(
        mesh: IndexedTriangleMesh, cell_xy_mm: tuple[tuple[Fraction, Fraction], ...], *,
        algorithm_version: str, max_vertices: int, max_triangles: int,
        max_mesh_pair_checks: int, max_cell_vertices: int, max_centroid_tests: int,
        max_facet_clip_tests: int, cancelled: Callable[[], bool]) -> PlanarCellTopCoverage:
    _validate(mesh, (max_vertices, max_triangles, max_mesh_pair_checks,
                     max_cell_vertices, max_centroid_tests, max_facet_clip_tests), cancelled)
    if type(algorithm_version) is not str or algorithm_version != "planar_cell_top_v1":
        raise ContractError(ReasonCode.INVALID_SETTING, "unsupported planar top algorithm")
    check = _cancellation(cancelled)

    def disposition(state, reason, cell=None, plane=None, area=None):
        try:
            check()
            if plane is None:
                receipt = PlanarCellTopCoverage(state, reason, None, None, None, None, None)
            else:
                for point in cell:
                    check()
                    for _ in point:
                        check()
                receipt = PlanarCellTopCoverage(state, reason, cell, *plane, area)
            check()
            return receipt
        except _Stopped as stop:
            return PlanarCellTopCoverage(stop.state, stop.reason, None, None, None, None, None)

    try:
        check()
        area = _cell_area(cell_xy_mm, max_cell_vertices, check)
        check()
        _, topology = _embedding(mesh, max_vertices, max_triangles,
                                 max_mesh_pair_checks, cancelled, check)
        faces = len(topology.oriented_triangles)
        k = len(cell_xy_mm)
        check()
        if 3*faces > max_centroid_tests:
            raise _Stopped("incomplete", "resource-limit")
        vertices = tuple(tuple(Fraction(float(v)) for v in (point.x_mm, point.y_mm, point.z_mm))
                         for point in mesh.vertices)
        centroid = (sum((p[0] for p in cell_xy_mm), Fraction(0))/k,
                    sum((p[1] for p in cell_xy_mm), Fraction(0))/k)
        highest, selected, highest_planes = None, None, set()
        for face in topology.oriented_triangles:
            check()
            triangle = tuple(vertices[i] for i in face)
            sides = []
            for i in range(3):
                check()
                sides.append(_turn(triangle[i], triangle[(i+1) % 3], centroid))
            nz = _turn(triangle[0], triangle[1], triangle[2])
            if nz == 0 or not (all(v >= 0 for v in sides) or all(v <= 0 for v in sides)):
                continue
            plane = _plane(triangle)
            if plane is None:
                continue
            height = plane[0]*centroid[0]+plane[1]*centroid[1]+plane[2]
            if highest is None or height > highest:
                highest, selected = height, plane
                highest_planes = {plane}
            elif height == highest:
                highest_planes.add(plane)
        if selected is None:
            raise _Stopped("rejected", "no-top-facing-facet")
        if len(highest_planes) != 1:
            raise _Stopped("rejected", "ambiguous-top-plane")
        check()
        if faces*k*(k+3) > max_facet_clip_tests:
            raise _Stopped("incomplete", "resource-limit")
        covered = Fraction(0)
        for face in topology.oriented_triangles:
            check()
            triangle = tuple(vertices[i] for i in face)
            piece = _clip(triangle, cell_xy_mm, check)
            if not piece:
                continue
            a, b, c = selected
            for point in piece:
                check()
                if point[2] > a*point[0]+b*point[1]+c:
                    raise _Stopped("rejected", "above-top-plane")
            if _plane(triangle) == selected:
                covered += _area(piece, check)
        if covered > area:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "top area exceeds cell")
        if covered < area:
            raise _Stopped("rejected", "uncovered-top")
        return disposition("complete", "planar-top-covered", cell_xy_mm, selected, area)
    except _Stopped as stop:
        return disposition(stop.state, stop.reason)
