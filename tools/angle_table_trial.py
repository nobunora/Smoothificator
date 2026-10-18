"""Reusable finite slope-bin rectangle policy; no source or printer authority."""
from dataclasses import dataclass, asdict, replace
from fractions import Fraction as F
from hashlib import sha256
import json
from math import ceil, floor

from tools.solve_two_tier_rectangles import PosedSectionRectangle as Rect, TwoTierSectionBlock as Block
from tools.solve_triangle_rectangle import finite_triangle_rectangle_intersection_area as inside


@dataclass(frozen=True)
class AngleTablePolicy:
    layer_height_mm: F = F('.2')
    minimum_width_mm: F = F('.21')
    maximum_width_mm: F = F('.45')
    minimum_exposed_mm: F = F('.08')
    overlap_percent: F = F(0)
    grid_mm: F = F('.001')
    physical_height_step_mm: F = F('.01')
    slope_step: F = F('.01')
    maximum_slope: F = F(1)
    epsilon_fraction: F = F('.02')
    minimum_improvement_fraction: F = F('.05')
    width_samples_mm: tuple = (F('.211'), F('.251'), F('.301'), F('.351'), F('.401'), F('.449'))
    stack_topology_version: int = 2
    maximum_paths: int = 128
    maximum_events: int = 30000000

    def __post_init__(self):
        numbers = tuple(v for k,v in asdict(self).items() if k not in ('width_samples_mm','stack_topology_version','maximum_paths','maximum_events'))
        if any(type(v) is not F or max(v.numerator.bit_length(),v.denominator.bit_length())>128 for v in numbers):
            raise ValueError('bounded exact policy required')
        if not (0<self.minimum_width_mm<=self.maximum_width_mm and 0<self.minimum_exposed_mm<self.layer_height_mm
                and 0<=self.overlap_percent<=30 and 0<self.grid_mm<self.layer_height_mm
                and 0<self.physical_height_step_mm<self.layer_height_mm
                and (self.physical_height_step_mm/self.grid_mm).denominator==1
                and 0<self.slope_step<=self.maximum_slope<=1 and self.maximum_slope/self.slope_step<=1000
                and 0<=self.epsilon_fraction<=1 and 0<=self.minimum_improvement_fraction<=1):
            raise ValueError('ordered finite policy bounds required')
        if (type(self.width_samples_mm) is not tuple or not self.width_samples_mm
                or len(self.width_samples_mm)>64
                or tuple(sorted(set(self.width_samples_mm)))!=self.width_samples_mm
                or any(type(w) is not F or not self.minimum_width_mm<=w<=self.maximum_width_mm for w in self.width_samples_mm)
                or type(self.stack_topology_version) is not int or self.stack_topology_version!=2
                or type(self.maximum_paths) is not int or not 1<=self.maximum_paths<=512
                or type(self.maximum_events) is not int or not 1<=self.maximum_events<=100000000):
            raise ValueError('bounded explicit template family required')
        if self.layer_height_mm/self.grid_mm>10000 or self.layer_height_mm/self.physical_height_step_mm>10000:
            raise ValueError('physical height lattice exceeds bounded preflight limit')
        if not self.heights: raise ValueError('no exact overlap/grid-compatible physical height')

    @property
    def heights(self):
        remaining=1-self.overlap_percent/100
        strict_cap=(ceil(self.layer_height_mm/self.grid_mm)-1)*self.grid_mm
        proposed={i*self.physical_height_step_mm for i in range(1,ceil(self.layer_height_mm/self.physical_height_step_mm))}
        proposed.add(strict_cap)
        return tuple(sorted(h for h in proposed if h<self.layer_height_mm and h*remaining>=self.minimum_exposed_mm
                     and (h*remaining/self.grid_mm).denominator==1))

    @property
    def identity(self):
        return sha256(json.dumps(asdict(self),default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class SectionMember:
    blocks: tuple
    error_mm2: F

    @property
    def topology(self): return tuple(block.upper is not None for block in self.blocks)

    @property
    def path_count(self): return len(self.blocks)+sum(self.topology)


@dataclass(frozen=True)
class AngleBin:
    slope: F
    state: str
    member: SectionMember | None
    baseline_error_mm2: F | None
    reason: str
    alternatives: tuple = ()
    sensitivities: tuple = ()


@dataclass(frozen=True)
class AngleTable:
    policy: AngleTablePolicy
    bins: tuple
    events: int
    boundary_brackets: tuple
    content_identity: str


def _table_identity(policy,bins):
    return sha256(json.dumps({'policy':policy.identity,'bins':[asdict(b) for b in bins]},
                            default=str,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _clipped(rect):
    return Rect(rect.left_mm,rect.right_mm,max(F(0),rect.bottom_mm),rect.top_mm)


def floor_union_error(base,rise,blocks):
    """Exact disjoint-root union error above the already present infinite floor."""
    contribution=F(0)
    for block in blocks:
        a=_clipped(block.lower)
        rectangles=[a]
        if block.upper is not None: rectangles.append(_clipped(block.upper))
        for r in rectangles:
            if r.top_mm>r.bottom_mm:
                contribution+=r.area_mm2-2*inside(base,rise,r.left_mm,r.right_mm,r.bottom_mm,r.top_mm)
        if len(rectangles)==2:
            b=rectangles[1]
            l,r=max(a.left_mm,b.left_mm),min(a.right_mm,b.right_mm)
            z,t=max(a.bottom_mm,b.bottom_mm),min(a.top_mm,b.top_mm)
            if l<r and z<t: contribution-=(r-l)*(t-z)-2*inside(base,rise,l,r,z,t)
    return base*rise/2+contribution


def physical_spill_legal(base,rise,rect):
    return 2*inside(base,rise,rect.left_mm,rect.right_mm,rect.bottom_mm,rect.top_mm)>=rect.area_mm2


def select_epsilon(members,baseline,policy):
    if not members or baseline<=0: return None
    best=min(m.error_mm2 for m in members)
    eligible=[m for m in members if m.error_mm2<=best+policy.epsilon_fraction*baseline]
    chosen=min(eligible,key=lambda m:(m.path_count,sum(m.topology),m.error_mm2,repr(m.blocks)))
    if baseline-chosen.error_mm2<policy.minimum_improvement_fraction*baseline:return None
    return chosen


def build_angle_table(policy,*,cancelled=lambda:False):
    if type(policy) is not AngleTablePolicy or not callable(cancelled):raise ValueError('explicit finite table policy required')
    events=0;bins=[];overlap=policy.overlap_percent/100;rise=policy.layer_height_mm
    def tick():
        nonlocal events
        events+=1
        answer=cancelled()
        if type(answer) is not bool:raise ValueError('exact cancellation bool required')
        if answer or events>policy.maximum_events:raise ValueError('angle-table-cancelled-or-event-limit')
    for i in range(floor(policy.maximum_slope/policy.slope_step)+1):
        tick();slope=i*policy.slope_step
        if not slope:
            bins.append(AngleBin(slope,'skip',None,F(0),'flat'));continue
        base=rise/slope;baseline=base*rise/2;members=[]
        if base*base<2*policy.minimum_width_mm**2:
            bins.append(AngleBin(slope,'skip',None,baseline,'strict-short-base'));continue
        for width in policy.width_samples_mm:
            count=floor((base+policy.grid_mm)/(width+policy.grid_mm))
            if not 1<=count<=policy.maximum_paths:continue
            length=count*width+(count-1)*policy.grid_mm
            for shift in (F(0),(base-length)/2,base-length):
                # Uniform row templates are explicit: every lane chooses independently,
                # preserving minimal error for every (total paths, upper count) pair.
                frontier={(0,0):(F(0),())}
                for lane in range(count):
                    left=shift+lane*(width+policy.grid_mm);options=[]
                    for h in policy.heights:
                        tick();root=Rect(left,left+width,-h*overlap,h*(1-overlap))
                        if not physical_spill_legal(base,rise,root):continue
                        single=Block(root,None)
                        options.append((single,floor_union_error(base,rise,(single,))-baseline))
                        for upper_h in policy.heights:
                            tick();top=root.top_mm+upper_h*(1-overlap)
                            if top>=rise or upper_h>h:continue
                            for upper_width in policy.width_samples_mm:
                                tick()
                                if upper_width>=width:continue
                                inset=(width-upper_width)/2
                                upper=Rect(left+inset,left+width-inset,root.top_mm-upper_h*overlap,top)
                                if not physical_spill_legal(base,rise,upper):continue
                                block=Block(root,upper)
                                options.append((block,floor_union_error(base,rise,(block,))-baseline))
                    # Empty lanes are part of the finite family; preserves feasible
                    # high-angle rows whose low lane cannot satisfy exposed height.
                    best_options={}
                    for block,gain in options:
                        topology=block.upper is not None
                        if gain<0 and (topology not in best_options or gain<best_options[topology][1]):
                            best_options[topology]=(block,gain)
                    options=tuple(best_options.values())
                    updated=dict(frontier)
                    for (paths,uppers),(error,blocks) in frontier.items():
                        for block,gain in options:
                            tick();key=(paths+1+(block.upper is not None),uppers+(block.upper is not None))
                            if key[0]>policy.maximum_paths:continue
                            candidate=(error+gain,blocks+(block,))
                            if key not in updated or candidate[0]<updated[key][0]:updated[key]=candidate
                    frontier=updated
                members.extend(SectionMember(blocks,baseline+error) for error,blocks in frontier.values() if blocks)
        chosen=select_epsilon(members,baseline,policy)
        # Retain distinct precomputed geometry for bounded source validation;
        # this is never a location-dependent search/optimization.
        alternatives=[];seen=set()
        best_error=min((m.error_mm2 for m in members),default=baseline)
        threshold=best_error+policy.epsilon_fraction*baseline
        for member in sorted(members,key=lambda m:(m.error_mm2>threshold,
                m.path_count if m.error_mm2<=threshold else 0,sum(m.topology),m.error_mm2,repr(m.blocks))):
            if baseline-member.error_mm2<policy.minimum_improvement_fraction*baseline:continue
            if member==chosen or member.blocks in seen:continue
            seen.add(member.blocks);alternatives.append(member)
            if len(alternatives)==64:break
        sensitivity=[]
        for epsilon in (F('.01'),F('.02'),F('.05')):
            for gain in (F('.05'),F('.1')):
                alternative=select_epsilon(members,baseline,replace(policy,epsilon_fraction=epsilon,minimum_improvement_fraction=gain))
                sensitivity.append((epsilon,gain,None if alternative is None else alternative.path_count,
                    None if alternative is None else sum(alternative.topology),None if alternative is None else alternative.error_mm2))
        bins.append(AngleBin(slope,'selected' if chosen else 'skip',chosen,baseline,
                             'finite-template-selected' if chosen else 'no-member-meets-improvement',tuple(alternatives),tuple(sensitivity)))
    brackets=tuple((a.slope,b.slope) for a,b in zip(bins,bins[1:])
                   if (a.state,None if a.member is None else a.member.topology)!=(b.state,None if b.member is None else b.member.topology))
    return AngleTable(policy,tuple(bins),events,brackets,_table_identity(policy,bins))


_VALIDATED_TABLES = {}


def validate_angle_table(table):
    """Authenticate immutable table once; bounded strong cache prevents id reuse."""
    if _VALIDATED_TABLES.get(id(table)) is table:
        return table
    if type(table) is not AngleTable or type(table.policy) is not AngleTablePolicy:
        raise ValueError('exact bounded angle table required')
    p=table.policy
    if (type(table.bins) is not tuple or len(table.bins)!=floor(p.maximum_slope/p.slope_step)+1
            or any(type(row) is not AngleBin or row.slope!=i*p.slope_step for i,row in enumerate(table.bins))
            or any(row.member is not None and (type(row.member) is not SectionMember
                or type(row.member.blocks) is not tuple or len(row.member.blocks)>p.maximum_paths
                or any(type(b) is not Block or type(b.lower) is not Rect
                    or b.upper is not None and type(b.upper) is not Rect for b in row.member.blocks)) for row in table.bins)):
        raise ValueError('bounded table shape mismatch')
    if any(type(row.alternatives) is not tuple or len(row.alternatives)>64
           or any(type(m) is not SectionMember or type(m.blocks) is not tuple or len(m.blocks)>p.maximum_paths
               or any(type(b) is not Block or type(b.lower) is not Rect
                   or b.upper is not None and type(b.upper) is not Rect for b in m.blocks) for m in row.alternatives) for row in table.bins):
        raise ValueError('bounded alternative table shape mismatch')
    for row in table.bins:
        if row.slope==0:
            if row.state!='skip' or row.member is not None or row.alternatives or row.baseline_error_mm2!=0:
                raise ValueError('flat table row must skip without material')
        elif row.baseline_error_mm2!=p.layer_height_mm**2/(2*row.slope):
            raise ValueError('table row baseline identity mismatch')
        if (row.state not in ('skip','selected') or (row.state=='selected')!=(row.member is not None)
                or any(m.path_count>p.maximum_paths for m in ((row.member,) if row.member else ())+row.alternatives)):
            raise ValueError('table state/topology path limit mismatch')
    if table.content_identity!=_table_identity(p,table.bins):raise ValueError('stale table content identity')
    if len(_VALIDATED_TABLES)>=4:
        _VALIDATED_TABLES.pop(next(iter(_VALIDATED_TABLES)))
    _VALIDATED_TABLES[id(table)]=table
    return table


def lookup_angle_table(table,base,rise,*,alternative_index=0):
    """Conservative finite bins: no optimization/inter-topology interpolation."""
    validate_angle_table(table)
    p=table.policy
    if type(base) is not F or type(rise) is not F or base<=0 or rise!=p.layer_height_mm:
        return None,'unsupported-section'
    if base*base<2*p.minimum_width_mm*p.minimum_width_mm:
        return None,'strict-short-base'
    slope=rise/base
    if slope>p.maximum_slope:return None,'outside-table-domain'
    index=floor(slope/p.slope_step)
    row=table.bins[index]
    if row.member is None:return None,'precomputed-bin-'+row.reason
    if type(alternative_index) is not int or not 0<=alternative_index<=len(row.alternatives):
        return None,'outside-precomputed-alternative-domain'
    selected=row.member if not alternative_index else row.alternatives[alternative_index-1]
    scale=base/(rise/row.slope)
    def pose(r):
        # Floor quantization is deterministic and never expands a bin template.
        return Rect(floor(r.left_mm*scale/p.grid_mm)*p.grid_mm,
                    floor(r.right_mm*scale/p.grid_mm)*p.grid_mm,r.bottom_mm,r.top_mm)
    blocks=tuple(Block(pose(b.lower),None if b.upper is None else pose(b.upper)) for b in selected.blocks)
    previous=None
    for block in blocks:
        if previous is not None and block.lower.left_mm<previous:return None,'bin-root-overlap-revalidation'
        previous=block.lower.right_mm
        support=F(0)
        for r in (block.lower,)+( () if block.upper is None else (block.upper,)):
            coords=(r.left_mm,r.right_mm,r.bottom_mm,r.top_mm)
            if any(type(v) is not F or max(v.numerator.bit_length(),v.denominator.bit_length())>128 for v in coords):
                return None,'bin-coordinate-revalidation'
            height=r.top_mm-r.bottom_mm;remaining=r.top_mm-support
            if (not 0<height<p.layer_height_mm or height>r.right_mm-r.left_mm
                    or remaining<p.minimum_exposed_mm or remaining!=height*(1-p.overlap_percent/100)
                    or r.top_mm>=rise or any((v/p.grid_mm).denominator!=1 for v in (height,r.top_mm,remaining))):
                return None,'bin-height-grid-revalidation'
            if not p.minimum_width_mm<=r.right_mm-r.left_mm<=p.maximum_width_mm:return None,'bin-width-revalidation'
            if not physical_spill_legal(base,rise,r):return None,'bin-physical-spill-revalidation'
            if support and (r.left_mm<block.lower.left_mm or r.right_mm>block.lower.right_mm
                    or r.right_mm-r.left_mm>=block.lower.right_mm-block.lower.left_mm
                    or height>block.lower.top_mm-block.lower.bottom_mm):
                return None,'bin-parent-containment-revalidation'
            support=r.top_mm
    member=SectionMember(blocks,floor_union_error(base,rise,blocks))
    baseline=base*rise/2
    if baseline-member.error_mm2<p.minimum_improvement_fraction*baseline:return None,'bin-improvement-revalidation'
    return member,'validated-finite-bin-member'
