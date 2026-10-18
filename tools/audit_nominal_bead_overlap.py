"""Exact bounded nominal bead-pair volume audit; not physical tool clearance."""
from dataclasses import dataclass, field
from fractions import Fraction as F
from typing import Callable

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from adaptive_subedge.engine.support_cell import query_exact_nominal_top_cell


@dataclass(frozen=True)
class BeadOverlapPolicy:
    max_depth: int
    max_queries: int
    max_coordinate_bits: int
    sqrt_fraction_bits: int
    stop_after_overlap: bool = True

    def __post_init__(self):
        if type(self.max_depth) is not int or not 0 <= self.max_depth <= 32:
            raise ValueError('exact maximum depth0..32 required')
        if any(type(v) is not int or v < 1 for v in
               (self.max_queries, self.max_coordinate_bits, self.sqrt_fraction_bits)):
            raise ValueError('positive exact finite query/bit limits required')
        if self.sqrt_fraction_bits > 4096 or type(self.stop_after_overlap) is not bool:
            raise ValueError('valid kernel precision and exact stop flag required')


@dataclass(frozen=True)
class BeadOverlapCell:
    cell: ExactTopCellXY
    depth: int
    state: str
    reason: str
    overlap_bottom_upper_mm: F | None = None
    overlap_top_lower_mm: F | None = None


@dataclass(frozen=True)
class BeadOverlapReport:
    first_segment_id: str
    second_segment_id: str
    policy: BeadOverlapPolicy
    state: str
    reason: str
    overlap_xy_box: ExactTopCellXY | None
    kernel_queries: int
    disjoint_cells: int
    overlap_cells: int
    unresolved_cells: int
    cancelled: bool
    cells: tuple[BeadOverlapCell, ...]
    printable_authorized: bool = field(default=False, init=False)
    physical_print_authorized: bool = field(default=False, init=False)
    physical_clearance_verified: bool = field(default=False, init=False)


def reflected_bead(segment):
    """Reflected top is negative original bottom, using the same stadium owner."""
    if type(segment) is not ExactNominalTopSegment:
        raise ValueError('exact immutable nominal bead required')
    reflect = lambda point: (*point[:2], segment.height_mm-point[2])
    return ExactNominalTopSegment(segment.segment_id, reflect(segment.start_xyz_mm),
        reflect(segment.end_xyz_mm), segment.width_mm, segment.height_mm, segment.source_kind)


def _envelope(segment):
    start, end = segment.start_xyz_mm, segment.end_xyz_mm
    radius = segment.width_mm/2
    # Axis-aligned flat caps have no axial extension. Other orientations keep
    # the larger radius-expanded AABB; this is exclusion only, never a solid.
    x_margin = F(0) if start[1] == end[1] else radius
    y_margin = F(0) if start[0] == end[0] else radius
    return ((min(start[0], end[0])-x_margin, max(start[0], end[0])+x_margin),
            (min(start[1], end[1])-y_margin, max(start[1], end[1])+y_margin),
            (min(start[2], end[2])-segment.height_mm, max(start[2], end[2])))


def audit_nominal_bead_overlap(first: ExactNominalTopSegment, second: ExactNominalTopSegment, *,
                              policy: BeadOverlapPolicy, cancelled: Callable[[], bool]):
    """Classify one nominal pair; caller owns chronology and job association.

    Zero-measure touching is disjoint-interiors, never a physical clearance claim.
    Early overlap returns all remaining XY work explicitly unresolved.
    """
    if type(first) is not ExactNominalTopSegment or type(second) is not ExactNominalTopSegment:
        raise ValueError('two exact immutable nominal beads required')
    if type(policy) is not BeadOverlapPolicy or not callable(cancelled):
        raise ValueError('exact bounded policy and cancellation callback required')
    if first.segment_id == second.segment_id:
        raise ValueError('distinct pair segment identities required')
    cancellation_latched = False

    def is_cancelled():
        nonlocal cancellation_latched
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('cancellation callback must return exact bool')
        cancellation_latched = cancellation_latched or answer
        return cancellation_latched

    def report(cells=(), box=None, queries=0, reason='bounded-xy-partition'):
        if is_cancelled():
            reason = 'cancelled'
        disjoint = sum(cell.state == 'disjoint' for cell in cells)
        overlap = sum(cell.state == 'overlap' for cell in cells)
        unresolved = sum(cell.state == 'unresolved' for cell in cells)
        state = 'overlap-proven' if overlap else 'incomplete' if unresolved or reason in ('cancelled', 'input-bit-limit') else 'disjoint-interiors'
        return BeadOverlapReport(first.segment_id, second.segment_id, policy, state, reason,
            box, queries, disjoint, overlap, unresolved, cancellation_latched, tuple(cells))

    if is_cancelled():
        return report(reason='cancelled')
    def exceeds_input_bits(segment):
        coordinates = (*segment.start_xyz_mm, *segment.end_xyz_mm, segment.width_mm, segment.height_mm)
        return any(integer.bit_length() > policy.max_coordinate_bits for value in coordinates
                   for integer in (value.numerator, value.denominator))

    if any(exceeds_input_bits(segment) for segment in (first, second)):
        return report(reason='input-bit-limit')
    reflected = (reflected_bead(first), reflected_bead(second))
    if any(exceeds_input_bits(segment) for segment in reflected):
        return report(reason='input-bit-limit')
    envelopes = (_envelope(first), _envelope(second))
    if any(min(a[1], b[1]) <= max(a[0], b[0]) for a, b in zip(*envelopes)):
        return report(reason='separated-or-touching-xyz-envelopes')
    x, y = tuple((max(a[0], b[0]), min(a[1], b[1])) for a, b in zip(*envelopes))[:2]
    initial = ExactTopCellXY(*x, *y)
    pending, leaves, queries = [(initial, 0)], [], 0
    found_overlap = False
    while pending:
        if is_cancelled() or queries+4 > policy.max_queries or (found_overlap and policy.stop_after_overlap):
            reason = ('cancelled' if cancellation_latched else 'overlap-found-remaining-work'
                      if found_overlap and policy.stop_after_overlap else 'query-resource-limit')
            leaves.extend(BeadOverlapCell(cell, depth, 'unresolved', reason) for cell, depth in pending)
            pending.clear()
            break
        cell, depth = pending.pop()
        outcomes = []
        for segment in (first, second, *reflected):
            outcomes.append(query_exact_nominal_top_cell(cell, (segment,), max_sources=1,
                max_coordinate_bits=policy.max_coordinate_bits, sqrt_fraction_bits=policy.sqrt_fraction_bits,
                cancelled=is_cancelled))
            queries += 1
        if is_cancelled() or any(query.state == 'incomplete' for query in outcomes):
            reason = 'cancelled' if cancellation_latched else 'kernel-resource-limit'
            leaves.append(BeadOverlapCell(cell, depth, 'unresolved', reason))
            continue
        a_top, b_top, a_reflected, b_reflected = outcomes
        if any(query.state == 'absent' for query in outcomes):
            leaves.append(BeadOverlapCell(cell, depth, 'disjoint', 'xy-support-absent'))
            continue
        # Reflected top bounds negate into original bottom bounds in reverse order.
        a_bottom_lower, b_bottom_lower = -a_reflected.top_z_upper_mm, -b_reflected.top_z_upper_mm
        if a_top.top_z_upper_mm <= b_bottom_lower or b_top.top_z_upper_mm <= a_bottom_lower:
            leaves.append(BeadOverlapCell(cell, depth, 'disjoint', 'vertical-interiors-separated-or-touching'))
            continue
        if all(query.top_z_lower_mm is not None for query in outcomes):
            lower = max(-a_reflected.top_z_lower_mm, -b_reflected.top_z_lower_mm)
            upper = min(a_top.top_z_lower_mm, b_top.top_z_lower_mm)
            if lower < upper:
                leaves.append(BeadOverlapCell(cell, depth, 'overlap', 'positive-area-and-vertical-interior', lower, upper))
                found_overlap = True
                continue
        if depth == policy.max_depth:
            leaves.append(BeadOverlapCell(cell, depth, 'unresolved', 'maximum-depth'))
            continue
        x0, x1, y0, y1 = cell.x_min_mm, cell.x_max_mm, cell.y_min_mm, cell.y_max_mm
        if x1-x0 >= y1-y0:
            midpoint = (x0+x1)/2
            children = (ExactTopCellXY(x0, midpoint, y0, y1), ExactTopCellXY(midpoint, x1, y0, y1))
        else:
            midpoint = (y0+y1)/2
            children = (ExactTopCellXY(x0, x1, y0, midpoint), ExactTopCellXY(x0, x1, midpoint, y1))
        pending.extend((child, depth+1) for child in reversed(children))
    area = lambda box: (box.x_max_mm-box.x_min_mm)*(box.y_max_mm-box.y_min_mm)
    if sum(area(leaf.cell) for leaf in leaves) != area(initial):
        raise RuntimeError('internal XY partition coverage failure')
    return report(leaves, initial, queries)
