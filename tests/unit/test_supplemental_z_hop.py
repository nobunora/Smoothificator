"""Explicit hops, saved retraction restoration and bounded volume commands."""
from dataclasses import replace
from fractions import Fraction as F
import math
import json
from hashlib import sha256
import unittest

from adaptive_subedge.domain.settings import CandidateBeadBounds
from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution, _words
from orca_plugin.gcode.source_profile import read_sliced_profile, SourceProfileError
from tests.unit.test_print_source_inspection import fixture, settings_fixture
from tools.supplemental_z_hop import (
    HopPolicy, SupplementalPath, compose_retracted_cycle, safe_ceiling, policy_from_slice,
)
from tools.review_supplemental_hops import review_hops


def policy_fixture():
    return HopPolicy(F('.4'),F(180),F(200),F(30),F(30),F(30),F(100),
        F('1.75'),F(1),F(1),F('.98'),False,F(1),CandidateBeadBounds(.08,.18,.25,.45),3,5)


def anchor_fixture():
    return MachineState((F(5),F(6),F('3.2')),True,True,True,F(1250),F(40),F('.8'),True,True,True)


def path_fixture(name='thin', height='.08'):
    top = F(3)+F(height)
    return SupplementalPath(name,F(3),F('.3'),F(height),
                            ((F(10),F(11),top),(F(12),F(11),top),(F(12),F(13),top)))


class SupplementalHopTests(unittest.TestCase):
    def test_thin_first_and_exact_modal_state_restoration(self):
        anchor = anchor_fixture()
        block = compose_retracted_cycle(anchor,(path_fixture('thick','.18'),path_fixture()),F('3.2'),policy_fixture())
        self.assertLess(block.index(b'PATH thin'),block.index(b'PATH thick'))
        trace = trace_linear_execution(block,initial_state=anchor)
        self.assertIsNone(trace.failure)
        self.assertEqual(trace.final_state,anchor)

    def test_every_nonextruding_xy_move_occurs_retracted_at_safe_z(self):
        anchor = anchor_fixture()
        block = compose_retracted_cycle(anchor,(path_fixture(),path_fixture('second','.18')),F('3.2'),policy_fixture())
        trace = trace_linear_execution(block,initial_state=anchor)
        travels = []
        for record in trace.records:
            _, words = _words(record.raw.decode().strip())
            xy_changed = record.before.xyz_mm[:2] != record.after.xyz_mm[:2]
            if xy_changed and 'E' not in words:
                travels.append(record)
                self.assertEqual(record.before.xyz_mm[2],F('3.6'))
                self.assertEqual(record.after.xyz_mm[2],F('3.6'))
                self.assertEqual(record.before.retraction_debt_mm,F('.8'))
            if record.before.xyz_mm[2] != record.after.xyz_mm[2]:
                self.assertEqual(record.before.xyz_mm[:2],record.after.xyz_mm[:2])
                self.assertEqual(record.before.retraction_debt_mm,F('.8'))
        self.assertEqual(len(travels),3)

    def test_safe_ceiling_uses_actual_saved_z_not_just_next_layer(self):
        policy = policy_fixture()
        self.assertEqual(safe_ceiling(F(4),F('3.2'),policy),F('4.4'))
        self.assertEqual(safe_ceiling(F(3),F('3.2'),replace(policy,z_hop_mm=F('.4001'))),F('3.601'))

    def test_ceiling_exact_limit_allowed_and_overflow_never_clamped(self):
        policy = replace(policy_fixture(),printable_height_mm=F('3.6'))
        self.assertEqual(safe_ceiling(F(3),F('3.2'),policy),F('3.6'))
        with self.assertRaisesRegex(ValueError,'cannot clamp'):
            safe_ceiling(F(3),F('3.2'),replace(policy,printable_height_mm=F('3.599')))

    def test_saved_actual_z_is_restored_even_below_upper_nominal_z(self):
        anchor = replace(anchor_fixture(),xyz_mm=(F(5),F(6),F('3.0')))
        block = compose_retracted_cycle(anchor,(path_fixture(),),F('3.2'),policy_fixture())
        self.assertEqual(trace_linear_execution(block,initial_state=anchor).final_state,anchor)
        self.assertIn(b'G1 Z3.000',block)

    def test_unknown_or_unretracted_anchor_rejected(self):
        for anchor in (MachineState(),replace(anchor_fixture(),retraction_debt_mm=F(0)),
                       replace(anchor_fixture(),logical_e_mm=None),
                       replace(anchor_fixture(),flow_override_100=False),
                       replace(anchor_fixture(),relative_e=1)):
            with self.subTest(anchor=anchor),self.assertRaises(ValueError):
                compose_retracted_cycle(anchor,(path_fixture(),),F('3.2'),policy_fixture())

    def test_restore_precision_loss_rejected(self):
        anchor = replace(anchor_fixture(),xyz_mm=(F('5.0001'),F(6),F('3.2')))
        with self.assertRaisesRegex(ValueError,'representable'):
            compose_retracted_cycle(anchor,(path_fixture(),),F('3.2'),policy_fixture())

    def test_mixed_layer_empty_duplicate_paths_rejected(self):
        for paths in ((),(path_fixture(),path_fixture()),
                      (path_fixture(),replace(path_fixture('other'),floor_z_mm=F(2)))):
            with self.subTest(paths=paths),self.assertRaises(ValueError):
                compose_retracted_cycle(anchor_fixture(),paths,F('3.2'),policy_fixture())

    def test_overlap_minimum_remaining_and_next_layer_bounds(self):
        path = path_fixture()
        for invalid in (replace(path,height_mm=F('.18')),
                        replace(path,points_mm=((F(1),F(2),F('3.079')),(F(2),F(2),F('3.079')))),
                        replace(path,points_mm=((F(1),F(2),F('3.3')),(F(2),F(2),F('3.3'))))):
            with self.subTest(path=invalid),self.assertRaises(ValueError):
                compose_retracted_cycle(anchor_fixture(),(invalid,),F('3.2'),policy_fixture())
        allowed = replace(path_fixture('overlap','.12'),points_mm=((F(1),F(2),F('3.084')),(F(2),F(2),F('3.084'))))
        self.assertTrue(compose_retracted_cycle(anchor_fixture(),(allowed,),F('3.2'),policy_fixture()))

    def test_zero_hop_zero_speed_and_id_command_injection_rejected(self):
        for policy in (replace(policy_fixture(),z_hop_mm=F(0)),replace(policy_fixture(),z_speed_mm_s=F(0))):
            with self.assertRaises(ValueError):
                compose_retracted_cycle(anchor_fixture(),(path_fixture(),),F('3.2'),policy)
        with self.assertRaises(ValueError):
            compose_retracted_cycle(anchor_fixture(),(path_fixture('bad\nM112'),),F('3.2'),policy_fixture())

    def test_collapsed_quantization_and_rounded_zero_e_rejected(self):
        path = replace(path_fixture(),points_mm=((F(10),F(11),F('3.08')),(F('10.0001'),F(11),F('3.08'))))
        with self.assertRaisesRegex(ValueError,'collapsed'):
            compose_retracted_cycle(anchor_fixture(),(path,),F('3.2'),policy_fixture())
        with self.assertRaisesRegex(ValueError,'E is zero'):
            compose_retracted_cycle(replace(anchor_fixture(),retraction_debt_mm=F(1)),
                (path_fixture(),),F('3.2'),replace(policy_fixture(),e_places=0))

    def test_quantized_e_volume_rate_never_exceeds_cap(self):
        policy = policy_fixture()
        anchor = anchor_fixture()
        block = compose_retracted_cycle(anchor,(path_fixture(),),F('3.2'),policy)
        trace = trace_linear_execution(block,initial_state=anchor)
        positive_moves = 0
        for record in trace.records:
            _,words = _words(record.raw.decode().strip())
            length = math.dist(tuple(map(float,record.before.xyz_mm)),tuple(map(float,record.after.xyz_mm)))
            if length and words.get('E',0)>0:
                rate = float(words['E'])*math.pi*float(policy.filament_diameter_mm)**2/4/length*float(record.after.feed_mm_min)/60
                self.assertLessEqual(rate,float(policy.max_volume_mm3_s))
                positive_moves += 1
        self.assertEqual(positive_moves,2)

    def test_speed_caps_come_from_slice_and_zero_z_inherits_then_caps(self):
        settings = settings_fixture()
        settings.update(layer_height='0.2',travel_speed=['700'],machine_max_speed_x=['500','200'],
                        machine_max_speed_y=['500','200'],machine_max_speed_z=['30','30'])
        profile = read_sliced_profile(*fixture(settings),include_motion_caps=True)
        policy = policy_from_slice(profile,policy_fixture().bounds,xyz_places=3,e_places=5)
        self.assertEqual(policy.xy_speed_mm_s,200)
        self.assertEqual(policy.z_speed_mm_s,30)
        self.assertEqual(policy.z_hop_mm,F('.8'))
        with self.assertRaisesRegex(ValueError,'90 percent'):
            policy_from_slice(profile,CandidateBeadBounds(.08,.181,.25,.45),xyz_places=3,e_places=5)
        settings['machine_max_speed_z'] = ['0','30']
        with self.assertRaises(SourceProfileError):
            read_sliced_profile(*fixture(settings),include_motion_caps=True)

    def test_speed_vectors_must_match_exported_configuration(self):
        settings = settings_fixture()
        settings.update(machine_max_speed_x=['500','200'],machine_max_speed_y=['500','200'],
                        machine_max_speed_z=['30','30'])
        changed = dict(settings,machine_max_speed_z=['60','30'])
        with self.assertRaisesRegex(SourceProfileError,'vector mismatch'):
            read_sliced_profile(*fixture(settings,json_bytes=json.dumps(changed).encode()),include_motion_caps=True)

    def test_real_shape_transition_adapter_does_not_invent_an_entry_anchor(self):
        settings = settings_fixture()
        settings.update(printable_height='180',z_hop=['0.4'],travel_speed=['700'],machine_max_speed_x=['500','200'],
                        machine_max_speed_y=['500','200'],machine_max_speed_z=['30','30'])
        project,source = fixture(settings)
        manifest = {'source_slice_sha256':sha256(source).hexdigest(),
            'placed_project_sha256':sha256(project).hexdigest(),
            'rectangle_constraints_exact_mm':{'minimum_remaining_height':'.08',
                'maximum_physical_height':'.18','minimum_width':'.25','maximum_width':'.45'},
            'rings':[], 'candidate_segments':[],
            'section_diagnostics':[{'floor_z_exact_mm':'3','upper_z_exact_mm':'3.2'}]}
        for name,height in (('thick','.18'),('thin','.08')):
            top = float(F(3)+F(height))
            manifest['rings'].append({'id':name,'chord_count':2,'floor_z_exact_mm':'3',
                'top_z_exact_mm':str(F(3)+F(height)),'width_exact_mm':'.3','height_exact_mm':height})
            a,b = [10,11,top],[12,11,top]
            for index,(start,end) in enumerate(((a,b),(b,a)),1):
                manifest['candidate_segments'].append({'ring_id':name,'chord_index':index,
                    'start_mm':start,'end_mm':end})
        report = review_hops(project,source,json.dumps(manifest).encode())
        self.assertFalse(report['printable_authorized'])
        self.assertEqual(report['path_count'],2)
        batch = report['batches'][0]
        self.assertEqual(batch['order'],['thin','thick'])
        self.assertFalse(batch['entry_exit_anchor_verified'])
        self.assertEqual(batch['transitions'][0]['unverified_bridge_commands'],[
            'G1 Z3.600 F1800.000','G1 X10.000 Y11.000 F12000.000','G1 Z3.180 F1800.000'])
        manifest['source_slice_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError,'hashes differ'):
            review_hops(project,source,json.dumps(manifest).encode())


if __name__ == '__main__':
    unittest.main()
