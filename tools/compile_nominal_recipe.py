"""Generic immutable geometry recipe construction for conditional job review."""
from dataclasses import asdict, dataclass
from fractions import Fraction as F
from hashlib import sha256
import json
import math
import re

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.build_revolved_top_review import ring_vertices
from tools.freeze_supplemental_emission import FrozenSupplementalEmission, freeze_numeric_emission, validate_supplemental_dimensions
from tools.prepare_executable_ring_intents import radial_segment_in_band
from tools.prepare_source_contour_intents import (
    ContourConstructionPolicy, SourceJointDetour, _cross, _intersects, _signed_area_twice, prepare_source_contour_proposal,
)
from tools.supplemental_z_hop import SupplementalPath, _validate_policy, rounded


@dataclass(frozen=True)
class CircleRecipe:
    center_xy_mm: tuple[F, F]
    radius_mm: F
    chord_count: int
    radial_band_budget_mm: F


@dataclass(frozen=True)
class GridVertexDisplacement:
    original_generated_vertex_index: int
    delta_xy_mm: tuple[F, F]
    reason: str


@dataclass(frozen=True)
class ContourRecipe:
    contour: tuple[ExactNominalTopSegment, ...]
    inward_offset_mm: F
    minimum_segment_mm: F
    detours: tuple[SourceJointDetour, ...] = ()
    retained_edge_indices: tuple[int, ...] | None = None
    vertex_displacements: tuple[GridVertexDisplacement, ...] = ()
    coalesce_collinear_source_vertices: bool = False


@dataclass(frozen=True)
class ExplicitPatchRecipe:
    points_xyz_mm: tuple[tuple[F, F, F], ...]
    support_source_segment_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class PinnedRingRecipe:
    original_path: SupplementalPath
    original_source_sha256: str
    original_project_sha256: str
    original_manifest_sha256: str
    center_xy_mm: tuple[F, F]
    radius_mm: F
    radial_band_budget_mm: F


@dataclass(frozen=True)
class CompiledNominalRecipe:
    proposal_id: str
    emitted_path_id: str
    recipe_identity: str
    source_sha256: str
    project_sha256: str
    upper_z_mm: F
    frozen_emission: FrozenSupplementalEmission
    construction_reference: object | None
    removed_reference_edge_indices: tuple[int, ...]
    geometry_matches_reference: bool
    relative_e_matches_reference: bool
    widths_match_reference: bool


def compile_nominal_recipe(*, proposal_id, emitted_path_id, source_sha256, project_sha256,
        floor_z_mm, upper_z_mm, width_mm, height_mm, remaining_height_mm,
        recipe, emission_policy, construction_policy, cancelled,
        reference_points=(), reference_relative_e=(), reference_widths=()):
    """Construct proposed geometry, then freeze final numeric emission once.

    A closed-contour reference can precede an explicit open arc. Its old numeric
    acceptance is never inherited: displacement/cuts create a separate intent.
    """
    if (type(proposal_id) is not str or not proposal_id or type(emitted_path_id) is not str
            or not re.fullmatch('[A-Za-z0-9_-]+', emitted_path_id)
            or type(construction_policy) is not ContourConstructionPolicy or not callable(cancelled)):
        raise ValueError('explicit proposal/emitted identities and bounded construction policy required')
    for digest in (source_sha256, project_sha256):
        if type(digest) is not str or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('source/project SHA256 required')
    if any(type(v) is not F for v in (floor_z_mm, upper_z_mm, width_mm, height_mm, remaining_height_mm)):
        raise ValueError('exact recipe dimensions required')
    if not 0 <= floor_z_mm < upper_z_mm or not 0 < remaining_height_mm <= upper_z_mm-floor_z_mm:
        raise ValueError('ordered source interval must contain declared recipe top')
    _validate_policy(emission_policy)
    validate_supplemental_dimensions(floor_z_mm, width_mm, height_mm, remaining_height_mm, emission_policy)

    def check_bits(numbers):
        if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > construction_policy.max_coordinate_bits for v in numbers):
            raise ValueError('recipe coordinate bit limit')

    check_bits((floor_z_mm, upper_z_mm, width_mm, height_mm, remaining_height_mm))

    def checkpoint():
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('exact bool cancellation required')
        if answer:
            raise ValueError('recipe compilation cancelled')

    checkpoint()
    top = floor_z_mm+remaining_height_mm
    construction, removed, expected_orientation = None, (), None
    if type(recipe) is CircleRecipe:
        if (type(recipe.center_xy_mm) is not tuple or len(recipe.center_xy_mm) != 2
                or any(type(v) is not F for v in recipe.center_xy_mm)
                or type(recipe.radius_mm) is not F or recipe.radius_mm <= 0
                or type(recipe.radial_band_budget_mm) is not F or recipe.radial_band_budget_mm < 0
                or type(recipe.chord_count) is not int or not 3 <= recipe.chord_count <= construction_policy.max_vertices):
            raise ValueError('bounded phase-zero exact circle recipe required')
        check_bits((*recipe.center_xy_mm, recipe.radius_mm, recipe.radial_band_budget_mm))
        try:
            finite_coordinates = tuple(map(float, (*recipe.center_xy_mm, recipe.radius_mm)))
        except OverflowError as exc:
            raise ValueError('nonfinite recipe circle construction') from exc
        if any(not math.isfinite(v) for v in finite_coordinates):
            raise ValueError('nonfinite recipe circle construction')
        points = ring_vertices(finite_coordinates[:2], recipe.radius_mm, top, recipe.chord_count)
        points = tuple(tuple(rounded(v, emission_policy.xyz_places) for v in p) for p in points)
        expected_orientation = 1
    elif type(recipe) is ContourRecipe:
        construction = prepare_source_contour_proposal(source_sha256=source_sha256, project_sha256=project_sha256,
            contour=recipe.contour, path_id=emitted_path_id+'-closed-reference', floor_z_mm=floor_z_mm,
            upper_z_mm=upper_z_mm, width_mm=width_mm, height_mm=height_mm, remaining_height_mm=remaining_height_mm,
            inward_offset_mm=recipe.inward_offset_mm, minimum_segment_mm=recipe.minimum_segment_mm,
            emission_policy=emission_policy, construction_policy=construction_policy, cancelled=cancelled,
            joint_detours=recipe.detours, coalesce_collinear_source_vertices=recipe.coalesce_collinear_source_vertices)
        points = construction.frozen_emission.path.points_mm
        expected_orientation = 1 if _signed_area_twice(tuple(p[:2] for p in points[:-1])) > 0 else -1
        if type(recipe.vertex_displacements) is not tuple:
            raise ValueError('immutable explicit pre-freeze displacement tuple required')
        displaced, seen = list(points[:-1]), set()
        for displacement in recipe.vertex_displacements:
            checkpoint()
            if (type(displacement) is not GridVertexDisplacement
                    or type(displacement.original_generated_vertex_index) is not int
                    or not 0 <= displacement.original_generated_vertex_index < len(displaced)
                    or displacement.original_generated_vertex_index in seen
                    or type(displacement.delta_xy_mm) is not tuple or len(displacement.delta_xy_mm) != 2
                    or any(type(v) is not F for v in displacement.delta_xy_mm)
                    or type(displacement.reason) is not str or not displacement.reason.strip()):
                raise ValueError('unique existing generated vertex, exact vector and reason required')
            i = displacement.original_generated_vertex_index
            check_bits(displacement.delta_xy_mm)
            seen.add(i)
            displaced[i] = tuple(displaced[i][k]+displacement.delta_xy_mm[k] for k in range(2))+(top,)
        points = tuple(displaced)+(displaced[0],)
        if recipe.retained_edge_indices is not None:
            retained = recipe.retained_edge_indices
            count = len(displaced)
            if (type(retained) is not tuple or not retained
                    or any(type(i) is not int or not 0 <= i < count for i in retained)
                    or len(set(retained)) != len(retained)
                    or any(b != (a+1) % count for a, b in zip(retained, retained[1:]))
                    or len(retained) >= count):
                raise ValueError('one explicit contiguous open arc without reconnection required')
            removed = tuple(i for i in range(count) if i not in retained)
            points = (points[retained[0]],)+tuple(points[i+1] for i in retained)
    elif type(recipe) is ExplicitPatchRecipe:
        if (type(recipe.support_source_segment_ids) is not tuple or not recipe.support_source_segment_ids
                or any(type(i) is not str or not i for i in recipe.support_source_segment_ids)
                or type(recipe.reason) is not str or not recipe.reason.strip()):
            raise ValueError('explicit patch support identities and construction reason required')
        points = recipe.points_xyz_mm
    elif type(recipe) is PinnedRingRecipe:
        for digest in (recipe.original_source_sha256, recipe.original_project_sha256, recipe.original_manifest_sha256):
            if type(digest) is not str or not re.fullmatch('[0-9a-f]{64}', digest):
                raise ValueError('pinned original ring construction provenance required')
        if type(recipe.original_path) is not SupplementalPath or recipe.original_path.floor_z_mm != floor_z_mm:
            raise ValueError('exact original ring factory path at declared floor required')
        points = tuple((*p[:2], top) for p in recipe.original_path.points_mm)
        expected_orientation = 1 if _signed_area_twice(tuple(p[:2] for p in points[:-1])) > 0 else -1
    else:
        raise ValueError('unknown nominal recipe kind')
    if (type(points) is not tuple or not 2 <= len(points) <= construction_policy.max_vertices+1
            or any(type(p) is not tuple or len(p) != 3 or any(type(v) is not F for v in p) for p in points)):
        raise ValueError('bounded exact immutable recipe XYZ graph required')
    if any(p[2] != top for p in points):
        raise ValueError('recipe top differs from declared floor/remaining height')
    check_bits(tuple(v for p in points for v in p))
    # Shared numeric rounding is part of the geometry actually emitted. Validate
    # that graph, so off-grid inputs cannot hide intersections introduced by XYZ.
    points = tuple(tuple(rounded(v, emission_policy.xyz_places) for v in p) for p in points)
    closed = points[0] == points[-1]
    if closed:
        area = _signed_area_twice(tuple(p[:2] for p in points[:-1]))
        if area == 0 or expected_orientation is not None and area*expected_orientation <= 0:
            raise ValueError('final quantized closed graph has zero area or reversed orientation')
    triples = tuple(zip(points, points[1:], points[2:]))
    if closed:
        triples += ((points[-2], points[0], points[1]),)
    for a, b, c in triples:
        if _cross(a, b, c) == 0 and sum((b[k]-a[k])*(c[k]-b[k]) for k in (0, 1)) <= 0:
            raise ValueError('final quantized graph has adjacent overlap/backtracking')
    intersection_checks = 0
    for i, (a, b) in enumerate(zip(points, points[1:])):
        checkpoint()
        if a == b:
            raise ValueError('zero-length proposed recipe edge')
        if type(recipe) in (CircleRecipe, PinnedRingRecipe) and not radial_segment_in_band(a[:2], b[:2],
                recipe.center_xy_mm, recipe.radius_mm, recipe.radial_band_budget_mm):
            raise ValueError('recipe circle outside exact radial band')
        for j in range(i+2, len(points)-1):
            checkpoint()
            if i == 0 and points[0] == points[-1] and j == len(points)-2:
                continue
            intersection_checks += 1
            if intersection_checks > construction_policy.max_intersection_checks:
                raise ValueError('recipe intersection check budget')
            if _intersects(a[:2], b[:2], points[j][:2], points[j+1][:2]):
                raise ValueError('self-intersecting proposed recipe')
    path = SupplementalPath(emitted_path_id, floor_z_mm, width_mm, height_mm, points)
    frozen = freeze_numeric_emission(path, emission_policy)
    checkpoint()
    identity = sha256(json.dumps(asdict(recipe), sort_keys=True, separators=(',', ':'), default=str).encode('ascii')).hexdigest()
    return CompiledNominalRecipe(proposal_id, emitted_path_id, identity, source_sha256, project_sha256,
        upper_z_mm, frozen, construction, removed, frozen.path.points_mm == reference_points,
        frozen.relative_e_mm == reference_relative_e, frozen.physical_width_mm == reference_widths)
