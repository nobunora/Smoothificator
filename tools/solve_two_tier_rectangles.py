"""Exact bounded two-tier section family; no continuous-optimum claim."""
from dataclasses import dataclass
from fractions import Fraction as F

from tools.solve_triangle_rectangle import finite_triangle_rectangle_intersection_area, pack


@dataclass(frozen=True)
class TwoTierSectionPolicy:
    grid_divisions: int
    physical_heights_mm: tuple[F, ...]
    overlap_percent: F
    minimum_width_mm: F
    maximum_width_mm: F
    minimum_remaining_mm: F
    maximum_physical_height_mm: F
    max_events: int
    max_candidates: int
    max_area_queries: int
    max_number_bits: int

    def __post_init__(self):
        for key in ('grid_divisions', 'max_events', 'max_candidates', 'max_area_queries', 'max_number_bits'):
            if type(getattr(self, key)) is not int or getattr(self, key) < 1:
                raise ValueError('finite positive exact section limits required')
        if self.grid_divisions > 10000:
            raise ValueError('grid exceeds existing floor comparator limit10000')
        numbers = (self.overlap_percent, self.minimum_width_mm, self.maximum_width_mm,
                   self.minimum_remaining_mm, self.maximum_physical_height_mm)
        if (any(type(n) is not F for n in numbers) or not 0 <= self.overlap_percent <= 30
                or not 0 < self.minimum_width_mm <= self.maximum_width_mm
                or not 0 < self.minimum_remaining_mm <= self.maximum_physical_height_mm):
            raise ValueError('exact ordered section dimensions and overlap0..30 required')
        if (type(self.physical_heights_mm) is not tuple or not self.physical_heights_mm
                or any(type(h) is not F or h <= 0 for h in self.physical_heights_mm)
                or tuple(sorted(set(self.physical_heights_mm))) != self.physical_heights_mm):
            raise ValueError('explicit increasing immutable physical-height family required')


@dataclass(frozen=True)
class PosedSectionRectangle:
    left_mm: F
    right_mm: F
    bottom_mm: F
    top_mm: F

    @property
    def area_mm2(self):
        return (self.right_mm-self.left_mm)*(self.top_mm-self.bottom_mm)


@dataclass(frozen=True)
class TwoTierSectionBlock:
    lower: PosedSectionRectangle
    upper: PosedSectionRectangle | None


@dataclass(frozen=True)
class TwoTierSectionReport:
    state: str
    reason: str
    base_mm: F
    rise_mm: F
    policy: TwoTierSectionPolicy
    finite_family_complete: bool
    family_error_area_mm2: F | None
    floor_comparator_error_area_mm2: F | None
    floor_comparator_feasible: bool
    selected_error_area_mm2: F | None
    selected_from: str
    blocks: tuple[TwoTierSectionBlock, ...]
    events: int
    candidates: int
    area_queries: int
    height_pair_tests: int


class _SectionLimit(ValueError):
    pass


def section_block_error_area(base_mm, rise_mm, block):
    """Finite triangle symmetric difference, shared parent/child area once."""
    if type(block) is not TwoTierSectionBlock:
        raise ValueError('exact section block required')
    rectangles = (block.lower,) if block.upper is None else (block.lower, block.upper)
    union, inside = F(0), F(0)
    for rectangle in rectangles:
        if (type(rectangle) is not PosedSectionRectangle
                or any(type(n) is not F for n in (rectangle.left_mm, rectangle.right_mm, rectangle.bottom_mm, rectangle.top_mm))
                or rectangle.left_mm >= rectangle.right_mm or rectangle.bottom_mm >= rectangle.top_mm):
            raise ValueError('exact nondegenerate section rectangle required')
        union += rectangle.area_mm2
        inside += finite_triangle_rectangle_intersection_area(base_mm, rise_mm, rectangle.left_mm, rectangle.right_mm,
                                                              rectangle.bottom_mm, rectangle.top_mm)
    if block.upper is not None:
        a, b = block.lower, block.upper
        left, right = max(a.left_mm, b.left_mm), min(a.right_mm, b.right_mm)
        bottom, top = max(a.bottom_mm, b.bottom_mm), min(a.top_mm, b.top_mm)
        if left < right and bottom < top:
            union -= (right-left)*(top-bottom)
            inside -= finite_triangle_rectangle_intersection_area(base_mm, rise_mm, left, right, bottom, top)
    return base_mm*rise_mm/2+union-2*inside


def solve_two_tier_section(base_mm, rise_mm, *, policy, cancelled):
    """Enumerate configured lattice blocks then exact weighted-interval DP."""
    if (type(base_mm) is not F or type(rise_mm) is not F or min(base_mm, rise_mm) < 0
            or type(policy) is not TwoTierSectionPolicy or not callable(cancelled)):
        raise ValueError('exact nonnegative section and bounded policy required')
    events = candidates = queries = height_pair_tests = 0
    cache = {}

    def checkpoint():
        nonlocal events
        events += 1
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('exact bool section cancellation required')
        if answer or events > policy.max_events:
            raise _SectionLimit('cancelled' if answer else 'event-limit')

    def report(state, reason, complete=False, family=None, baseline=None, feasible=False, selected=None, origin='none', blocks=()):
        return TwoTierSectionReport(state, reason, base_mm, rise_mm, policy, complete, family, baseline,
            feasible, selected, origin, blocks, events, candidates, queries, height_pair_tests)

    def area(rectangle):
        nonlocal queries
        if rectangle not in cache:
            checkpoint()
            if queries >= policy.max_area_queries:
                raise _SectionLimit('area-query-limit')
            queries += 1
            cache[rectangle] = finite_triangle_rectangle_intersection_area(base_mm, rise_mm,
                rectangle.left_mm, rectangle.right_mm, rectangle.bottom_mm, rectangle.top_mm)
        return cache[rectangle]

    def contribution(block):
        a, b = block.lower, block.upper
        union, inside = a.area_mm2, area(a)
        if b is not None:
            union += b.area_mm2
            inside += area(b)
            if b.bottom_mm < a.top_mm:
                shared = PosedSectionRectangle(b.left_mm, b.right_mm, b.bottom_mm, min(a.top_mm, b.top_mm))
                union -= shared.area_mm2
                inside -= area(shared)
        return union-2*inside

    def rectangle(left, right, height, support):
        return PosedSectionRectangle(left, right, support-height*overlap, support+height*(1-overlap))

    try:
        checkpoint()
        if len(policy.physical_heights_mm) > policy.max_events:
            raise _SectionLimit('height-family-event-limit')
        for n in (base_mm, rise_mm, policy.overlap_percent, policy.minimum_width_mm, policy.maximum_width_mm,
                  policy.minimum_remaining_mm, policy.maximum_physical_height_mm, *policy.physical_heights_mm):
            checkpoint()
            if max(n.numerator.bit_length(), n.denominator.bit_length()) > policy.max_number_bits:
                raise _SectionLimit('input-bit-limit')
        if rise_mm == 0:
            return report('flat', 'no-slope-fill-required', True, F(0), F(0), True, F(0), 'none')
        if base_mm**2 < 2*policy.minimum_width_mm**2:
            return report('excluded', 'strict-short-base', True)
        overlap = policy.overlap_percent/100
        if policy.minimum_remaining_mm/(1-overlap) > policy.maximum_physical_height_mm:
            empty_error = base_mm*rise_mm/2
            return report('complete', 'no-feasible-compensated-physical-height', True, empty_error,
                          None, False, empty_error, 'finite-two-tier-family')
        heights = []
        for h in policy.physical_heights_mm:
            checkpoint()
            if policy.minimum_remaining_mm/(1-overlap)<=h<=policy.maximum_physical_height_mm and h*(1-overlap)<rise_mm:
                heights.append(h)
        pairs = {}
        for h in heights:
            children = []
            for k in heights:
                checkpoint()
                height_pair_tests += 1
                if (h+k)*(1-overlap)<rise_mm:
                    children.append(k)
            pairs[h] = tuple(children)
        n = policy.grid_divisions
        step = base_mm/n
        minimum_cells = int(-(-policy.minimum_width_mm//step))
        maximum_cells = min(n, int(policy.maximum_width_mm//step))
        # Bound the uncancellable legacy comparator before entering its loop.
        estimate = n*(max(0, maximum_cells-minimum_cells+1)+1)
        if estimate > policy.max_events-events:
            raise _SectionLimit('comparator-event-limit')
        events += estimate
        baseline = pack(base_mm, rise_mm, grid_divisions=n, minimum_width_mm=policy.minimum_width_mm,
            maximum_width_mm=policy.maximum_width_mm, minimum_height_mm=policy.minimum_remaining_mm/(1-overlap),
            maximum_height_mm=policy.maximum_physical_height_mm)
        baseline_blocks = tuple(TwoTierSectionBlock(rectangle(r.left_mm, r.right_mm, r.height_mm, F(0)), None)
                                for r in baseline.rectangles)
        baseline_feasible = all(b.lower.top_mm < rise_mm and 2*area(b.lower) >= b.lower.area_mm2 for b in baseline_blocks)
        baseline_error = base_mm*rise_mm/2+sum((contribution(b) for b in baseline_blocks), F(0)) if baseline_feasible else None
        scores, counts, previous = [F(0)]*(n+1), [0]*(n+1), [None]*(n+1)
        for end in range(1, n+1):
            checkpoint()
            scores[end], counts[end], previous[end] = scores[end-1], counts[end-1], (end-1, None)
            for cells in range(minimum_cells, min(maximum_cells, end)+1):
                start = end-cells
                for h in heights:
                    checkpoint()
                    lower = rectangle(start*step, end*step, h, F(0))
                    candidates += 1
                    if candidates > policy.max_candidates:
                        raise _SectionLimit('candidate-limit')
                    if 2*area(lower) < lower.area_mm2:
                        continue
                    best = TwoTierSectionBlock(lower, None)
                    best_contribution = contribution(best)
                    for upper_h in pairs[h]:
                        for child_end in range(start+minimum_cells, end+1):
                            for child_cells in range(minimum_cells, min(maximum_cells, child_end-start)+1):
                                checkpoint()
                                candidates += 1
                                if candidates > policy.max_candidates:
                                    raise _SectionLimit('candidate-limit')
                                upper = rectangle((child_end-child_cells)*step, child_end*step, upper_h, lower.top_mm)
                                if 2*area(upper) < upper.area_mm2:
                                    continue
                                block = TwoTierSectionBlock(lower, upper)
                                cost = contribution(block)
                                if cost < best_contribution:
                                    best, best_contribution = block, cost
                    score, count = scores[start]-best_contribution, counts[start]+1+(best.upper is not None)
                    if score > scores[end] or score == scores[end] and count < counts[end]:
                        scores[end], counts[end], previous[end] = score, count, (start, best)
        blocks, cursor = [], n
        while cursor:
            cursor, block = previous[cursor]
            if block is not None:
                blocks.append(block)
        blocks = tuple(reversed(blocks))
        family_error = base_mm*rise_mm/2-scores[n]
        if baseline_error is not None and baseline_error <= family_error:
            return report('complete', 'finite-family-and-posed-floor-comparator', True, family_error, baseline_error,
                True, baseline_error, 'floor-comparator', baseline_blocks)
        return report('complete', 'finite-family-and-posed-floor-comparator', True, family_error, baseline_error,
            baseline_feasible, family_error, 'finite-two-tier-family', blocks)
    except _SectionLimit as failure:
        return report('incomplete', str(failure))
