"""Final-E admission, parent cascade and native no-bypass regressions."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tests.unit.test_gui_native_trial_copy import recipe_fixture
from adaptive_subedge.engine.empirical_material import resolve_policy,factor_for_angle
from adaptive_subedge.application.empirical_material_settings import policy_identity
from tools.native_empirical_material import NativeEmpiricalMaterialCorrection,NativeEmpiricalPathCorrection,evaluate_empirical_segments,apply_empirical_material_correction
from tools.filter_empirical_intents import filter_empirical_intents
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.native_supplement_end import NativeSupplementEndPolicy


def correction_for(recipe,*,threshold=F('.08'),angles=None):
    hop=recipe.insertions[0].policy
    policy=resolve_policy(admission_minimum_width_mm=F(str(hop.bounds.min_candidate_width_mm)),
        minimum_modeled_thickness_mm=threshold)
    records=[]
    for path in recipe.insertions[0].plan.paths:
        angle=policy.maximum_angle_degrees if angles is None else angles[path.intent.path_id]
        factor=factor_for_angle(angle,policy)
        records.append(NativeEmpiricalPathCorrection(path.intent.path_id,angle,factor.maximum_angle_degrees,factor.factor))
    return NativeEmpiricalMaterialCorrection(policy_identity(policy),policy,tuple(records))


class EmpiricalIntentFilterTests(unittest.TestCase):
    def test_all_below_minimum_return_no_survivors(self):
        recipe=recipe_fixture(); insertion=recipe.insertions[0]
        survivors,decisions=filter_empirical_intents(tuple(p.intent for p in insertion.plan.paths),
            hop=insertion.policy,correction=correction_for(recipe))
        self.assertEqual(survivors,())
        self.assertTrue(all(not d.retained and d.reason=='modeled-minimum-not-proven' for d in decisions))

    def test_parent_removal_cascades_even_when_child_own_area_passes(self):
        recipe=recipe_fixture();insertion=recipe.insertions[0]
        parent,child=tuple(p.intent for p in insertion.plan.paths)
        # Test graph filtering independently of final top/next-plane graph freeze.
        child=replace(child,physical_height_mm=F('.1'),remaining_height_mm=F('.1'),
            points_mm=tuple((x,y,child.support_plane_z_mm+F('.1')) for x,y,z in child.points_mm))
        c=correction_for(recipe,angles={parent.path_id:resolve_policy().maximum_angle_degrees,child.path_id:F(0)})
        # Recipe admission width differs from default; use the same exact max angle.
        c=correction_for(recipe,angles={parent.path_id:c.policy.maximum_angle_degrees,child.path_id:F(0)})
        survivors,decisions=filter_empirical_intents((parent,child),hop=insertion.policy,correction=c)
        self.assertEqual(survivors,())
        self.assertEqual(decisions[1].reason,'parent-removed')
        self.assertTrue(all(p.accepted for p in decisions[1].segment_proofs))

    def test_survivor_order_and_legacy_explicit_no_filter(self):
        recipe=recipe_fixture();insertion=recipe.insertions[0]
        c=correction_for(recipe,threshold=None)
        intents=tuple(p.intent for p in insertion.plan.paths)
        survivors,decisions=filter_empirical_intents(intents,hop=insertion.policy,correction=c)
        self.assertEqual(survivors,intents)
        self.assertTrue(all(d.retained for d in decisions))

    def test_native_adapter_rejects_unfiltered_under_minimum_and_threshold_mismatch(self):
        recipe=recipe_fixture()
        for threshold,reason in ((F('.08'),'minimum thickness not proven'),(F('.09'),'differs from nominal plan bound')):
            with self.assertRaisesRegex(ValueError,reason):
                rebuild_native_trial_copy(replace(recipe,empirical_correction=correction_for(recipe,threshold=threshold),
                    end_policy=NativeSupplementEndPolicy(retract_mm=F('1.6'),wipe_mm=F(1))),cancelled=lambda:False)

    def test_missing_parent_and_nonexact_length_fail_closed(self):
        recipe=recipe_fixture();insertion=recipe.insertions[0];paths=insertion.plan.paths
        with self.assertRaisesRegex(ValueError,'parent association'):
            filter_empirical_intents((paths[1].intent,),hop=insertion.policy,correction=correction_for(recipe))
        frozen=paths[0].local_support_numeric_adapter
        end=frozen.path.points_mm[-1]; diagonal=replace(frozen,path=replace(frozen.path,
            points_mm=(frozen.path.points_mm[0],(end[0],end[1]+F(1),end[2]))))
        c=correction_for(recipe)
        with self.assertRaisesRegex(ValueError,'axis-aligned'):
            evaluate_empirical_segments(diagonal,c.for_path(frozen.path.path_id),insertion.policy,c.policy)

    def test_direct_adapter_cannot_prove_and_emit_on_different_e_lattices(self):
        recipe=recipe_fixture();insertion=recipe.insertions[0];frozen=insertion.plan.paths[0].local_support_numeric_adapter
        c=correction_for(recipe)
        with self.assertRaisesRegex(ValueError,'precision differ'):
            apply_empirical_material_correction(b'',frozen,c.for_path(frozen.path.path_id),2,
                hop=insertion.policy,material_policy=c.policy)

    def test_rounded_zero_is_explicit_removal_not_builder_failure(self):
        recipe=recipe_fixture();insertion=recipe.insertions[0]
        policy=resolve_policy(admission_minimum_width_mm=F(str(insertion.policy.bounds.min_candidate_width_mm)),
            start_percent=F('.00000001'),end_percent=F('.00000001'))
        factor=factor_for_angle(F(0),policy)
        records=tuple(NativeEmpiricalPathCorrection(p.intent.path_id,F(0),factor.maximum_angle_degrees,factor.factor) for p in insertion.plan.paths)
        c=NativeEmpiricalMaterialCorrection(policy_identity(policy),policy,records)
        survivors,decisions=filter_empirical_intents(tuple(p.intent for p in insertion.plan.paths),hop=insertion.policy,correction=c)
        self.assertEqual(survivors,())
        self.assertTrue(all(d.reason=='corrected-deposition-rounded-zero' for d in decisions))
