"""Portable resource validation, safe export and proposal-only calibration."""
from io import BytesIO,StringIO
from zipfile import ZipFile
from hashlib import sha256
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import csv,json,re,shutil,subprocess,unittest
from smoothificator_preview.calibration_bundle import load_bundle,AXIS_VALUES,BASELINE,SCHEMA
from smoothificator_preview.calibration_profile import REQUIRED_PROFILE_KEYS,OPTIONAL_ABSENT_KEYS,current_profile_hashes,compare_profile
from smoothificator_preview.calibration_storage import export_trial,save_selection,load_selections
from smoothificator_preview.calibration_ui import page
from adaptive_subedge.application.calibration_refinement import AXES,proposal,AXIS_BOUNDS


def decimal(f):return format(Decimal(f.numerator)/Decimal(f.denominator),'f')
def fixture(change=None):
    entries={};trials=[];project=BytesIO()
    with ZipFile(project,'w') as z:z.writestr('3D/model.model','<model/>')
    for trial_id in AXES:
        axes={side:{'name':AXES[trial_id][i][0],'unit':'mm','values':[decimal(f) for f in AXIS_VALUES[trial_id][i]]} for i,side in enumerate(('rows','columns'))}
        cells=[]
        for n in range(25):
            c={'id':f'{n+1:02d}','row':n//5+1,'column':n%5+1,**{k:decimal(v) for k,v in BASELINE.items()},'startup_extra_e_mm':'0','actual_E_mm':'0.001'}
            for side,index in (('rows',n//5),('columns',n%5)):c[axes[side]['name']]=axes[side]['values'][index]
            cells.append(c)
        raw=b'G1 X10 E0.001\n';digest='a'*64
        frozen={'trial_id':trial_id,'source_sha256':digest,'geometry_sha256':digest,'profile_identity':digest,'recipe_identity':digest,'raw_sha256':sha256(raw).hexdigest(),'cells':cells}
        stream=StringIO();writer=csv.DictWriter(stream,fieldnames=list(cells[0]));writer.writeheader();writer.writerows(cells)
        blobs={'raw_gcode':(trial_id+'.gcode',raw),'conditions_csv':(trial_id+'.csv',stream.getvalue().encode()),'plot_png':(trial_id+'.png',b'\x89PNG\r\n\x1a\n'),'frozen_manifest_json':(trial_id+'.json',json.dumps(frozen).encode()),'source_project_3mf':('source.3mf',project.getvalue())}
        files={}
        for role,(name,blob) in blobs.items():entries[name]=blob;files[role]={'path':name,'size':len(blob),'sha256':sha256(blob).hexdigest()}
        trials.append({'id':trial_id,'title':trial_id,'axes':axes,'baseline_status':'provisional_not_selected','baseline':{k:decimal(v) for k,v in BASELINE.items()},'request_sha256':None,'source_sha256':digest,'geometry_sha256':digest,'profile_identity':digest,'recipe_identity':digest,'files':files})
    manifest={'schema':SCHEMA,'profile_gate':{'required_key_sha256':{k:'b'*64 for k in REQUIRED_PROFILE_KEYS},'optional_absent_keys':list(OPTIONAL_ABSENT_KEYS)},'trials':trials}
    if change:change(manifest,entries)
    output=BytesIO()
    with ZipFile(output,'w') as z:
        z.writestr('manifest.json',json.dumps(manifest))
        for name,blob in entries.items():z.writestr(name,blob)
    return output.getvalue()


class CalibrationLibraryTests(unittest.TestCase):
    def test_all_four_and_exact_export_persistence(self):
        bundle=load_bundle(fixture());self.assertEqual(len(bundle.trials),4)
        with TemporaryDirectory() as root:
            target,receipt=export_trial(root,bundle,'h_volume')
            self.assertEqual((target/'h_volume.gcode').read_bytes(),bundle.trial('h_volume').asset('raw_gcode').content)
            self.assertFalse(receipt['printing_started'])
            _,record=save_selection(root,bundle,'h_volume','13','acceptable',refine=True)
            self.assertFalse(record['new_gcode_generated']);self.assertEqual(load_selections(root,bundle)['h_volume']['selected_cell'],'13')
            target,_=export_trial(root,bundle,'h_volume',baseline_only=True)
            self.assertEqual({p.name for p in target.iterdir()},{'baseline-project.3mf','export-receipt.json'})
    def test_cancel_cleans_and_does_not_overwrite(self):
        bundle=load_bundle(fixture())
        with TemporaryDirectory() as root:
            keep=Path(root)/'unrelated';keep.write_bytes(b'keep')
            with self.assertRaises(InterruptedError):export_trial(root,bundle,'h_volume',cancelled=lambda:True)
            self.assertEqual(list(Path(root).iterdir()),[keep]);self.assertEqual(keep.read_bytes(),b'keep')
    def test_reject_closed_guard_extra_assets_alias_and_wrong_hash(self):
        mutations=[lambda m,e:m['profile_gate']['required_key_sha256'].pop(REQUIRED_PROFILE_KEYS[0]),lambda m,e:e.update({'SOURCE.3mf':e['source.3mf']}),lambda m,e:e.update({'extra.py':b'bad'}),lambda m,e:e.update({'h_volume.gcode':b'changed'}),lambda m,e:m.update({'extra':True})]
        for mutate in mutations:
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):load_bundle(fixture(mutate))
    def test_frozen_csv_numeric_disagreement(self):
        def mutate(m,e):
            name='h_volume.csv';e[name]=e[name].replace(b'0.001',b'0.002');d=m['trials'][0]['files']['conditions_csv'];d.update(size=len(e[name]),sha256=sha256(e[name]).hexdigest())
        with self.assertRaisesRegex(ValueError,'dose-mismatch'):load_bundle(fixture(mutate))
    def test_refinement_all_edges_stay_bounded_selected_retained(self):
        for trial_id in AXES:
            axes=AXIS_VALUES[trial_id]
            for cell in ('01','13','25'):
                p=proposal(trial_id,[decimal(v)for v in axes[0]],[decimal(v)for v in axes[1]],cell,'acceptable')
                if 'axes' not in p:
                    self.assertIn(p['status'],('resolution_limit_offline_range_review_required','offline_range_expansion_review_required'));continue
                for i,a in enumerate(p['axes']):
                    values=list(map(Decimal,a['values']));low,high=map(Decimal,AXIS_BOUNDS[trial_id][i]);self.assertTrue(low<=values[0]<values[-1]<=high)
                    selected=(int(cell)-1)//5 if i==0 else(int(cell)-1)%5
                    self.assertIn(Decimal(decimal(axes[i][selected])),values)
    def test_exact_profile_strings_no_normalization(self):
        class Host:
            def full_config_keys(self):return list(REQUIRED_PROFILE_KEYS)
            def full_config_value(self,key):return 'exact\\nstring '
        hashes=current_profile_hashes(Host());self.assertFalse(compare_profile(hashes,hashes));other=dict(hashes);other.pop(REQUIRED_PROFILE_KEYS[0]);self.assertEqual(compare_profile(hashes,other),(REQUIRED_PROFILE_KEYS[0],))
    @unittest.skipUnless(shutil.which('node'),'Node unavailable')
    def test_actual_rendered_javascript_syntax_and_safe_state(self):
        html=page({'trials':[],'reason':'</script><script>bad()</script>'})
        script=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
        self.assertNotIn('</script>',script)
        with TemporaryDirectory() as root:
            path=Path(root)/'page.js';path.write_text(script,encoding='utf8')
            completed=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
            self.assertEqual(completed.returncode,0,completed.stderr)

if __name__=='__main__':unittest.main()

class CalibrationLifecycleTests(unittest.TestCase):
    def setup_capability(self,root):
        from tests.unit.test_readonly_preview import PreviewLifecycleTests
        from types import SimpleNamespace
        from unittest.mock import patch
        module,windows=PreviewLifecycleTests().load_entrypoint()
        module.orca.host.plugin=SimpleNamespace(storage=lambda:root)
        module.orca.host.preset_bundle=lambda:(_ for _ in ()).throw(ValueError('unknown-profile'))
        module.orca.host.model=lambda:(_ for _ in ()).throw(AssertionError('must-not-copy-model'))
        bundle=load_bundle(fixture());cap=module.CalibrationMatrices()
        return module,windows,bundle,cap
    def test_unknown_profile_baseline_works_raw_denied_and_old_window_ignored(self):
        from unittest.mock import patch
        with TemporaryDirectory() as root:
            module,windows,bundle,cap=self.setup_capability(root)
            with patch('smoothificator_preview.calibration_bundle.installed_bundle',return_value=bundle):
                cap.execute();old=windows[-1];epoch=cap.epoch
                cap.on_message({'command':'calibration_export','trial_id':'h_volume'},epoch)
                self.assertIn('missing-or-mismatched',old.posted[-1]['reason']);self.assertIsNone(cap.worker)
                cap.on_message({'command':'calibration_baseline_export','trial_id':'h_volume'},epoch);cap.worker.join(5)
                self.assertFalse(cap.worker.is_alive());self.assertTrue(any('paths'in m for m in old.posted))
                self.assertFalse(old.posted[-1]['state']['busy'])
                cap.execute();count=len(list(Path(root).iterdir()))
                old.callbacks['on_message']({'command':'calibration_baseline_export','trial_id':'h_volume'})
                self.assertEqual(len(list(Path(root).iterdir())),count)
    def test_close_during_export_cancels_without_advertising(self):
        from unittest.mock import patch
        from threading import Event
        started=Event();release=Event()
        def blocked(*args,**kwargs):
            started.set();release.wait(3)
            return export_trial(*args,**kwargs)
        with TemporaryDirectory() as root:
            module,windows,bundle,cap=self.setup_capability(root)
            with patch('smoothificator_preview.calibration_bundle.installed_bundle',return_value=bundle),patch('smoothificator_preview.calibration_storage.export_trial',side_effect=blocked):
                cap.execute();cap.on_message({'command':'calibration_baseline_export','trial_id':'h_volume'})
                self.assertTrue(started.wait(2));cap.on_close();release.set();cap.worker.join(5)
                self.assertFalse(any('paths'in m for m in windows[-1].posted));self.assertEqual(list(Path(root).iterdir()),[])

class CalibrationPackagingTests(unittest.TestCase):
    def test_optional_validated_resources_and_provenance(self):
        from tests.unit.test_preview_package import PreviewPackageTests
        from tools.build_preview_plugin import build_wheel,DIST_INFO
        owner=PreviewPackageTests();owner.setUp()
        try:
            source=owner.root/'ready.zip';source.write_bytes(fixture());wheel=build_wheel(owner.root,owner.root/'bundled',source)
            with ZipFile(wheel) as z:
                self.assertEqual(z.read('smoothificator_preview/_calibration_bundle.zip'),source.read_bytes())
                lock=json.loads(z.read('smoothificator_preview/_calibration_bundle_lock.json'))
                provenance=json.loads(z.read(DIST_INFO+'/provenance.json'))
                self.assertEqual(provenance['calibration_bundle_sha256'],lock['bundle_sha256'])
                self.assertEqual(provenance['calibration_manifest_sha256'],lock['manifest_sha256'])
                self.assertIn('prepared experimental',provenance['scope'])
            source.write_bytes(b'bad')
            with self.assertRaises(ValueError):build_wheel(owner.root,owner.root/'bad',source)
        finally:owner.doCleanups()

class CalibrationRegressionTests(unittest.TestCase):
    def test_boundary_request_preserves_selection_without_false_narrowing(self):
        bundle=load_bundle(fixture())
        with TemporaryDirectory() as root:
            _,record=save_selection(root,bundle,'h_volume','01','missing_center',refine=True)
            self.assertEqual(record['proposal']['status'],'offline_range_expansion_review_required')
            self.assertNotIn('axes',record['proposal']);self.assertEqual(load_selections(root,bundle)['h_volume']['selected_cell'],'01')
    def test_optional_archive_must_embed_exact_raw(self):
        def mutate(m,e):
            output=BytesIO()
            with ZipFile(output,'w')as z:z.writestr('Metadata/plate_1.gcode',b'wrong')
            blob=output.getvalue();e['wrong.gcode.3mf']=blob
            m['trials'][0]['files']['gcode_3mf']={'path':'wrong.gcode.3mf','size':len(blob),'sha256':sha256(blob).hexdigest()}
        with self.assertRaisesRegex(ValueError,'archive-raw'):load_bundle(fixture(mutate))
    def test_installed_resource_lock_binds_bundle(self):
        from unittest.mock import patch
        from smoothificator_preview.calibration_bundle import installed_bundle
        with TemporaryDirectory() as root:
            folder=Path(root);content=fixture();bundle=load_bundle(content)
            (folder/'_calibration_bundle.zip').write_bytes(content)
            lock=folder/'_calibration_bundle_lock.json';lock.write_text(json.dumps({'bundle_sha256':bundle.bundle_sha256,'manifest_sha256':bundle.manifest_sha256}))
            with patch('smoothificator_preview.calibration_bundle.resources.files',return_value=folder):
                self.assertEqual(installed_bundle().bundle_sha256,bundle.bundle_sha256)
                lock.write_text(json.dumps({'bundle_sha256':'0'*64,'manifest_sha256':bundle.manifest_sha256}))
                with self.assertRaisesRegex(ValueError,'lock-mismatch'):installed_bundle()


class RelativeSpeedBundleTests(unittest.TestCase):
    @staticmethod
    def relative_fixture(mutate=None):
        from smoothificator_preview.calibration_bundle import SCHEMA_V2
        def convert(manifest,entries):
            manifest['schema']=SCHEMA_V2;trial=manifest['trials'][-1]
            reference={'schema':'matrix-source-speed-reference-v1','source_sha256':trial['source_sha256'],'profile_identity':trial['profile_identity'],'source_z_mm':'0.8','source_feature':'Outer wall','source_line_numbers':[3367,3368,3369,3370],'saved_outer_wall_speed_mm_s':'200','actual_wall_minimum_feed_mm_min':'12000','machine_x_cap_mm_s':'200','machine_y_cap_mm_s':'200','resolved_reference_speed_mm_s':'200'}
            trial['source_speed_reference']=reference;trial['axes']['columns']={'name':'print_speed_ratio','unit':'ratio','values':['0.2','0.4','0.6','0.8','1']}
            frozen=json.loads(entries['volume_speed.json']);frozen['source_speed_reference']=reference
            for cell in frozen['cells']:
                ratio=Decimal(trial['axes']['columns']['values'][cell['column']-1]);speed=ratio*200
                cell.update(print_speed_ratio=str(ratio),source_reference_speed_mm_s='200',requested_print_speed_mm_s=str(speed),print_speed_mm_s=str(speed),feed_mm_min=str(speed*60))
            if mutate:mutate(manifest,frozen)
            stream=StringIO();writer=csv.DictWriter(stream,fieldnames=list(frozen['cells'][0]));writer.writeheader();writer.writerows(frozen['cells'])
            entries['volume_speed.csv']=stream.getvalue().encode();entries['volume_speed.json']=json.dumps(frozen).encode()
            for role,name in [('conditions_csv','volume_speed.csv'),('frozen_manifest_json','volume_speed.json')]:
                trial['files'][role].update(size=len(entries[name]),sha256=sha256(entries[name]).hexdigest())
        return fixture(convert)
    def test_v1_and_v2_axes_requests_independently_bound(self):
        old=load_bundle(fixture());new=load_bundle(self.relative_fixture())
        for trial in old.trials[:-1]:self.assertEqual(trial.assets,new.trial(trial.id).assets)
        self.assertEqual(old.trial('volume_speed').bundle_schema_version,1)
        self.assertEqual(new.trial('volume_speed').presentation()['source_speed_reference']['resolved_reference_speed_mm_s'],'200')
        with TemporaryDirectory() as root:
            _,record=save_selection(root,new,'volume_speed','13','acceptable',refine=True)
            self.assertEqual(record['schema'],'prepared-calibration-proposal-request-v2')
            self.assertEqual(record['proposal']['axes'][1]['name'],'print_speed_ratio')
            self.assertIn('0.6',record['proposal']['axes'][1]['values'])
            self.assertEqual(record['source_speed_reference']['resolved_reference_speed_mm_s'],'200')
        old_proposal=proposal('volume_speed',[decimal(v)for v in AXIS_VALUES['volume_speed'][0]],['5','10','20','30','40'],'13','acceptable')
        self.assertEqual(old_proposal['axes'][1]['name'],'print_speed_mm_s');self.assertNotIn('schema_version',old_proposal)
    def test_reject_forged_reference_and_speed_even_consistent_csv(self):
        def reference(m,f):m['trials'][-1]['source_speed_reference']['resolved_reference_speed_mm_s']='199'
        def speed(m,f):f['cells'][0]['print_speed_mm_s']='39'
        def ratio(m,f):f['cells'][0]['print_speed_ratio']='0.21'
        def identity(m,f):m['trials'][-1]['source_speed_reference']['source_sha256']='0'*64
        for mutation in (reference,speed,ratio,identity):
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):load_bundle(self.relative_fixture(mutation))
    def test_closed_reference_no_bool_lines_and_legacy_schema_no_extra(self):
        for mutation in (lambda m,f:m['trials'][-1]['source_speed_reference'].update(extra='bad'),lambda m,f:m['trials'][-1]['source_speed_reference'].update(source_line_numbers=[True])):
            with self.assertRaises(ValueError):load_bundle(self.relative_fixture(mutation))
        with self.assertRaises(ValueError):proposal('volume_speed',['0.000075','0.00015','0.0003','0.0006','0.0012'],['.2','.4','.6','.8','1'],'13','acceptable',schema_version=True)
