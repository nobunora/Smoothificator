"""Bounded dimension resolution and native independent-mapping regressions."""
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch

from tests.unit.test_gui_native_trial_copy import recipe_fixture
from tests.unit.test_two_tier_intents import graph_policy
from tests.unit.test_native_empirical_material import corrected_recipe
from adaptive_subedge.engine.smooth_dimensions import resolve_policy
from tools.native_smooth_dimensions import NativeSmoothDimensionSourcePath,NativeSmoothDimensionTaper,resolve_tapered_root
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.prepare_two_tier_intents import freeze_supported_graph
from tools.conditional_nominal_body import fingerprint
from tools.native_supplement_end import NativeSupplementEndPolicy
import tools.native_smooth_dimensions as owner


def fixture(*,rise=F('.2')):
    recipe=recipe_fixture(annotations=True); insertion=recipe.insertions[0]
    root=next(p.intent for p in insertion.plan.paths if p.intent.parent_path_id is None)
    policy=resolve_policy(admission_minimum_width_mm=F(str(insertion.policy.bounds.min_candidate_width_mm)),
        minimum_width_mm=F(str(insertion.policy.bounds.min_candidate_width_mm)))
    source=NativeSmoothDimensionSourcePath(root,F(1),rise,fingerprint(insertion.plan))
    return recipe,insertion,policy,source


def native_recipe():
    recipe,insertion,policy,source=fixture(rise=F('.5'))
    decision=resolve_tapered_root(source,insertion.policy,policy)
    plan=freeze_supported_graph((decision.resolved_intent,),source_context_identity=source.original_intent.source_context_identity,
        policy=insertion.policy,graph_policy=graph_policy(),cancelled=lambda:False)
    taper=NativeSmoothDimensionTaper(policy,'a'*64,(source,))
    return replace(recipe,insertions=(replace(insertion,plan=plan),),dimension_taper=taper,
        end_policy=NativeSupplementEndPolicy(retract_mm=F('1.6'),wipe_mm=F(1)))


class NativeSmoothDimensionsTests(unittest.TestCase):
    def test_low_angle_plateau_preserves_exact_original_intent(self):
        recipe,insertion,policy,source=fixture(rise=F('.1'))
        decision=resolve_tapered_root(source,insertion.policy,policy)
        self.assertEqual(decision.targets.retention,F(1))
        self.assertEqual(decision.resolved_intent,source.original_intent)

    def test_transition_floors_height_preserves_bottom_xy_and_contains_width(self):
        recipe,insertion,policy,source=fixture(rise=F('.5'))
        decision=resolve_tapered_root(source,insertion.policy,policy);new=decision.resolved_intent;old=source.original_intent
        self.assertLess(decision.targets.retention,1)
        self.assertLessEqual(new.physical_height_mm,decision.targets.target_height_mm)
        self.assertLess(decision.targets.target_height_mm-new.physical_height_mm,policy.dimension_grid_mm)
        self.assertLessEqual(decision.targets.target_width_mm,new.width_mm)
        self.assertLessEqual(new.width_mm,old.width_mm)
        self.assertEqual(new.support_plane_z_mm,old.support_plane_z_mm)
        self.assertEqual(new.remaining_height_mm,new.physical_height_mm)
        self.assertEqual(tuple(p[:2] for p in new.points_mm),tuple(p[:2] for p in old.points_mm))
        self.assertTrue(all(p[2]-new.physical_height_mm==old.support_plane_z_mm for p in new.points_mm))

    def test_bounded_first_valid_width_search_and_unknown_error_propagation(self):
        recipe,insertion,policy,source=fixture(rise=F('.5'));real=owner.freeze_numeric_emission;attempts=[]
        def try_width(path,hop):
            attempts.append(path.width_mm)
            if len(attempts)==1:raise ValueError('nearest E implies width outside bounds')
            return real(path,hop)
        with patch.object(owner,'freeze_numeric_emission',side_effect=try_width):
            decision=resolve_tapered_root(source,insertion.policy,policy)
        self.assertEqual(decision.width_attempts_mm,tuple(attempts))
        self.assertEqual(attempts[1]-attempts[0],policy.dimension_grid_mm)
        with patch.object(owner,'freeze_numeric_emission',side_effect=ValueError('unsupported drift')):
            with self.assertRaisesRegex(ValueError,'unsupported drift'):resolve_tapered_root(source,insertion.policy,policy)
        with patch.object(owner,'freeze_numeric_emission',side_effect=ValueError('nearest E implies width outside bounds')):
            rejected=resolve_tapered_root(source,insertion.policy,replace(policy,maximum_extra_width_ticks=0))
        self.assertIsNone(rejected.resolved_intent)
        self.assertEqual(rejected.width_attempts_mm[-1],source.original_intent.width_mm)

    def test_parent_overlap_angle_and_width_budget_reject(self):
        recipe,insertion,policy,source=fixture(rise=F('.5'))
        for original in (replace(source.original_intent,parent_path_id='parent'),
                         replace(source.original_intent,remaining_height_mm=F('.09'))):
            with self.assertRaisesRegex(ValueError,'zero-overlap roots'):
                resolve_tapered_root(replace(source,original_intent=original),insertion.policy,policy)
        with self.assertRaisesRegex(ValueError,'admission maximum'):
            resolve_tapered_root(replace(source,section_rise_mm=F(100)),insertion.policy,policy)
        with self.assertRaisesRegex(ValueError,'representation budget'):
            resolve_tapered_root(source,insertion.policy,replace(policy,maximum_width_ticks=1))

    def test_native_full_stadium_e_and_state_source_restoration(self):
        recipe=native_recipe();copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        expected=sum(recipe.insertions[0].plan.paths[0].local_support_numeric_adapter.relative_e_mm,F(0))
        self.assertEqual(copy.total_added_relative_e_mm,expected)
        span=copy.insertion_spans[0]
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],recipe.source_bytes)
        self.assertIn(b'E-0.80000 F2250.000',copy.output_bytes)

    def test_native_mapping_context_coverage_profile_and_mode_binding(self):
        recipe=native_recipe();taper=recipe.dimension_taper;source=taper.paths[0]
        for mutated in (replace(source,section_rise_mm=F('.1')),
                        replace(source,original_intent=replace(source.original_intent,source_context_identity='b'*64))):
            with self.assertRaises(ValueError):
                rebuild_native_trial_copy(replace(recipe,dimension_taper=replace(taper,paths=(mutated,))),cancelled=lambda:False)
        with self.assertRaises(ValueError):
            rebuild_native_trial_copy(replace(recipe,dimension_taper=replace(taper,policy=resolve_policy(admission_layer_height_mm=F('.3'),admission_minimum_width_mm=F('.25'),minimum_width_mm=F('.25')))),cancelled=lambda:False)
        with self.assertRaisesRegex(ValueError,'cannot combine'):
            rebuild_native_trial_copy(replace(recipe,empirical_correction=corrected_recipe().empirical_correction),cancelled=lambda:False)

    def test_one_extra_width_tick_only_after_all_original_widths_fail(self):
        recipe,insertion,policy,source=fixture(rise=F('.5'));real=owner.freeze_numeric_emission
        tried=[]
        def only_extra_passes(path,hop):
            tried.append(path.width_mm)
            if path.width_mm<=source.original_intent.width_mm:raise ValueError('nearest E implies width outside bounds')
            return real(path,hop)
        with patch.object(owner,'freeze_numeric_emission',side_effect=only_extra_passes):
            decision=resolve_tapered_root(source,insertion.policy,policy)
        self.assertEqual(decision.resolved_intent.width_mm,source.original_intent.width_mm+policy.dimension_grid_mm)
        self.assertEqual(decision.width_expansion_mm,F('.001'))
        self.assertEqual(tried[-2:], [source.original_intent.width_mm,source.original_intent.width_mm+F('.001')])
        ordinary=resolve_tapered_root(source,insertion.policy,policy)
        self.assertEqual(decision.resolved_intent.physical_height_mm,ordinary.resolved_intent.physical_height_mm)
        self.assertEqual(ordinary.width_expansion_mm,F(0))
        self.assertEqual(decision.reason,'standard-numeric-freeze-passed-one-width-tick-expansion')

    def test_extra_zero_or_configured_max_prevents_expansion(self):
        recipe,insertion,policy,source=fixture(rise=F('.5'))
        for hop,chosen in ((insertion.policy,replace(policy,maximum_extra_width_ticks=0)),
                           (replace(insertion.policy,bounds=replace(insertion.policy.bounds,max_candidate_width_mm=.4)),policy)):
            with patch.object(owner,'freeze_numeric_emission',side_effect=ValueError('nearest E implies width outside bounds')):
                decision=resolve_tapered_root(source,hop,chosen)
            self.assertIsNone(decision.resolved_intent)
            self.assertLessEqual(max(decision.width_attempts_mm),source.original_intent.width_mm)
