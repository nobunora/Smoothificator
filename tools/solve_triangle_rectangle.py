"""Floor-anchored symmetric-difference rectangle research solvers.

The single-rectangle analytic solution is a comparison baseline. The preview
uses multiple independent rectangles selected by exact-area lattice DP.
"""
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class TriangleRectangle:
    width_mm: F
    height_mm: F
    line_count: int
    error_area_mm2: F
    spill_area_mm2: F


def spill_area(base_mm, rise_mm, left_mm, right_mm, height_mm):
    """Integral of max(h - rise*x/base, 0) on a subinterval."""
    slope = rise_mm/base_mm
    return (max(F(0), height_mm-slope*left_mm)**2
            - max(F(0), height_mm-slope*right_mm)**2)/(2*slope)


def finite_triangle_rectangle_intersection_area(base_mm, rise_mm, left_mm, right_mm,
                                                bottom_mm, top_mm):
    """Exact area inside (0,0),(base,0),(base,rise) and a finite rectangle.

    Clip X to the finite base and Y to the floor/rise, then integrate the
    rising triangular portion followed by the constant rectangle-height part.
    """
    coordinates = (base_mm, rise_mm, left_mm, right_mm, bottom_mm, top_mm)
    if (any(type(v) is not F for v in coordinates) or base_mm <= 0 or rise_mm <= 0
            or left_mm >= right_mm or bottom_mm >= top_mm):
        raise ValueError('positive exact triangle and nondegenerate exact rectangle required')
    left, right = max(F(0), left_mm), min(base_mm, right_mm)
    bottom, top = max(F(0), bottom_mm), min(rise_mm, top_mm)
    if left >= right or bottom >= top:
        return F(0)
    slope = rise_mm/base_mm
    ramp_left, ramp_right = max(left, bottom/slope), min(right, top/slope)
    area = F(0)
    if ramp_left < ramp_right:
        area += slope*(ramp_right*ramp_right-ramp_left*ramp_left)/2-bottom*(ramp_right-ramp_left)
    flat_left = max(left, top/slope)
    if flat_left < right:
        area += (right-flat_left)*(top-bottom)
    return area


def solve(base_mm, rise_mm, *, minimum_width_mm, maximum_width_mm,
          minimum_height_mm, maximum_height_mm):
    """Global optimum for one bottom/right-anchored logical rectangle.

    Enumerate every feasible equal-line tiling width interval. In each box,
    the objective's boundary minima and sole interior stationary point exhaust
    its minimum. This does not optimize multiple different-height rectangles.
    """
    numbers = (base_mm, rise_mm, minimum_width_mm, maximum_width_mm,
               minimum_height_mm, maximum_height_mm)
    if (any(type(v) is not F for v in numbers) or min(numbers) <= 0
            or minimum_width_mm > maximum_width_mm
            or minimum_height_mm > maximum_height_mm):
        raise ValueError('positive exact triangle and ordered dimensions required')
    low_h, high_h = minimum_height_mm, min(rise_mm, maximum_height_mm)
    if low_h > high_h:
        return None
    slope = rise_mm/base_mm
    clamp = lambda v, lo, hi: min(hi, max(lo, v))
    choices = []
    for count in range(1, int(base_mm//minimum_width_mm)+1):
        low_w = count*minimum_width_mm
        high_w = min(base_mm, count*maximum_width_mm)
        if low_w > high_w:
            continue
        points = {(w,h) for w in (low_w, high_w) for h in (low_h, high_h)}
        for w in (low_w, high_w):
            points.add((w, clamp(rise_mm-slope*w/2, low_h, high_h)))
        for h in (low_h, high_h):
            points.add((clamp((rise_mm-h/2)/slope, low_w, high_w), h))
        points.add((2*base_mm/3, 2*rise_mm/3))
        for w,h in points:
            if not low_w <= w <= high_w or not low_h <= h <= high_h:
                continue
            spill = spill_area(base_mm, rise_mm, base_mm-w, base_mm, h)
            if 2*spill > w*h:
                continue
            error = base_mm*rise_mm/2-w*h+2*spill
            choices.append(TriangleRectangle(w,h,count,error,spill))
    return min(choices, key=lambda r:(r.error_area_mm2, r.line_count, -r.height_mm)) if choices else None


@dataclass(frozen=True)
class PackedRectangle:
    left_mm: F
    right_mm: F
    height_mm: F
    spill_area_mm2: F


@dataclass(frozen=True)
class TrianglePacking:
    rectangles: tuple[PackedRectangle, ...]
    error_area_mm2: F
    spill_area_mm2: F
    grid_divisions: int


def pack(base_mm, rise_mm, *, grid_divisions, minimum_width_mm, maximum_width_mm,
         minimum_height_mm, maximum_height_mm):
    """Minimum union symmetric difference on an explicit position lattice.

    All rectangles rest on the triangle floor and have disjoint X interiors.
    Their heights are continuous exact interval medians, clamped to the height
    policy. DP can leave gaps and choose any count, including repeated sizes.
    This is globally optimal within this lattice/model, not over continuous
    positions, stacked rectangles, overlapping rectangles or rounded beads.
    """
    # Share exact dimension validation with the analytic comparison solver.
    solve(base_mm,rise_mm,minimum_width_mm=minimum_width_mm,maximum_width_mm=maximum_width_mm,
          minimum_height_mm=minimum_height_mm,maximum_height_mm=maximum_height_mm)
    if type(grid_divisions) is not int or not 1 <= grid_divisions <= 10000:
        raise ValueError('bounded positive integer grid divisions required')
    step = base_mm/grid_divisions
    minimum_cells = -(-minimum_width_mm//step)
    maximum_cells = min(grid_divisions, maximum_width_mm//step)
    slope = rise_mm/base_mm
    scores = [F(0)]*(grid_divisions+1)
    counts = [0]*(grid_divisions+1)
    previous = [None]*(grid_divisions+1)
    high_h = min(rise_mm,maximum_height_mm)
    for end in range(1,grid_divisions+1):
        scores[end],counts[end] = scores[end-1],counts[end-1]
        previous[end] = (end-1,None)
        if minimum_height_mm > high_h:
            continue
        for cells in range(int(minimum_cells), min(int(maximum_cells),end)+1):
            start = end-cells
            a,b = start*step,end*step
            h = min(high_h,max(minimum_height_mm,slope*(a+b)/2))
            spill = spill_area(base_mm,rise_mm,a,b,h)
            area = (b-a)*h
            if 2*spill > area:
                continue
            gain = area-2*spill
            score,count = scores[start]+gain,counts[start]+1
            if score > scores[end] or (score == scores[end] and count < counts[end]):
                scores[end],counts[end] = score,count
                previous[end] = (start,PackedRectangle(a,b,h,spill))
    rectangles = []
    cursor = grid_divisions
    while cursor:
        cursor,rectangle = previous[cursor]
        if rectangle is not None:
            rectangles.append(rectangle)
    rectangles.reverse()
    return TrianglePacking(tuple(rectangles),base_mm*rise_mm/2-scores[-1],
        sum((r.spill_area_mm2 for r in rectangles),F(0)),grid_divisions)
