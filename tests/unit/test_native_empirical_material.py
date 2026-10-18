"""Empirical native volume keeps nominal freeze and source debt independent."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tests.unit.test_gui_native_trial_copy import recipe_fixture
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.native_empirical_material import NativeEmpiricalMaterialCorrection, NativeEmpiricalPathCorrection
from tools.native_supplement_end import NativeSupplementEndPolicy
from tools.supplemental_z_hop import rounded
from adaptive_subedge.engine.empirical_material import resolve_policy
from adaptive_subedge.application.empirical_material_settings import policy_identity


def corrected_recipe(factor=F(1,2)):
    recipe=recipe_fixture(annotations=True)
    policy=resolve_policy(admission_minimum_width_mm=F(str(recipe.insertions[0].policy.bounds.min_candidate_width_mm)),
        start_percent=100*factor,end_percent=100*factor,minimum_modeled_thickness_mm=None)
    paths=tuple(NativeEmpiricalPathCorrection(p.intent.path_id,F(10),policy.maximum_angle_degrees,factor)
        for insertion in recipe.insertions for p in insertion.plan.paths)
    return replace(recipe,empirical_correction=NativeEmpiricalMaterialCorrection(policy_identity(policy),policy,paths),
        end_policy=NativeSupplementEndPolicy(retract_mm=F('1.6'),wipe_mm=F(1)))


class NativeEmpiricalTests(unittest.TestCase):
    def test_half_volume_preserves_nominal_metadata_and_exact_debt(self):
        recipe=corrected_recipe()
        copy=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        nominal=rebuild_native_trial_copy(replace(recipe,empirical_correction=None),cancelled=lambda:False)
        expected=sum((rounded(e/2,i.policy.e_places) for i in recipe.insertions for p in i.plan.paths
            for e in p.local_support_numeric_adapter.relative_e_mm),F(0))
        self.assertEqual(copy.total_added_relative_e_mm,expected)
        self.assertIn(b'G1 E0.80000 F1800.000',copy.output_bytes)
        self.assertIn(b'G1 E-0.80000 F1800.000',copy.output_bytes)
        self.assertIn(b'E-0.80000 F2250.000',copy.output_bytes)
        self.assertEqual([l for l in copy.output_bytes.splitlines() if l.startswith(b';')],
                         [l for l in nominal.output_bytes.splitlines() if l.startswith(b';')])
        recovered=copy.output_bytes
        for span in reversed(copy.insertion_spans): recovered=recovered[:span.output_start]+recovered[span.output_end:]
        self.assertEqual(recovered,recipe.source_bytes)
        self.assertNotEqual(copy.emission_policy_identity,nominal.emission_policy_identity)

    def test_unity_reproduces_bytes_but_has_distinct_policy_identity(self):
        recipe=corrected_recipe(F(1))
        a=rebuild_native_trial_copy(recipe,cancelled=lambda:False)
        b=rebuild_native_trial_copy(replace(recipe,empirical_correction=None),cancelled=lambda:False)
        self.assertEqual(a.output_bytes,b.output_bytes)
        self.assertNotEqual(a.emission_policy_identity,b.emission_policy_identity)

    def test_missing_extra_and_rounded_zero_reject(self):
        recipe=corrected_recipe()
        for paths in (recipe.empirical_correction.paths[:-1],
                      recipe.empirical_correction.paths+(NativeEmpiricalPathCorrection('extra',F(0),F(20),F(1)),)):
            with self.assertRaises(ValueError):
                rebuild_native_trial_copy(replace(recipe,empirical_correction=NativeEmpiricalMaterialCorrection(recipe.empirical_correction.policy_identity,recipe.empirical_correction.policy,paths)),cancelled=lambda:False)
        with self.assertRaisesRegex(ValueError,'collapsed'):
            rebuild_native_trial_copy(corrected_recipe(F(1,10**8)),cancelled=lambda:False)

    def test_invalid_exact_factors_reject(self):
        for factor in (F(0),F(-1),F(2),.5,True):
            with self.assertRaises(ValueError):NativeEmpiricalPathCorrection('path',F(0),F(20),factor)

    def test_policy_hash_factor_endpoint_and_end_settings_cannot_be_forged(self):
        recipe=corrected_recipe(); correction=recipe.empirical_correction
        for change in ({'policy_identity':'b'*64},
                       {'paths':(replace(correction.paths[0],factor=F(3,4)),)+correction.paths[1:]},
                       {'paths':(replace(correction.paths[0],maximum_angle_degrees=F(20)),)+correction.paths[1:]}):
            with self.assertRaises(ValueError):replace(correction,**change)
        with self.assertRaisesRegex(ValueError,'end policy mismatch'):
            rebuild_native_trial_copy(replace(recipe,end_policy=NativeSupplementEndPolicy()),cancelled=lambda:False)

    def test_numeric_and_path_count_bounds(self):
        for name in ('x'*129,'invalid path'):
            with self.assertRaises(ValueError):NativeEmpiricalPathCorrection(name,F(0),F(20),F(1))
        with self.assertRaises(ValueError):NativeEmpiricalPathCorrection('x',F(1,2**300),F(20),F(1))
        recipe=corrected_recipe();c=recipe.empirical_correction
        with self.assertRaises(ValueError):replace(c,paths=c.paths*1001)

    def test_admission_binding_rejects_different_saved_height_or_width(self):
        recipe=corrected_recipe();c=recipe.empirical_correction
        for kwargs in ({'admission_layer_height_mm':F('.3')},{'admission_minimum_width_mm':F('.3')}):
            policy=resolve_policy(start_percent=F(50),end_percent=F(50),minimum_modeled_thickness_mm=None,**kwargs)
            paths=tuple(replace(p,maximum_angle_degrees=policy.maximum_angle_degrees) for p in c.paths)
            correction=NativeEmpiricalMaterialCorrection(policy_identity(policy),policy,paths)
            with self.assertRaisesRegex(ValueError,'admission policy differs'):
                rebuild_native_trial_copy(replace(recipe,empirical_correction=correction),cancelled=lambda:False)
