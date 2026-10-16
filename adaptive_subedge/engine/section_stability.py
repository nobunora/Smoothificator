"""Continuous exact event-partition bounds for a supplied Z uncertainty interval."""
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.numeric import finite_binary64
from adaptive_subedge.domain.section_stability import SectionStabilityResult
from adaptive_subedge.domain.settings import MeshSectionPolicy
from .material_side import _Stopped, _cancellation, _embedding, _validate
from .mesh_section import _SectionStop, _section


def _event_guard(topology, points, z, loop, check):
    represented = {v.source_vertex_ids for v in loop.vertices}
    for i, point in enumerate(points):
        check()
        if point[2] == z and (i,) not in represented:
            raise _Stopped("incomplete", "topology-event-unproven")
    for a, b, first, second in topology.edges:
        check()
        if points[a][2] != z or points[b][2] != z:
            continue
        thirds = [next(i for i in topology.mesh.triangles[face] if i not in (a, b))
                  for face in (first, second)]
        if (points[thirds[0]][2]-z)*(points[thirds[1]][2]-z) >= 0:
            raise _Stopped("incomplete", "topology-event-unproven")


def _slab_speed(points, loop, check):
    maximum_xy_speed = Fraction(0)
    for vertex in loop.vertices:
        check()
        a, b = (points[i] for i in vertex.source_vertex_ids)
        speed = (abs(b[0]-a[0])+abs(b[1]-a[1])) / abs(b[2]-a[2])
        maximum_xy_speed = max(maximum_xy_speed, speed)
    return 1+maximum_xy_speed


def certify_section_stability(mesh: IndexedTriangleMesh, command_z_mm: float,
                              uncertainty_halfwidth_mm: float, *, policy: MeshSectionPolicy,
                              max_vertices: int, max_triangles: int, max_mesh_pair_checks: int,
                              max_section_segments: int, max_section_pair_checks: int,
                              max_section_queries: int,
                              cancelled: Callable[[], bool]) -> SectionStabilityResult:
    if (not finite_binary64(command_z_mm) or not finite_binary64(uncertainty_halfwidth_mm)
            or float(uncertainty_halfwidth_mm) <= 0):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "finite Z and positive halfwidth required")
    _validate(mesh, (max_vertices, max_triangles, max_mesh_pair_checks, max_section_segments,
                     max_section_pair_checks, max_section_queries), cancelled)
    if (type(policy) is not MeshSectionPolicy or policy.version != "indexed_plane_section_v1"
            or policy.section_stability_sampling_convergence_version != "exact_event_partition_v1"):
        raise ContractError(ReasonCode.INVALID_SETTING, "unsupported section stability policy")
    center, halfwidth = Fraction(float(command_z_mm)), Fraction(float(uncertainty_halfwidth_mm))
    lower, upper = center-halfwidth, center+halfwidth
    check = _cancellation(cancelled)
    try:
        _, topology = _embedding(mesh, max_vertices, max_triangles, max_mesh_pair_checks,
                                  cancelled, check)
        points, knots = [], {lower, center, upper}
        for vertex in mesh.vertices:
            check()
            point = tuple(Fraction(float(v)) for v in (vertex.x_mm, vertex.y_mm, vertex.z_mm))
            points.append(point)
            if lower <= point[2] <= upper:
                knots.add(point[2])
        knots = sorted(knots)
        if 2*len(knots)-1 > max_section_queries:
            raise _Stopped("incomplete", "resource-limit")
        left_bound = right_bound = Fraction(0)
        for index, z in enumerate(knots):
            check()
            section = _section(topology, z, max_section_segments, max_section_pair_checks, check,
                               coplanar=Fraction(0), epsilon=Fraction(0), join_tolerance=Fraction(0))
            if section.state == "empty":
                raise _Stopped("rejected", "non-simple-section")
            _event_guard(topology, points, z, section.loop, check)
            if index == len(knots)-1:
                continue
            following = knots[index+1]
            check()
            midpoint = _section(topology, (z+following)/2, max_section_segments,
                                max_section_pair_checks, check, coplanar=Fraction(0),
                                epsilon=Fraction(0), join_tolerance=Fraction(0))
            if midpoint.state == "empty":
                raise _Stopped("rejected", "non-simple-section")
            displacement = _slab_speed(points, midpoint.loop, check)*(following-z)
            check()
            if following <= center:
                left_bound += displacement
            else:
                right_bound += displacement
        bound = max(left_bound, right_bound)
        check()
        if bound > Fraction(float(policy.section_quantization_geometry_tolerance_mm)):
            return SectionStabilityResult("incomplete", "displacement-unproven", lower, upper, bound)
        return SectionStabilityResult("complete", "stable", lower, upper, bound)
    except (_Stopped, _SectionStop) as stopped:
        return SectionStabilityResult(stopped.state, stopped.reason, lower, upper, None)
