"""Bounded exact plan-space length, time and adjacent flow/shape checks."""
from fractions import Fraction
from typing import Callable

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.path_regularity import PathRegularityResult
from adaptive_subedge.domain.plan import SubEdgePath
from adaptive_subedge.domain.settings import CandidateSegmentRegularityPolicy


class _Cancelled(Exception):
    pass


def _fraction(value):
    return Fraction(float(value))


def evaluate_path_regularity(path: SubEdgePath, *, policy: CandidateSegmentRegularityPolicy,
                             max_segments: int, cancelled: Callable[[], bool]) -> PathRegularityResult:
    if type(path) is not SubEdgePath:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact planned path required")
    if (type(policy) is not CandidateSegmentRegularityPolicy
            or policy.version != "planned_segment_regularity_v1"
            or type(max_segments) is not int or max_segments <= 0 or not callable(cancelled)):
        raise ContractError(ReasonCode.INVALID_SETTING, "invalid regularity policy, limit or callback")

    def check():
        stopped = cancelled()
        if type(stopped) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "cancellation must return exact bool")
        if stopped:
            raise _Cancelled()

    def finish(state, reason, indices):
        check()
        return PathRegularityResult(state, reason, indices)

    try:
        check()
        if len(path.segments) > max_segments:
            return finish("incomplete", "resource-limit", ())
        minimum_length_squared = _fraction(policy.min_candidate_segment_length_mm)**2
        minimum_time = _fraction(policy.min_candidate_segment_time_s)
        maximum_steps = (
            _fraction(policy.max_adjacent_commanded_volumetric_rate_step_mm3_s),
            _fraction(policy.max_adjacent_width_step_mm),
            _fraction(policy.max_adjacent_effective_height_step_mm),
        )
        segment_rates_and_shapes = []
        for index, segment in enumerate(path.segments):
            check()
            dx = _fraction(segment.end_xy.x_mm)-_fraction(segment.start_xy.x_mm)
            dy = _fraction(segment.end_xy.y_mm)-_fraction(segment.start_xy.y_mm)
            length_squared = dx*dx+dy*dy
            if length_squared <= minimum_length_squared:
                return finish("rejected", "segment-length", (index,))
            speed = _fraction(segment.requested_speed_mm_s)
            if length_squared < (speed*minimum_time)**2:
                return finish("rejected", "segment-time", (index,))
            segment_rates_and_shapes.append((
                _fraction(segment.commanded_mm3_per_mm)*speed,
                _fraction(segment.width_mm), _fraction(segment.effective_bead_height_mm),
            ))
        reasons = ("adjacent-rate-step", "adjacent-width-step", "adjacent-height-step")
        for index, (first, second) in enumerate(zip(segment_rates_and_shapes, segment_rates_and_shapes[1:])):
            check()
            for before, after, maximum, reason in zip(first, second, maximum_steps, reasons):
                if abs(after-before) > maximum:
                    return finish("rejected", reason, (index, index+1))
        return finish("complete", "regular", ())
    except _Cancelled:
        return PathRegularityResult("incomplete", "cancelled", ())
