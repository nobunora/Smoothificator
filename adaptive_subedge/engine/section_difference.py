"""Exact two-plane convex-section difference, without exposed-surface authority."""
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.numeric import finite_binary64
from adaptive_subedge.domain.section_difference import ConvexSectionDifference

from .material_side import _Stopped, _cancellation, _embedding, _validate
from .mesh_section import _SectionStop, _orientation, _section


def _area(points, check):
    doubled = Fraction(0)
    for a, b in zip(points, points[1:]+points[:1]):
        check()
        doubled += a[0]*b[1]-a[1]*b[0]
    return doubled/2


def _between(a, p, b):
    return (min(a[0], b[0]) < p[0] < max(a[0], b[0])
            or min(a[1], b[1]) < p[1] < max(a[1], b[1])) and all(
                min(x, y) <= z <= max(x, y) for x, y, z in zip(a, b, p))


def _canonical(points, check):
    rows = list(points)
    while len(rows) >= 3:
        changed = False
        for i in range(len(rows)):
            check()
            previous, current, following = rows[i-1], rows[i], rows[(i+1) % len(rows)]
            if current == previous or current == following:
                rows.pop(i)
                changed = True
                break
            if _orientation(previous, current, following) == 0:
                if not _between(previous, current, following):
                    raise _Stopped("rejected", "nonconvex-section")
                rows.pop(i)
                changed = True
                break
        if not changed:
            break
    if len(rows) < 3 or _area(rows, check) == 0:
        return ()
    if _area(rows, check) < 0:
        raise _Stopped("rejected", "nonconvex-section")
    for i in range(len(rows)):
        check()
        if _orientation(rows[i-1], rows[i], rows[(i+1) % len(rows)]) <= 0:
            raise _Stopped("rejected", "nonconvex-section")
    start = 0
    for i in range(1, len(rows)):
        check()
        if rows[i] < rows[start]:
            start = i
    return tuple(rows[start:]+rows[:start])


def _section_polygon(loop, check):
    points = []
    for vertex in loop.vertices:
        check()
        points.append((vertex.x_mm, vertex.y_mm))
    points = tuple(points)
    for i in range(len(points)):
        check()
        if _orientation(points[i-1], points[i], points[(i+1) % len(points)]) < 0:
            raise _Stopped("rejected", "nonconvex-section")
    polygon = _canonical(points, check)
    if not polygon:
        raise _Stopped("rejected", "zero-area")
    return polygon


def _plane(a, b, point):
    return _orientation(a, b, point)


def _split(points, a, b, check):
    values = []
    for point in points:
        check()
        values.append(_plane(a, b, point))
    inside, outside = [], []
    for i, current in enumerate(points):
        check()
        previous = points[i-1]
        d_previous, d_current = values[i-1], values[i]
        if d_previous*d_current < 0:
            ratio = d_previous/(d_previous-d_current)
            intersection = tuple(previous[k]+ratio*(current[k]-previous[k]) for k in (0, 1))
            inside.append(intersection)
            outside.append(intersection)
        if d_current >= 0:
            inside.append(current)
        if d_current <= 0:
            outside.append(current)
    return _canonical(tuple(outside), check), _canonical(tuple(inside), check)


def derive_convex_section_difference(
        mesh: IndexedTriangleMesh, lower_z_mm: float, upper_z_mm: float, *,
        algorithm_version: str, max_vertices: int, max_triangles: int,
        max_mesh_pair_checks: int, max_section_segments: int,
        max_section_pair_checks: int, max_clip_vertex_tests: int,
        cancelled: Callable[[], bool]) -> ConvexSectionDifference:
    if not finite_binary64(lower_z_mm) or not finite_binary64(upper_z_mm):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "finite section heights required")
    lower_z, upper_z = Fraction(float(lower_z_mm)), Fraction(float(upper_z_mm))
    if lower_z >= upper_z:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "ordered section heights required")
    _validate(mesh, (max_vertices, max_triangles, max_mesh_pair_checks,
                     max_section_segments, max_section_pair_checks, max_clip_vertex_tests), cancelled)
    if type(algorithm_version) is not str or algorithm_version != "convex_section_difference_v1":
        raise ContractError(ReasonCode.INVALID_SETTING, "unsupported section difference algorithm")
    check = _cancellation(cancelled)

    def result(state, reason, lower=None, upper=None, cells=(), area=None):
        if reason == "cancelled":
            return ConvexSectionDifference(state, reason, lower_z, upper_z,
                                           None, None, (), None)
        try:
            check()
            for cell in cells:
                for point in cell:
                    check()
            candidate = ConvexSectionDifference(state, reason, lower_z, upper_z,
                                                lower, upper, cells, area)
            check()
            return candidate
        except _Stopped as stopped:
            return ConvexSectionDifference(stopped.state, stopped.reason,
                                           lower_z, upper_z, None, None, (), None)

    def get_section(topology, z):
        check()
        section = _section(topology, z, max_section_segments, max_section_pair_checks,
                           check, coplanar=Fraction(0), epsilon=Fraction(0),
                           join_tolerance=Fraction(0))
        if section.state == "empty":
            raise _Stopped("rejected", "empty-section")
        if section.state != "complete":
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "unexpected section disposition")
        return section.loop

    try:
        check()
        _, topology = _embedding(mesh, max_vertices, max_triangles, max_mesh_pair_checks,
                                 cancelled, check)
        lower = get_section(topology, lower_z)
        upper = get_section(topology, upper_z)
        lower_poly = _section_polygon(lower, check)
        upper_poly = _section_polygon(upper, check)
        n, m = len(lower_poly), len(upper_poly)
        check()
        if 2*n*m + m*m > max_clip_vertex_tests:
            raise _Stopped("incomplete", "resource-limit")
        for a, b in zip(lower_poly, lower_poly[1:]+lower_poly[:1]):
            for point in upper_poly:
                check()
                if _plane(a, b, point) < 0:
                    raise _Stopped("rejected", "non-nested-sections")
        remaining = lower_poly
        cells = []
        for a, b in zip(upper_poly, upper_poly[1:]+upper_poly[:1]):
            check()
            if not remaining:
                break
            outside, inside = _split(remaining, a, b, check)
            if outside:
                cells.append(outside)
            remaining = inside
        area = sum((_area(cell, check) for cell in cells), Fraction(0))
        if area != _area(lower_poly, check)-_area(upper_poly, check):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "section difference area mismatch")
        reason = "difference-derived" if cells else "empty-difference"
        return result("complete", reason, lower, upper, tuple(cells), area)
    except (_Stopped, _SectionStop) as stopped:
        return result(stopped.state, stopped.reason)
