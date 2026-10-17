"""Adaptive actual-bead coverage in a straight candidate's exact local frame."""
from dataclasses import dataclass
from fractions import Fraction as F
from math import isfinite, isqrt, nextafter, inf
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import CandidateBeadBounds, SupportCoverageThresholds, SupportRefinementPolicy
from adaptive_subedge.domain.settings_v2 import SupportQueryNumericPolicy
from adaptive_subedge.domain.support_cell import NominalSupportSegment, SupportCellQueryPolicy, SupportCellQueryResult, SupportCellXY
from adaptive_subedge.domain.support_coverage import AdaptiveSupportResult, SupportCoverageSnapshot, SupportFootprint
from .support_cell import _sqrt_bounds, query_nominal_support_cell
from .support_width import _minimum_supported_width


class _Cancelled(Exception):
    pass


class _CoordinateRange(Exception):
    pass


@dataclass(frozen=True, slots=True)
class _Leaf:
    t0: F
    t1: F
    v0: F
    v1: F
    evidence: SupportCellQueryResult | None


def _r(value: float) -> F:
    return F(float(value))


def _ceil(value: F) -> int:
    return -(-value.numerator // value.denominator)


def _ceil_sqrt(value: F) -> int:
    root = isqrt(value.numerator // value.denominator)
    return root if root * root * value.denominator == value.numerator else root + 1


def _outward(value: F, upper: bool) -> float:
    try:
        rounded = float(value)
    except OverflowError as exc:
        raise _CoordinateRange from exc
    if not isfinite(rounded):
        raise _CoordinateRange
    if (upper and F(rounded) < value) or (not upper and F(rounded) > value):
        rounded = nextafter(rounded, inf if upper else -inf)
    if not isfinite(rounded):
        raise _CoordinateRange
    return rounded


def _normal_component(component: F, length_squared: F, bits: int) -> tuple[F, F]:
    lower, upper = _sqrt_bounds(component * component / length_squared, bits)
    upper = min(F(1), upper)
    return (-upper, -lower) if component < 0 else (lower, upper)


def _world_cell(leaf: _Leaf, origin: tuple[F, F], direction: tuple[F, F],
                normal: tuple[tuple[F, F], tuple[F, F]]) -> SupportCellXY:
    ranges = []
    for start, delta, (nlo, nhi) in zip(origin, direction, normal):
        lows, highs = [], []
        for t in (leaf.t0, leaf.t1):
            for v in (leaf.v0, leaf.v1):
                offsets = (v * nlo, v * nhi)
                lows.append(start + t * delta + min(offsets))
                highs.append(start + t * delta + max(offsets))
        ranges.extend((_outward(min(lows), False), _outward(max(highs), True)))
    if ranges[0] >= ranges[1] or ranges[2] >= ranges[3]:
        raise _CoordinateRange
    return SupportCellXY(*ranges)


def _snapshot(leaves: list[_Leaf], width: F, check_cancelled: Callable[[], None]) -> SupportCoverageSnapshot:
    supported = [leaf for leaf in leaves if leaf.evidence.state == "proven-supported"]
    area = sum(((x.t1 - x.t0) * (x.v1 - x.v0) for x in supported), F(0)) / width
    unknown = sum(((x.t1 - x.t0) * (x.v1 - x.v0) for x in leaves
                   if x.evidence.state == "unresolved"), F(0)) / width
    contiguous = _minimum_supported_width(tuple((x.t0, x.t1, x.v0, x.v1) for x in supported), check_cancelled)
    lower = min((x.evidence.effective_height_lower_mm for x in supported), default=None)
    upper = max((x.evidence.effective_height_upper_mm for x in supported), default=None)
    return SupportCoverageSnapshot(area, contiguous, lower, upper, unknown, len(leaves))


def _stable(previous: SupportCoverageSnapshot, current: SupportCoverageSnapshot,
            refinement: SupportRefinementPolicy, numeric: SupportQueryNumericPolicy) -> bool:
    if (abs(current.supported_area_fraction_lower_bound - previous.supported_area_fraction_lower_bound)
            > _r(refinement.support_metric_convergence_fraction)
            or abs(current.minimum_contiguous_support_width_lower_bound_mm
                   - previous.minimum_contiguous_support_width_lower_bound_mm)
            > _r(refinement.support_width_convergence_mm)):
        return False
    for field in ("minimum_effective_height_lower_bound_mm", "maximum_effective_height_upper_bound_mm"):
        before, after = getattr(previous, field), getattr(current, field)
        if before is None or after is None:
            if before is not after:
                return False
        elif abs(after - before) > _r(numeric.support_query_length_tolerance_mm):
            return False
    return True


def evaluate_support_coverage(
    footprint: SupportFootprint, sources: tuple[NominalSupportSegment, ...], *,
    bead_bounds: CandidateBeadBounds, thresholds: SupportCoverageThresholds,
    refinement_policy: SupportRefinementPolicy, numeric_policy: SupportQueryNumericPolicy,
    query_policy: SupportCellQueryPolicy, max_cells: int,
    cancelled: Callable[[], bool],
) -> AdaptiveSupportResult:
    """Return bounded numerical evidence, preserving only complete-pass snapshots."""
    for instance, cls in ((bead_bounds, CandidateBeadBounds), (thresholds, SupportCoverageThresholds),
                          (refinement_policy, SupportRefinementPolicy), (numeric_policy, SupportQueryNumericPolicy),
                          (query_policy, SupportCellQueryPolicy)):
        if type(instance) is not cls:
            raise ContractError(ReasonCode.INVALID_SETTING, "exact support settings required")
    if type(max_cells) is not int or max_cells < 1 or not callable(cancelled):
        raise ContractError(ReasonCode.INVALID_SETTING, "explicit query budget and cancellation callable required")
    if type(footprint) is not SupportFootprint or type(sources) is not tuple:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact footprint/source tuple required")
    width = _r(footprint.width_mm)
    if not _r(bead_bounds.min_candidate_width_mm) <= width <= _r(bead_bounds.max_candidate_width_mm):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "footprint width outside candidate bounds")
    metrics = None
    levels = evaluated = 0

    def result(reason: str, state: str = "incomplete") -> AdaptiveSupportResult:
        return AdaptiveSupportResult(state, reason, metrics, levels, evaluated)

    def check_cancelled() -> None:
        value = cancelled()
        if type(value) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation must return exact bool")
        if value:
            raise _Cancelled

    origin = (_r(footprint.start.x_mm), _r(footprint.start.y_mm))
    direction = (_r(footprint.end.x_mm) - origin[0], _r(footprint.end.y_mm) - origin[1])
    squared_length = sum((d * d for d in direction), F(0))
    target = _r(refinement_policy.initial_support_cell_size_mm)
    minimum = _r(refinement_policy.minimum_support_cell_size_mm)
    leaves = [_Leaf(F(0), F(1), -width / 2, width / 2, None)]
    try:
        check_cancelled()
        normal = (_normal_component(-direction[1], squared_length, query_policy.sqrt_fraction_bits),
                  _normal_component(direction[0], squared_length, query_policy.sqrt_fraction_bits))
        for level in range(refinement_policy.max_support_refinement_levels):
            check_cancelled()
            if level:
                # Below the minimum every later proposed split is blocked. Do
                # not grow unused rational powers for huge refinement factors.
                if target is not None:
                    target /= _r(refinement_policy.support_refinement_factor)
                    if target < minimum:
                        target = None
            proposals = []
            prospective = 0
            for leaf in leaves:
                if leaf.evidence is not None and leaf.evidence.state != "unresolved":
                    proposals.append((leaf, 0, 0))
                    continue
                dt, dv = leaf.t1 - leaf.t0, leaf.v1 - leaf.v0
                if target is None:
                    nt = nv = 1
                else:
                    nt = max(1, _ceil_sqrt(squared_length * dt * dt / (target * target)))
                    nv = max(1, _ceil(dv / target))
                    if level:
                        if nt > 1 and squared_length * (dt / nt)**2 < minimum * minimum:
                            nt = 1
                        if nv > 1 and dv / nv < minimum:
                            nv = 1
                prospective += nt * nv
                if evaluated + prospective > max_cells:
                    return result("resource-limit")
                proposals.append((leaf, nt, nv))
            replacement = []
            for leaf, nt, nv in proposals:
                if not nt:
                    replacement.append(leaf)
                    continue
                for i in range(nt):
                    t0 = leaf.t0 + (leaf.t1 - leaf.t0) * F(i, nt)
                    t1 = leaf.t0 + (leaf.t1 - leaf.t0) * F(i + 1, nt)
                    for j in range(nv):
                        check_cancelled()
                        v0 = leaf.v0 + (leaf.v1 - leaf.v0) * F(j, nv)
                        v1 = leaf.v0 + (leaf.v1 - leaf.v0) * F(j + 1, nv)
                        cell = _Leaf(t0, t1, v0, v1, None)
                        evidence = query_nominal_support_cell(
                            _world_cell(cell, origin, direction, normal), sources,
                            command_z_mm=footprint.command_z_mm, execution_order=footprint.execution_order,
                            height_bounds=bead_bounds, policy=query_policy)
                        evaluated += 1
                        if evidence.reason == "resource-limit":
                            return result("resource-limit")
                        replacement.append(_Leaf(t0, t1, v0, v1, evidence))
            snapshot = _snapshot(replacement, width, check_cancelled)
            previous, metrics = metrics, snapshot
            leaves = replacement
            levels += 1
            if previous is not None and snapshot.unresolved_area_fraction == 0 and _stable(previous, snapshot, refinement_policy, numeric_policy):
                lower, upper = snapshot.minimum_effective_height_lower_bound_mm, snapshot.maximum_effective_height_upper_bound_mm
                passes = (snapshot.supported_area_fraction_lower_bound >= _r(thresholds.min_support_area_fraction)
                          and snapshot.minimum_contiguous_support_width_lower_bound_mm >= _r(thresholds.min_support_contact_width_mm)
                          and lower is not None and upper is not None
                          and _r(bead_bounds.min_candidate_height_mm) <= lower <= upper <= _r(bead_bounds.max_candidate_height_mm))
                return result("converged" if passes else "thresholds-failed",
                              "numerically-supported" if passes else "numerically-rejected")
        return result("max-levels")
    except _Cancelled:
        return result("cancelled")
    except _CoordinateRange:
        return result("coordinate-range")
