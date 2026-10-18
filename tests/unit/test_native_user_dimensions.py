"""Normal configurable endpoint/formula policy drives native full-volume geometry."""
from dataclasses import replace
from fractions import Fraction as F
import unittest
from tests.unit.test_research_micro_dimensions import micro_recipe
from tests.unit.test_two_tier_intents import graph_policy
from adaptive_subedge.engine.smooth_dimensions import resolve_user_policy
from tools.native_smooth_dimensions import NativeSmoothDimensionTaper,resolve_tapered_root,emission_hop_for_taper,uses_distinct_emission_bounds
from tools.prepare_two_tier_intents import freeze_supported_graph
from tools.gui_native_trial_copy import rebuild_native_trial_copy


def user_recipe(expression='1-(6*t**5-15*t**4+10*t**3)'):
    old_recipe,original,decision=micro_recipe()
    source=old_recipe.dimension_taper.paths[0]
    policy=resolve_user_policy(admission_minimum_width_mm=F(str(original.policy.bounds.min_candidate_width_mm)),
        retention_expression=expression,schema_version=4)
    decision=resolve_tapered_root(source,original.policy,policy)
    emission=emission_hop_for_taper(original.policy,policy)
    plan=freeze_supported_graph((decision.resolved_intent,),source_context_identity=source.original_intent.source_context_identity,
        policy=emission,graph_policy=graph_policy(),cancelled=lambda:False)
    return replace(old_recipe,insertions=(replace(original,policy=emission,plan=plan),),
        dimension_taper=NativeSmoothDimensionTaper(policy,'a'*64,(source,)))


class NativeUserDimensionTests(unittest.TestCase):
    def test_normal_v4_requires_original_hop_without_experimental_flag(self):
        recipe=user_recipe();p=recipe.dimension_taper.policy
        self.assertEqual(p.schema_version,4)
        self.assertFalse(p.research_endpoint_envelope)
        self.assertTrue(uses_distinct_emission_bounds(p))
        copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        self.assertEqual(copy.total_added_relative_e_mm,sum(recipe.insertions[0].plan.paths[0].local_support_numeric_adapter.relative_e_mm,F(0)))
        with self.assertRaises(ValueError):replace(recipe.dimension_taper,paths=(replace(recipe.dimension_taper.paths[0],admission_hop=None),))

    def test_editing_formula_changes_actual_dimensions_e_and_identity(self):
        default=user_recipe();linear=user_recipe('1-t')
        a=rebuild_native_trial_copy(default,cancelled=lambda:False);b=rebuild_native_trial_copy(linear,cancelled=lambda:False)
        self.assertNotEqual(default.insertions[0].plan.paths[0].intent.physical_height_mm,linear.insertions[0].plan.paths[0].intent.physical_height_mm)
        self.assertNotEqual(a.total_added_relative_e_mm,b.total_added_relative_e_mm)
        self.assertNotEqual(a.emission_policy_identity,b.emission_policy_identity)
        for recipe,copy in ((default,a),(linear,b)):
            span=copy.insertion_spans[0]
            self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],recipe.source_bytes)

    def test_formula_change_cannot_reuse_previously_frozen_intents(self):
        recipe=user_recipe();changed=replace(recipe.dimension_taper,policy=replace(recipe.dimension_taper.policy,retention_expression='1-t'))
        with self.assertRaisesRegex(ValueError,'authoritative mapping'):
            rebuild_native_trial_copy(replace(recipe,dimension_taper=changed),cancelled=lambda:False)
