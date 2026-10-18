"""Native-only end wipe, debt restoration and role metadata regressions."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tests.unit.test_gui_native_trial_copy import recipe_fixture
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.native_supplement_end import NativeSupplementEndPolicy
from tools.gui_native_trial_copy import _validate_native_profile_policy
from tools.gui_native_trial_trace import native_profile_caps


class NativeSupplementEndTests(unittest.TestCase):
    def test_explicit_strict_saved_height_gate_preserves_profile_fields(self):
        recipe=recipe_fixture();insertion=recipe.insertions[0]
        profile=native_profile_caps(recipe.source_bytes,recipe.project_bytes,recipe.geometry_project_bytes,recipe.limits)[0]
        enabled=replace(recipe.copy_policy,allow_strict_saved_layer_height=True)
        strict=replace(insertion.policy,bounds=replace(insertion.policy.bounds,max_candidate_height_mm=.199))
        _validate_native_profile_policy(profile,strict,enabled)
        with self.assertRaises(ValueError):_validate_native_profile_policy(profile,strict,recipe.copy_policy)
        for height in (.2,.201):
            with self.assertRaises(ValueError):
                _validate_native_profile_policy(profile,replace(strict,bounds=replace(strict.bounds,max_candidate_height_mm=height)),enabled)
        with self.assertRaises(ValueError):
            _validate_native_profile_policy(profile,replace(strict,xy_speed_mm_s=strict.xy_speed_mm_s+1),enabled)

    def test_opt_in_wipe_replays_and_preserves_source_and_total_e(self):
        recipe = recipe_fixture(annotations=True)
        baseline = rebuild_native_trial_copy(recipe, cancelled=lambda: False)
        modified = rebuild_native_trial_copy(replace(recipe, end_policy=NativeSupplementEndPolicy()), cancelled=lambda: False)
        self.assertEqual(baseline.total_added_relative_e_mm, modified.total_added_relative_e_mm)
        self.assertIn(b'X19.500 Y11.000 E-0.40000 F2250.000', modified.output_bytes)
        self.assertIn(b'G1 E-0.40000 F1800.000', modified.output_bytes)
        span = modified.insertion_spans[0]
        self.assertEqual(modified.output_bytes[:span.output_start]+modified.output_bytes[span.output_end:], recipe.source_bytes)

    def test_source_debt_different_from_end_debt_is_restored_exactly(self):
        recipe = recipe_fixture()
        for debt in (F('.4'), F('1.2')):
            copy = rebuild_native_trial_copy(replace(recipe,end_policy=NativeSupplementEndPolicy(retract_mm=debt)),cancelled=lambda:False)
            adjustment = debt-F('.8')
            self.assertIn(f'G1 E{float(adjustment):.5f} F1800.000'.encode(), copy.output_bytes)
            self.assertEqual(copy.total_added_relative_e_mm, rebuild_native_trial_copy(recipe,cancelled=lambda:False).total_added_relative_e_mm)

    def test_custom_role_and_restoration(self):
        recipe = recipe_fixture(annotations=True)
        annotation = replace(recipe.annotation_policy,supplemental_feature='Custom')
        copy = rebuild_native_trial_copy(replace(recipe,annotation_policy=annotation,end_policy=NativeSupplementEndPolicy()),cancelled=lambda:False)
        span = copy.insertion_spans[0]
        block = copy.output_bytes[span.output_start:span.output_end]
        self.assertEqual(block.count(b'; FEATURE: Custom'),2)
        self.assertTrue(block.rstrip().endswith(b'; FEATURE: Outer wall\nM204 S6000.000'))

    def test_invalid_staging_and_speed_fail_closed(self):
        for fraction in (F(0),F(1),F(-1)):
            with self.assertRaises(ValueError): NativeSupplementEndPolicy(stationary_fraction=fraction)
        recipe = recipe_fixture()
        with self.assertRaisesRegex(ValueError,'profile cap'):
            rebuild_native_trial_copy(replace(recipe,end_policy=NativeSupplementEndPolicy(retract_speed_mm_s=F(10000))),cancelled=lambda:False)

    def test_clipped_reverse_wipe_and_precision_rejection(self):
        recipe = recipe_fixture()
        copy = rebuild_native_trial_copy(replace(recipe,end_policy=NativeSupplementEndPolicy(wipe_mm=F(20))),cancelled=lambda:False)
        self.assertIn(b'G1 X10.000 Y11.000 E-0.40000',copy.output_bytes)
        for policy in (NativeSupplementEndPolicy(wipe_mm=F('.0001')),
                       NativeSupplementEndPolicy(retract_mm=F('.800001'))):
            with self.assertRaisesRegex(ValueError,'exactly representable'):
                rebuild_native_trial_copy(replace(recipe,end_policy=policy),cancelled=lambda:False)
