"""Finite contact-aware straight-block trial planning; no source/print authority."""
from bisect import bisect_right
from dataclasses import dataclass,field,replace
from fractions import Fraction as F
import re

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment

from tools.audit_continuous_path_contact import ContactPath,ChronologicalSource,audit_continuous_path_contact
from tools.native_certified_contact import NativeStripContactPolicy,audit_native_constant_z_contact
from tools.audit_two_tier_material import TwoTierMaterialPolicy,audit_two_tier_material
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.prepare_two_tier_intents import SupportedPathIntent,TwoTierGraphPolicy,FrozenTwoTierPlan,freeze_supported_graph
from tools.solve_triangle_rectangle import pack,finite_triangle_rectangle_intersection_area
from tools.solve_two_tier_rectangles import PosedSectionRectangle,TwoTierSectionBlock,section_block_error_area
from tools.supplemental_z_hop import SupplementalPath,HopPolicy,rounded,_validate_policy


@dataclass(frozen=True)
class NativeTrialStep:
    step_id: str
    source_context_identity: str
    floor_z_mm: F
    next_layer_z_mm: F
    triangle_left_y_mm: F
    triangle_right_y_mm: F
    x_span_mm: tuple[F,F]
    execution_order: int


@dataclass(frozen=True)
class NativeTrialPlannerPolicy:
    widths_mm: tuple[F,...]
    physical_heights_mm: tuple[F,...]
    centers_relative_mm: tuple[F,...]
    child_alignment_insets_mm: tuple[F,...]
    overlap_percent: F
    floor_comparator_divisions: int
    max_events: int
    max_candidates: int
    max_contact_queries: int
    max_number_bits: int
    graph: TwoTierGraphPolicy
    material: TwoTierMaterialPolicy
    certified_strip_contact: NativeStripContactPolicy | None=None

    def __post_init__(self):
        if self.certified_strip_contact is not None and type(self.certified_strip_contact) is not NativeStripContactPolicy:
            raise ValueError('explicit native certified-strip contact policy required')
        for name in ('max_events','max_candidates','max_contact_queries','max_number_bits','floor_comparator_divisions'):
            if type(getattr(self,name)) is not int or getattr(self,name)<1:
                raise ValueError('positive exact finite planner budgets required')
        if self.floor_comparator_divisions>10000: raise ValueError('bounded floor comparator lattice required')
        for name in ('widths_mm','physical_heights_mm','centers_relative_mm','child_alignment_insets_mm'):
            sequence=getattr(self,name)
            if (type(sequence) is not tuple or not sequence or len(sequence)>self.max_events
                    or any(type(v) is not F for v in sequence) or tuple(sorted(set(sequence)))!=sequence):
                raise ValueError('explicit increasing exact finite planner family required')
            for number in sequence:
                if max(number.numerator.bit_length(),number.denominator.bit_length())>self.max_number_bits:
                    raise ValueError('bounded planner family numbers required')
        if (min(self.widths_mm)<=0 or min(self.physical_heights_mm)<=0 or min(self.child_alignment_insets_mm)<0
                or type(self.overlap_percent) is not F or not 0<=self.overlap_percent<=30
                or type(self.graph) is not TwoTierGraphPolicy or type(self.material) is not TwoTierMaterialPolicy):
            raise ValueError('ordered physical planner family and explicit overlap0..30 required')
        if max(self.overlap_percent.numerator.bit_length(),self.overlap_percent.denominator.bit_length())>self.max_number_bits:
            raise ValueError('bounded exact configured overlap required')


@dataclass(frozen=True)
class TrialCandidateBlock:
    root_intent: SupportedPathIntent
    upper_intent: SupportedPathIntent | None
    section: TwoTierSectionBlock
    error_area_mm2: F
    parent_contact_queries: int=0


@dataclass(frozen=True)
class NativeTrialPlannerReport:
    step: NativeTrialStep
    state: str
    reason: str
    finite_family_complete: bool
    candidates: int
    contact_queries: int
    events: int
    rejection_counts: tuple[tuple[str,int],...]
    family_error_area_mm2: F | None
    floor_comparator_error_area_mm2: F | None
    selected_blocks: tuple[TrialCandidateBlock,...]
    plan: FrozenTwoTierPlan | None
    physical_authority: bool=field(default=False,init=False)


class _PlannerLimit(ValueError):
    pass


def plan_native_trial_step(step,prior_sources,emission_policy,*,policy,cancelled):
    """Admit actual E-width/contact blocks BEFORE exact interval selection.

    The caller owns authentic chronological source extraction and unsupported
    material accounting. This pure DTO boundary makes no source authenticity claim.
    """
    if type(step) is not NativeTrialStep or type(policy) is not NativeTrialPlannerPolicy or not callable(cancelled):
        raise ValueError('immutable native step and finite planner policy required')
    if type(emission_policy) is not HopPolicy: raise ValueError('immutable numeric emission policy required')
    try: _validate_policy(emission_policy)
    except OverflowError as exc: raise ValueError('nonfinite planner motion policy') from exc
    if (type(step.step_id) is not str or re.fullmatch('[A-Za-z0-9_-]+',step.step_id) is None
            or type(step.source_context_identity) is not str or re.fullmatch('[0-9a-f]{64}',step.source_context_identity) is None
            or type(step.x_span_mm) is not tuple or len(step.x_span_mm)!=2
            or type(step.execution_order) is not int or step.execution_order<0):
        raise ValueError('explicit step identity/Xspan/order required')
    for number in (step.floor_z_mm,step.next_layer_z_mm,step.triangle_left_y_mm,step.triangle_right_y_mm,*step.x_span_mm):
        if type(number) is not F or max(number.numerator.bit_length(),number.denominator.bit_length())>policy.max_number_bits:
            raise ValueError('bounded exact step geometry required')
    if step.floor_z_mm<0 or step.next_layer_z_mm<=step.floor_z_mm or step.x_span_mm[0]>=step.x_span_mm[1]:
        raise ValueError('ordered positive native step interval required')
    if (type(prior_sources) is not tuple or len(prior_sources)>policy.graph.contact.max_input_sources
            or any(type(source) is not ChronologicalSource or source.execution_order>=step.execution_order for source in prior_sources)):
        raise ValueError('complete immutable strictly prior source DTOs required')
    base=step.triangle_right_y_mm-step.triangle_left_y_mm
    rise=step.next_layer_z_mm-step.floor_z_mm
    if base<0: raise ValueError('ordered caller triangle required')
    events=candidates=queries=0; rejected={}; contact_cache={}; blocks=[]
    family_error=baseline_error=None
    minimum_width=F(str(emission_policy.bounds.min_candidate_width_mm))
    maximum_width=F(str(emission_policy.bounds.max_candidate_width_mm))
    minimum_remaining=F(str(emission_policy.bounds.min_candidate_height_mm))
    maximum_height=F(str(emission_policy.bounds.max_candidate_height_mm))
    overlap=policy.overlap_percent/100

    def tick():
        nonlocal events
        events+=1
        answer=cancelled()
        if type(answer) is not bool: raise ValueError('exact planner cancellation bool required')
        if answer or events>policy.max_events: raise _PlannerLimit('cancelled' if answer else 'event-limit')

    def reject(reason): rejected[reason]=rejected.get(reason,0)+1

    def report(state,reason,complete=False,selected=(),plan=None):
        return NativeTrialPlannerReport(step,state,reason,complete,candidates,queries,events,tuple(sorted(rejected.items())),
            family_error,baseline_error,selected,plan)

    def posed(frozen):
        path=frozen.path; width=F(str(frozen.physical_width_mm[0])); center=path.points_mm[0][1]-step.triangle_left_y_mm
        top=path.points_mm[0][2]-step.floor_z_mm
        return PosedSectionRectangle(center-width/2,center+width/2,top-path.height_mm,top)

    def spill_legal(rectangle):
        tick()
        inside=finite_triangle_rectangle_intersection_area(base,rise,rectangle.left_mm,rectangle.right_mm,rectangle.bottom_mm,rectangle.top_mm)
        return 2*inside>=rectangle.area_mm2

    def numeric(name,width,height,center,support):
        remaining=height*(1-overlap)
        if remaining<minimum_remaining or height>maximum_height or not minimum_width<=width<=maximum_width:
            reject('dimensions-outside-family-bounds'); return None
        top=rounded(support+remaining,emission_policy.xyz_places)
        if top>=step.next_layer_z_mm or top<=support:
            reject('strict-original-upper-bound'); return None
        points=tuple((x,center,top) for x in step.x_span_mm)
        path=SupplementalPath(name,support,width,height,points)
        try: frozen=freeze_numeric_emission(path,emission_policy)
        except ValueError:
            reject('numeric-freeze-rejected'); return None
        if frozen.path.points_mm[0][2]-support<minimum_remaining:
            reject('formatted-minimum-remaining'); return None
        if frozen.path.points_mm[0][2]-support!=remaining:
            reject('fixed-overlap-not-exact-on-format-grid'); return None
        return frozen

    def root_contact(frozen):
        nonlocal queries
        path=frozen.path
        bottom=path.points_mm[0][2]-path.height_mm
        key=(path.points_mm,bottom)
        if key not in contact_cache:
            if queries>=policy.max_contact_queries: raise _PlannerLimit('contact-query-limit')
            candidate=ContactPath(path.path_id,step.execution_order,
                tuple(point[:2] for point in path.points_mm),bottom)
            if policy.certified_strip_contact is not None:
                contact=audit_native_constant_z_contact(candidate,prior_sources,
                    policy=replace(policy.certified_strip_contact,max_queries=min(policy.certified_strip_contact.max_queries,
                        policy.max_contact_queries-queries)),cancelled=cancelled)
            else:
                contact=audit_continuous_path_contact(candidate,prior_sources,
                    policy=replace(policy.graph.contact,max_queries=min(policy.graph.contact.max_queries,
                        policy.max_contact_queries-queries)),cancelled=cancelled)
            queries+=contact.query_count
            if queries>policy.max_contact_queries: raise _PlannerLimit('contact-query-limit')
            contact_cache[key]=contact.nominal_centerline_contact_proven
            if not contact.nominal_centerline_contact_proven and contact.state=='incomplete':
                raise _PlannerLimit('contact-proof-incomplete')
        return contact_cache[key]

    def intent(frozen,parent=None):
        path=frozen.path
        return SupportedPathIntent(path.path_id,step.source_context_identity,step.floor_z_mm,step.next_layer_z_mm,
            path.floor_z_mm,path.width_mm,path.height_mm,path.points_mm[0][2]-path.floor_z_mm,path.points_mm,parent)

    try:
        tick()
        if base==0: return report('excluded','flat-source-step',True)
        if base*base<2*minimum_width**2: return report('excluded','strict-short-base',True)
        if minimum_remaining/(1-overlap)>maximum_height:
            return report('no-selection','no-legal-height-after-overlap-compensation',True)
        n=policy.floor_comparator_divisions
        estimate=n*(n+1)
        if estimate>policy.max_events-events: raise _PlannerLimit('floor-comparator-event-limit')
        events+=estimate
        baseline=pack(base,rise,grid_divisions=n,minimum_width_mm=minimum_width,maximum_width_mm=maximum_width,
            minimum_height_mm=minimum_remaining/(1-overlap),maximum_height_mm=maximum_height)
        baseline_blocks=tuple(TwoTierSectionBlock(PosedSectionRectangle(r.left_mm,r.right_mm,-r.height_mm*overlap,
            r.height_mm*(1-overlap)),None) for r in baseline.rectangles)
        if all(b.lower.top_mm<rise and spill_legal(b.lower) for b in baseline_blocks):
            baseline_error=base*rise/2+sum((section_block_error_area(base,rise,b)-base*rise/2 for b in baseline_blocks),F(0))
        for center_relative in policy.centers_relative_mm:
            for width in policy.widths_mm:
                for height in policy.physical_heights_mm:
                    tick(); candidates+=1
                    if candidates>policy.max_candidates: raise _PlannerLimit('candidate-limit')
                    name=f'{step.step_id}_r{candidates:07d}'
                    root=numeric(name,width,height,step.triangle_left_y_mm+center_relative,step.floor_z_mm)
                    if root is None: continue
                    lower=posed(root)
                    if not spill_legal(lower): reject('root-spill-over-half'); continue
                    if not root_contact(root): reject('root-contact-not-proven'); continue
                    root_intent=intent(root)
                    best=TrialCandidateBlock(root_intent,None,TwoTierSectionBlock(lower,None),
                        section_block_error_area(base,rise,TwoTierSectionBlock(lower,None)))
                    for child_width in policy.widths_mm:
                        for child_height in policy.physical_heights_mm:
                            tick()
                            if child_height*(1-overlap)+root.path.points_mm[0][2]>=step.next_layer_z_mm: continue
                            for inset in policy.child_alignment_insets_mm:
                                for alignment in ('center','left','right'):
                                    tick(); candidates+=1
                                    if candidates>policy.max_candidates: raise _PlannerLimit('candidate-limit')
                                    root_center=root.path.points_mm[0][1]
                                    child_center=(root_center if alignment=='center' else root_center+
                                        (-1 if alignment=='left' else 1)*(F(str(root.physical_width_mm[0]))/2-child_width/2-inset))
                                    child=numeric(f'{name}_u{candidates:07d}',child_width,child_height,child_center,root.path.points_mm[0][2])
                                    if child is None: continue
                                    upper=posed(child)
                                    if not spill_legal(upper): reject('upper-spill-over-half'); continue
                                    if (upper.left_mm<lower.left_mm or upper.right_mm>lower.right_mm):
                                        reject('actual-child-width-containment'); continue
                                    child_intent=intent(child,name)
                                    section=TwoTierSectionBlock(lower,upper)
                                    error=section_block_error_area(base,rise,section)
                                    if error>=best.error_area_mm2:
                                        reject('child-objective-dominated-for-same-root-interval'); continue
                                    if queries>=policy.max_contact_queries: raise _PlannerLimit('contact-query-limit')
                                    parent_bead=ExactNominalTopSegment(name,*root.path.points_mm,
                                        F(str(root.physical_width_mm[0])),root.path.height_mm,'candidate')
                                    contact=audit_continuous_path_contact(ContactPath(child.path.path_id,1,
                                        tuple(point[:2] for point in child.path.points_mm),
                                        child.path.points_mm[0][2]-child.path.height_mm),
                                        (ChronologicalSource(parent_bead,0),),policy=replace(policy.graph.contact,
                                            max_queries=min(policy.graph.contact.max_queries,policy.max_contact_queries-queries)),cancelled=cancelled)
                                    queries+=contact.query_count
                                    if contact.state=='incomplete': raise _PlannerLimit('parent-contact-proof-incomplete')
                                    if not contact.nominal_centerline_contact_proven:
                                        reject('parent-contact-not-proven'); continue
                                    best=TrialCandidateBlock(root_intent,child_intent,section,error,contact.query_count)
                    blocks.append(best)
        sorting_work=len(blocks)*max(1,len(blocks).bit_length())
        tick()
        if sorting_work>policy.max_events-events: raise _PlannerLimit('interval-sort-event-limit')
        events+=sorting_work
        blocks.sort(key=lambda b:(b.section.lower.right_mm,b.section.lower.left_mm,b.root_intent.path_id))
        ends=[b.section.lower.right_mm for b in blocks]
        scores=[F(0)]; counts=[0]; links=[None]
        for index,block in enumerate(blocks):
            tick()
            previous=bisect_right(ends,block.section.lower.left_mm,0,index)
            gain=base*rise/2-block.error_area_mm2
            score=scores[previous]+gain
            count=counts[previous]+1+(block.upper_intent is not None)
            if score>scores[-1] or score==scores[-1] and count<counts[-1]:
                scores.append(score);counts.append(count);links.append((previous,block))
            else:
                scores.append(scores[-1]);counts.append(counts[-1]);links.append((index,None))
        selected=[]; cursor=len(blocks)
        while cursor:
            cursor,block=links[cursor]
            if block is not None: selected.append(block)
        selected=tuple(reversed(selected)); family_error=base*rise/2-scores[-1]
        if baseline_error is not None and family_error>baseline_error:
            return report('no-selection','finite-family-worse-than-posed-floor-comparator',True)
        if not selected: return report('no-selection','no-beneficial-member-of-declared-family',True)
        intents=tuple(p for block in selected for p in (block.root_intent,block.upper_intent) if p is not None)
        if len(intents)>policy.graph.max_paths: raise _PlannerLimit('selected-path-limit')
        remaining=(policy.max_contact_queries-queries)//2
        needed=sum(block.parent_contact_queries for block in selected)
        if needed>min(remaining,policy.graph.max_contact_queries):
            raise _PlannerLimit('selected-parent-reproof-query-limit')
        final_graph=replace(policy.graph,max_contact_queries=max(1,needed))
        plan=freeze_supported_graph(intents,source_context_identity=step.source_context_identity,policy=emission_policy,
            graph_policy=final_graph,cancelled=cancelled)
        parent_queries=sum(s.centerline_contact.query_count for s in plan.immediate_support_slabs)
        queries+=2*parent_queries
        material=audit_two_tier_material(plan,emission_policy,policy=policy.material,cancelled=cancelled)
        if not material.all_candidate_pairs_accounted:
            return report('incomplete' if material.state=='incomplete' else 'failed','selected-material-pair-'+material.reason)
        return report('complete','finite-contact-admitted-family-selected',True,selected,plan)
    except _PlannerLimit as failure:
        return report('incomplete',str(failure))
