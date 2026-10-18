"""Exact research solver for axis-aligned rectangles in planar step sections.

This is a 2D rectangular cross-section model, not a stadium extrusion or
continuous 3D support certificate. It cannot authorize viewer/print paths.
"""
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class Section:
    left: F
    right: F
    bottom: F
    slope: F
    intercept: F


@dataclass(frozen=True)
class Rectangle:
    left: F
    right: F
    bottom: F
    top: F

    @property
    def area(self):
        return (self.right-self.left)*(self.top-self.bottom)


def split_line_intervals(rectangle: Rectangle, *, minimum_width: F, maximum_width: F):
    """Exactly tile the rectangle with equal, bounded nominal line widths."""
    if (type(minimum_width) is not F or type(maximum_width) is not F
            or not 0 < minimum_width <= maximum_width):
        raise ValueError('invalid exact line width bounds')
    span = rectangle.right-rectangle.left
    if span <= 0:
        raise ValueError('positive rectangle width required')
    count = -(-span//maximum_width)
    if span < count*minimum_width:
        return ()
    width = span/count
    return tuple((rectangle.left+i*width,rectangle.left+(i+1)*width) for i in range(count))


def largest_rectangle(section: Section, *, minimum_width: F,
                      minimum_height: F, maximum_height: F,
                      maximum_width: F | None = None):
    """Maximize w*h exactly in one flat-floor, positive-slope section.

    A rectangle's bottom rests on the current floor. For fixed height its
    greatest width reaches the right boundary. The remaining area objective
    is piecewise quadratic in its width, so critical points and
    constraint boundaries exhaust the global optimum for this section.
    """
    numbers = (section.left,section.right,section.bottom,section.slope,section.intercept,
               minimum_width,minimum_height,maximum_height)
    if (any(type(v) is not F for v in numbers) or section.left >= section.right
            or section.slope <= 0 or minimum_width <= 0
            or not 0 < minimum_height <= maximum_height):
        raise ValueError('invalid exact step-section constraints')
    a,b,s,m,c = section.left,section.right,section.bottom,section.slope,section.intercept
    if maximum_width is not None and (type(maximum_width) is not F or maximum_width < minimum_width):
        raise ValueError('invalid exact maximum width')
    if maximum_width is None:
        maximum_width = b-a
    gap = m*b+c-s
    low = minimum_width
    high = min(maximum_width,b-a,(gap-minimum_height)/m)
    if low > high:
        return None
    critical = (low,high,gap/(2*m),(gap-maximum_height)/m)
    feasible = []
    for width in critical:
        if not low <= width <= high:
            continue
        left = b-width
        height = min(maximum_height,m*left+c-s)
        if minimum_height <= height <= maximum_height:
            feasible.append(Rectangle(left,b,s,s+height))
    return max(feasible,key=lambda r:(r.area,r.right-r.left)) if feasible else None


def fill_section(section: Section, *, minimum_width: F, minimum_height: F,
                 maximum_height: F, maximum_width: F | None = None,
                 max_rectangles: int = 256):
    """Repeated largest-area insertion; exact local optimum, not global packing.

    Keep every remaining section, including infeasible sections. Updated
    floor includes earlier rectangles, allowing multiple rows and tiers.
    """
    constraints = dict(minimum_width=minimum_width,minimum_height=minimum_height,
                       maximum_height=maximum_height,maximum_width=maximum_width)
    return _fill(section,lambda s:largest_rectangle(s,**constraints),max_rectangles)


def largest_tiled_rectangle(section: Section, *, minimum_line_width: F,
                            maximum_line_width: F, minimum_height: F,
                            maximum_height: F, max_lines: int = 256):
    """Optimize over the union of feasible n-line total-width intervals.

    The line-width cap does not cap the logical rectangle. A width falling
    between n*w_max and (n+1)*w_min is infeasible; never silently narrow lines.
    The optimum is exact within the explicit line-count resource bound.
    """
    if (type(max_lines) is not int or max_lines < 1 or type(minimum_line_width) is not F
            or type(maximum_line_width) is not F or not 0 < minimum_line_width <= maximum_line_width):
        raise ValueError('invalid tiled rectangle policy')
    largest_rectangle(section,minimum_width=minimum_line_width,maximum_width=maximum_line_width,
        minimum_height=minimum_height,maximum_height=maximum_height)
    proposals = []
    for count in range(1,min(max_lines,int((section.right-section.left)//minimum_line_width))+1):
        rectangle = largest_rectangle(section,minimum_width=count*minimum_line_width,
            maximum_width=count*maximum_line_width,minimum_height=minimum_height,
            maximum_height=maximum_height)
        if rectangle is not None:
            proposals.append(rectangle)
    return max(proposals,key=lambda r:(r.area,r.right-r.left)) if proposals else None


def fill_tiled_section(section: Section, *, minimum_line_width: F,
                       maximum_line_width: F, minimum_height: F,
                       maximum_height: F, max_rectangles: int = 256):
    return _fill(section,lambda s:largest_tiled_rectangle(s,
        minimum_line_width=minimum_line_width,maximum_line_width=maximum_line_width,
        minimum_height=minimum_height,maximum_height=maximum_height),max_rectangles)


def _fill(section,propose,max_rectangles):
    if type(max_rectangles) is not int or max_rectangles < 1:
        raise ValueError('invalid rectangle budget')
    pending = [section]
    placed = []
    while len(placed) < max_rectangles:
        proposals = [(i,propose(s)) for i,s in enumerate(pending)]
        proposals = [(i,r) for i,r in proposals if r is not None]
        if not proposals:
            break
        index,rectangle = max(proposals,key=lambda pair:pair[1].area)
        previous = pending.pop(index)
        placed.append(rectangle)
        if previous.left < rectangle.left:
            pending.append(Section(previous.left,rectangle.left,previous.bottom,
                                   previous.slope,previous.intercept))
        pending.append(Section(rectangle.left,rectangle.right,rectangle.top,
                               previous.slope,previous.intercept))
    return tuple(placed),tuple(pending)
