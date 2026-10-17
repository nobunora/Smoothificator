"""Certified bounds on actual stadium-sweep support over a closed XY rectangle."""
from fractions import Fraction
from math import isqrt
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.convex_chords import ChordProposal
from adaptive_subedge.domain.numeric import finite_binary64
from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.domain.support_cell import (
    ExactNominalTopBounds, ExactNominalTopSegment, ExactTopCellXY,
    NominalStructuralTopBounds, NominalSupportSegment, SupportCellQueryPolicy,
    SupportCellQueryResult, SupportCellXY,
)


def _r(value: float) -> Fraction:
    return Fraction(float(value))


def _sqrt_bounds(radicand: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    denominator = 1 << bits
    root = isqrt((radicand.numerator << (2 * bits)) // radicand.denominator)
    lower = Fraction(root, denominator)
    upper = lower if lower * lower == radicand else Fraction(root + 1, denominator)
    return lower, upper


def _cap_bounds(lateral_squared: Fraction, radius: Fraction,
                flat_half_width: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    if lateral_squared <= flat_half_width * flat_half_width:
        return radius, radius
    lateral_lower, lateral_upper = _sqrt_bounds(lateral_squared, bits)
    side_lower = max(Fraction(0), lateral_lower - flat_half_width)
    side_upper = max(Fraction(0), lateral_upper - flat_half_width)
    radicand_lower = max(Fraction(0), radius * radius - side_upper * side_upper)
    radicand_upper = max(Fraction(0), radius * radius - side_lower * side_lower)
    cap_lower = _sqrt_bounds(radicand_lower, bits)[0]
    cap_upper = min(radius, _sqrt_bounds(radicand_upper, bits)[1])
    return cap_lower, cap_upper


def _segment_top_bounds(
    source: NominalSupportSegment, corners: tuple[tuple[Fraction, Fraction], ...], bits: int,
) -> tuple[Fraction | None, Fraction] | None:
    return _segment_top_bounds_exact(_exact_top_segment_from_nominal(source), corners, bits)


def exact_top_segment_from_structural(source: NominalSupportSegment) -> ExactNominalTopSegment:
    if type(source) is not NominalSupportSegment or source.source_kind != "structural":
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "structural nominal source required")
    return _exact_top_segment_from_nominal(source)


def _exact_top_segment_from_nominal(source: NominalSupportSegment) -> ExactNominalTopSegment:
    return ExactNominalTopSegment(
        source.segment_id,
        (_r(source.start.x_mm), _r(source.start.y_mm), _r(source.start.z_mm)),
        (_r(source.end.x_mm), _r(source.end.y_mm), _r(source.end.z_mm)),
        _r(source.width_mm), _r(source.height_mm), source.source_kind,
    )


def exact_top_segment_from_chord(
    proposal: ChordProposal, *, segment_id: str, command_z_mm: Fraction,
    width_mm: Fraction, height_mm: Fraction,
) -> ExactNominalTopSegment:
    if type(proposal) is not ChordProposal or proposal.state != "proposed" or proposal.reason != "unscored":
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "proposed unscored chord required")
    return ExactNominalTopSegment(
        segment_id,
        (proposal.start_xy_mm[0], proposal.start_xy_mm[1], command_z_mm),
        (proposal.end_xy_mm[0], proposal.end_xy_mm[1], command_z_mm),
        width_mm, height_mm, "candidate",
    )


def _segment_top_bounds_exact(
    source: ExactNominalTopSegment, corners: tuple[tuple[Fraction, Fraction], ...], bits: int,
) -> tuple[Fraction | None, Fraction] | None:
    sx, sy, sz = source.start_xyz_mm
    dx, dy = source.end_xyz_mm[0] - sx, source.end_xyz_mm[1] - sy
    dz = source.end_xyz_mm[2] - sz
    length_squared = dx * dx + dy * dy
    parameters = tuple(((x - sx) * dx + (y - sy) * dy) / length_squared for x, y in corners)
    crosses = tuple((x - sx) * dy - (y - sy) * dx for x, y in corners)
    t_min, t_max = min(parameters), max(parameters)
    c_min, c_max = min(crosses), max(crosses)
    q_min = (Fraction(0) if c_min <= 0 <= c_max
             else min(c_min * c_min, c_max * c_max) / length_squared)
    q_max = max(c_min * c_min, c_max * c_max) / length_squared
    half_width, radius = source.width_mm / 2, source.height_mm / 2
    if t_max < 0 or t_min > 1 or q_min > half_width * half_width:
        return None
    fully_covered = t_min >= 0 and t_max <= 1 and q_max <= half_width * half_width
    nozzle_endpoints = (sz + max(Fraction(0), t_min) * dz,
                        sz + min(Fraction(1), t_max) * dz)
    flat_half_width = half_width - radius
    upper = max(nozzle_endpoints) - radius + _cap_bounds(q_min, radius, flat_half_width, bits)[1]
    lower = None
    if fully_covered:
        lower = min(nozzle_endpoints) - radius + _cap_bounds(q_max, radius, flat_half_width, bits)[0]
    return lower, upper


def _exact_top_query(
    corners: tuple[tuple[Fraction, Fraction], ...],
    sources: tuple[ExactNominalTopSegment, ...], *,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    cancelled: Callable[[], bool], full_reason: str,
) -> ExactNominalTopBounds:
    if (type(max_sources) is not int or max_sources < 1
            or type(max_coordinate_bits) is not int or max_coordinate_bits < 1
            or type(sqrt_fraction_bits) is not int or not 1 <= sqrt_fraction_bits <= 4096
            or not callable(cancelled)):
        raise ContractError(ReasonCode.INVALID_SETTING, "invalid exact top query settings")
    if type(sources) is not tuple:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact source tuple required")

    def is_cancelled() -> bool:
        answer = cancelled()
        if type(answer) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation callback must return exact bool")
        return answer

    def publish(state: str, reason: str, lower: Fraction | None = None,
                upper: Fraction | None = None) -> ExactNominalTopBounds:
        if is_cancelled():
            return ExactNominalTopBounds("incomplete", "cancelled", None, None)
        result = ExactNominalTopBounds(state, reason, lower, upper)
        if is_cancelled():
            return ExactNominalTopBounds("incomplete", "cancelled", None, None)
        return result

    if is_cancelled():
        return ExactNominalTopBounds("incomplete", "cancelled", None, None)
    if len(sources) > max_sources:
        return publish("incomplete", "resource-limit")
    if any(component.bit_length() > max_coordinate_bits
           for corner in corners for coordinate in corner
           for component in (coordinate.numerator, coordinate.denominator)):
        return publish("incomplete", "resource-limit")
    identifiers: set[str] = set()
    for source in sources:
        if is_cancelled():
            return ExactNominalTopBounds("incomplete", "cancelled", None, None)
        if type(source) is not ExactNominalTopSegment:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact nominal top segment required")
        if source.segment_id in identifiers:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "duplicate exact top segment identity")
        identifiers.add(source.segment_id)
        coordinates = source.start_xyz_mm + source.end_xyz_mm + (source.width_mm, source.height_mm)
        if any(component.bit_length() > max_coordinate_bits
               for coordinate in coordinates
               for component in (coordinate.numerator, coordinate.denominator)):
            return publish("incomplete", "resource-limit")
    top_lower = top_upper = None
    for source in sources:
        if is_cancelled():
            return ExactNominalTopBounds("incomplete", "cancelled", None, None)
        bounds = _segment_top_bounds_exact(source, corners, sqrt_fraction_bits)
        if is_cancelled():
            return ExactNominalTopBounds("incomplete", "cancelled", None, None)
        if bounds is None:
            continue
        lower, upper = bounds
        top_upper = upper if top_upper is None else max(top_upper, upper)
        if lower is not None:
            top_lower = lower if top_lower is None else max(top_lower, lower)
    if top_upper is None:
        return publish("absent", "disjoint")
    if top_lower is None:
        return publish("unresolved-partial", "union-coverage-unproven", upper=top_upper)
    return publish("full-bounded", full_reason, top_lower, top_upper)


def query_exact_nominal_top_point(
    x_mm: Fraction, y_mm: Fraction, sources: tuple[ExactNominalTopSegment, ...], *,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    cancelled: Callable[[], bool],
) -> ExactNominalTopBounds:
    if type(x_mm) is not Fraction or type(y_mm) is not Fraction:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact point required")
    return _exact_top_query(((x_mm, y_mm),), sources, max_sources=max_sources,
                            max_coordinate_bits=max_coordinate_bits,
                            sqrt_fraction_bits=sqrt_fraction_bits, cancelled=cancelled,
                            full_reason="covered-point")


def query_exact_nominal_top_cell(
    cell: ExactTopCellXY, sources: tuple[ExactNominalTopSegment, ...], *,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    cancelled: Callable[[], bool],
) -> ExactNominalTopBounds:
    if type(cell) is not ExactTopCellXY:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact cell required")
    corners = tuple((x, y) for x in (cell.x_min_mm, cell.x_max_mm)
                    for y in (cell.y_min_mm, cell.y_max_mm))
    return _exact_top_query(corners, sources, max_sources=max_sources,
                            max_coordinate_bits=max_coordinate_bits,
                            sqrt_fraction_bits=sqrt_fraction_bits, cancelled=cancelled,
                            full_reason="one-segment-covers-cell")


def _structural_top_query(
    corners: tuple[tuple[Fraction, Fraction], ...],
    sources: tuple[NominalSupportSegment, ...],
    policy: SupportCellQueryPolicy,
    cancelled: Callable[[], bool],
    full_reason: str,
) -> NominalStructuralTopBounds:
    def is_cancelled() -> bool:
        answer = cancelled()
        if type(answer) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation callback must return exact bool")
        return answer

    def publish(state: str, reason: str, lower: Fraction | None = None,
                upper: Fraction | None = None) -> NominalStructuralTopBounds:
        if is_cancelled():
            return NominalStructuralTopBounds("incomplete", "cancelled", None, None)
        result = NominalStructuralTopBounds(state, reason, lower, upper)
        if is_cancelled():
            return NominalStructuralTopBounds("incomplete", "cancelled", None, None)
        return result

    if len(sources) > policy.max_source_segments:
        return publish("incomplete", "resource-limit")
    identifiers: set[str] = set()
    top_lower = top_upper = None
    for source in sources:
        if is_cancelled():
            return NominalStructuralTopBounds("incomplete", "cancelled", None, None)
        if type(source) is not NominalSupportSegment or source.source_kind != "structural":
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact structural source required")
        if float(source.start.z_mm) != float(source.end.z_mm):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "horizontal structural source required")
        if source.segment_id in identifiers:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "duplicate structural source identity")
        identifiers.add(source.segment_id)
        segment_bounds = _segment_top_bounds(source, corners, policy.sqrt_fraction_bits)
        if is_cancelled():
            return NominalStructuralTopBounds("incomplete", "cancelled", None, None)
        if segment_bounds is None:
            continue
        lower, upper = segment_bounds
        top_upper = upper if top_upper is None else max(top_upper, upper)
        if lower is not None:
            top_lower = lower if top_lower is None else max(top_lower, lower)
    if top_upper is None:
        return publish("absent", "disjoint")
    if top_lower is None:
        return publish("unresolved-partial", "union-coverage-unproven", upper=top_upper)
    return publish("full-bounded", full_reason, top_lower, top_upper)


def query_nominal_structural_top_point(
    x_mm: Fraction, y_mm: Fraction, sources: tuple[NominalSupportSegment, ...], *,
    policy: SupportCellQueryPolicy, max_point_coordinate_bits: int,
    cancelled: Callable[[], bool],
) -> NominalStructuralTopBounds:
    """Bound the nominal structural union top at one exact XY point."""
    if (type(policy) is not SupportCellQueryPolicy or type(max_point_coordinate_bits) is not int
            or max_point_coordinate_bits < 1 or not callable(cancelled)):
        raise ContractError(ReasonCode.INVALID_SETTING, "invalid structural top query settings")
    if type(x_mm) is not Fraction or type(y_mm) is not Fraction or type(sources) is not tuple:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact structural point inputs required")
    if any(component.bit_length() > max_point_coordinate_bits
           for point in (x_mm, y_mm)
           for component in (point.numerator, point.denominator)):
        answer = cancelled()
        if type(answer) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation callback must return exact bool")
        return NominalStructuralTopBounds("incomplete", "cancelled" if answer else "resource-limit", None, None)
    return _structural_top_query(((x_mm, y_mm),) * 4, sources, policy, cancelled, "covered-point")


def query_nominal_structural_top_cell(
    cell: SupportCellXY, sources: tuple[NominalSupportSegment, ...], *,
    policy: SupportCellQueryPolicy, cancelled: Callable[[], bool],
) -> NominalStructuralTopBounds:
    """Conservatively bound union top over a closed rectangular cell."""
    if type(policy) is not SupportCellQueryPolicy or not callable(cancelled):
        raise ContractError(ReasonCode.INVALID_SETTING, "invalid structural top query settings")
    if type(cell) is not SupportCellXY or type(sources) is not tuple:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact structural cell inputs required")
    corners = tuple((x, y) for x in (_r(cell.x_min_mm), _r(cell.x_max_mm))
                    for y in (_r(cell.y_min_mm), _r(cell.y_max_mm)))
    return _structural_top_query(corners, sources, policy, cancelled, "one-segment-covers-cell")


def query_nominal_support_cell(
    cell: SupportCellXY, sources: tuple[NominalSupportSegment, ...], *,
    command_z_mm: float, execution_order: int,
    height_bounds: CandidateBeadBounds, policy: SupportCellQueryPolicy,
) -> SupportCellQueryResult:
    """Prove local vertical eligibility or return conservative unresolved bounds.

    Single-segment full coverage is sufficient. General union coverage and
    adaptive area/width convergence deliberately remain outside this provider.
    """
    if type(policy) is not SupportCellQueryPolicy or type(height_bounds) is not CandidateBeadBounds:
        raise ContractError(ReasonCode.INVALID_SETTING, "exact support query settings required")
    if (type(cell) is not SupportCellXY or type(sources) is not tuple
            or not finite_binary64(command_z_mm)
            or type(execution_order) is not int or execution_order < 0):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid support query inputs")
    if len(sources) > policy.max_source_segments:
        return SupportCellQueryResult("unresolved", None, None, None, None, "resource-limit")
    identifiers = set()
    for source in sources:
        if type(source) is not NominalSupportSegment:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact nominal source segment required")
        if source.segment_id in identifiers or source.execution_order >= execution_order:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "duplicate or nonchronological support source")
        identifiers.add(source.segment_id)
        if source.source_kind == "candidate" and _r(source.start.z_mm) >= _r(command_z_mm):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "candidate support must be strictly lower Z")
    corners = tuple((x, y) for x in (_r(cell.x_min_mm), _r(cell.x_max_mm))
                    for y in (_r(cell.y_min_mm), _r(cell.y_max_mm)))
    top_lower = top_upper = None
    for source in sources:
        segment_bounds = _segment_top_bounds(source, corners, policy.sqrt_fraction_bits)
        if segment_bounds is None:
            continue
        lower, upper = segment_bounds
        top_upper = upper if top_upper is None else max(top_upper, upper)
        if lower is not None:
            top_lower = lower if top_lower is None else max(top_lower, lower)
    if top_upper is None:
        return SupportCellQueryResult("proven-unsupported", None, None, None, None, "disjoint")
    height_lower = _r(command_z_mm) - top_upper
    height_upper = None if top_lower is None else _r(command_z_mm) - top_lower
    minimum, maximum = _r(height_bounds.min_candidate_height_mm), _r(height_bounds.max_candidate_height_mm)
    if height_lower > maximum or (height_upper is not None and height_upper < minimum):
        state, reason = "proven-unsupported", "height-outside-bounds"
    elif height_upper is not None and minimum <= height_lower <= height_upper <= maximum:
        state, reason = "proven-supported", "height-within-bounds"
    elif top_lower is None:
        state, reason = "unresolved", "coverage-unresolved"
    else:
        state, reason = "unresolved", "height-unresolved"
    return SupportCellQueryResult(state, top_lower, top_upper, height_lower, height_upper, reason)
