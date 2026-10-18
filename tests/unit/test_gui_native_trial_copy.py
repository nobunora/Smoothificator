"""Native relative-counter equivalence, source binding and scoped acceleration."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tests.unit.test_gui_native_trial_trace import native_fixture,LIMITS,interpret
from tests.unit.test_two_tier_intents import intent,graph_policy
from tests.unit.test_supplemental_z_hop import policy_fixture
from tests.unit.test_conditional_preview_annotations import PRIOR,ANNOTATIONS,TAGS
from tools.supplemental_z_hop import policy_from_slice
from tools.gui_native_trial_trace import native_profile_caps
from tools.prepare_two_tier_intents import freeze_supported_graph
from tools.gui_native_trial_copy import (
    NativeTrialCopyPolicy,NativeTrialInsertion,NativeTrialCopyRecipe,rebuild_native_trial_copy,
)


COPY_POLICY=NativeTrialCopyPolicy(10,30,2000000,100000,True)


def recipe_fixture(*, inherited=6000,branch=True,annotations=False,reset_after=b''):
    branch_body=b'M622.1 S1\nM1002 judge_flag timelapse_record_flag\nM622 J1\nG92 E0\nM623\n' if branch else b''
    body=(PRIOR+branch_body+b'; FEATURE: Outer wall\nM624 AQAAAAAAAAA=\n'+f'M204 S{inherited}\n'.encode()+
        b'G1 X1 Y2 Z3 F6000\nG1 E.8 F1800\nG1 X2 Y2 E.1 F6000\nG1 E-.8 F1800\n'+reset_after+
        b'M625\nM624 AQAAAAAAAAA=\nG1 X1 Y2 Z3.2 F6000\nG1 E.8 F1800\nG1 X2 Y2 E.1 F6000\nG1 E-.8 F1800\nM625\n')
    inputs=native_fixture(body); trace=interpret(inputs)
    anchor_event=next(e for e in trace.events if e.relative_e_mm==F('-.8'))
    policy=policy_from_slice(native_profile_caps(inputs[0],inputs[1],inputs[4],LIMITS)[0],
        policy_fixture().bounds,xyz_places=3,e_places=5)
    paths=(intent('lower'),intent('upper',parent='lower',support=F('3.1'),height=F('.08'),width=F('.3')))
    paths=tuple(replace(p,source_context_identity=trace.context_identity) for p in paths)
    plan=freeze_supported_graph(paths,source_context_identity=trace.context_identity,policy=policy,
        graph_policy=graph_policy(),cancelled=lambda:False)
    insertion=NativeTrialInsertion(anchor_event.byte_offset+len(anchor_event.raw),plan,policy)
    return NativeTrialCopyRecipe(*inputs[:4],(insertion,),LIMITS,COPY_POLICY,inputs[4],ANNOTATIONS if annotations else None)


class NativeTrialCopyTests(unittest.TestCase):
    def test_explicit_fresh_posthop_witness_restores_raised_anchor(self):
        recipe=recipe_fixture(reset_after=b'G17\nG3 Z3.6 I1 J0 P1 F6000\n')
        trace=interpret((recipe.source_bytes,recipe.project_bytes,recipe.producer_bytes,recipe.context,recipe.geometry_project_bytes))
        hop=next(e for e in trace.events if e.command=='G3')
        original=recipe.insertions[0]
        raised=replace(original,byte_offset=hop.byte_offset+len(hop.raw),original_floor_anchor_offset=original.byte_offset)
        with self.assertRaises(ValueError):rebuild_native_trial_copy(replace(recipe,insertions=(replace(raised,original_floor_anchor_offset=None),)),cancelled=lambda:False)
        copy=rebuild_native_trial_copy(replace(recipe,insertions=(raised,)),cancelled=lambda:False)
        span=copy.insertion_spans[0];block=copy.output_bytes[span.output_start:span.output_end]
        self.assertIn(b'G1 Z3.600',block)
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],recipe.source_bytes)
        for offset in (True,raised.byte_offset,original.byte_offset+1,original.byte_offset-1):
            with self.assertRaises(ValueError):rebuild_native_trial_copy(replace(recipe,insertions=(replace(raised,original_floor_anchor_offset=offset),)),cancelled=lambda:False)

    def test_posthop_rejects_changed_debt_modes_opaque_and_wrong_height(self):
        for commands in (b'G1 E.00001 F1800\nG17\nG3 Z3.6 I1 J0 P1 F6000\n',
                         b'G18\nG17\nG3 Z3.6 I1 J0 P1 F6000\n',
                         b'M106 S255\nG17\nG3 Z3.6 I1 J0 P1 F6000\n',
                         b'G17\nG3 Z3.5 I1 J0 P1 F6000\n',
                         b'G17\nG3 Z3.6 I1 J0 P1 F6000\nG1 F6000\n'):
            with self.subTest(commands=commands):
                if commands.startswith(b'G18'):
                    with self.assertRaises(ValueError):recipe_fixture(reset_after=commands)
                    continue
                recipe=recipe_fixture(reset_after=commands)
                trace=interpret((recipe.source_bytes,recipe.project_bytes,recipe.producer_bytes,recipe.context,recipe.geometry_project_bytes))
                hop=next(e for e in trace.events if e.command=='G3')
                offset=hop.byte_offset+len(hop.raw)
                if commands.endswith(b'G1 F6000\n'):offset+=len(b'G1 F6000\n')
                original=recipe.insertions[0]
                raised=replace(original,byte_offset=offset,original_floor_anchor_offset=original.byte_offset)
                with self.assertRaises(ValueError):rebuild_native_trial_copy(replace(recipe,insertions=(raised,)),cancelled=lambda:False)

    def test_unknown_logical_counter_no_g92_exact_physical_restore_and_profile_wrapper(self):
        recipe=recipe_fixture(); copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        span=copy.insertion_spans[0]; block=copy.output_bytes[span.output_start:span.output_end]
        self.assertNotIn(b'G92',block)
        self.assertTrue(block.startswith(b'M204 S5000.000\n'))
        self.assertTrue(block.endswith(b'M204 S6000.000\n'))
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],recipe.source_bytes)
        self.assertEqual(copy.total_added_relative_e_mm,sum((e for p in recipe.insertions[0].plan.paths
            for e in p.local_support_numeric_adapter.relative_e_mm),F(0)))
        self.assertLess(block.index(b'PATH lower'),block.index(b'PATH upper'))
        self.assertFalse(copy.physical_authority)
        self.assertFalse(copy.whole_original_job_complete)
        self.assertEqual(len(copy.added_path_bounds_mm),2)
        self.assertEqual(copy.body_end_counter_translation_candidates_mm,(copy.total_added_relative_e_mm,))

    def test_eligible_acceleration_needs_no_wrapper_and_annotations_only_change_comments(self):
        recipe=recipe_fixture(inherited=2000)
        plain=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        annotated=rebuild_native_trial_copy(replace(recipe,annotation_policy=ANNOTATIONS),cancelled=lambda:False)
        a,b=plain.insertion_spans[0],annotated.insertion_spans[0]
        block=annotated.output_bytes[b.output_start:b.output_end]
        self.assertNotIn(b'M204',block)
        self.assertEqual(b''.join(l for l in block.splitlines(keepends=True) if not l.startswith(TAGS)),plain.output_bytes[a.output_start:a.output_end])
        self.assertIn(b'; LAYER_HEIGHT: 0.08',block)

    def test_executed_original_reset_clears_translation_and_skipped_branch_retains_it(self):
        recipe=recipe_fixture(reset_after=b'G92 E0\n')
        copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        self.assertEqual(copy.body_end_counter_translation_candidates_mm,(F(0),))
        recipe=recipe_fixture(reset_after=b'M622.1 S1\nM1002 judge_flag timelapse_record_flag\nM622 J1\nG92 E0\nM623\n')
        copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        self.assertEqual(copy.body_end_counter_translation_candidates_mm,(F(0),copy.total_added_relative_e_mm))

    def test_stale_policy_plan_profile_caps_unknown_jerk_and_absolute_e_reject(self):
        recipe=recipe_fixture()
        with self.assertRaises(ValueError):
            rebuild_native_trial_copy(replace(recipe,copy_policy=replace(COPY_POLICY,allow_saved_acceleration_wrapper=False)),cancelled=lambda:False)
        insertion=recipe.insertions[0]
        for policy in (replace(insertion.policy,z_hop_mm=F('.001')),replace(insertion.policy,filament_diameter_mm=F('2.85')),
                       replace(insertion.policy,candidate_speed_mm_s=F(101))):
            with self.assertRaises(ValueError):
                rebuild_native_trial_copy(replace(recipe,insertions=(replace(insertion,policy=policy),)),cancelled=lambda:False)
        for context in (replace(recipe.context,entry=replace(recipe.context.entry,classic_jerk_xy_mm_s=None)),
                        replace(recipe.context,source_sha256='f'*64)):
            with self.assertRaises(ValueError): rebuild_native_trial_copy(replace(recipe,context=context),cancelled=lambda:False)
        with self.assertRaises(ValueError): rebuild_native_trial_copy(replace(recipe,copy_policy=replace(COPY_POLICY,max_paths=1)),cancelled=lambda:False)
        with self.assertRaises(ValueError): rebuild_native_trial_copy(recipe,cancelled=lambda:True)

    def test_stale_frozen_geometry_rejected_and_source_floor_wall_minimum_enforced(self):
        recipe=recipe_fixture(); insertion=recipe.insertions[0]
        plan=replace(insertion.plan,execution_order=('upper','lower'))
        with self.assertRaises(ValueError):
            rebuild_native_trial_copy(replace(recipe,insertions=(replace(insertion,plan=plan),)),cancelled=lambda:False)
        bad=replace(recipe,copy_policy=replace(COPY_POLICY,max_output_bytes=len(recipe.source_bytes)))
        with self.assertRaises(ValueError): rebuild_native_trial_copy(bad,cancelled=lambda:False)

    def test_anchor_before_stationary_or_vertical_positive_deposition_rejected(self):
        for commands in (b'G1 E1.0 F1800\nG1 E-.8 F1800\n',
                         b'G1 Z3.1 E1.0 F1800\nG1 E-.8 F1800\n'):
            recipe=recipe_fixture(reset_after=commands)
            trace=interpret((recipe.source_bytes,recipe.project_bytes,recipe.producer_bytes,recipe.context,recipe.geometry_project_bytes))
            self.assertTrue(any(e.deposited_filament_mm==F('.2') for e in trace.events))
            with self.assertRaisesRegex(ValueError,'all deposition'):
                rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        recipe=recipe_fixture(reset_after=b'M622.1 S1\nM1002 judge_flag timelapse_record_flag\nM622 J1\nG1 E-.1 F1800\nM623\n')
        with self.assertRaisesRegex(ValueError,'unknown future deposited material'):
            rebuild_native_trial_copy(recipe,cancelled=lambda:False)


if __name__=='__main__': unittest.main()
