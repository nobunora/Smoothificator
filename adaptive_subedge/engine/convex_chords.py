"""Bounded axis-aligned chord proposals with exact transverse-footprint containment."""
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.convex_chords import ChordProposal, ConvexChordProposalSet
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.numeric import finite_binary64
from .material_side import _Stopped, _cancellation, _classify_segment, _embedding, _validate
from .mesh_section import _SectionStop, _orientation, _section


def _convex_halfplanes(loop, check):
    points = [(v.x_mm, v.y_mm) for v in loop.vertices]
    planes = []
    for i, start in enumerate(points):
        check()
        end, following = points[(i+1) % len(points)], points[(i+2) % len(points)]
        if _orientation(start, end, following) < 0:
            raise _Stopped("rejected", "nonconvex-section")
        dx, dy = end[0]-start[0], end[1]-start[1]
        planes.append((-dy, dx, dy*start[0]-dx*start[1]))
    return points, planes


def _propose(position, running, width, trim, bounds, planes, triangles, z, max_rays, check):
    lower, upper = bounds
    for a, b, c in planes:
        check()
        slope, transverse = (a, b) if running == 0 else (b, a)
        constant = transverse*position+c-abs(transverse)*width/2
        if slope == 0:
            if constant < 0:
                return ChordProposal(position, "rejected", "empty-footprint", None, None)
        elif slope > 0:
            lower = max(lower, -constant/slope)
        else:
            upper = min(upper, -constant/slope)
        if lower > upper:
            return ChordProposal(position, "rejected", "empty-footprint", None, None)
    lower, upper = lower+trim, upper-trim
    if lower >= upper:
        return ChordProposal(position, "rejected", "insufficient-span", None, None)
    start = (lower, position) if running == 0 else (position, lower)
    end = (upper, position) if running == 0 else (position, upper)
    side = _classify_segment(triangles, (*start, z), (*end, z), max_rays, check)
    if side == "strictly-inside":
        return ChordProposal(position, "proposed", "unscored", start, end)
    reason = "centerline-contact" if side == "boundary-contact" else "centerline-outside"
    return ChordProposal(position, "rejected", reason, None, None)


def propose_convex_chords(mesh: IndexedTriangleMesh, command_z_mm: float, *,
                          axis: str, width_mm: float, end_trim_mm: float,
                          chord_positions_mm: tuple[float, ...], algorithm_version: str,
                          max_positions: int, max_vertices: int, max_triangles: int,
                          max_mesh_pair_checks: int, max_section_segments: int,
                          max_section_pair_checks: int, max_ray_directions: int,
                          cancelled: Callable[[], bool]) -> ConvexChordProposalSet:
    if (not finite_binary64(command_z_mm) or type(axis) is not str or axis not in ("X", "Y")
            or not finite_binary64(width_mm) or float(width_mm) <= 0
            or not finite_binary64(end_trim_mm) or float(end_trim_mm) <= 0
            or type(chord_positions_mm) is not tuple):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid chord geometry inputs")
    _validate(mesh, (max_positions, max_vertices, max_triangles, max_mesh_pair_checks,
                     max_section_segments, max_section_pair_checks, max_ray_directions), cancelled)
    if type(algorithm_version) is not str or algorithm_version != "convex_axis_chords_v1":
        raise ContractError(ReasonCode.INVALID_SETTING, "unsupported chord algorithm")
    z, width, trim = (Fraction(float(x)) for x in (command_z_mm, width_mm, end_trim_mm))
    check = _cancellation(cancelled)
    try:
        check()
        if len(chord_positions_mm) > max_positions:
            raise _Stopped("incomplete", "resource-limit")
        if not chord_positions_mm:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "nonempty chord positions required")
        positions = set()
        for position in chord_positions_mm:
            check()
            if not finite_binary64(position):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "finite chord position required")
            position = Fraction(float(position))
            if position in positions:
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "duplicate normalized chord position")
            positions.add(position)
        check()
        triangles, topology = _embedding(mesh, max_vertices, max_triangles, max_mesh_pair_checks,
                                         cancelled, check)
        check()
        section = _section(topology, z, max_section_segments, max_section_pair_checks, check,
                           coplanar=Fraction(0), epsilon=Fraction(0), join_tolerance=Fraction(0))
        if section.state == "empty":
            raise _Stopped("rejected", "empty-section")
        points, planes = _convex_halfplanes(section.loop, check)
        running = 0 if axis == "X" else 1
        bounds = min(p[running] for p in points), max(p[running] for p in points)
        proposals = []
        for position in sorted(positions):
            check()
            proposals.append(_propose(position, running, width, trim, bounds, planes, triangles,
                                       z, max_ray_directions, check))
        check()
        return ConvexChordProposalSet("complete", "proposals-evaluated", z, axis, width, tuple(proposals))
    except (_Stopped, _SectionStop) as stopped:
        return ConvexChordProposalSet(stopped.state, stopped.reason, z, axis, width, ())
