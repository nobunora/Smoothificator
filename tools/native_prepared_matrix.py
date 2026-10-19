"""Execute finite prepared matrix V2; ordinary and historical V1 paths stay intact."""
from dataclasses import dataclass,replace
from fractions import Fraction as F
from hashlib import sha256
import re
from adaptive_subedge.domain.prepared_matrix import PreparedMatrixPolicy,PreparedMatrixCondition,prepared_conditions,SourceRatioMatrixPolicy,source_relative_conditions,SPEED_RATIOS
from tools.native_microextrusion_matrix import (PI,MatrixCommandPath,FrozenMatrixLine,matrix_identity,matrix_source_evidence,_prior_comments)
from tools.flat_matrix_fixture import FlatMatrixFixture,matrix_cells,verify_flat_matrix
from tools.gui_native_trial_trace import NativeTrialContext,NativeTrialLimits,interpret_native_trial,native_profile_caps,_anchor_from_native_trace,checkpoint
from tools.supplemental_z_hop import policy_from_slice,_text,rounded
from tools.conditional_nominal_copy import validate_profile_bound_policy
from tools.native_supplement_end import NativeSupplementEndPolicy,apply_native_end_policy
from adaptive_subedge.domain.settings import CandidateBeadBounds
from orca_plugin.gcode.linear_trace import _advance,_words

@dataclass(frozen=True)
class FrozenPreparedMatrixLine:
    path:MatrixCommandPath
    row:int
    column:int
    clearance_mm:F
    requested_volume_mm3_per_mm:F
    commanded_e_mm:F
    achieved_volume_mm3_per_mm:F
    relative_volume_error:F
    feed_mm_min:F
    envelope_lower_xyz_mm:tuple
    envelope_upper_xyz_mm:tuple
    condition:PreparedMatrixCondition
    baseline_total_e_mm:F
    segments:tuple

@dataclass(frozen=True)
class MatrixSourceSpeedReference:
    schema:str
    source_sha256:str
    profile_identity:str
    source_z_mm:F
    source_feature:str
    source_line_numbers:tuple
    saved_outer_wall_speed_mm_s:F
    actual_wall_minimum_feed_mm_min:F
    machine_x_cap_mm_s:F
    machine_y_cap_mm_s:F
    resolved_reference_speed_mm_s:F
    def __post_init__(self):
        if self.schema!='matrix-source-speed-reference-v1' or self.source_z_mm!=F('.8') or type(self.source_z_mm) is not F or self.source_feature!='Outer wall' or any(type(v) is not str or re.fullmatch('[0-9a-f]{64}',v) is None for v in (self.source_sha256,self.profile_identity)):
            raise ValueError('closed source speed reference identity required')
        if type(self.source_line_numbers) is not tuple or not 0<len(self.source_line_numbers)<=20000 or any(type(v) is not int or v<=0 for v in self.source_line_numbers) or tuple(sorted(set(self.source_line_numbers)))!=self.source_line_numbers:
            raise ValueError('bounded source speed reference lines required')
        values=(self.saved_outer_wall_speed_mm_s,self.actual_wall_minimum_feed_mm_min,self.machine_x_cap_mm_s,self.machine_y_cap_mm_s,self.resolved_reference_speed_mm_s)
        if any(type(v) is not F or v<=0 or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>128 for v in values) or self.resolved_reference_speed_mm_s!=min(values[0],values[1]/60,values[2],values[3]):
            raise ValueError('source speed reference cap arithmetic differs')


def resolve_source_speed_reference(trace,profile,source_sha256):
    evidence=tuple(e for e in trace.events if e.feature=='Outer wall' and e.deposited_filament_mm is not None and e.deposited_filament_mm>0 and e.before.machine.xyz_mm[2]==e.after.machine.xyz_mm[2]==F('.8') and e.before.machine.xyz_mm[:2]!=e.after.machine.xyz_mm[:2])
    if not evidence or any(type(e.after.machine.feed_mm_min) is not F or e.after.machine.feed_mm_min<=0 or e.branch_depth!=0 for e in evidence):raise ValueError('source base-top outer-wall speed evidence unavailable')
    outer=profile.setting('outer_wall_speed').number();x=profile.setting('conservative_machine_max_speed_x').number();y=profile.setting('conservative_machine_max_speed_y').number();minimum=min(e.after.machine.feed_mm_min for e in evidence)
    if any(type(v) is not F or v<=0 for v in (outer,x,y,minimum)):raise ValueError('source relative speed cap unavailable')
    return MatrixSourceSpeedReference('matrix-source-speed-reference-v1',source_sha256,profile.projection_identity,F('.8'),'Outer wall',tuple(e.line_number for e in evidence),outer,minimum,x,y,min(outer,minimum/60,x,y))


@dataclass(frozen=True)
class NativePreparedMatrixRecipe:
    source_bytes:bytes
    project_bytes:bytes
    producer_bytes:bytes
    context:NativeTrialContext
    geometry_project_bytes:bytes
    limits:NativeTrialLimits
    fixture:FlatMatrixFixture
    anchor_offset:int
    policy:PreparedMatrixPolicy
    def __post_init__(self):
        if any(type(v) is not bytes for v in (self.source_bytes,self.project_bytes,self.producer_bytes,self.geometry_project_bytes)) or type(self.context) is not NativeTrialContext or type(self.limits) is not NativeTrialLimits or type(self.fixture) is not FlatMatrixFixture or type(self.policy) not in (PreparedMatrixPolicy,SourceRatioMatrixPolicy) or type(self.anchor_offset) is not int:
            raise ValueError('closed immutable prepared matrix recipe required')


def freeze_prepared_line(condition,*,diameter_mm,speed_mm_s,maximum_volume_mm3_s,policy,source_reference=None):
    if type(policy) is SourceRatioMatrixPolicy:
        if type(source_reference) is not MatrixSourceSpeedReference:raise ValueError('source speed reference required')
        family=source_relative_conditions(policy,source_reference.resolved_reference_speed_mm_s)
    elif type(policy) is PreparedMatrixPolicy and source_reference is None:family=prepared_conditions(policy)
    else:raise ValueError('closed prepared policy and reference required')
    if type(condition) is not PreparedMatrixCondition or condition not in family or any(type(v) is not F or v<=0 or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>128 for v in (diameter_mm,speed_mm_s,maximum_volume_mm3_s)):
        raise ValueError('source-bound exact prepared condition and caps required')
    if condition.print_speed_mm_s>speed_mm_s:raise ValueError('prepared drawing speed exceeds saved source cap')
    cell=matrix_cells()[condition.row*5+condition.column];area=PI*diameter_mm**2/4
    baseline=rounded(10*condition.final_volume_mm3_per_mm/area,5)
    error=(baseline*area/10-condition.final_volume_mm3_per_mm)/condition.final_volume_mm3_per_mm
    if baseline<=0 or abs(error)>F('.02'):raise ValueError('prepared baseline E collapsed or volume error exceeds policy')
    z=F('.8')+condition.h_cmd_mm;a=(*cell['start_xy_mm'],z);b=(*cell['end_xy_mm'],z)
    if policy.trial_id=='startup_extra_speed':
        first=rounded(2*condition.final_volume_mm3_per_mm/area,5)
        segments=(((*a[:1],a[1],z), (a[0]+2,a[1],z),first+condition.startup_extra_e_mm),( (a[0]+2,a[1],z),b,baseline-first))
        points=(a,segments[0][1],b)
    else:segments=((a,b,baseline),);points=(a,b)
    total=sum(segment[2] for segment in segments);feed=condition.print_speed_mm_s*60
    if source_reference is not None:
        feed=F((feed*1000).numerator//(feed*1000).denominator,1000)
        if feed<=0:raise ValueError('source relative feed collapsed at command precision')
    for start,end,amount in segments:
        length=end[0]-start[0]
        if amount<=0 or length<=0 or amount*area/length*(feed/60)>maximum_volume_mm3_s:raise ValueError('prepared emitted segment violates positive E or saved volume cap')
    radius=F('.225');achieved=total*area/10
    return FrozenPreparedMatrixLine(MatrixCommandPath('matrix_'+condition.cell_id,points),condition.row,condition.column,condition.h_cmd_mm,condition.final_volume_mm3_per_mm,total,achieved,error,feed,(a[0]-radius,a[1]-radius,F('.8')),(b[0]+radius,b[1]+radius,F(1)),condition,baseline,segments)


def _line_cycle(line,anchor,hop,ceiling):
    c=line.condition;end=NativeSupplementEndPolicy(retract_mm=c.retract_mm,wipe_mm=c.wipe_mm)
    a=line.path.points_mm[0];xyz=lambda v:_text(v,hop.xyz_places);ew=lambda v:_text(v,hop.e_places);feed=lambda v:_text(v*60,3);debt=anchor.retraction_debt_mm
    lines=[f'; PATH {line.path.path_id} HEIGHT {line.clearance_mm}', '; MATRIX_VISUALIZATION width .45 height clearance; actual physical shape unknown','; FEATURE: Custom',f'; LAYER_HEIGHT: {xyz(line.clearance_mm)}',f'; Z_HEIGHT: {xyz(a[2])}','; LINE_WIDTH: 0.45',f'G1 Z{xyz(ceiling)} F{feed(hop.z_speed_mm_s)}',f'G1 X{xyz(a[0])} Y{xyz(a[1])} F{feed(hop.xy_speed_mm_s)}',f'G1 Z{xyz(a[2])} F{feed(hop.z_speed_mm_s)}',f'G1 E{ew(debt)} F{feed(hop.deretract_speed_mm_s)}']
    for start,b,amount in line.segments:lines.append(f'G1 X{xyz(b[0])} Y{xyz(b[1])} E{ew(amount)} F{_text(line.feed_mm_min,3)}')
    lines.extend((f'G1 E-{ew(debt)} F{feed(hop.retract_speed_mm_s)}',f'G1 Z{xyz(ceiling)} F{feed(hop.z_speed_mm_s)}',f'G1 X{xyz(anchor.xyz_mm[0])} Y{xyz(anchor.xyz_mm[1])} F{feed(hop.xy_speed_mm_s)}',f'G1 Z{xyz(anchor.xyz_mm[2])} F{feed(hop.z_speed_mm_s)}',f'G1 F{_text(anchor.feed_mm_min,3)}'))
    return apply_native_end_policy(('\n'.join(lines)+'\n').encode(),line,anchor,hop,end,start_deretract_speed_mm_s=c.start_debt_unretract_speed_mm_s)


def rebuild_prepared_matrix(recipe,*,cancelled):
    from tools.gui_native_trial_copy import NativeTrialCopy,NativeTrialInsertionSpan,STUDIO_NATIVE_METADATA_MARKER,_counter_translations
    if type(recipe) is not NativePreparedMatrixRecipe:raise ValueError('exact matrix recipe required')
    checkpoint(cancelled);verify_flat_matrix(recipe.geometry_project_bytes,recipe.fixture)
    trace=interpret_native_trial(recipe.source_bytes,recipe.project_bytes,recipe.producer_bytes,recipe.context,geometry_project=recipe.geometry_project_bytes,limits=recipe.limits,cancelled=cancelled)
    profile,acceleration_cap,jerk_cap=native_profile_caps(recipe.source_bytes,recipe.project_bytes,recipe.geometry_project_bytes,recipe.limits,cancelled=cancelled)
    if profile.setting('layer_height').number()!=F('.2'):raise ValueError('matrix source layer height differs')
    anchor=_anchor_from_native_trace(trace,recipe.context,recipe.anchor_offset,acceleration_cap_mm_s2=acceleration_cap,jerk_cap_mm_s=jerk_cap);issues=set(anchor.eligibility_issues)
    if type(anchor.saved_state.acceleration_mm_s2) is F and anchor.saved_state.acceleration_mm_s2>0:issues.discard('native-acceleration-cap-exceeded-or-unknown')
    if issues or anchor.saved_state.xy_plane is not True:raise ValueError('ineligible matrix anchor:'+','.join(sorted(issues)))
    matrix_source_evidence(recipe,trace)
    hop=policy_from_slice(profile,CandidateBeadBounds(.08,.18,.25,.45),xyz_places=3,e_places=5);validate_profile_bound_policy(profile,hop)
    wall=[e.after.machine.feed_mm_min/60 for e in trace.events if e.feature=='Outer wall' and e.after.machine.xyz_mm[2]==F('.8') and e.deposited_filament_mm is not None and e.deposited_filament_mm>0]
    if not wall:raise ValueError('actual source base wall feed absent')
    speed=min(hop.candidate_speed_mm_s,min(wall));ceiling=max(anchor.saved_state.machine.xyz_mm[2],F(1))+hop.z_hop_mm
    if ceiling>hop.printable_height_mm or hop.z_hop_mm<=0:raise ValueError('matrix ceiling outside saved profile')
    reference=resolve_source_speed_reference(trace,profile,recipe.context.source_sha256) if type(recipe.policy) is SourceRatioMatrixPolicy else None
    conditions=source_relative_conditions(recipe.policy,reference.resolved_reference_speed_mm_s) if reference is not None else prepared_conditions(recipe.policy)
    frozen=tuple(freeze_prepared_line(c,diameter_mm=hop.filament_diameter_mm,speed_mm_s=speed,maximum_volume_mm3_s=hop.max_volume_mm3_s,policy=recipe.policy,source_reference=reference) for c in conditions)
    zero=replace(anchor.saved_state.machine,logical_e_mm=F(0));blocks=[];motion=[];total=F(0)
    for line in frozen:
        checkpoint(cancelled);block=_line_cycle(line,zero,hop,ceiling);machine=zero
        for raw in block.splitlines():
            text=raw.split(b';',1)[0].strip().decode('ascii')
            if not text:continue
            command,words=_words(text)
            if command!='G1':raise ValueError('matrix formatter command drift')
            before=machine;machine,deposited=_advance(machine,command,words);motion.append(machine.xyz_mm)
            if deposited and before.xyz_mm[:2]==machine.xyz_mm[:2]:raise ValueError('matrix unintended stationary positive deposition')
        if replace(machine,logical_e_mm=F(0))!=zero or machine.logical_e_mm!=line.commanded_e_mm:raise ValueError('matrix physical state or symbolic E restoration failed')
        blocks.append(block);total+=line.commanded_e_mm
    inherited=anchor.saved_state.acceleration_mm_s2;executed=min(inherited,acceleration_cap);body=b'; MATRIX_EXPERIMENT_BEGIN independent commanded clearance/final volume; not a physical bead model\n'+b''.join(blocks)+_prior_comments(trace,recipe.anchor_offset)+b'; MATRIX_EXPERIMENT_END\n'
    if executed!=inherited:body=f'M204 S{_text(executed,3)}\n'.encode()+body+f'M204 S{_text(inherited,3)}\n'.encode()
    prefix=STUDIO_NATIVE_METADATA_MARKER+b'\n';start=len(prefix)+recipe.anchor_offset;span=NativeTrialInsertionSpan(recipe.anchor_offset,start,start+len(body),tuple(line.path.path_id for line in frozen),total,inherited,executed)
    replay=zero;acceleration=inherited
    for raw in body.splitlines():
        text=raw.split(b';',1)[0].strip().decode('ascii')
        if not text:continue
        command,words=_words(text)
        if command=='M204':
            if set(words)!={'S'}:raise ValueError('matrix acceleration wrapper drift')
            acceleration=words['S']
        elif command=='G1':replay,_=_advance(replay,command,words)
        else:raise ValueError('matrix wrapper command drift')
    if acceleration!=inherited or replace(replay,logical_e_mm=F(0))!=zero or replay.logical_e_mm!=total:raise ValueError('matrix complete wrapper state restoration failed')
    output=prefix+recipe.source_bytes[:recipe.anchor_offset]+body+recipe.source_bytes[recipe.anchor_offset:]
    bounds=tuple(tuple(op(p[k] for p in motion) for k in range(3)) for op in (min,max));path_bounds=tuple((f.path.path_id,f.envelope_lower_xyz_mm,f.envelope_upper_xyz_mm) for f in frozen)
    checkpoint(cancelled)
    return NativeTrialCopy(output,sha256(output).hexdigest(),recipe.context.source_sha256,recipe.context.project_sha256,recipe.context.producer_sha256,trace.context_identity,(span,),path_bounds,bounds,total,_counter_translations(trace,(span,)),recipe.context.unresolved_premises+('experimental-independent-clearance-volume-no-physical-bead-shape-proof','unknown-sample-envelope-.45-wide-.2-high-assumption','own-forming-reversewipe-centerline-vertical-retreat-physical-obligation','original-OEM-suffix-execution-remains-unverified'),matrix_identity({'schema':'prepared-matrix-emission-v2','context':recipe.context,'fixture':recipe.fixture,'anchor_offset':recipe.anchor_offset,'policy':recipe.policy,'transport_caps':hop,'frozen_lines':frozen,'pi_rational':PI,**({'source_speed_reference':reference} if reference is not None else {})}),prefix)
