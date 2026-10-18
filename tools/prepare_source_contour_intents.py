"""Generic pre-freeze source-following/parallel contour proposals, no acceptance."""
from dataclasses import asdict, dataclass, field
from fractions import Fraction as F
from hashlib import sha256
import json
import math
import re

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.freeze_supplemental_emission import (
    FrozenSupplementalEmission, freeze_numeric_emission, validate_supplemental_dimensions,
)
from tools.supplemental_z_hop import SupplementalPath, _validate_policy, rounded


class ContourProposalError(ValueError):
    def __init__(self, reason, message):
        self.reason = reason
        super().__init__(message)


@dataclass(frozen=True)
class ContourConstructionPolicy:
    construction_places: int
    max_vertices: int
    max_coordinate_bits: int
    max_intersection_checks: int

    def __post_init__(self):
        if type(self.construction_places) is not int or not 0 <= self.construction_places <= 12:
            raise ValueError('explicit construction precision0..12 required')
        if any(type(v) is not int or v < 1 for v in
               (self.max_vertices, self.max_coordinate_bits, self.max_intersection_checks)):
            raise ValueError('explicit positive finite construction limits required')


@dataclass(frozen=True)
class RemovedContourVertex:
    original_vertex_index: int
    source_segment_id: str
    reason: str
    quantized_xy_mm: tuple[F, F]


@dataclass(frozen=True)
class SourceJointDetour:
    source_segment_id: str
    locality_mm: F


@dataclass(frozen=True)
class DetourWaypoint:
    vertex_identity: str
    joint_source_segment_id: str
    direction: str
    source_segment_id: str
    source_edge_parameter: F
    walked_source_segment_ids: tuple[str, ...]
    proposed_xy_mm: tuple[F, F]
    quantized_xy_mm: tuple[F, F]


@dataclass(frozen=True)
class SourceContourProposal:
    source_sha256: str
    project_sha256: str
    source_segment_ids: tuple[str, ...]
    upper_z_mm: F
    remaining_height_mm: F
    inward_offset_mm: F
    minimum_segment_mm: F
    construction_policy: ContourConstructionPolicy
    construction_identity: str
    removed_vertices: tuple[RemovedContourVertex, ...]
    frozen_emission: FrozenSupplementalEmission
    accepted: bool = field(default=False, init=False)
    contact_verified: bool = field(default=False, init=False)
    future_volume_verified: bool = field(default=False, init=False)
    printable_authorized: bool = field(default=False, init=False)


@dataclass(frozen=True)
class SourceJointContourProposal(SourceContourProposal):
    joint_detours: tuple[SourceJointDetour, ...]
    waypoints: tuple[DetourWaypoint, ...]
    joint_replacements: tuple[tuple[str, tuple[F, F], tuple[F, F]], ...]
    initial_removed_vertex_count: int


@dataclass(frozen=True)
class CoalescedSourceContourProposal(SourceJointContourProposal):
    coalesced_source_vertex_indices: tuple[int, ...]


def _cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def _on_segment(a, b, c):
    return _cross(a, b, c) == 0 and all(min(x, y) <= z <= max(x, y) for x, y, z in zip(a, b, c))


def _intersects(a, b, c, d):
    ca, cb, cc, cd = _cross(a, b, c), _cross(a, b, d), _cross(c, d, a), _cross(c, d, b)
    return (ca*cb < 0 and cc*cd < 0 or _on_segment(a, b, c) or _on_segment(a, b, d)
            or _on_segment(c, d, a) or _on_segment(c, d, b))


def _signed_area_twice(points):
    return sum(a[0]*b[1]-a[1]*b[0] for a, b in zip(points, points[1:]+points[:1]))


def prepare_source_contour_proposal(*, source_sha256, project_sha256, contour, path_id,
        floor_z_mm, upper_z_mm, width_mm, height_mm, remaining_height_mm, inward_offset_mm,
        minimum_segment_mm, emission_policy, construction_policy, cancelled, joint_detours=(),
        coalesce_collinear_source_vertices=False):
    """Construct once, regularize before freeze, and return unaccepted immutable intent."""
    if type(construction_policy) is not ContourConstructionPolicy or not callable(cancelled):
        raise ContourProposalError('invalid-policy', 'exact construction policy and cancellation required')
    if type(coalesce_collinear_source_vertices) is not bool:
        raise ContourProposalError('invalid-policy', 'exact explicit collinear-coalescing flag required')
    _validate_policy(emission_policy)
    for digest in (source_sha256, project_sha256):
        if type(digest) is not str or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ContourProposalError('invalid-identity', 'source/project SHA256 identities required')
    if type(path_id) is not str or not re.fullmatch('[A-Za-z0-9_-]+', path_id):
        raise ContourProposalError('invalid-identity', 'safe path identity required')
    numbers = (floor_z_mm, upper_z_mm, width_mm, height_mm, remaining_height_mm, inward_offset_mm, minimum_segment_mm)
    if any(type(v) is not F for v in numbers) or floor_z_mm < 0 or upper_z_mm <= floor_z_mm:
        raise ContourProposalError('invalid-dimensions', 'exact ordered floor/upper and dimensions required')
    if inward_offset_mm < 0 or minimum_segment_mm < 0:
        raise ContourProposalError('invalid-dimensions', 'nonnegative exact offset and minimum segment required')
    try:
        validate_supplemental_dimensions(floor_z_mm, width_mm, height_mm, remaining_height_mm, emission_policy)
    except ValueError as exc:
        raise ContourProposalError('invalid-dimensions', str(exc)) from exc
    top = floor_z_mm+remaining_height_mm
    if top > upper_z_mm:
        raise ContourProposalError('invalid-dimensions', 'top must remain within next layer and exactly representable')
    if type(contour) is not tuple or len(contour) < 3 or any(type(s) is not ExactNominalTopSegment for s in contour):
        raise ContourProposalError('invalid-contour', 'immutable ordered structural contour required')
    if len(contour) > construction_policy.max_vertices:
        raise ContourProposalError('resource-limit', 'source contour exceeds vertex budget')
    if len({s.segment_id for s in contour}) != len(contour):
        raise ContourProposalError('invalid-contour', 'unique source segment identities required')
    if (type(joint_detours) is not tuple or any(type(d) is not SourceJointDetour for d in joint_detours)
            or any(type(d.locality_mm) is not F or d.locality_mm <= 0 for d in joint_detours)
            or any(type(d.source_segment_id) is not str for d in joint_detours)
            or len({d.source_segment_id for d in joint_detours}) != len(joint_detours)
            or any(d.source_segment_id not in {s.segment_id for s in contour} for d in joint_detours)):
        raise ContourProposalError('invalid-detour', 'unique existing original start-joint identities and exact positive locality required')
    cancellation_latched, checks = False, 0

    def checkpoint():
        nonlocal cancellation_latched
        answer = cancelled()
        if type(answer) is not bool:
            raise ContourProposalError('invalid-policy', 'cancellation must return exact bool')
        cancellation_latched = cancellation_latched or answer
        if cancellation_latched:
            raise ContourProposalError('cancelled', 'source contour construction cancelled')

    def check_bits(coordinates):
        if any(integer.bit_length() > construction_policy.max_coordinate_bits for value in coordinates
               for integer in (value.numerator, value.denominator)):
            raise ContourProposalError('resource-limit', 'construction coordinate bit budget exceeded')

    checkpoint()
    check_bits(numbers)
    check_bits(tuple(d.locality_mm for d in joint_detours))
    for a, b in zip(contour, contour[1:]+contour[:1]):
        checkpoint()
        check_bits((*a.start_xyz_mm, *a.end_xyz_mm, a.width_mm, a.height_mm))
        if (a.source_kind != 'structural' or a.start_xyz_mm[2] != floor_z_mm or a.end_xyz_mm[2] != floor_z_mm
                or a.end_xyz_mm != b.start_xyz_mm):
            raise ContourProposalError('invalid-contour', 'closed connected constant-floor structural contour required')
    original = tuple(s.start_xyz_mm[:2] for s in contour)

    def validate_polygon(points):
        nonlocal checks
        if len(points) < 3 or _signed_area_twice(points) == 0 or any(a == b for a, b in zip(points, points[1:]+points[:1])):
            raise ContourProposalError('degenerate-contour', 'nondegenerate closed polygon required')
        edges = tuple(zip(points, points[1:]+points[:1]))
        for i, (a, b) in enumerate(edges):
            c = edges[(i+1) % len(edges)][1]
            if _cross(a, b, c) == 0 and sum((b[k]-a[k])*(c[k]-b[k]) for k in range(2)) <= 0:
                raise ContourProposalError('nonsimple-contour', 'overlapping adjacent contour edges')
            for j in range(i+1, len(edges)):
                checkpoint()
                if j == i+1 or i == 0 and j == len(edges)-1:
                    continue
                checks += 1
                if checks > construction_policy.max_intersection_checks:
                    raise ContourProposalError('resource-limit', 'simple-contour intersection budget exceeded')
                if _intersects(a, b, *edges[j]):
                    raise ContourProposalError('nonsimple-contour', 'self-intersecting or self-touching contour')

    validate_polygon(original)
    orientation = 1 if _signed_area_twice(original) > 0 else -1
    protected = {i for i, segment in enumerate(contour)
                 if segment.segment_id in {d.source_segment_id for d in joint_detours}}
    active_indices, coalesced = list(range(len(original))), []
    if coalesce_collinear_source_vertices:
        while True:
            removal = None
            for position, index in enumerate(active_indices):
                checkpoint()
                checks += 1
                if checks > construction_policy.max_intersection_checks:
                    raise ContourProposalError('resource-limit', 'collinear construction check budget exceeded')
                a, b, c = (original[active_indices[j % len(active_indices)]] for j in (position-1, position, position+1))
                if _cross(a, b, c) == 0 and sum((b[k]-a[k])*(c[k]-b[k]) for k in range(2)) > 0:
                    if index in protected:
                        raise ContourProposalError('unsupported-detour', 'selected source joint is collinear and cannot be coalesced')
                    removal = position
                    break
            if removal is None:
                break
            coalesced.append(active_indices.pop(removal))
            if len(active_indices) < 3:
                raise ContourProposalError('degenerate-contour', 'collinear coalescing collapsed construction')
    offset_original = tuple(original[i] for i in active_indices)
    proposed = offset_original
    def finite_float(value):
        try:
            proposed_float = float(value)
        except OverflowError as exc:
            raise ContourProposalError('unsupported-offset', 'construction value exceeds finite float range') from exc
        if not math.isfinite(proposed_float):
            raise ContourProposalError('unsupported-offset', 'nonfinite construction value')
        return proposed_float
    if inward_offset_mm > 0:
        if any(_cross(a, b, c) == 0 for a, b, c in zip(offset_original, offset_original[1:]+offset_original[:1], offset_original[2:]+offset_original[:2])):
            raise ContourProposalError('unsupported-offset', 'collinear adjacent source edges need explicit handling')
        lines = []
        for a, b in zip(offset_original, offset_original[1:]+offset_original[:1]):
            checkpoint()
            dx, dy = finite_float(b[0]-a[0]), finite_float(b[1]-a[1])
            length = math.hypot(dx, dy)
            if not math.isfinite(length) or length <= 0:
                raise ContourProposalError('unsupported-offset', 'nonfinite construction edge')
            nx, ny = -orientation*dy/length, orientation*dx/length
            lines.append(((finite_float(a[0])+finite_float(inward_offset_mm)*nx,
                           finite_float(a[1])+finite_float(inward_offset_mm)*ny), (dx, dy)))
        proposals = []
        for (a, u), (b, v) in zip(lines[-1:]+lines[:-1], lines):
            checkpoint()
            determinant = u[0]*v[1]-u[1]*v[0]
            if determinant == 0:
                raise ContourProposalError('unsupported-offset', 'collinear/parallel adjacent offset lines')
            t = ((b[0]-a[0])*v[1]-(b[1]-a[1])*v[0])/determinant
            point = tuple(a[i]+t*u[i] for i in range(2))
            if any(not math.isfinite(v) for v in point):
                raise ContourProposalError('unsupported-offset', 'nonfinite miter proposal')
            proposals.append(tuple(F(f'{v:.{construction_policy.construction_places}f}') for v in point))
        proposed = tuple(proposals)
    vertices = [(i, tuple(rounded(v, emission_policy.xyz_places) for v in point)) for i, point in zip(active_indices, proposed)]
    removed = [RemovedContourVertex(i, contour[i].segment_id, 'exact-codirectional-source-vertex',
        tuple(rounded(v, emission_policy.xyz_places) for v in original[i])) for i in coalesced]
    waypoints, replacements = [], []
    source_positions = dict(enumerate(original))

    def regularize():
        while True:
            checkpoint()
            duplicate = next((i for i in range(len(vertices)) if vertices[i][1] == vertices[i-1][1]), None)
            if duplicate is not None:
                end, reason = duplicate, 'grid-duplicate'
            else:
                lengths = [sum((y-x)**2 for x, y in zip(a[1], b[1])) for a, b in zip(vertices, vertices[1:]+vertices[:1])]
                shortest = min(range(len(lengths)), key=lambda i: (lengths[i], i))
                if lengths[shortest] >= minimum_segment_mm**2:
                    break
                end, reason = (shortest+1) % len(vertices), 'declared-short-edge'
            start = (end-1) % len(vertices)
            if vertices[end][0] in protected:
                if vertices[start][0] in protected:
                    raise ContourProposalError('unsupported-detour', 'protected detour vertices share a duplicate/short edge')
                end = start
            index, point = vertices.pop(end)
            # All generated waypoint vertices are protected; only original
            # vertices can reach removal, so their original indices stay honest.
            removed.append(RemovedContourVertex(index, contour[index].segment_id, reason, point))
            if len(vertices) < 3:
                raise ContourProposalError('degenerate-contour', 'regularization collapsed contour')

    regularize()
    initial_removed_count = len(removed)
    occupied = []

    def waypoint_at(joint, detour, reverse):
        nonlocal checks
        remaining = finite_float(detour.locality_mm)
        traversed = []
        for step in range(len(contour)):
            checkpoint()
            checks += 1
            if checks > construction_policy.max_intersection_checks:
                raise ContourProposalError('resource-limit', 'detour walk/check budget exceeded')
            edge = (joint-1-step if reverse else joint+step) % len(contour)
            a, b = original[edge], original[(edge+1) % len(contour)]
            dx, dy = (finite_float(b[k]-a[k]) for k in range(2))
            length = math.hypot(dx, dy)
            if not math.isfinite(length) or length <= 0:
                raise ContourProposalError('unsupported-detour', 'nonfinite/degenerate source walk')
            traversed.append(contour[edge].segment_id)
            used = min(remaining, length)
            parameter = F(str(1-used/length if reverse else used/length))
            interval = (edge, parameter if reverse else F(0), F(1) if reverse else parameter)
            if interval[1] >= interval[2]:
                raise ContourProposalError('unsupported-detour', 'ambiguous source walk precision')
            if any(edge == old[0] and max(interval[1], old[1]) < min(interval[2], old[2]) for old in occupied):
                raise ContourProposalError('overlapping-detours', 'detour source neighborhoods overlap or wrap')
            occupied.append(interval)
            if remaining <= length:
                nx, ny = -orientation*dy/length, orientation*dx/length
                source_point = tuple(a[k]+parameter*(b[k]-a[k]) for k in range(2))
                t = float(parameter)
                offset_point = (finite_float(a[0])+t*dx+finite_float(inward_offset_mm)*nx,
                                finite_float(a[1])+t*dy+finite_float(inward_offset_mm)*ny)
                if any(not math.isfinite(v) for v in offset_point):
                    raise ContourProposalError('unsupported-detour', 'nonfinite source waypoint')
                proposed_point = tuple(F(f'{v:.{construction_policy.construction_places}f}') for v in offset_point)
                point = tuple(rounded(v, emission_policy.xyz_places) for v in proposed_point)
                identity = f'detour:{joint}:{"before" if reverse else "after"}'
                check_bits((*source_point, parameter, *proposed_point, *point))
                source_positions[identity] = source_point
                waypoints.append(DetourWaypoint(identity, detour.source_segment_id,
                    'before' if reverse else 'after', contour[edge].segment_id, parameter,
                    tuple(traversed), proposed_point, point))
                return identity, point
            remaining -= length
        raise ContourProposalError('unsupported-detour', 'detour locality wraps entire original contour')

    for detour in joint_detours:
        joint = next(i for i, s in enumerate(contour) if s.segment_id == detour.source_segment_id)
        location = next((i for i, vertex in enumerate(vertices) if vertex[0] == joint), None)
        if location is None:
            raise ContourProposalError('vanished-joint', 'selected source joint was removed by initial regularization')
        before, after = waypoint_at(joint, detour, True), waypoint_at(joint, detour, False)
        actual_joint = tuple(rounded(v, emission_policy.xyz_places) for v in original[joint])
        replacements.append((detour.source_segment_id, vertices[location][1], actual_joint))
        # At index0 keep closure order joint,after,...,before for default parity.
        if location == 0:
            vertices = [(joint, actual_joint), after]+vertices[1:]+[before]
        else:
            vertices[location:location+1] = [before, (joint, actual_joint), after]
        protected.update((joint, before[0], after[0]))
        if len(vertices) > construction_policy.max_vertices:
            raise ContourProposalError('resource-limit', 'detour expanded vertex budget exceeded')
    if joint_detours:
        regularize()
    points = tuple(point for index, point in vertices)
    for point in points:
        check_bits(point)
    validate_polygon(points)
    if _signed_area_twice(points)*orientation <= 0:
        raise ContourProposalError('unsupported-offset', 'construction changed contour orientation')
    if inward_offset_mm > 0:
        for (i, a), (j, b) in zip(vertices, vertices[1:]+vertices[:1]):
            if sum((b[k]-a[k])*(source_positions[j][k]-source_positions[i][k]) for k in range(2)) <= 0:
                raise ContourProposalError('unsupported-offset', 'offset collapsed/reversed source edge direction')
    path = SupplementalPath(path_id, floor_z_mm, width_mm, height_mm,
                            tuple((*point, top) for point in points+points[:1]))
    checkpoint()
    frozen = freeze_numeric_emission(path, emission_policy)
    checkpoint()
    identity = sha256(json.dumps({'construction': asdict(construction_policy),
        'emission_policy_identity': frozen.policy_identity}, sort_keys=True, separators=(',', ':')).encode('ascii')).hexdigest()
    if joint_detours or coalesce_collinear_source_vertices:
        identity = sha256(json.dumps({'base': identity, 'detours': [asdict(d) for d in joint_detours],
            'waypoints': [asdict(w) for w in waypoints], 'replacements': replacements,
            'removed': [asdict(v) for v in removed], 'initial_removed_count': initial_removed_count,
            **({'collinear_coalescing': True, 'coalesced_indices': coalesced} if coalesce_collinear_source_vertices else {})},
            sort_keys=True, separators=(',', ':'), default=str).encode('ascii')).hexdigest()
        arguments = (source_sha256, project_sha256, tuple(s.segment_id for s in contour), upper_z_mm,
            remaining_height_mm, inward_offset_mm, minimum_segment_mm, construction_policy, identity, tuple(removed), frozen,
            joint_detours, tuple(waypoints), tuple(replacements), initial_removed_count)
        return (CoalescedSourceContourProposal(*arguments, tuple(coalesced)) if coalesce_collinear_source_vertices
                else SourceJointContourProposal(*arguments))
    return SourceContourProposal(source_sha256, project_sha256, tuple(s.segment_id for s in contour), upper_z_mm,
        remaining_height_mm, inward_offset_mm, minimum_segment_mm, construction_policy, identity, tuple(removed), frozen)
