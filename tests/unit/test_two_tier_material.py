"""Intended local slabs do not exempt unrelated intersecting candidates."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tests.unit.test_two_tier_intents import intent,freeze
from tests.unit.test_supplemental_z_hop import policy_fixture
from tools.audit_nominal_bead_overlap import BeadOverlapPolicy
from tools.audit_two_tier_material import TwoTierMaterialPolicy,audit_two_tier_material


POLICY=TwoTierMaterialPolicy(100,10000,BeadOverlapPolicy(12,10000,4096,128))


class TwoTierMaterialTests(unittest.TestCase):
    def test_actual_parent_overlap_is_confined_to_exact_declared_slab(self):
        lower=intent('lower',height=F('.12'),remaining=F('.084'))
        upper=intent('upper',parent='lower',support=F('3.084'),height=F('.12'),remaining=F('.084'),width=F('.3'))
        plan=freeze((lower,upper))
        report=audit_two_tier_material(plan,policy_fixture(),policy=POLICY,cancelled=lambda:False)
        self.assertTrue(report.all_candidate_pairs_accounted)
        proof=report.pairs[0]
        self.assertEqual(proof.state,'declared-immediate-support-slab')
        self.assertEqual((proof.intended_slab.bottom_z_mm,proof.intended_slab.top_z_mm),(F('3.048'),F('3.084')))
        self.assertEqual(proof.intended_slab.child_height_fraction,F('.3'))
        self.assertFalse(report.physical_authority)

    def test_unrelated_intersection_remains_failure_and_never_inherits_parent_permission(self):
        first=intent('first')
        second=replace(intent('second'),points_mm=tuple((x,y+F('.1'),z) for x,y,z in first.points_mm))
        report=audit_two_tier_material(freeze((first,second)),policy_fixture(),policy=POLICY,cancelled=lambda:False)
        self.assertEqual(report.state,'failed')
        self.assertFalse(report.all_candidate_pairs_accounted)
        self.assertIsNone(report.pairs[0].intended_slab)
        self.assertEqual(report.pairs[0].unrelated_pair_audit.state,'overlap-proven')

    def test_unrelated_separation_pair_budget_and_forged_slab_rebuild(self):
        first=intent('first')
        second=replace(intent('second'),points_mm=tuple((x,y+F(1),z) for x,y,z in first.points_mm))
        third=replace(intent('third'),points_mm=tuple((x,y+F(2),z) for x,y,z in first.points_mm))
        plan=freeze((first,second,third))
        report=audit_two_tier_material(plan,policy_fixture(),policy=POLICY,cancelled=lambda:False)
        self.assertTrue(report.all_candidate_pairs_accounted)
        limited=audit_two_tier_material(plan,policy_fixture(),policy=replace(POLICY,max_pairs=1),cancelled=lambda:False)
        self.assertEqual(limited.state,'incomplete')
        self.assertFalse(limited.all_candidate_pairs_accounted)
        with self.assertRaises(ValueError):
            audit_two_tier_material(replace(plan,execution_order=tuple(reversed(plan.execution_order))),policy_fixture(),
                policy=POLICY,cancelled=lambda:False)


if __name__=='__main__':
    unittest.main()
