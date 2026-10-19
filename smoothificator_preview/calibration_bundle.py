"""Closed portable prepared-trial bytes. No G-code generation or tools imports."""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
from io import BytesIO,StringIO
from importlib import resources
from zipfile import ZipFile,BadZipFile
import csv,json,re,stat
from .calibration_profile import REQUIRED_PROFILE_KEYS,OPTIONAL_ABSENT_KEYS
from adaptive_subedge.application.calibration_refinement import AXES

SCHEMA='smoothificator-calibration-ready-bundle-v1'
SCHEMA_V2='smoothificator-calibration-ready-bundle-v2'
SPEED_RATIOS=tuple(map(F,('.2','.4','.6','.8','1')))
REFERENCE_KEYS=('schema','source_sha256','profile_identity','source_z_mm','source_feature','source_line_numbers','saved_outer_wall_speed_mm_s','actual_wall_minimum_feed_mm_min','machine_x_cap_mm_s','machine_y_cap_mm_s','resolved_reference_speed_mm_s')
MAX_BUNDLE_BYTES=32*1024*1024
MAX_TOTAL_BYTES=64*1024*1024
MAX_ASSET_BYTES=16*1024*1024
ROLES={'raw_gcode','conditions_csv','plot_png','frozen_manifest_json','source_project_3mf','gcode_3mf'}
REQUIRED_ROLES=ROLES-{'gcode_3mf'}
BASELINE={'h_cmd_mm':F('.02'),'final_volume_mm3_per_mm':F('.0003'),'print_speed_mm_s':F(20),'retract_mm':F('1.6'),'wipe_mm':F(1),'start_debt_unretract_speed_mm_s':F(30),'ceiling_reconcile_speed_mm_s':F(30)}
VOLUME=tuple(map(F,('.000075','.000150','.000300','.000600','.001200')))
AXIS_VALUES={'h_volume':(tuple(map(F,('.010','.015','.020','.030','.040'))),VOLUME),'retract_wipe':(tuple(map(F,('.4','.7','1','1.3','1.6'))),tuple(map(F,('.25','.5','1','1.5','2')))),'startup_extra_speed':(tuple(map(F,('0','.00005','.00010','.00015','.00020'))),tuple(map(F,('6','12','18','24','30')))),'volume_speed':(VOLUME,tuple(map(F,('5','10','20','30','40'))))}


def _closed(root,keys,reason):
    if type(root) is not dict or set(root)!=set(keys):raise ValueError(reason)


def _digest(number):
    if type(number) is not str or re.fullmatch('[0-9a-f]{64}',number) is None:raise ValueError('invalid-calibration-digest')
    return number


def _number(number):
    if type(number) is not str or len(number)>40 or re.fullmatch(r'(?:0|[1-9][0-9]{0,5})(?:\.[0-9]{1,12})?',number) is None:raise ValueError('invalid-calibration-decimal')
    return F(number)


def _json(content,limit=2*1024*1024):
    if type(content) is not bytes or len(content)>limit:raise ValueError('calibration-json-limit')
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('duplicate-calibration-key')
            out[key]=value
        return out
    try:return json.loads(content.decode('utf8'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite-calibration-json')))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as error:raise ValueError('invalid-calibration-json') from error


def _path(name):
    if type(name) is not str or len(name)>180 or not 1<=len(name.split('/'))<=3 or any(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,80}',part) is None or part in ('.','..') or part.split('.')[0].upper() in ('CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))) for part in name.split('/')):raise ValueError('invalid-calibration-asset-path')
    return name


@dataclass(frozen=True)
class PreparedAsset:
    role:str
    path:str
    content:bytes
    sha256:str


@dataclass(frozen=True)
class PreparedTrial:
    id:str
    title:str
    axes_json:bytes
    baseline_json:bytes
    source_sha256:str
    geometry_sha256:str
    profile_identity:str
    recipe_identity:str
    assets:tuple
    cells_json:bytes
    bundle_schema_version:int=1
    source_speed_reference_json:bytes|None=None

    def asset(self,role):
        return next(a for a in self.assets if a.role==role)

    def presentation(self):
        return {'id':self.id,'title':self.title,'axes':_json(self.axes_json),'baseline':_json(self.baseline_json),'baseline_status':'provisional_not_selected','source_sha256':self.source_sha256,'recipe_identity':self.recipe_identity,'cells':_json(self.cells_json),'bundle_schema_version':self.bundle_schema_version,'source_speed_reference':_json(self.source_speed_reference_json) if self.source_speed_reference_json else None}


@dataclass(frozen=True)
class PreparedBundle:
    bundle_sha256:str
    manifest_sha256:str
    profile_hashes:tuple
    trials:tuple

    def trial(self,trial_id):
        if type(trial_id) is not str:raise ValueError('invalid-calibration-trial-id')
        matches=tuple(t for t in self.trials if t.id==trial_id)
        if len(matches)!=1:raise ValueError('unknown-calibration-trial')
        return matches[0]


def load_bundle(content):
    if type(content) is not bytes or not 0<len(content)<=MAX_BUNDLE_BYTES:raise ValueError('calibration-bundle-byte-limit')
    try:
        with ZipFile(BytesIO(content)) as archive:
            entries=archive.infolist();names=[e.filename for e in entries]
            if len(entries)>32 or len(names)!=len({n.casefold() for n in names}) or sum(e.file_size for e in entries)>MAX_TOTAL_BYTES or any(e.file_size>MAX_ASSET_BYTES or e.is_dir() or e.flag_bits&1 or stat.S_ISLNK(e.external_attr>>16) for e in entries):raise ValueError('calibration-bundle-inventory-limit')
            for name in names:_path(name)
            if 'manifest.json' not in names:raise ValueError('missing-calibration-manifest')
            manifest_bytes=archive.read('manifest.json');root=_json(manifest_bytes)
            _closed(root,('schema','profile_gate','trials'),'closed-calibration-bundle-schema-required')
            if root['schema'] not in (SCHEMA,SCHEMA_V2):raise ValueError('unsupported-calibration-bundle-schema')
            gate=root['profile_gate'];_closed(gate,('required_key_sha256','optional_absent_keys'),'closed-profile-guard-required')
            _closed(gate['required_key_sha256'],REQUIRED_PROFILE_KEYS,'profile-guard-key-set-differs')
            for digest in gate['required_key_sha256'].values():_digest(digest)
            if type(gate['optional_absent_keys']) is not list or sorted(gate['optional_absent_keys'])!=sorted(OPTIONAL_ABSENT_KEYS):raise ValueError('optional-profile-scope-differs')
            if type(root['trials']) is not list or len(root['trials'])!=4:raise ValueError('four-prepared-trials-required')
            trials=[];declared={'manifest.json'};shared={};shared_roles={}
            for raw in root['trials']:
                relative=root['schema']==SCHEMA_V2 and type(raw) is dict and raw.get('id')=='volume_speed'
                _closed(raw,('id','title','axes','baseline_status','baseline','source_sha256','geometry_sha256','profile_identity','recipe_identity','request_sha256','files')+(('source_speed_reference',) if relative else ()),'closed-prepared-trial-required')
                trial_id=raw['id']
                if type(trial_id) is not str or trial_id not in AXES or type(raw['title']) is not str or not 0<len(raw['title'])<=120:raise ValueError('invalid-prepared-trial-id-or-title')
                if raw['baseline_status']!='provisional_not_selected' or raw['request_sha256'] is not None:raise ValueError('prepared-baseline-is-not-user-selected')
                _closed(raw['baseline'],BASELINE,'closed-prepared-baseline-required')
                if any(_number(raw['baseline'][k])!=v for k,v in BASELINE.items()):raise ValueError('prepared-baseline-differs')
                _closed(raw['axes'],('rows','columns'),'closed-calibration-axes-required')
                for i,key in enumerate(('rows','columns')):
                    axis=raw['axes'][key];_closed(axis,('name','unit','values'),'closed-calibration-axis-required')
                    expected_name='print_speed_ratio' if relative and i==1 else AXES[trial_id][i][0]
                    expected_axis=SPEED_RATIOS if relative and i==1 else AXIS_VALUES[trial_id][i]
                    if relative and i==1 and axis['unit']!='ratio':raise ValueError('relative-speed-axis-unit-differs')
                    if axis['name']!=expected_name or type(axis['unit']) is not str or not 0<len(axis['unit'])<=32 or type(axis['values']) is not list or len(axis['values'])!=5 or tuple(_number(v) for v in axis['values'])!=expected_axis:raise ValueError('prepared-axis-differs')
                for k in ('source_sha256','geometry_sha256','profile_identity','recipe_identity'):_digest(raw[k])
                reference=None
                if relative:
                    reference=raw['source_speed_reference'];_closed(reference,REFERENCE_KEYS,'closed-source-speed-reference-required')
                    if reference['schema']!='matrix-source-speed-reference-v1' or reference['source_sha256']!=raw['source_sha256'] or reference['profile_identity']!=raw['profile_identity'] or reference['source_z_mm']!='0.8' or reference['source_feature']!='Outer wall':raise ValueError('source-speed-reference-identity-differs')
                    lines=reference['source_line_numbers']
                    if type(lines) is not list or not 1<=len(lines)<=32 or any(type(n) is not int or not 1<=n<=10000000 for n in lines) or lines!=sorted(set(lines)):raise ValueError('invalid-source-speed-line-witnesses')
                    limits=[_number(reference[k]) for k in ('saved_outer_wall_speed_mm_s','machine_x_cap_mm_s','machine_y_cap_mm_s')]
                    limits.append(_number(reference['actual_wall_minimum_feed_mm_min'])/60)
                    if not all(0<n<=1000 for n in limits) or _number(reference['resolved_reference_speed_mm_s'])!=min(limits):raise ValueError('source-speed-reference-minimum-differs')
                files=raw['files']
                if type(files) is not dict or not REQUIRED_ROLES<=set(files)<=ROLES:raise ValueError('prepared-trial-assets-incomplete')
                assets=[]
                for role,descriptor in sorted(files.items()):
                    _closed(descriptor,('path','size','sha256'),'closed-calibration-asset-required');name=_path(descriptor['path']);digest=_digest(descriptor['sha256'])
                    if type(descriptor['size']) is not int or not 0<descriptor['size']<=MAX_ASSET_BYTES or name=='manifest.json' or name not in names:raise ValueError('invalid-calibration-asset-size')
                    blob=archive.read(name)
                    if len(blob)!=descriptor['size'] or sha256(blob).hexdigest()!=digest:raise ValueError('calibration-asset-hash-mismatch')
                    if name in shared and (shared[name]!=descriptor or shared_roles[name]!=role):raise ValueError('conflicting-shared-calibration-asset')
                    expected_suffix={'raw_gcode':'.gcode','conditions_csv':'.csv','plot_png':'.png','frozen_manifest_json':'.json','source_project_3mf':'.3mf','gcode_3mf':'.gcode.3mf'}[role]
                    if not name.endswith(expected_suffix):raise ValueError('calibration-asset-extension-differs')
                    shared_roles[name]=role
                    shared[name]=descriptor;declared.add(name);assets.append(PreparedAsset(role,name,blob,digest))
                by_role={a.role:a for a in assets}
                for archive_role in ('source_project_3mf','gcode_3mf'):
                    if archive_role not in by_role:continue
                    with ZipFile(BytesIO(by_role[archive_role].content)) as project:
                        members=project.infolist()
                        if len(members)>64 or sum(member.file_size for member in members)>MAX_TOTAL_BYTES or len({member.filename.casefold() for member in members})!=len(members):raise ValueError('prepared-project-shape-limit')
                        if any(member.flag_bits&1 or member.file_size>MAX_ASSET_BYTES or stat.S_ISLNK(member.external_attr>>16) for member in members):raise ValueError('unsafe-prepared-project-member')
                        gcode=[member for member in members if member.filename.lower().endswith('.gcode')]
                        if archive_role=='source_project_3mf' and gcode:raise ValueError('baseline-project-must-not-contain-gcode')
                        if archive_role=='gcode_3mf' and (len(gcode)!=1 or project.read(gcode[0])!=by_role['raw_gcode'].content):raise ValueError('prepared-archive-raw-gcode-differs')
                frozen=_json(by_role['frozen_manifest_json'].content)
                if type(frozen) is not dict:raise ValueError('frozen-manifest-object-required')
                for key in ('trial_id','source_sha256','geometry_sha256','profile_identity','recipe_identity'):
                    if frozen.get(key)!=raw['id' if key=='trial_id' else key]:raise ValueError('frozen-prepared-identity-mismatch')
                if relative and frozen.get('source_speed_reference')!=reference:raise ValueError('frozen-source-speed-reference-differs')
                if frozen.get('raw_sha256')!=by_role['raw_gcode'].sha256:raise ValueError('frozen-raw-identity-mismatch')
                cells=frozen.get('cells')
                if type(cells) is not list or len(cells)!=25 or {(c.get('id'),c.get('row'),c.get('column')) for c in cells if type(c) is dict}!={(f'{r*5+c+1:02d}',r+1,c+1) for r in range(5) for c in range(5)}:raise ValueError('prepared-cells-not-25-unique')
                rows=list(csv.DictReader(StringIO(by_role['conditions_csv'].content.decode('utf8'))))
                if len(rows)!=25 or {(c.get('id'),c.get('row'),c.get('column')) for c in rows}!={(f'{r*5+c+1:02d}',str(r+1),str(c+1)) for r in range(5) for c in range(5)}:raise ValueError('prepared-CSV-cells-differ')
                if any(type(c.get('row')) is not int or type(c.get('column')) is not int for c in cells):raise ValueError('exact-cell-indices-required')
                frozen_by_id={c['id']:c for c in cells}
                condition_keys=set(BASELINE)|{'startup_extra_e_mm'}
                for cell in cells:
                    expected=dict(BASELINE,startup_extra_e_mm=F(0))
                    for axis_key,index in (('rows',cell['row']-1),('columns',cell['column']-1)):
                        axis=raw['axes'][axis_key];expected[axis['name']]=_number(axis['values'][index])
                    if relative:
                        expected.pop('print_speed_mm_s')
                        ratio=_number(cell['print_speed_ratio']);ref=_number(reference['resolved_reference_speed_mm_s']);requested=ratio*ref
                        feed=F((requested*60000).numerator//(requested*60000).denominator,1000)
                        if feed<=0:raise ValueError('relative-speed-feed-not-representable')
                        expected.update(source_reference_speed_mm_s=ref,requested_print_speed_mm_s=requested,print_speed_mm_s=feed/60,feed_mm_min=feed)
                    if any(key not in cell or _number(cell[key])!=amount for key,amount in expected.items()):raise ValueError('frozen-cell-does-not-match-prepared-axes')
                for csv_cell in rows:
                    frozen_cell=frozen_by_id[csv_cell['id']]
                    if type(frozen_cell.get('actual_E_mm')) is not str or 'actual_E_mm' not in csv_cell or _number(csv_cell['actual_E_mm'])!=_number(frozen_cell['actual_E_mm']):raise ValueError('CSV-frozen-command-dose-mismatch')
                    for key in ('h_cmd_mm','final_volume_mm3_per_mm','print_speed_mm_s','retract_mm','wipe_mm','start_debt_unretract_speed_mm_s','startup_extra_e_mm')+(('print_speed_ratio','source_reference_speed_mm_s','requested_print_speed_mm_s','feed_mm_min') if relative else ()):
                        if relative and key not in csv_cell:raise ValueError('missing-relative-speed-CSV-condition')
                        if key in csv_cell and (key not in frozen_cell or _number(csv_cell[key])!=_number(frozen_cell[key])):raise ValueError('CSV-frozen-condition-mismatch')
                if not by_role['plot_png'].content.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('prepared-plot-not-PNG')
                trials.append(PreparedTrial(trial_id,raw['title'],json.dumps(raw['axes']).encode(),json.dumps(raw['baseline']).encode(),raw['source_sha256'],raw['geometry_sha256'],raw['profile_identity'],raw['recipe_identity'],tuple(assets),json.dumps(cells).encode(),2 if relative else 1,json.dumps(reference).encode() if reference else None))
            if {t.id for t in trials}!=set(AXES) or len({t.id for t in trials})!=4 or set(names)!=declared:raise ValueError('calibration-bundle-has-extra-or-duplicate-cases-assets')
            if len({(t.source_sha256,t.geometry_sha256,t.profile_identity) for t in trials})!=1:raise ValueError('prepared-trials-do-not-share-frozen-source-profile')
            return PreparedBundle(sha256(content).hexdigest(),sha256(manifest_bytes).hexdigest(),tuple(sorted(gate['required_key_sha256'].items())),tuple(trials))
    except (BadZipFile,UnicodeError,KeyError,StopIteration,TypeError,OverflowError) as error:raise ValueError('invalid-calibration-bundle') from error


def installed_bundle():
    package=resources.files('smoothificator_preview')
    try:content=package.joinpath('_calibration_bundle.zip').read_bytes()
    except FileNotFoundError:return None
    lock=_json(package.joinpath('_calibration_bundle_lock.json').read_bytes(),4096)
    _closed(lock,('bundle_sha256','manifest_sha256'),'closed-calibration-lock-required')
    bundle=load_bundle(content)
    if lock!={'bundle_sha256':bundle.bundle_sha256,'manifest_sha256':bundle.manifest_sha256}:raise ValueError('installed-calibration-resource-lock-mismatch')
    return bundle
