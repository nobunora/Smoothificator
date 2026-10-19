"""Reproducible offline preparation of four closed source-bound matrix trials."""
from pathlib import Path
from dataclasses import asdict,replace
from fractions import Fraction as F
from hashlib import sha256
from io import BytesIO,StringIO
from zipfile import ZipFile,ZIP_DEFLATED,ZipInfo
import json,csv,sys,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.prepared_matrix_inputs import load_recipe
from tools.gui_native_trial_trace import interpret_native_trial
from tools.native_microextrusion_matrix import freeze_matrix_line,MatrixExperimentPolicy,matrix_identity,matrix_source_evidence,PI
from tools.native_prepared_matrix import NativePreparedMatrixRecipe,freeze_prepared_line,resolve_source_speed_reference
from adaptive_subedge.domain.prepared_matrix import PreparedMatrixPolicy,prepared_conditions,STAGES,AXES,SourceRatioMatrixPolicy,source_relative_conditions,SPEED_RATIOS
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.gui_native_trial_trace import native_profile_caps,_anchor_from_native_trace
from tools.supplemental_z_hop import policy_from_slice
from tools.package_gui_native_trial import NativePackagePolicy,build_native_trial_package
from adaptive_subedge.domain.settings import CandidateBeadBounds
from tools.flat_matrix_fixture import matrix_cells,verify_flat_matrix,FlatMatrixFixture
from smoothificator_preview.calibration_profile import REQUIRED_PROFILE_KEYS,OPTIONAL_ABSENT_KEYS

BASELINE=dict(h_cmd_mm='0.02',final_volume_mm3_per_mm='0.0003',print_speed_mm_s='20',retract_mm='1.6',wipe_mm='1',start_debt_unretract_speed_mm_s='30',ceiling_reconcile_speed_mm_s='30')
TITLES={'h_volume':'Commanded clearance / final volume','retract_wipe':'End retraction / reverse wipe','startup_extra_speed':'First 2mm extra filament E / start debt recovery speed','volume_speed':'Final volume / drawing speed'}

def decimal(v):
 if isinstance(v,F):
  from decimal import Decimal,localcontext
  with localcontext() as c:c.prec=40;return format(Decimal(v.numerator)/Decimal(v.denominator),'f')
 return str(v)

def recipe_for(stage,old,*,source_relative_speed=False):
 if stage=='h_volume':return old
 return NativePreparedMatrixRecipe(old.source_bytes,old.project_bytes,old.producer_bytes,old.context,old.geometry_project_bytes,old.limits,old.fixture,old.anchor_offset,SourceRatioMatrixPolicy() if source_relative_speed and stage=='volume_speed' else PreparedMatrixPolicy(stage))

def json_bytes(value):return (json.dumps(value,sort_keys=True,indent=2,default=str)+'\n').encode()

def profile_guard(source):
 start=source.index(b'; CONFIG_BLOCK_START');end=source.index(b'; CONFIG_BLOCK_END',start);values={}
 for raw in source[start:end].splitlines():
  if raw.startswith(b'; ') and b' = ' in raw:
   key,value=raw[2:].decode('utf8').split(' = ',1)
   if key in values and key in REQUIRED_PROFILE_KEYS:raise ValueError('duplicate required source config key')
   values[key]=value
 if not set(REQUIRED_PROFILE_KEYS)<=set(values):raise ValueError('required source guard keys absent:'+str(set(REQUIRED_PROFILE_KEYS)-set(values)))
 if any(k in values for k in OPTIONAL_ABSENT_KEYS):raise ValueError('optional-absent keys unexpectedly present')
 return {'required_key_sha256':{k:sha256(values[k].encode('utf8')).hexdigest() for k in REQUIRED_PROFILE_KEYS},'optional_absent_keys':list(OPTIONAL_ABSENT_KEYS)}

def prepare(destination,old,baseline_project,*,source_relative_speed=False):
 destination=Path(destination);destination.mkdir(exist_ok=False)
 trace=interpret_native_trial(old.source_bytes,old.project_bytes,old.producer_bytes,old.context,geometry_project=old.geometry_project_bytes,limits=old.limits,cancelled=lambda:False);profile,accel,jerk=native_profile_caps(old.source_bytes,old.project_bytes,old.geometry_project_bytes,old.limits)
 hop=policy_from_slice(profile,CandidateBeadBounds(.08,.18,.25,.45),xyz_places=3,e_places=5)
 wall=min(e.after.machine.feed_mm_min/60 for e in trace.events if e.feature=='Outer wall' and e.after.machine.xyz_mm[2]==F('.8') and e.deposited_filament_mm is not None and e.deposited_filament_mm>0)
 baseline_path=Path(baseline_project)
 if baseline_path.stat().st_size>20000000:raise ValueError('baseline project byte limit')
 sourceproject=baseline_path.read_bytes()
 verify_flat_matrix(sourceproject,FlatMatrixFixture(serialization_mode='input-v1'))
 with ZipFile(BytesIO(sourceproject)) as z:
  if any(n.lower().endswith('.gcode') for n in z.namelist()):raise ValueError('geometry-only source project contains Gcode')
  if z.getinfo('Metadata/project_settings.config').file_size>2000000:raise ValueError('baseline settings byte limit')
  settings=json.loads(z.read('Metadata/project_settings.config'))
 with ZipFile(BytesIO(old.geometry_project_bytes)) as z:
  if z.getinfo('Metadata/project_settings.config').file_size>2000000:raise ValueError('actual settings byte limit')
  actual_settings=json.loads(z.read('Metadata/project_settings.config'))
 if any(actual_settings.get(k)!=v for k,v in settings.items()) or not set(actual_settings)-set(settings)<={'plugins','inherits_group','compatible_machine_expression_group','compatible_process_expression_group'} or any(type(actual_settings[k]) is not list or any(v!='' for v in actual_settings[k]) for k in set(actual_settings)-set(settings)):
  raise ValueError('baseline project settings differ from actual sliced reference')
 (destination/'source-project.3mf').write_bytes(sourceproject)
 trials=[]
 for stage in STAGES:
  recipe=recipe_for(stage,old,source_relative_speed=source_relative_speed);copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
  if stage=='h_volume' and copy.output_sha256!='eba3727f0c32d05ad4d03f681c06c46ae376232b16087c4589be822a5c5154f3':raise ValueError('historical V1 raw changed')
  folder=destination/stage;folder.mkdir();raw=folder/(stage+'.gcode');raw.write_bytes(copy.output_bytes)
  package=build_native_trial_package(recipe.project_bytes,recipe.source_bytes,copy,copy_recipe=recipe,policy=NativePackagePolicy(recipe.context.source_sha256,recipe.context.project_sha256),cancelled=lambda:False)
  (folder/(stage+'.gcode.3mf')).write_bytes(package.archive_bytes)
  reference=resolve_source_speed_reference(trace,profile,old.context.source_sha256) if source_relative_speed and stage=='volume_speed' else None
  conditions=source_relative_conditions(recipe.policy,reference.resolved_reference_speed_mm_s) if reference is not None else prepared_conditions(PreparedMatrixPolicy(stage));cells=[]
  for index,c in enumerate(conditions):
   if stage=='h_volume':
    line=freeze_matrix_line(matrix_cells()[index],diameter_mm=hop.filament_diameter_mm,speed_mm_s=min(wall,F(20)),maximum_volume_mm3_s=hop.max_volume_mm3_s,policy=MatrixExperimentPolicy());segments=((line.path.points_mm[0],line.path.points_mm[-1],line.commanded_e_mm),);baseline=line.commanded_e_mm
   else:line=freeze_prepared_line(c,diameter_mm=hop.filament_diameter_mm,speed_mm_s=min(wall,hop.candidate_speed_mm_s),maximum_volume_mm3_s=hop.max_volume_mm3_s,policy=recipe.policy,source_reference=reference);segments=line.segments;baseline=line.baseline_total_e_mm
   row={k:decimal(getattr(c,k)) for k in ('h_cmd_mm','final_volume_mm3_per_mm','print_speed_mm_s','retract_mm','wipe_mm','start_debt_unretract_speed_mm_s','startup_extra_e_mm')}
   a,b=line.path.points_mm[0],line.path.points_mm[-1]
   row.update(ceiling_reconcile_speed_mm_s='30',id=c.cell_id,row=c.row+1,column=c.column+1,actual_E_mm=decimal(line.commanded_e_mm),achieved_final_volume_mm3_per_mm=decimal(line.achieved_volume_mm3_per_mm),relative_volume_error=decimal(line.relative_volume_error),feed_mm_min=decimal(line.feed_mm_min),start_x_mm=decimal(a[0]),end_x_mm=decimal(b[0]),y_mm=decimal(a[1]),z_mm=decimal(a[2]),startup_baseline_E_mm=decimal(segments[0][2]-c.startup_extra_e_mm) if stage=='startup_extra_speed' else '0',startup_extra_E_mm=decimal(c.startup_extra_e_mm),startup_total_E_mm=decimal(segments[0][2]) if stage=='startup_extra_speed' else '0',remainder_E_mm=decimal(segments[1][2]) if len(segments)==2 else '0')
   if reference is not None:
    row.update(print_speed_ratio=decimal(SPEED_RATIOS[c.column]),source_reference_speed_mm_s=decimal(reference.resolved_reference_speed_mm_s),requested_print_speed_mm_s=decimal(c.print_speed_mm_s),print_speed_mm_s=decimal(line.feed_mm_min/60))
   row['baseline_total_relative_volume_error']=decimal(line.relative_volume_error)
   if stage=='startup_extra_speed':
    filament_area=PI*hop.filament_diameter_mm**2/4;requested_start_volume=2*c.final_volume_mm3_per_mm+c.startup_extra_e_mm*filament_area
    row['startup_achieved_volume_mm3_per_mm']=decimal(segments[0][2]*filament_area/2)
    row['startup_relative_volume_error']=decimal((segments[0][2]*filament_area-requested_start_volume)/requested_start_volume)
    row['remainder_achieved_volume_mm3_per_mm']=decimal(segments[1][2]*filament_area/8)
   else:
    row['startup_achieved_volume_mm3_per_mm']='0';row['startup_relative_volume_error']='0';row['remainder_achieved_volume_mm3_per_mm']='0'
   row['frozen_line']=asdict(line);row['segments']=segments;row['baseline_total_E_mm']=baseline;cells.append(row)
  manifest=dict(schema='prepared-matrix-frozen-commands-v2',trial_id=stage,source_sha256=recipe.context.source_sha256,geometry_sha256=recipe.context.geometry_project_sha256,profile_identity=profile.projection_identity,recipe_identity=copy.emission_policy_identity,raw_sha256=copy.output_sha256,policy=asdict(recipe.policy),transport_policy=asdict(hop),anchor_offset=recipe.anchor_offset,safe_ceiling_z_mm='1.8',source_regions=matrix_source_evidence(recipe,trace),inherited_premises=copy.unresolved_premises,numeric_convention='FINAL A; no second saved flow multiplier. Startup first2mm baseE nearest5 plus exact extra, remainder preserves baseline total.',physical_authority=False,cells=cells,copy=asdict(copy))
  if reference is not None:manifest['source_speed_reference']={k:(list(v) if type(v) is tuple else decimal(v) if type(v) is F else v) for k,v in asdict(reference).items()}
  manifest['copy'].pop('output_bytes');(folder/'frozen-manifest.json').write_bytes(json_bytes(manifest))
  fields=[k for k in cells[0] if k not in ('frozen_line','segments','baseline_total_E_mm')]
  with (folder/'conditions.csv').open('x',newline='',encoding='utf8') as stream:
   writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows({k:row[k] for k in fields} for row in cells)
  trial=dict(id=stage,title=TITLES[stage],axes={side:dict(name=axis[0],unit=axis[1],values=[decimal(v) for v in axis[2]]) for side,axis in zip(('rows','columns'),AXES[stage])},baseline_status='provisional_not_selected',baseline=BASELINE,source_sha256=recipe.context.source_sha256,geometry_sha256=recipe.context.geometry_project_sha256,profile_identity=profile.projection_identity,recipe_identity=copy.emission_policy_identity,request_sha256=None,files={})
  if reference is not None:
   trial['axes']['columns']=dict(name='print_speed_ratio',unit='ratio',values=[decimal(v) for v in SPEED_RATIOS]);trial['source_speed_reference']=manifest['source_speed_reference']
  trials.append(trial);print(stage,copy.output_sha256,copy.total_added_relative_e_mm,flush=True)
 (destination/'pending-catalog.json').write_bytes(json_bytes(dict(schema='smoothificator-calibration-ready-bundle-v2' if source_relative_speed else 'smoothificator-calibration-ready-bundle-v1',profile_gate=profile_guard(old.source_bytes),trials=trials)))
 return destination

def bundle(destination):
 from smoothificator_preview.calibration_bundle import load_bundle
 destination=Path(destination);catalog=json.loads((destination/'pending-catalog.json').read_text());assets={}
 for trial in catalog['trials']:
  stage=trial['id'];roles={'raw_gcode':f'{stage}/{stage}.gcode','conditions_csv':f'{stage}/conditions.csv','plot_png':f'{stage}/overview.png','frozen_manifest_json':f'{stage}/frozen-manifest.json','source_project_3mf':'source-project.3mf','gcode_3mf':f'{stage}/{stage}.gcode.3mf'}
  for role,path in roles.items():
   content=(destination/path).read_bytes();assets[path]=content;trial['files'][role]=dict(path=path,size=len(content),sha256=sha256(content).hexdigest())
 content=BytesIO()
 with ZipFile(content,'w',compression=ZIP_DEFLATED) as archive:
  for path,blob in [('manifest.json',json_bytes(catalog)),*sorted(assets.items())]:
   info=ZipInfo(path,date_time=(2026,10,19,0,0,0));info.compress_type=ZIP_DEFLATED;archive.writestr(info,blob)
 raw=content.getvalue();checked=load_bundle(raw);target=destination/'calibration-ready-bundle.zip'
 with target.open('xb') as stream:stream.write(raw)
 (destination/'bundle-lock.json').write_bytes(json_bytes(dict(bundle_sha256=checked.bundle_sha256,manifest_sha256=checked.manifest_sha256)))
 print('BUNDLE',checked.bundle_sha256,len(raw),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 prep=sub.add_parser('prepare');prep.add_argument('--output',required=True,type=Path)
 for name in ('source','sliced-archive','producer','geometry-project','context-json','baseline-project'):prep.add_argument('--'+name,required=True,type=Path)
 prep.add_argument('--context-sha256',required=True);prep.add_argument('--source-relative-speed',action='store_true',help='V3 volume-speed policy; preserve historical absolute-speed default')
 pack=sub.add_parser('bundle');pack.add_argument('--output',required=True,type=Path)
 a=p.parse_args()
 if a.command=='bundle':bundle(a.output)
 else:
  recipe=load_recipe(source_path=a.source,project_path=a.sliced_archive,producer_path=a.producer,geometry_path=a.geometry_project,context_path=a.context_json,context_sha256=a.context_sha256)
  prepare(a.output,recipe,a.baseline_project,source_relative_speed=a.source_relative_speed)
