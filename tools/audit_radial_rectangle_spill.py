"""Sufficient exact spill bounds over whole radial/width parameter ranges."""
from dataclasses import dataclass
from fractions import Fraction as F

from tools.solve_triangle_rectangle import finite_triangle_rectangle_intersection_area


@dataclass(frozen=True)
class RadialRectangleSpillCell:
    center_interval_mm: tuple[F, F]
    width_interval_mm: tuple[F, F]
    common_horizontal_interval_mm: tuple[F, F]
    guaranteed_intersection_mm2: F
    maximum_rectangle_area_mm2: F
    spill_upper_bound: F


@dataclass(frozen=True)
class RadialRectangleSpillReport:
    triangle_base_mm: F
    triangle_rise_mm: F
    triangle_left_radius_mm: F
    center_radius_interval_mm: tuple[F, F]
    width_interval_mm: tuple[F, F]
    bottom_top_mm: tuple[F, F]
    requested_bins: tuple[int, int]
    effective_bins: tuple[int, int]
    max_cells: int
    max_coordinate_bits: int
    status: str
    reason: str | None
    cells: tuple[RadialRectangleSpillCell, ...]
    spill_upper_bound: F | None


def bound_radial_rectangle_spill(*, triangle_base_mm, triangle_rise_mm,
        triangle_left_radius_mm, center_radius_lower_mm, center_radius_upper_mm,
        width_lower_mm, width_upper_mm, bottom_mm, top_mm, center_bins, width_bins,
        max_cells, max_coordinate_bits, cancelled):
    """Bound every rectangle in an exact partition, with no sampling acceptance.

    Each common subrectangle lies inside every posed rectangle in its parameter
    cell. Its finite-triangle intersection divided by the largest rectangle area
    is a guaranteed retained fraction. Incomplete reports have no global bound.
    """
    coordinates = (triangle_base_mm, triangle_rise_mm, triangle_left_radius_mm,
        center_radius_lower_mm, center_radius_upper_mm, width_lower_mm,
        width_upper_mm, bottom_mm, top_mm)
    if (any(type(v) is not F for v in coordinates) or triangle_base_mm <= 0
            or triangle_rise_mm <= 0 or triangle_left_radius_mm < 0
            or not 0 <= center_radius_lower_mm <= center_radius_upper_mm
            or not 0 < width_lower_mm <= width_upper_mm or bottom_mm >= top_mm):
        raise ValueError('exact positive triangle/width/height and ordered nonnegative radii required')
    if any(type(v) is not int or v < 1 for v in (center_bins, width_bins, max_cells, max_coordinate_bits)):
        raise ValueError('positive exact integer partition/resource limits required')
    if not callable(cancelled):
        raise ValueError('explicit cancellation callback required')

    def stopped():
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('cancellation callback must return exact bool')
        return answer

    def bounded(numbers):
        return all(max(v.numerator.bit_length(), v.denominator.bit_length()) <= max_coordinate_bits
                   for v in numbers)

    nc = 1 if center_radius_lower_mm == center_radius_upper_mm else center_bins
    nw = 1 if width_lower_mm == width_upper_mm else width_bins
    cells = []

    def report(reason=None):
        return RadialRectangleSpillReport(triangle_base_mm, triangle_rise_mm,
            triangle_left_radius_mm, (center_radius_lower_mm, center_radius_upper_mm),
            (width_lower_mm, width_upper_mm), (bottom_mm, top_mm), (center_bins, width_bins),
            (nc, nw), max_cells, max_coordinate_bits, 'incomplete' if reason else 'complete',
            reason, tuple(cells), None if reason else max(c.spill_upper_bound for c in cells))

    if stopped():
        return report('cancelled')
    if not bounded(coordinates):
        return report('coordinate-bit-limit')
    if nc*nw > max_cells:
        return report('cell-limit')
    for ci in range(nc):
        c0 = center_radius_lower_mm+(center_radius_upper_mm-center_radius_lower_mm)*ci/nc
        c1 = center_radius_lower_mm+(center_radius_upper_mm-center_radius_lower_mm)*(ci+1)/nc
        for wi in range(nw):
            if stopped():
                return report('cancelled')
            w0 = width_lower_mm+(width_upper_mm-width_lower_mm)*wi/nw
            w1 = width_lower_mm+(width_upper_mm-width_lower_mm)*(wi+1)/nw
            left, right = c1-w0/2-triangle_left_radius_mm, c0+w0/2-triangle_left_radius_mm
            if not bounded((c0, c1, w0, w1, left, right)):
                return report('coordinate-bit-limit')
            area = F(0) if left >= right else finite_triangle_rectangle_intersection_area(
                triangle_base_mm, triangle_rise_mm, left, right, bottom_mm, top_mm)
            maximum_area = w1*(top_mm-bottom_mm)
            upper = 1-area/maximum_area
            if not bounded((area, maximum_area, upper)):
                return report('coordinate-bit-limit')
            cells.append(RadialRectangleSpillCell((c0, c1), (w0, w1), (left, right), area, maximum_area, upper))
    if stopped():
        return report('cancelled')
    return report()
