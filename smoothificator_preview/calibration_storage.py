"""Contained exact prepared export and immutable calibration result/proposal files."""
from pathlib import Path
from hashlib import sha256
from uuid import uuid4
import json,os,re
from .calibration_bundle import PreparedBundle
from adaptive_subedge.application.calibration_refinement import SYMPTOMS,proposal


def _root(storage):
    if type(storage) is not str or not storage:raise ValueError('invalid-calibration-storage')
    root=Path(storage)
    if root.is_symlink():raise ValueError('unsafe-calibration-storage')
    root=root.resolve();root.mkdir(parents=True,exist_ok=True)
    return root


def _check(cancelled):
    if cancelled():raise InterruptedError('calibration-operation-cancelled')


def remove_created_export(path,storage):
    root=_root(storage);path=Path(path)
    if path.is_symlink() or not path.resolve().is_relative_to(root) or path.parent!=root or not path.name.startswith(('calibration-','.calibration-')):raise ValueError('unsafe-calibration-export-cleanup')
    if path.exists():
        for file in path.iterdir():
            if file.is_symlink() or not file.is_file():raise ValueError('unexpected-calibration-export-entry')
            file.unlink()
        path.rmdir()


def export_trial(storage,bundle,trial_id,*,baseline_only=False,cancelled=lambda:False):
    if type(bundle) is not PreparedBundle or type(baseline_only) is not bool:raise ValueError('immutable-prepared-bundle-required')
    trial=bundle.trial(trial_id);root=_root(storage);token=uuid4().hex
    staging=root/('.calibration-'+token);target=root/('calibration-'+trial.id+'-'+token)
    staging.mkdir(exist_ok=False);published=False
    filenames={'raw_gcode':trial.id+'.gcode','conditions_csv':'conditions.csv','plot_png':'overview.png','frozen_manifest_json':'frozen-trial.json','source_project_3mf':'baseline-project.3mf','gcode_3mf':trial.id+'.gcode.3mf'}
    copied=[]
    try:
        for asset in trial.assets:
            if baseline_only and asset.role!='source_project_3mf':continue
            _check(cancelled);filename=filenames[asset.role];path=staging/filename
            with path.open('xb') as output:
                for offset in range(0,len(asset.content),65536):
                    _check(cancelled);output.write(asset.content[offset:offset+65536])
                output.flush();os.fsync(output.fileno())
            if sha256(path.read_bytes()).hexdigest()!=asset.sha256:raise ValueError('calibration-export-readback-mismatch')
            copied.append({'role':asset.role,'filename':filename,'sha256':asset.sha256})
        receipt={'schema':'prepared-calibration-export-v1','trial_id':trial.id,'bundle_sha256':bundle.bundle_sha256,'manifest_sha256':bundle.manifest_sha256,'source_sha256':trial.source_sha256,'recipe_identity':trial.recipe_identity,'baseline_only':baseline_only,'files':copied,'generated_from_live_model':False,'printing_started':False}
        (staging/'export-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2),encoding='utf8')
        _check(cancelled);staging.rename(target);published=True;_check(cancelled)
        return target,receipt
    except BaseException:
        remove_created_export(target if published else staging,storage)
        raise


def save_selection(storage,bundle,trial_id,cell_id,symptom,*,refine=False):
    if type(bundle) is not PreparedBundle or type(refine) is not bool or type(symptom) is not str or symptom not in SYMPTOMS:raise ValueError('invalid-calibration-selection')
    trial=bundle.trial(trial_id)
    if symptom=='none_acceptable':
        if cell_id is not None:raise ValueError('no-acceptable-result-must-not-force-cell')
    elif type(cell_id) is not str or cell_id not in {f'{n:02d}'for n in range(1,26)}:raise ValueError('invalid-calibration-cell')
    axes=json.loads(trial.axes_json)
    record={'schema':'prepared-calibration-result-v1','trial_id':trial.id,'selected_cell':cell_id,'symptom':symptom,'bundle_sha256':bundle.bundle_sha256,'manifest_sha256':bundle.manifest_sha256,'source_sha256':trial.source_sha256,'profile_identity':trial.profile_identity,'recipe_identity':trial.recipe_identity,'status':'selection_only','new_gcode_generated':False}
    if refine:
        record['schema']='prepared-calibration-proposal-request-v2' if trial.bundle_schema_version==2 else 'prepared-calibration-proposal-request-v1'
        if trial.bundle_schema_version==2:record['source_speed_reference']=json.loads(trial.source_speed_reference_json)
        record['status']='proposal_only_not_generated'
        record['proposal']=proposal(trial.id,axes['rows']['values'],axes['columns']['values'],cell_id,symptom,schema_version=trial.bundle_schema_version) if cell_id else {'status':'no_acceptable_cell_offline_range_review_required','offline_revalidation_required':True}
    root=_root(storage);target=root/('calibration-'+('proposal-'if refine else'result-')+uuid4().hex+'.json')
    content=(json.dumps(record,sort_keys=True,indent=2)+'\n').encode('utf8')
    with target.open('xb') as output:output.write(content);output.flush();os.fsync(output.fileno())
    if target.read_bytes()!=content:raise ValueError('calibration-result-readback-mismatch')
    _save_index(root,bundle,trial.id,target.name)
    return target,record


def load_selections(storage,bundle):
    root=_root(storage);index=root/'calibration-selection-index.json'
    if not index.exists():return {}
    if index.is_symlink() or index.stat().st_size>16384:raise ValueError('invalid-calibration-selection-index')
    try:record=json.loads(index.read_text(encoding='utf8'))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as error:raise ValueError('invalid-calibration-selection-index') from error
    if type(record) is not dict or set(record)!={'schema','bundle_sha256','results'} or record['schema']!='prepared-selection-index-v1' or type(record['results']) is not dict or len(record['results'])>4:raise ValueError('invalid-calibration-selection-index')
    if record['bundle_sha256']!=bundle.bundle_sha256:return {}
    selections={}
    for trial_id,name in record['results'].items():
        trial=bundle.trial(trial_id)
        if type(name) is not str or re.fullmatch(r'calibration-(?:result|proposal)-[0-9a-f]{32}\.json',name) is None:raise ValueError('invalid-calibration-result-name')
        path=root/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size>32768:raise ValueError('invalid-calibration-result-file')
        try:saved=json.loads(path.read_text(encoding='utf8'))
        except (UnicodeError,json.JSONDecodeError,RecursionError) as error:raise ValueError('invalid-calibration-result-file') from error
        if type(saved) is not dict:raise ValueError('invalid-calibration-result-file')
        if saved.get('bundle_sha256')!=bundle.bundle_sha256 or saved.get('trial_id')!=trial_id or saved.get('recipe_identity')!=trial.recipe_identity or saved.get('symptom') not in SYMPTOMS or saved.get('selected_cell') not in (None,*(f'{n:02d}'for n in range(1,26))):raise ValueError('stale-calibration-result')
        selections[trial_id]={'selected_cell':saved['selected_cell'],'symptom':saved['symptom'],'path':str(path)}
    return selections


def _save_index(root,bundle,trial_id,name):
    index=root/'calibration-selection-index.json';results={}
    if index.exists():
        # Validate referenced records before retaining pointers.
        existing=load_selections(str(root),bundle)
        results={key:Path(record['path']).name for key,record in existing.items()}
    results[trial_id]=name
    content=(json.dumps({'schema':'prepared-selection-index-v1','bundle_sha256':bundle.bundle_sha256,'results':results},sort_keys=True)+'\n').encode()
    temporary=root/('.calibration-index-'+uuid4().hex+'.tmp')
    try:
        with temporary.open('xb') as output:output.write(content);output.flush();os.fsync(output.fileno())
        os.replace(temporary,index)
    finally:temporary.unlink(missing_ok=True)
