"""Continuous constant-Z contact by kernel-certified closed parameter intervals."""
from dataclasses import dataclass,field,replace
from fractions import Fraction as F

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from adaptive_subedge.engine.support_cell import _sqrt_bounds,query_exact_nominal_top_span,query_exact_nominal_top_point
from tools.audit_continuous_path_contact import ContactPath,ChronologicalSource


@dataclass(frozen=True)
class NativeStripContactPolicy:
    max_sources: int
    max_path_segments: int
    max_intervals: int
    max_queries: int
    max_events: int
    max_coordinate_bits: int
    sqrt_fraction_bits: int
    inner_inset_mm: F

    def __post_init__(self):
        for name in ('max_sources','max_path_segments','max_intervals','max_queries','max_events','max_coordinate_bits','sqrt_fraction_bits'):
            if type(getattr(self,name)) is not int or getattr(self,name)<1:raise ValueError('explicit positive exact interval-contact budgets required')
        if (self.sqrt_fraction_bits>4096 or type(self.inner_inset_mm) is not F or self.inner_inset_mm<0
                or max(self.inner_inset_mm.numerator.bit_length(),self.inner_inset_mm.denominator.bit_length())>self.max_coordinate_bits):
            raise ValueError('bounded exact inward contact inset/precision required')


@dataclass(frozen=True)
class CertifiedContactInterval:
    path_segment_index: int
    source_id: str
    source_execution_order: int
    parameter_start: F
    parameter_end: F
    start_xy_mm: tuple[F,F]
    end_xy_mm: tuple[F,F]
    top_lower_mm: F
    top_upper_mm: F


@dataclass(frozen=True)
class ContactGapPoint:
    path_segment_index: int
    parameter: F
    point_xy_mm: tuple[F,F]
    query_state: str
    top_upper_mm: F | None


@dataclass(frozen=True)
class NativeStripContactReport:
    candidate_id: str
    state: str
    reason: str
    policy: NativeStripContactPolicy
    source_count: int
    earlier_source_count: int
    query_count: int
    events: int
    certificates: tuple[CertifiedContactInterval,...]
    uncovered_intervals: tuple[tuple[int,F,F],...]
    gap_witness: ContactGapPoint | None
    cancelled: bool
    nominal_centerline_contact_proven: bool
    physical_authority: bool=field(default=False,init=False)


class _ContactLimit(ValueError):pass


def _clip_affine(low,high,constant,slope):
    if slope==0:return (F(0),F(1)) if low<=constant<=high else None
    a,b=sorted(((low-constant)/slope,(high-constant)/slope))
    a,b=max(F(0),a),min(F(1),b)
    return (a,b) if a<b else None


def audit_native_constant_z_contact(path,sources,*,policy,cancelled):
    if (type(path) is not ContactPath or type(sources) is not tuple or type(policy) is not NativeStripContactPolicy
            or not callable(cancelled) or len(sources)>policy.max_sources
            or len(path.points_xy_mm)-1>policy.max_path_segments):
        raise ValueError('immutable bounded native contact DTOs required')
    events=queries=0;latched=False;certificates=[];uncovered=[];gap=None
    ids=set();orders=set();earlier=[]

    def poll():
        nonlocal latched
        answer=cancelled()
        if type(answer) is not bool:raise ValueError('exact interval-contact cancellation bool required')
        latched|=answer
        return latched

    def tick():
        nonlocal events
        events+=1
        if poll():raise _ContactLimit('cancelled')
        if events>policy.max_events:raise _ContactLimit('event-limit')

    def bounded(*numbers):
        for number in numbers:
            if type(number) is not F:raise ValueError('exact rational native contact geometry required')
            if max(number.numerator.bit_length(),number.denominator.bit_length())>policy.max_coordinate_bits:
                raise _ContactLimit('coordinate-bit-limit')

    def query_budget():
        nonlocal queries
        tick()
        if queries>=policy.max_queries:raise _ContactLimit('query-limit')
        queries+=1

    def publish(state,reason):
        if poll():state,reason='incomplete','cancelled'
        report=NativeStripContactReport(path.candidate_id,state,reason,policy,len(sources),len(earlier),queries,events,
            tuple(certificates),tuple(uncovered),gap,latched,state=='nominal-centerline-contact-proven')
        if poll():return replace(report,state='incomplete',reason='cancelled',cancelled=True,nominal_centerline_contact_proven=False)
        return report

    try:
        tick();bounded(path.bottom_z_mm,*(v for p in path.points_xy_mm for v in p))
        for source in sources:
            tick()
            if type(source) is not ChronologicalSource or type(source.segment) is not ExactNominalTopSegment:
                raise ValueError('exact chronological original/candidate sources required')
            segment=source.segment
            if type(segment.segment_id) is not str or not segment.segment_id or segment.segment_id in ids or segment.segment_id==path.candidate_id:
                raise ValueError('unique exact source identities required')
            ids.add(segment.segment_id)
            if source.execution_order in orders:raise ValueError('unique source execution orders required')
            orders.add(source.execution_order)
            bounded(*segment.start_xyz_mm,*segment.end_xyz_mm,segment.width_mm,segment.height_mm)
            if segment.width_mm<segment.height_mm or segment.height_mm<=0:
                raise ValueError('valid stadium source dimensions required')
            if source.execution_order<path.execution_order:earlier.append(source)
        for index,(start,end) in enumerate(zip(path.points_xy_mm,path.points_xy_mm[1:])):
            tick();direction=tuple(b-a for a,b in zip(start,end));intervals=[]
            for source in earlier:
                tick();segment=source.segment;a,b=segment.start_xyz_mm,segment.end_xyz_mm
                if a[2]!=b[2] or path.bottom_z_mm>a[2]:continue
                dx,dy=b[0]-a[0],b[1]-a[1];length_squared=dx*dx+dy*dy
                bounded(length_squared)
                if length_squared<=0:raise ValueError('nondegenerate XY source required')
                radius=segment.height_mm/2;flat=(segment.width_mm-segment.height_mm)/2
                offset=path.bottom_z_mm-(a[2]-radius)
                if offset<=0:half_width=segment.width_mm/2
                else:
                    radicand=radius*radius-offset*offset;bounded(radicand)
                    if radicand<0:continue
                    half_width=flat+_sqrt_bounds(radicand,policy.sqrt_fraction_bits)[0]
                half_width=max(F(0),half_width-policy.inner_inset_mm)
                cross_limit=half_width*_sqrt_bounds(length_squared,policy.sqrt_fraction_bits)[0]
                px,py=start[0]-a[0],start[1]-a[1]
                dot0,dot_delta=px*dx+py*dy,direction[0]*dx+direction[1]*dy
                cross0,cross_delta=dx*py-dy*px,dx*direction[1]-dy*direction[0]
                bounded(cross_limit,dot0,dot_delta,cross0,cross_delta)
                axial=_clip_affine(F(0),length_squared,dot0,dot_delta)
                lateral=_clip_affine(-cross_limit,cross_limit,cross0,cross_delta)
                if axial is None or lateral is None:continue
                lo,hi=max(axial[0],lateral[0]),min(axial[1],lateral[1])
                if lo>=hi:continue
                endpoints=tuple(tuple(x+t*d for x,d in zip(start,direction)) for t in (lo,hi))
                bounded(lo,hi,*(v for p in endpoints for v in p));query_budget()
                proof=query_exact_nominal_top_span(*endpoints,(segment,),max_sources=1,
                    max_coordinate_bits=policy.max_coordinate_bits,sqrt_fraction_bits=policy.sqrt_fraction_bits,cancelled=poll)
                if poll():raise _ContactLimit('cancelled')
                if (proof.state=='full-bounded' and proof.top_z_lower_mm is not None
                        and proof.top_z_lower_mm>=path.bottom_z_mm):
                    if len(certificates)>=policy.max_intervals:raise _ContactLimit('interval-limit')
                    certificate=CertifiedContactInterval(index,segment.segment_id,source.execution_order,lo,hi,
                        *endpoints,proof.top_z_lower_mm,proof.top_z_upper_mm)
                    certificates.append(certificate);intervals.append((lo,hi))
            work=len(intervals)*max(1,len(intervals).bit_length())
            tick()
            if work>policy.max_events-events:raise _ContactLimit('interval-sort-event-limit')
            events+=work;intervals.sort();cursor=F(0)
            gaps=[]
            for lo,hi in intervals:
                tick()
                if lo>cursor:gaps.append((cursor,lo))
                cursor=max(cursor,hi)
            if cursor<1:gaps.append((cursor,F(1)))
            uncovered.extend((index,lo,hi) for lo,hi in gaps)
            if gaps:
                # A missing inner interval is not a gap proof. Only this exact
                # all-eligible-source point upper bound may prove a negative.
                lo,hi=gaps[0];parameter=(lo+hi)/2
                point=tuple(x+parameter*d for x,d in zip(start,direction));bounded(parameter,*point);query_budget()
                proof=query_exact_nominal_top_point(*point,tuple(s.segment for s in earlier),max_sources=policy.max_sources,
                    max_coordinate_bits=policy.max_coordinate_bits,sqrt_fraction_bits=policy.sqrt_fraction_bits,cancelled=poll)
                if poll():raise _ContactLimit('cancelled')
                if proof.state=='absent' or proof.top_z_upper_mm is not None and proof.top_z_upper_mm<path.bottom_z_mm:
                    gap=ContactGapPoint(index,parameter,point,proof.state,proof.top_z_upper_mm)
                    return publish('gap-proven','all-source-point-upper-bound-below-bottom')
                return publish('incomplete','inward-interval-union-not-covered')
        return publish('nominal-centerline-contact-proven','closed-union-of-public-kernel-certified-spans')
    except _ContactLimit as failure:
        return publish('incomplete',str(failure))
