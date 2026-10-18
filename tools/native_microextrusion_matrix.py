"""Closed independent-clearance/volume offline matrix adapter; no stadium coercion."""
from dataclasses import dataclass,replace,asdict,is_dataclass
from fractions import Fraction as F
from hashlib import sha256
import math,re,json
from adaptive_subedge.domain.settings import CandidateBeadBounds
from tools.flat_matrix_fixture import FlatMatrixFixture,matrix_cells,verify_flat_matrix
from tools.gui_native_trial_trace import NativeTrialContext,NativeTrialLimits,interpret_native_trial,native_profile_caps,_anchor_from_native_trace,checkpoint
from tools.supplemental_z_hop import policy_from_slice,_text,rounded
from tools.conditional_nominal_copy import validate_profile_bound_policy
from tools.native_supplement_end import NativeSupplementEndPolicy,apply_native_end_policy
from orca_plugin.gcode.linear_trace import _advance,_words

PI=F(str(math.pi))

def matrix_identity(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':'),default=lambda v:asdict(v) if is_dataclass(v) else str(v)).encode('ascii')).hexdigest()

@dataclass(frozen=True)
class MatrixExperimentPolicy:
    speed_mm_s:F=F(20)
    maximum_volume_error_fraction:F=F('.02')
    visualization_width_mm:F=F('.45')
    envelope_width_mm:F=F('.45')
    envelope_height_mm:F=F('.2')
    xyz_places:int=3
    e_places:int=5
    schema_version:int=1
    def __post_init__(self):
        if type(self.schema_version) is not int or self.schema_version!=1 or type(self.xyz_places) is not int or self.xyz_places!=3 or type(self.e_places) is not int or self.e_places!=5:
            raise ValueError('closed matrix command precision and version required')
        if any(type(v) is not F or v<=0 or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>128 for v in (self.speed_mm_s,self.maximum_volume_error_fraction,self.visualization_width_mm,self.envelope_width_mm,self.envelope_height_mm)):
            raise ValueError('bounded positive exact matrix policy required')
        if self.speed_mm_s>20 or self.maximum_volume_error_fraction>F('.02') or (self.visualization_width_mm,self.envelope_width_mm,self.envelope_height_mm)!=(F('.45'),F('.45'),F('.2')):
            raise ValueError('matrix policy outside accepted fixed experiment envelope')

@dataclass(frozen=True)
class MatrixCommandPath:
    path_id:str
    points_mm:tuple

@dataclass(frozen=True)
class FrozenMatrixLine:
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

@dataclass(frozen=True)
class NativeMicroextrusionMatrixRecipe:
    source_bytes:bytes
    project_bytes:bytes
    producer_bytes:bytes
    context:NativeTrialContext
    geometry_project_bytes:bytes
    limits:NativeTrialLimits
    fixture:FlatMatrixFixture
    anchor_offset:int
    policy:MatrixExperimentPolicy=MatrixExperimentPolicy()
    end_policy:NativeSupplementEndPolicy=NativeSupplementEndPolicy(retract_mm=F('1.6'),wipe_mm=F(1))
    def __post_init__(self):
        if any(type(v) is not bytes for v in (self.source_bytes,self.project_bytes,self.producer_bytes,self.geometry_project_bytes)) or type(self.context) is not NativeTrialContext or type(self.limits) is not NativeTrialLimits or type(self.fixture) is not FlatMatrixFixture or type(self.policy) is not MatrixExperimentPolicy or type(self.end_policy) is not NativeSupplementEndPolicy or type(self.anchor_offset) is not int:
            raise ValueError('closed immutable matrix recipe required')
        if self.end_policy.retract_mm!=F('1.6') or self.end_policy.wipe_mm!=F(1):raise ValueError('matrix fixed end treatment differs')


def _canonical_cell(cell):
    keys={'id','row','column','h_cmd_mm','final_volume_mm3_per_mm','start_xy_mm','end_xy_mm','label_origin_xy_mm'}
    if type(cell) is not dict or set(cell)!=keys or type(cell['id']) is not str or not re.fullmatch(r'[0-9]{2}',cell['id']) or any(type(cell[k]) is not int for k in ('row','column')) or any(type(cell[k]) is not F for k in ('h_cmd_mm','final_volume_mm3_per_mm')):
        return False
    if any(type(cell[k]) is not tuple or len(cell[k])!=2 or any(type(v) is not F for v in cell[k]) for k in ('start_xy_mm','end_xy_mm','label_origin_xy_mm')):return False
    return cell in matrix_cells()


def freeze_matrix_line(cell,*,diameter_mm,speed_mm_s,maximum_volume_mm3_s,policy):
    if type(policy) is not MatrixExperimentPolicy or not _canonical_cell(cell) or any(type(v) is not F or v<=0 or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>128 for v in (diameter_mm,speed_mm_s,maximum_volume_mm3_s)):
        raise ValueError('source-bound exact matrix cell and rates required')
    length=cell['end_xy_mm'][0]-cell['start_xy_mm'][0];area=PI*diameter_mm**2/4;amount=rounded(length*cell['final_volume_mm3_per_mm']/area,policy.e_places)
    if amount<=0:raise ValueError('matrix positive E collapsed at precision')
    achieved=amount*area/length;error=(achieved-cell['final_volume_mm3_per_mm'])/cell['final_volume_mm3_per_mm']
    if abs(error)>policy.maximum_volume_error_fraction:raise ValueError('matrix rounded final-volume error exceeds policy')
    speed=min(policy.speed_mm_s,speed_mm_s,maximum_volume_mm3_s/achieved);feed=F((speed*60000).numerator//(speed*60000).denominator,1000)
    if feed<=0:raise ValueError('matrix feed collapsed at precision')
    z=F('.8')+cell['h_cmd_mm'];points=tuple((*p,z) for p in (cell['start_xy_mm'],cell['end_xy_mm']));radius=policy.envelope_width_mm/2
    return FrozenMatrixLine(MatrixCommandPath('matrix_'+cell['id'],points),cell['row'],cell['column'],cell['h_cmd_mm'],cell['final_volume_mm3_per_mm'],amount,achieved,error,feed,
        (points[0][0]-radius,points[0][1]-radius,F('.8')),(points[1][0]+radius,points[1][1]+radius,F('.8')+policy.envelope_height_mm))


def matrix_source_evidence(recipe,trace):
    """Check actual source layer and cell regions, not an inferred physical top."""
    if b'MATRIX_EXPERIMENT_' in recipe.source_bytes:raise ValueError('already supplemented matrix source')
    positive=tuple(e for e in trace.events if e.deposited_filament_mm is not None and e.deposited_filament_mm>0)
    if not positive or any(e.byte_offset>=recipe.anchor_offset for e in positive):raise ValueError('matrix anchor must follow ALL original model and label deposition')
    if any(e.relative_e_mm>0 and e.deposited_filament_mm is None for e in trace.events):raise ValueError('matrix unknown original positive material')
    if {e.after.machine.xyz_mm[2] for e in positive}!={F('.2'),F('.4'),F('.6'),F('.8'),F(1)}:raise ValueError('matrix actual five source layers differ')
    cells=matrix_cells();records=[]
    for cell in cells:
        ox,oy=cell['label_origin_xy_mm'];label=[];base=[]
        for e in positive:
            a,b=e.before.machine.xyz_mm,e.after.machine.xyz_mm
            if any(type(v) is not F for v in (*a,*b)):raise ValueError('matrix original source coordinates unknown')
            if a[2]==b[2]==F(1) and ox-F('.3')<=b[0]<=ox+F('4.7') and oy-F('.3')<=b[1]<=oy+F('3.8'):label.append(e.line_number)
            if a[2]==b[2]==F('.8') and min(a[0],b[0])<=cell['end_xy_mm'][0] and max(a[0],b[0])>=cell['start_xy_mm'][0] and min(a[1],b[1])-F('.5')<=cell['start_xy_mm'][1]<=max(a[1],b[1])+F('.5'):base.append(e.line_number)
        if not label or not base:raise ValueError('matrix original base or numbered label region absent:'+cell['id'])
        records.append((cell['id'],tuple(base),tuple(label)))
    for e in positive:
        if e.after.machine.xyz_mm[2]==F(1) and not any(ox-F('.4')<=e.after.machine.xyz_mm[0]<=ox+F('4.8') and oy-F('.4')<=e.after.machine.xyz_mm[1]<=oy+F('3.9') for ox,oy in (c['label_origin_xy_mm'] for c in cells)):
            raise ValueError('original final layer contains deposition outside label regions')
    return tuple(records)


def _prior_comments(trace,offset):
    prior={}
    for event in trace.events:
        if event.byte_offset>=offset:break
        for key in ('FEATURE','LAYER_HEIGHT','LINE_WIDTH','Z_HEIGHT'):
            if event.raw.startswith(('; '+key+':').encode()):prior[key]=event.raw.rstrip(b'\r\n')
    if set(prior)!={'FEATURE','LAYER_HEIGHT','LINE_WIDTH','Z_HEIGHT'} or any(len(v)>256 for v in prior.values()):raise ValueError('matrix prior preview state unavailable')
    return b'\n'.join(prior[k] for k in ('FEATURE','LAYER_HEIGHT','LINE_WIDTH','Z_HEIGHT'))+b'\n'


def _line_cycle(line,anchor,hop,ceiling,end):
    a,b=line.path.points_mm;xyz=lambda v:_text(v,hop.xyz_places);ew=lambda v:_text(v,hop.e_places);feed=lambda v:_text(v*60,3);debt=anchor.retraction_debt_mm
    lines=[f'; PATH {line.path.path_id} HEIGHT {line.clearance_mm}',f'; MATRIX_VISUALIZATION width .45 height clearance; actual physical shape unknown',
      '; FEATURE: Custom',f'; LAYER_HEIGHT: {xyz(line.clearance_mm)}',f'; Z_HEIGHT: {xyz(a[2])}','; LINE_WIDTH: 0.45',
      f'G1 Z{xyz(ceiling)} F{feed(hop.z_speed_mm_s)}',f'G1 X{xyz(a[0])} Y{xyz(a[1])} F{feed(hop.xy_speed_mm_s)}',f'G1 Z{xyz(a[2])} F{feed(hop.z_speed_mm_s)}',f'G1 E{ew(debt)} F{feed(hop.deretract_speed_mm_s)}',
      f'G1 X{xyz(b[0])} Y{xyz(b[1])} E{ew(line.commanded_e_mm)} F{_text(line.feed_mm_min,3)}',f'G1 E-{ew(debt)} F{feed(hop.retract_speed_mm_s)}',f'G1 Z{xyz(ceiling)} F{feed(hop.z_speed_mm_s)}',
      f'G1 X{xyz(anchor.xyz_mm[0])} Y{xyz(anchor.xyz_mm[1])} F{feed(hop.xy_speed_mm_s)}',f'G1 Z{xyz(anchor.xyz_mm[2])} F{feed(hop.z_speed_mm_s)}',f'G1 F{_text(anchor.feed_mm_min,3)}']
    block=('\n'.join(lines)+'\n').encode();return apply_native_end_policy(block,line,anchor,hop,end)


def rebuild_microextrusion_matrix(recipe,*,cancelled):
    from tools.gui_native_trial_copy import NativeTrialCopy,NativeTrialInsertionSpan,STUDIO_NATIVE_METADATA_MARKER,_counter_translations
    if type(recipe) is not NativeMicroextrusionMatrixRecipe:raise ValueError('exact matrix recipe required')
    checkpoint(cancelled);verify_flat_matrix(recipe.geometry_project_bytes,recipe.fixture)
    trace=interpret_native_trial(recipe.source_bytes,recipe.project_bytes,recipe.producer_bytes,recipe.context,geometry_project=recipe.geometry_project_bytes,limits=recipe.limits,cancelled=cancelled)
    profile,acceleration_cap,jerk_cap=native_profile_caps(recipe.source_bytes,recipe.project_bytes,recipe.geometry_project_bytes,recipe.limits,cancelled=cancelled)
    if profile.setting('layer_height').number()!=F('.2'):raise ValueError('matrix source layer height differs')
    anchor=_anchor_from_native_trace(trace,recipe.context,recipe.anchor_offset,acceleration_cap_mm_s2=acceleration_cap,jerk_cap_mm_s=jerk_cap);issues=set(anchor.eligibility_issues)
    if type(anchor.saved_state.acceleration_mm_s2) is F and anchor.saved_state.acceleration_mm_s2>0:issues.discard('native-acceleration-cap-exceeded-or-unknown')
    if issues or anchor.saved_state.xy_plane is not True:raise ValueError('ineligible matrix anchor:'+','.join(sorted(issues)))
    matrix_source_evidence(recipe,trace)
    hop=policy_from_slice(profile,CandidateBeadBounds(.08,.18,.25,.45),xyz_places=3,e_places=5);hop=replace(hop,candidate_speed_mm_s=min(F(20),hop.candidate_speed_mm_s));validate_profile_bound_policy(profile,hop)
    wall=[e.after.machine.feed_mm_min/60 for e in trace.events if e.feature=='Outer wall' and e.after.machine.xyz_mm[2]==F('.8') and e.deposited_filament_mm is not None and e.deposited_filament_mm>0]
    if not wall:raise ValueError('actual source base wall feed absent')
    speed=min(hop.candidate_speed_mm_s,min(wall));ceiling=max(anchor.saved_state.machine.xyz_mm[2],F(1))+hop.z_hop_mm
    if ceiling>hop.printable_height_mm or hop.z_hop_mm<=0:raise ValueError('matrix ceiling outside saved profile')
    frozen=tuple(freeze_matrix_line(c,diameter_mm=hop.filament_diameter_mm,speed_mm_s=speed,maximum_volume_mm3_s=hop.max_volume_mm3_s,policy=recipe.policy) for c in matrix_cells())
    zero=replace(anchor.saved_state.machine,logical_e_mm=F(0));blocks=[];motion=[];total=F(0)
    for line in frozen:
        checkpoint(cancelled);block=_line_cycle(line,zero,hop,ceiling,recipe.end_policy);machine=zero
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
    return NativeTrialCopy(output,sha256(output).hexdigest(),recipe.context.source_sha256,recipe.context.project_sha256,recipe.context.producer_sha256,trace.context_identity,(span,),path_bounds,bounds,total,_counter_translations(trace,(span,)),recipe.context.unresolved_premises+('experimental-independent-clearance-volume-no-physical-bead-shape-proof','unknown-sample-envelope-.45-wide-.2-high-assumption','own-forming-reversewipe-centerline-vertical-retreat-physical-obligation','original-OEM-suffix-execution-remains-unverified'),matrix_identity({'schema':'microextrusion-matrix-emission-v1','context':recipe.context,'fixture':recipe.fixture,'anchor_offset':recipe.anchor_offset,'policy':recipe.policy,'end_policy':recipe.end_policy,'transport_caps':hop,'frozen_lines':frozen,'pi_rational':PI}),prefix)
