"""Closed domain/usage resolution never rewrites the genuine GUI archives."""
from dataclasses import replace
from fractions import Fraction as F
from hashlib import md5,sha256
from io import BytesIO
import json
from pathlib import Path
import unittest
from zipfile import ZipFile

from orca_plugin.gcode.source_profile import SlicedProfile,read_sliced_profile
from tests.unit.native_trial_fixture import material_fixture,change_member
from tools.native_used_material_profile import NativeMaterialProfileLimits,read_native_used_material_profile


LIMITS=NativeMaterialProfileLimits(1000000,10000000,100,20000000,20000,4096)
BODY=b'M624 AQAAAAAAAAA=\nG1 X1 Y2 Z3 F6000\nM625\n'


def fixture(**changes): return material_fixture(BODY,**changes)[:3]


def read(inputs,**changes):
    source,project,geometry=inputs
    return read_native_used_material_profile(project,source,geometry,**dict(dict(limits=LIMITS),**changes))


def member(project,name):
    with ZipFile(BytesIO(project)) as archive:return archive.read(name)


def settings_changed(inputs,changes):
    source,project,geometry=inputs
    settings=json.loads(member(project,'Metadata/project_settings.config'))
    for key,value in changes.items():
        if value is None:settings.pop(key)
        else:settings[key]=value
    raw=json.dumps(settings).encode()
    return source,change_member(project,'Metadata/project_settings.config',raw),change_member(geometry,'Metadata/project_settings.config',raw)


def source_changed(inputs,source):
    _,project,geometry=inputs
    project=change_member(project,'Metadata/plate_1.gcode',source)
    project=change_member(project,'Metadata/plate_1.gcode.md5',md5(source).hexdigest().upper().encode())
    return source,project,geometry


class NativeUsedMaterialProfileTests(unittest.TestCase):
    def test_contiguous_empty_nominal_suffix_requires_independent_source_counts(self):
        inputs=fixture()
        source=inputs[0].replace(b'; model label id:',b'; max_z_height: 0.8\n; model label id:')
        source+=b'; CHANGE_LAYER\n; Z_HEIGHT: 0.2\n; LAYER_HEIGHT: 0.2\n; layer num/total_layer_count: 1/4\n; CHANGE_LAYER\n; Z_HEIGHT: 0.4\n; LAYER_HEIGHT: 0.2\n; layer num/total_layer_count: 2/4\n; LAYER_HEIGHT: 0.2\n; LAYER_HEIGHT: 0.2\n'
        inputs=source_changed(inputs,source)
        usage=member(inputs[1],'Metadata/slice_info.config').replace(b'layer_ranges="2 2"',b'layer_ranges="2 3"')
        inputs=(source,change_member(inputs[1],'Metadata/slice_info.config',usage),inputs[2])
        profile=read(inputs)
        self.assertEqual(profile.selection.layer_material_ranges[-1],(2,3,()))
        for replacement in (source.replace(b'2/4',b'2/5'),source.replace(b'1/4',b'2/4'),
                            source.replace(b'max_z_height: 0.8',b'max_z_height: 0.81'),
                            source.replace(b'max_z_height: 0.8',b'max_z_height: 20000'),
                            source.replace(b'; CHANGE_LAYER\n',b'',1),
                            source.replace(b'; layer_height = 0.2',b'; layer_height = 0.1'),
                            source.replace(b'; Z_HEIGHT: 0.2',b'; Z_HEIGHT: 0.1'),
                            source.replace(b'; Z_HEIGHT: 0.4',b'; Z_HEIGHT: 0.3')):
            with self.subTest(source=replacement[-150:]):
                with self.assertRaises(ValueError):read(source_changed(inputs,replacement))
        # Feature thickness, including thick bridges, does not change nominal Z.
        read(source_changed(inputs,source.replace(b'; LAYER_HEIGHT: 0.2',b'; LAYER_HEIGHT: 0.4',1)))
        for malformed in (usage.replace(b'filament_list=""',b'filament_list="2"'),
                          usage.replace(b'layer_ranges="0 1"',b'layer_ranges="0 0"'),
                          usage.replace(b'layer_ranges="2 3"',b'layer_ranges="3 3"'),
                          usage.replace(b'layer_ranges="2 3"',b'layer_ranges="2 4"'),
                          usage.replace(b'layer_ranges="0 1"',b'layer_ranges="0 2"')):
            with self.assertRaises(ValueError):read((source,change_member(inputs[1],'Metadata/slice_info.config',malformed),inputs[2]))
        # The original one-empty-plane fixture remains accepted unchanged.
        self.assertEqual(read(fixture()).selection.layer_material_ranges[-1],(2,2,()))

    def test_three_presets_one_used_material_and_single_physical_extruder_domains(self):
        inputs=fixture();profile=read(inputs)
        self.assertNotIsInstance(profile,SlicedProfile)
        self.assertEqual(profile.selection.material_index,2)
        self.assertEqual(profile.selection.physical_extruder_index,0)
        self.assertEqual(profile.setting('filament_flow_ratio').number(),F('.98'))
        self.assertEqual(profile.setting('filament_max_volumetric_speed').number(),21)
        self.assertEqual(profile.setting('nozzle_diameter').physical_extruder_index,0)
        self.assertEqual(profile.setting('retraction_length').source_key,'retraction_length')
        self.assertEqual(profile.setting('retraction_length').material_index,2)
        with self.assertRaises(ValueError):profile.setting('bed_temperature')
        with self.assertRaises(ValueError):read_sliced_profile(inputs[1],inputs[0])

    def test_usage_header_object_layers_tool_and_physical_nozzle_disagreement_rejected(self):
        inputs=fixture();source,project,geometry=inputs
        plate=json.loads(member(project,'Metadata/plate_1.json'));plate['filament_ids']=[0]
        cases=[(source,change_member(project,'Metadata/plate_1.json',json.dumps(plate).encode()),geometry),
            (source,change_member(project,'Metadata/slice_info.config',member(project,'Metadata/slice_info.config').replace(b'filament_list="2"',b'filament_list="1"')),geometry),
            (source,change_member(project,'Metadata/slice_info.config',member(project,'Metadata/slice_info.config').replace(b'extruder_id="1"',b'extruder_id="3"')),geometry),
            (source,project,change_member(geometry,'Metadata/model_settings.config',member(geometry,'Metadata/model_settings.config').replace(b'key="extruder" value="3"',b'key="extruder" value="1"'))),
            source_changed(inputs,source.replace(b'; filament: 3',b'; filament: 1')),
            source_changed(inputs,source.replace(b'\nT2\n',b'\nT1\n')),
            source_changed(inputs,source.replace(b'\nM625\n',b'\nT2\nM625\n'))]
        for case in cases:
            with self.subTest(case=sha256(case[1]).hexdigest()),self.assertRaises(ValueError):read(case)
        extra=member(project,'Metadata/slice_info.config').replace(b'<nozzle ',b'<filament id="1" used_for_object="false" used_for_support="true"/><nozzle ')
        with self.assertRaises(ValueError):read((source,change_member(project,'Metadata/slice_info.config',extra),geometry))

    def test_closed_domain_cardinality_and_full_vector_agreement(self):
        inputs=fixture()
        for changes in ({'filament_flow_ratio':['.98']},{'nozzle_diameter':['.4','.4','.4']},{'layer_height':['.2']},
                        {'filament_flow_ratio':['.9','1','.98']}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):read(settings_changed(inputs,changes))
        source,project,geometry=inputs
        bad=source.replace(b'; filament_flow_ratio = 1,1,0.98',b'; filament_flow_ratio = 1,0.5,0.98')
        with self.assertRaises(ValueError):read(source_changed(inputs,bad))
        duplicate=source.replace(b'; CONFIG_BLOCK_END',b'; filament_flow_ratio = 1,1,0.98\n; CONFIG_BLOCK_END')
        with self.assertRaises(ValueError):read(source_changed(inputs,duplicate))

    def test_explicit_nil_override_non_nil_override_and_missing_are_distinct(self):
        profile=read(fixture(settings_changes={'filament_retraction_length':['nil','nil','1.2']}))
        self.assertEqual(profile.setting('retraction_length').number(),F('1.2'))
        self.assertEqual(profile.setting('retraction_length').source_key,'filament_retraction_length')
        self.assertEqual(profile.setting('retraction_length').full_saved_vector,('nil','nil','1.2'))
        profile=read(fixture())
        self.assertEqual(profile.setting('z_hop').number(),F('.4'))
        with self.assertRaises(ValueError):read(settings_changed(fixture(),{'filament_z_hop':None}))
        with self.assertRaises(ValueError):read(fixture(settings_changes={'filament_z_hop':['nil','nil','NaN']}))

    def test_machine_mode_vectors_remain_full_and_unused_settings_bind_identity(self):
        profile=read(fixture(settings_changes={'machine_max_speed_x':['500','200','100']}))
        setting=profile.setting('machine_max_speed_x')
        self.assertEqual(setting.full_saved_vector,('500','200','100'))
        self.assertEqual(setting.domain,'MACHINE_MODE')
        self.assertEqual(profile.setting('conservative_machine_max_speed_x').number(),100)
        inputs=fixture();before=read(inputs)
        after=read(settings_changed(inputs,{'unused_material_note':['changed','unused','same']}))
        self.assertNotEqual(before.full_settings_sha256,after.full_settings_sha256)
        self.assertNotEqual(before.projection_identity,after.projection_identity)
        self.assertEqual(before.setting('filament_diameter'),after.setting('filament_diameter'))

    def test_actual_source_settings_geometry_and_limits_must_bind(self):
        inputs=fixture();source,project,geometry=inputs
        with self.assertRaises(ValueError):read((source+b'; stale\n',project,geometry))
        with self.assertRaises(ValueError):read((source,change_member(project,'Metadata/plate_1.gcode.md5',b'0'*32),geometry))
        with self.assertRaises(ValueError):read((source,project,settings_changed(inputs,{'layer_height':'.3'})[2]))
        for changes in (dict(limits=replace(LIMITS,max_source_bytes=1)),dict(limits=replace(LIMITS,max_archive_members=1)),
                        dict(cancelled=lambda:True),dict(cancelled=lambda:1)):
            with self.subTest(changes=changes),self.assertRaises(ValueError):read(inputs,**changes)

    def test_current_gui_snapshot_resolves_basic_without_modifying_real_inputs(self):
        folder=Path(__file__).resolve().parents[2]/'artifacts/gui-angle0to30-trial-v2'
        paths=(folder/'source-input-a6314651.gcode',folder/'source-input-1d714338.gcode.3mf',folder/'geometry-input-6812137d.3mf')
        contents=tuple(path.read_bytes() for path in paths);before=tuple(map(lambda b:sha256(b).hexdigest(),contents))
        profile=read(contents)
        self.assertEqual(profile.selection.material_index,2)
        self.assertEqual(profile.setting('filament_settings_id').value,'Bambu PLA Basic @BBL A1M')
        self.assertEqual(profile.full_settings_sha256,'33df726ee13a5f6458106abd9de1553d456b7e7f6a264b480582da1ab969a482')
        self.assertEqual(before,tuple(sha256(path.read_bytes()).hexdigest() for path in paths))


if __name__=='__main__':unittest.main()
