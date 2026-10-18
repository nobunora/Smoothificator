"""Explicit research endpoint envelope; original admission/profile stays separate."""
from dataclasses import replace
from fractions import Fraction as F
import json
import unittest
from tests.unit.test_native_smooth_dimensions import fixture
from tests.unit.test_two_tier_intents import graph_policy
from adaptive_subedge.engine.smooth_dimensions import resolve_policy,target_dimensions_for_angle
from adaptive_subedge.application.smooth_dimension_settings import encode_policy,decode_policy,policy_identity
from tools.native_smooth_dimensions import NativeSmoothDimensionSourcePath,NativeSmoothDimensionTaper,resolve_tapered_root,emission_hop_for_taper
from tools.prepare_two_tier_intents import freeze_supported_graph
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.native_supplement_end import NativeSupplementEndPolicy


def micro_recipe(*,rise=F('.5')):
    recipe,insertion,old_policy,old_source=fixture(rise=rise)
    policy=resolve_policy(admission_minimum_width_mm=old_policy.admission_minimum_width_mm,
        minimum_height_mm=F('.01'),minimum_width_mm=F('.1'),schema_version=3,research_endpoint_envelope=True)
    source=replace(old_source,admission_hop=insertion.policy)
    emission=emission_hop_for_taper(insertion.policy,policy)
    decision=resolve_tapered_root(source,insertion.policy,policy)
    plan=freeze_supported_graph((decision.resolved_intent,),source_context_identity=source.original_intent.source_context_identity,
        policy=emission,graph_policy=graph_policy(),cancelled=lambda:False)
    return replace(recipe,insertions=(replace(insertion,plan=plan,policy=emission),),
        dimension_taper=NativeSmoothDimensionTaper(policy,'a'*64,(source,)),
        end_policy=NativeSupplementEndPolicy(retract_mm=F('1.6'),wipe_mm=F(1))),insertion,decision


class ResearchMicroDimensionsTests(unittest.TestCase):
    def test_v3_explicit_endpoint_and_legacy_relationships(self):
        for kwargs in ({'schema_version':2,'research_endpoint_envelope':False},
                       {'schema_version':3,'research_endpoint_envelope':False},
                       {'schema_version':2,'research_endpoint_envelope':True}):
            with self.assertRaises(ValueError):resolve_policy(minimum_height_mm=F('.01'),minimum_width_mm=F('.1'),**kwargs)
        p=resolve_policy(minimum_height_mm=F('.01'),minimum_width_mm=F('.1'),schema_version=3,research_endpoint_envelope=True)
        target=target_dimensions_for_angle(p.maximum_angle_degrees,F('.4'),F('.18'),p)
        self.assertEqual((target.target_height_mm,target.target_width_mm),(F('.01'),F('.1')))
        self.assertEqual(p.admission_minimum_width_mm,F('.21'))
        for kwargs in ({'minimum_height_mm':F('.009')},{'minimum_width_mm':F('.099')}):
            with self.assertRaises(ValueError):resolve_policy(schema_version=3,research_endpoint_envelope=True,**kwargs)

    def test_v1_v2_canonical_bytes_and_safe_defaults_unchanged(self):
        safe=resolve_policy()
        self.assertEqual((safe.schema_version,safe.minimum_height_mm,safe.minimum_width_mm),(2,F('.08'),F('.21')))
        self.assertEqual(policy_identity(safe),'ef495b4dcea8fdbb3d92488c93996e9f5a251bbea2b51315256c884698234ab2')
        legacy=replace(safe,schema_version=1,maximum_extra_width_ticks=0)
        self.assertEqual(policy_identity(legacy),'9a975ddbfc72cbd62ce2b56f23a288a48eef6a59aaac1e3414cde1472d3484bb')
        for p in (safe,legacy):self.assertEqual(encode_policy(decode_policy(encode_policy(p))),encode_policy(p))

    def test_v3_codec_flag_strict_and_roundtrip(self):
        p=micro_recipe()[0].dimension_taper.policy;content=encode_policy(p)
        self.assertEqual(decode_policy(content),p)
        for flag in (False,1,'true'):
            document=json.loads(content);document['settings']['research_endpoint_envelope']=flag
            with self.assertRaises(ValueError):decode_policy(json.dumps(document).encode())
        document=json.loads(content);document['schema']='smoothificator-geometric-dimension-taper-v2'
        with self.assertRaises(ValueError):decode_policy(json.dumps(document).encode())

    def test_exact_bounds_only_adapter_and_new_numeric_freeze(self):
        recipe,old,decision=micro_recipe();emitted=recipe.insertions[0].policy
        self.assertEqual(replace(emitted,bounds=old.policy.bounds),old.policy)
        self.assertEqual(replace(emitted.bounds,min_candidate_height_mm=old.policy.bounds.min_candidate_height_mm,
            min_candidate_width_mm=old.policy.bounds.min_candidate_width_mm),old.policy.bounds)
        self.assertEqual((F(str(emitted.bounds.min_candidate_height_mm)),F(str(emitted.bounds.min_candidate_width_mm))),(F('.01'),F('.1')))
        intent=decision.resolved_intent
        self.assertLess(intent.physical_height_mm,F('.08'))
        self.assertLess(intent.width_mm,F('.21'))
        self.assertTrue(all(z-intent.physical_height_mm==intent.support_plane_z_mm for x,y,z in intent.points_mm))
        self.assertTrue(all(w>=.1 for w in recipe.insertions[0].plan.paths[0].local_support_numeric_adapter.physical_width_mm))

    def test_native_full_e_source_debt_and_state_restore(self):
        recipe,old,decision=micro_recipe();copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        self.assertEqual(copy.total_added_relative_e_mm,sum(recipe.insertions[0].plan.paths[0].local_support_numeric_adapter.relative_e_mm,F(0)))
        span=copy.insertion_spans[0]
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],recipe.source_bytes)
        self.assertIn(b'E-0.80000 F2250.000',copy.output_bytes)

    def test_native_independent_adapter_reconstruction_and_saved_profile_guard(self):
        recipe,old,decision=micro_recipe();insertion=recipe.insertions[0];source=recipe.dimension_taper.paths[0]
        for hop in (replace(insertion.policy,e_places=4),replace(insertion.policy,print_flow_ratio=insertion.policy.print_flow_ratio+F('.1')),
                    replace(insertion.policy,bounds=replace(insertion.policy.bounds,min_candidate_width_mm=.09))):
            with self.assertRaises(ValueError):rebuild_native_trial_copy(replace(recipe,insertions=(replace(insertion,policy=hop),)),cancelled=lambda:False)
        mutated=replace(source,admission_hop=replace(old.policy,filament_flow_ratio=old.policy.filament_flow_ratio+F('.1')))
        with self.assertRaises(ValueError):rebuild_native_trial_copy(replace(recipe,dimension_taper=replace(recipe.dimension_taper,paths=(mutated,))),cancelled=lambda:False)
        with self.assertRaises(ValueError):replace(recipe.dimension_taper,paths=(replace(source,admission_hop=None),))

    def test_v3_plateau_original_dimensions_and_ordinary_e_exact(self):
        recipe,old,decision=micro_recipe(rise=F('.1'))
        self.assertEqual(decision.resolved_intent,recipe.dimension_taper.paths[0].original_intent)
        ordinary=freeze_supported_graph((decision.resolved_intent,),source_context_identity=decision.resolved_intent.source_context_identity,
            policy=old.policy,graph_policy=graph_policy(),cancelled=lambda:False)
        self.assertEqual(ordinary.paths[0].local_support_numeric_adapter.relative_e_mm,
                         recipe.insertions[0].plan.paths[0].local_support_numeric_adapter.relative_e_mm)

    def test_legacy_cannot_lower_numeric_height_without_explicit_envelope(self):
        recipe,old,policy,source=fixture(rise=F('.5'))
        legacy=replace(policy,minimum_height_mm=F('.01'))
        with self.assertRaisesRegex(ValueError,'minima differ'):
            resolve_tapered_root(source,old.policy,legacy)

    def test_original_intent_must_pass_original_admission_before_research_mapping(self):
        recipe,old,decision=micro_recipe();source=recipe.dimension_taper.paths[0];policy=recipe.dimension_taper.policy
        original=source.original_intent
        for changed in (replace(original,width_mm=F('.15')),
                        replace(original,physical_height_mm=F('.02'),remaining_height_mm=F('.02'),
                            points_mm=tuple((x,y,original.support_plane_z_mm+F('.02')) for x,y,z in original.points_mm))):
            with self.assertRaises(ValueError):resolve_tapered_root(replace(source,original_intent=changed),old.policy,policy)
