"""Bound continuous nominal centerline-bottom contact; no physical authority."""
from dataclasses import dataclass, field
from fractions import Fraction as F
from typing import Callable

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from adaptive_subedge.engine.support_cell import query_exact_nominal_top_cell, query_exact_nominal_top_span


@dataclass(frozen=True)
class ChronologicalSource:
    segment: ExactNominalTopSegment
    execution_order: int

    def __post_init__(self):
        if type(self.segment) is not ExactNominalTopSegment:
            raise ValueError('exact immutable nominal source segment required')
        if type(self.execution_order) is not int or self.execution_order < 0:
            raise ValueError('nonnegative exact source execution order required')


@dataclass(frozen=True)
class ContactPath:
    candidate_id: str
    execution_order: int
    points_xy_mm: tuple[tuple[F, F], ...]
    bottom_z_mm: F

    def __post_init__(self):
        if type(self.candidate_id) is not str or not self.candidate_id.strip():
            raise ValueError('nonblank candidate identity required')
        if type(self.execution_order) is not int or self.execution_order < 0:
            raise ValueError('nonnegative exact candidate execution order required')
        if type(self.bottom_z_mm) is not F:
            raise ValueError('constant exact rational bottom plane required')
        if type(self.points_xy_mm) is not tuple or len(self.points_xy_mm) < 2:
            raise ValueError('immutable nonempty polyline required')
        for point in self.points_xy_mm:
            if type(point) is not tuple or len(point) != 2 or any(type(v) is not F for v in point):
                raise ValueError('exact immutable XY points required')
        if any(a == b for a, b in zip(self.points_xy_mm, self.points_xy_mm[1:])):
            raise ValueError('nonzero original XY segments required')


@dataclass(frozen=True)
class ContactPolicy:
    xy_resolution_mm: F
    padding_mm: F
    max_depth: int
    max_queries: int
    max_path_segments: int
    max_input_sources: int
    kernel_max_sources: int
    max_coordinate_bits: int
    sqrt_fraction_bits: int
    query_geometry_mode: str = 'padded-axis-box'

    def __post_init__(self):
        if any(type(v) is not F or v <= 0 for v in (self.xy_resolution_mm, self.padding_mm)):
            raise ValueError('explicit positive rational grid and padding required')
        if type(self.max_depth) is not int or not 0 <= self.max_depth <= 32:
            raise ValueError('explicit maximum parameter depth0..32 required')
        for name in ('max_queries', 'max_path_segments', 'max_input_sources',
                     'kernel_max_sources', 'max_coordinate_bits', 'sqrt_fraction_bits'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f'explicit positive integer required: {name}')
        if self.sqrt_fraction_bits > 4096:
            raise ValueError('sqrt precision exceeds kernel limit4096')
        if type(self.query_geometry_mode) is not str or self.query_geometry_mode not in ('padded-axis-box', 'exact-span'):
            raise ValueError('explicit supported query geometry mode required')


@dataclass(frozen=True)
class ContactInterval:
    segment_index: int
    parameter_start: F
    parameter_end: F
    state: str
    reason: str
    enclosing_cell: ExactTopCellXY | None
    top_lower_mm: F | None = None
    top_upper_mm: F | None = None
    queried_span_xy_mm: tuple[tuple[F, F], tuple[F, F]] | None = None


@dataclass(frozen=True)
class QueriedContactSpan:
    segment_index: int
    parameter_start: F
    parameter_end: F
    endpoints_xy_mm: tuple[tuple[F, F], tuple[F, F]]


@dataclass(frozen=True)
class ContactReport:
    candidate_id: str
    state: str
    bottom_z_mm: F
    policy: ContactPolicy
    source_count: int
    earlier_source_count: int
    excluded_source_count: int
    cells_queried: int
    supported_intervals: int
    gap_intervals: int
    unresolved_intervals: int
    cancelled: bool
    intervals: tuple[ContactInterval, ...]
    nominal_centerline_contact_proven: bool
    spans_queried: int = 0
    query_count: int = 0
    queried_spans: tuple[QueriedContactSpan, ...] = ()
    printable_authorized: bool = field(default=False, init=False)
    physical_print_authorized: bool = field(default=False, init=False)


def _piece_endpoints(path, index, t0, t1):
    start, end = path.points_xy_mm[index:index+2]
    a = tuple(x+(y-x)*t0 for x, y in zip(start, end))
    b = tuple(x+(y-x)*t1 for x, y in zip(start, end))
    return a, b


def _piece_box(path, index, t0, t1, padding):
    a, b = _piece_endpoints(path, index, t0, t1)
    return ExactTopCellXY(min(a[0], b[0])-padding, max(a[0], b[0])+padding,
                          min(a[1], b[1])-padding, max(a[1], b[1])+padding)


def audit_continuous_path_contact(path: ContactPath, sources: tuple[ChronologicalSource, ...], *,
                                  policy: ContactPolicy, cancelled: Callable[[], bool]) -> ContactReport:
    """Bisect line parameters, never off-line box regions, to cover every segment.

    Intersection permits penetration. Certificates concern only the nominal
    centerline bottom; full footprint/contact area and tool clearance are absent.
    """
    if type(path) is not ContactPath or type(policy) is not ContactPolicy:
        raise ValueError('exact immutable path and policy required')
    if type(sources) is not tuple or not callable(cancelled):
        raise ValueError('immutable chronological sources and cancellation callback required')
    if any(type(source) is not ChronologicalSource for source in sources):
        raise ValueError('exact chronological source required')
    ids = [source.segment.segment_id for source in sources]
    orders = [source.execution_order for source in sources]
    if len(set(ids)) != len(ids) or path.candidate_id in ids or len(set(orders)) != len(orders):
        raise ValueError('unique noncandidate source identities and execution orders required')
    if any((v/policy.xy_resolution_mm).denominator != 1 for point in path.points_xy_mm for v in point):
        raise ValueError('candidate XY points must lie on the declared quantized grid')
    earlier = tuple(source.segment for source in sources if source.execution_order < path.execution_order)
    pending = [(i, F(0), F(1), 0) for i in reversed(range(len(path.points_xy_mm)-1))]
    intervals, queried, queried_spans = [], 0, []
    cancellation_latched = False

    def is_cancelled():
        nonlocal cancellation_latched
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('cancellation callback must return exact bool')
        cancellation_latched = cancellation_latched or answer
        return cancellation_latched

    input_limit = len(sources) > policy.max_input_sources or len(pending) > policy.max_path_segments
    while pending:
        if is_cancelled() or input_limit or queried >= policy.max_queries:
            reason = 'cancelled' if cancellation_latched else 'input-resource-limit' if input_limit else 'query-resource-limit'
            intervals.extend(ContactInterval(i, t0, t1, 'unresolved', reason, None)
                             for i, t0, t1, depth in pending)
            pending.clear()
            break
        index, t0, t1, depth = pending.pop()
        span = _piece_endpoints(path, index, t0, t1) if policy.query_geometry_mode == 'exact-span' else None
        cell = None if span is not None else _piece_box(path, index, t0, t1, policy.padding_mm)
        arguments = dict(max_sources=policy.kernel_max_sources, max_coordinate_bits=policy.max_coordinate_bits,
                         sqrt_fraction_bits=policy.sqrt_fraction_bits, cancelled=is_cancelled)
        query = (query_exact_nominal_top_span(*span, earlier, **arguments) if span is not None
                 else query_exact_nominal_top_cell(cell, earlier, **arguments))
        queried += 1
        if span is not None:
            queried_spans.append(QueriedContactSpan(index, t0, t1, span))
        def witness(state, reason, lower=None, upper=None):
            return ContactInterval(index, t0, t1, state, reason, cell, lower, upper, span)
        if is_cancelled() or query.state == 'incomplete':
            intervals.append(witness('unresolved', 'cancelled' if cancellation_latched else f'kernel-{query.reason}'))
        elif query.top_z_lower_mm is not None and query.top_z_lower_mm >= path.bottom_z_mm:
            intervals.append(witness('supported', 'whole-piece-lower-bound', query.top_z_lower_mm, query.top_z_upper_mm))
        elif query.state == 'absent' or (query.top_z_upper_mm is not None and query.top_z_upper_mm < path.bottom_z_mm):
            intervals.append(witness('gap', 'whole-piece-disjoint' if query.state == 'absent'
                else 'whole-piece-upper-below-bottom', query.top_z_lower_mm, query.top_z_upper_mm))
        elif depth == policy.max_depth:
            intervals.append(witness('unresolved', 'maximum-depth', query.top_z_lower_mm, query.top_z_upper_mm))
        else:
            midpoint = (t0+t1)/2
            pending.extend(((index, midpoint, t1, depth+1), (index, t0, midpoint, depth+1)))
    intervals.sort(key=lambda piece: (piece.segment_index, piece.parameter_start))
    # Every leaf comes from a parameter partition; assert its exact coverage.
    cursor, current_segment = F(0), 0
    for piece in intervals:
        if piece.segment_index != current_segment:
            if cursor != 1 or piece.segment_index != current_segment+1:
                raise RuntimeError('internal path interval coverage failure')
            current_segment, cursor = piece.segment_index, F(0)
        if piece.parameter_start != cursor or not piece.parameter_start < piece.parameter_end <= 1:
            raise RuntimeError('internal path interval partition failure')
        cursor = piece.parameter_end
    if current_segment != len(path.points_xy_mm)-2 or cursor != 1:
        raise RuntimeError('internal incomplete path interval coverage')
    supported = sum(piece.state == 'supported' for piece in intervals)
    gaps = sum(piece.state == 'gap' for piece in intervals)
    unresolved = sum(piece.state == 'unresolved' for piece in intervals)
    state = 'gap-proven' if gaps else 'incomplete' if unresolved else 'nominal-centerline-contact-proven'
    return ContactReport(path.candidate_id, state, path.bottom_z_mm, policy, len(sources), len(earlier),
        len(sources)-len(earlier), queried if policy.query_geometry_mode == 'padded-axis-box' else 0,
        supported, gaps, unresolved, cancellation_latched, tuple(intervals), not gaps and not unresolved,
        queried if policy.query_geometry_mode == 'exact-span' else 0, queried, tuple(queried_spans))
