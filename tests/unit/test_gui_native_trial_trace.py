"""Native branches/arcs retain uncertainty without changing legacy readers."""
from dataclasses import replace
from fractions import Fraction as F
from hashlib import sha256
import unittest
from unittest.mock import patch

from tests.unit.native_trial_fixture import material_fixture
from tests.unit.test_supplemental_z_hop import anchor_fixture
from tools.native_used_material_profile import read_native_used_material_profile,NativeMaterialProfileLimits
from tools.gui_native_trial_trace import (
    NativeTrialLimits, NativeTrialState, NativeTrialContext, interpret_native_trial,
    _anchor_from_native_trace,
)


LIMITS=NativeTrialLimits(1000000,1000000,1000000,10000,8,4096,100,2000000)


def native_fixture(body):
    source,project,geometry,start,end,scope=material_fixture(body,count=1,index=0)
    producer=b'pinned synthetic producer'
    opaque=tuple(sorted(set(raw.split(b';',1)[0].strip().decode('ascii') for raw in body.splitlines()
        if raw.strip().startswith((b'M106 ',b'M73 ',b'M991 ',b'M400',b'M1004 ',b'M971 ',b'G39 ',b'G39.3 ',b'G392 ')))))
    profile=read_native_used_material_profile(project,source,geometry,
        limits=NativeMaterialProfileLimits(1000000,1000000,100,2000000,10000,4096))
    context=NativeTrialContext(sha256(source).hexdigest(),sha256(project).hexdigest(),sha256(producer).hexdigest(),
        start,end,NativeTrialState(anchor_fixture(),True,F(6000),F(9),scope),
        'AQAAAAAAAAA=',('timelapse_record_flag',),opaque,('unverified-OEM-no-hidden-E-or-jerk','unverified-startup-frame'),
        sha256(geometry).hexdigest(),profile.projection_identity)
    return source,project,producer,context,geometry


def interpret(inputs,**changes):
    return interpret_native_trial(*inputs[:4],geometry_project=inputs[4],**dict(dict(limits=LIMITS,cancelled=lambda:False),**changes))


class NativeTrialTraceTests(unittest.TestCase):
    def test_branch_join_g92_does_not_change_debt_and_unconditional_fields_reconverge(self):
        body=(b'M624 AQAAAAAAAAA=\nM622.1 S1\nM1002 judge_flag timelapse_record_flag\nM622 J1\n'
              b'G92 E0\nG1 X99 F1000\nM623\nG1 X10 Y11 Z3 F6000\nM204 S5000\n')
        inputs=native_fixture(body); trace=interpret(inputs)
        join=next(e for e in trace.events if e.command=='M623')
        self.assertIsNone(join.after.machine.xyz_mm[0])
        self.assertIsNone(join.after.machine.logical_e_mm)
        self.assertEqual(join.after.machine.retraction_debt_mm,F('.8'))
        self.assertEqual(trace.final_state.machine.xyz_mm,(F(10),F(11),F(3)))
        anchor=_anchor_from_native_trace(trace,inputs[3],inputs[3].body_end_offset,
            acceleration_cap_mm_s2=F(5000),jerk_cap_mm_s=F(9))
        self.assertEqual(anchor.eligibility_issues,())
        self.assertIsNone(anchor.saved_state.machine.logical_e_mm)

    def test_opaque_motion_effects_invalidate_fields_until_actual_literal_writes(self):
        inputs=native_fixture(b'M624 AQAAAAAAAAA=\nG39 S1 X187 Y178\nG1 X10 Y11\nG1 Z3 F6000\nM204 S5000\n')
        trace=interpret(inputs)
        opaque=trace.events[1]
        self.assertEqual(opaque.after.machine.xyz_mm,(None,None,None))
        self.assertIsNone(opaque.after.acceleration_mm_s2)
        self.assertIsNone(trace.events[2].after.machine.xyz_mm[2])
        self.assertEqual(trace.final_state.machine.xyz_mm,(F(10),F(11),F(3)))
        self.assertEqual(trace.final_state.acceleration_mm_s2,F(5000))

    def test_arcs_keep_endpoint_debt_handedness_and_conservative_full_disk(self):
        inputs=native_fixture(b'G17\nG3 Z3.4 I1 J0 P1 F6000\nG2 X12 Y11 I1 J0 E1 F1200\n')
        trace=interpret(inputs)
        spiral,deposit=trace.events[1:]
        self.assertFalse(spiral.arc.clockwise)
        self.assertEqual(spiral.arc.xyz_min_mm[2],inputs[3].entry.machine.xyz_mm[2])
        self.assertEqual(spiral.arc.xyz_max_mm[2],F('3.4'))
        self.assertTrue(deposit.arc.clockwise)
        self.assertEqual(deposit.deposited_filament_mm,F('.2'))
        self.assertFalse(deposit.arc.support_available)
        self.assertEqual(deposit.after.machine.xyz_mm,(F(12),F(11),F('3.4')))
        for point in (deposit.before.machine.xyz_mm,deposit.after.machine.xyz_mm):
            self.assertTrue(all(lo<=v<=hi for lo,v,hi in zip(deposit.arc.xyz_min_mm,point,deposit.arc.xyz_max_mm)))

    def test_derived_arc_envelope_numbers_obey_declared_bit_budget(self):
        inputs=native_fixture(b'G17\nG3 I1 J1 P1 F6000\n')
        with self.assertRaisesRegex(ValueError,'bounded exact native trial number'):
            interpret(inputs,limits=replace(LIMITS,max_number_bits=14))
        arc=interpret(inputs).events[1].arc
        self.assertGreaterEqual(arc.radius_upper_mm**2,F(2))
        for number in (*arc.center_xy_mm,arc.radius_upper_mm,*arc.xyz_min_mm,*arc.xyz_max_mm,arc.turns):
            self.assertLessEqual(max(number.numerator.bit_length(),number.denominator.bit_length()),LIMITS.max_number_bits)

    def test_nested_errors_absolute_e_unknown_words_and_limits_fail_closed(self):
        for body in (b'M623\n',b'M622 J1\n',b'M622 J2\nM623\n',b'M82\n',b'G3 I1 J0 P2\n',
                     b'G1 X1 X2\n',b'G18\n',b'M1002 judge_flag other\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): interpret(native_fixture(body))
        inputs=native_fixture(b'; mixed\r'*100+b'G1 X10\n')
        with patch('tools.gui_native_trial_trace.read_native_used_material_profile') as read:
            with self.assertRaisesRegex(ValueError,'event budget'): interpret(inputs,limits=replace(LIMITS,max_events=10))
            read.assert_not_called()
        with self.assertRaises(ValueError): interpret(native_fixture(b'G1 X10\n'),cancelled=lambda:True)
        with self.assertRaises(ValueError): interpret(native_fixture(b'G1 X10\n'),limits=replace(LIMITS,max_producer_bytes=1))
        inputs=native_fixture(b'G1 X10\n')
        with self.assertRaisesRegex(ValueError,'hide state-bearing'):
            interpret((*inputs[:3],replace(inputs[3],opaque_command_texts=('G1 X10',)),inputs[4]))

    def test_anchor_requires_top_level_known_motion_caps_and_rebuilt_context(self):
        inputs=native_fixture(b'M624 AQAAAAAAAAA=\nM622.1 S1\nM1002 judge_flag timelapse_record_flag\nM622 J1\nG1 X10\nM623\n')
        trace=interpret(inputs)
        event=next(e for e in trace.events if e.command=='M622')
        active=_anchor_from_native_trace(trace,inputs[3],event.byte_offset+len(event.raw),
            acceleration_cap_mm_s2=F(5000),jerk_cap_mm_s=F(9))
        self.assertIn('active-native-branch',active.eligibility_issues)
        self.assertIn('native-acceleration-cap-exceeded-or-unknown',active.eligibility_issues)

    def test_forged_material_selection_projection_or_geometry_binding_rejected(self):
        inputs=native_fixture(b'G1 X10\n')
        profile=read_native_used_material_profile(inputs[1],inputs[0],inputs[4],
            limits=NativeMaterialProfileLimits(1000000,1000000,100,2000000,10000,4096))
        forged=replace(profile,selection=replace(profile.selection,material_index=99))
        for context in (replace(inputs[3],effective_profile_identity=forged.projection_identity),
                        replace(inputs[3],geometry_project_sha256='0'*64)):
            with self.assertRaises(ValueError):interpret((*inputs[:3],context,inputs[4]))


if __name__=='__main__': unittest.main()
