"""Contact admission precedes interval optimization and preserves finite limits."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.audit_continuous_path_contact import ChronologicalSource
from tools.plan_gui_native_trial import NativeTrialStep,NativeTrialPlannerPolicy,plan_native_trial_step
from tests.unit.test_two_tier_intents import graph_policy
from tests.unit.test_two_tier_material import POLICY as MATERIAL
from tests.unit.test_supplemental_z_hop import policy_fixture


def step(base=F('.55')):
    return NativeTrialStep('trial','0'*64,F(3),F('3.2'),F(0),base,(F(1),F(9)),10)


def family(**changes):
    return replace(NativeTrialPlannerPolicy((F('.3'),),(F('.12'),F('.14')),(F('.3'),),(F('.001'),),
        F(30),1,10000,1000,1000,4096,graph_policy(),MATERIAL),**changes)


def source(y=F('.12'),width=F('.4')):
    return (ChronologicalSource(ExactNominalTopSegment('actual-source',(F(0),y,F(3)),(F(10),y,F(3)),width,F('.2'),'structural'),0),)


def plan(**changes):
    kwargs=dict(step=step(),prior_sources=source(),emission_policy=policy_fixture(),policy=family(),cancelled=lambda:False)
    kwargs.update(changes)
    return plan_native_trial_step(**kwargs)


class NativeTrialPlannerTests(unittest.TestCase):
    def test_opt_in_certified_strip_preserves_selected_numeric_plan(self):
        from tools.native_certified_contact import NativeStripContactPolicy
        strip=NativeStripContactPolicy(100,10,100,100,10000,4096,128,F(1,10**12))
        previous=plan()
        current=plan(policy=family(certified_strip_contact=strip))
        self.assertEqual(current.state,'complete')
        self.assertEqual(current.plan,previous.plan)
        self.assertEqual(current.family_error_area_mm2,previous.family_error_area_mm2)

    def test_alternate_contact_height_admitted_before_selection_not_trimmed_after(self):
        report=plan()
        self.assertTrue(report.finite_family_complete)
        self.assertEqual(report.state,'complete')
        self.assertIsNotNone(report.plan)
        self.assertEqual(report.selected_blocks[0].root_intent.physical_height_mm,F('.14'))
        self.assertGreater(dict(report.rejection_counts).get('root-contact-not-proven',0),0)
        self.assertLessEqual(report.family_error_area_mm2,report.floor_comparator_error_area_mm2)
        self.assertEqual(report.plan.paths[0].intent.remaining_height_mm,F('.098'))

    def test_actual_width_intervals_prevent_unrelated_lane_overlap(self):
        report=plan(step=step(F('.8')),prior_sources=source(F('.45'),F(2)),
            policy=family(centers_relative_mm=(F('.3'),F('.599')),physical_heights_mm=(F('.12'),)))
        self.assertTrue(report.finite_family_complete)
        for a,b in zip(report.selected_blocks,report.selected_blocks[1:]):
            self.assertLessEqual(a.section.lower.right_mm,b.section.lower.left_mm)
        self.assertLessEqual(len(report.selected_blocks),1)

    def test_selected_upper_has_only_completed_actual_parent_support(self):
        report=plan(prior_sources=source(F('.4'),F(2)),
            policy=family(centers_relative_mm=(F('.42'),),physical_heights_mm=(F('.12'),)))
        self.assertEqual(report.state,'complete')
        self.assertEqual(len(report.plan.paths),2)
        self.assertEqual(len(report.plan.immediate_support_slabs),1)
        self.assertTrue(report.plan.immediate_support_slabs[0].centerline_contact.nominal_centerline_contact_proven)
        self.assertEqual(report.plan.immediate_support_slabs[0].child_height_fraction,F('.3'))
        self.assertLessEqual(report.contact_queries,family().max_contact_queries)

    def test_no_support_is_explicit_finite_family_result_not_success(self):
        report=plan(prior_sources=())
        self.assertTrue(report.finite_family_complete)
        self.assertEqual(report.state,'no-selection')
        self.assertIsNone(report.plan)
        self.assertFalse(report.physical_authority)

    def test_budget_cancel_and_unknown_contact_never_claim_complete(self):
        for changes in (dict(policy=family(max_candidates=1)),dict(policy=family(max_events=2)),
                        dict(cancelled=lambda:True),dict(policy=family(max_contact_queries=1))):
            with self.subTest(changes=changes):
                report=plan(**changes)
                self.assertEqual(report.state,'incomplete')
                self.assertFalse(report.finite_family_complete)
                self.assertIsNone(report.plan)
        with self.assertRaises(ValueError): plan(cancelled=lambda:1)

    def test_fixed_overlap_format_grid_and_short_flat_steps(self):
        exact=plan(prior_sources=source(F('.3'),F(2)),policy=family(physical_heights_mm=(F('.13'),)))
        self.assertEqual(exact.state,'complete')
        self.assertEqual(exact.plan.paths[0].intent.remaining_height_mm,F('.091'))
        report=plan(policy=family(physical_heights_mm=(F('.131'),)))
        self.assertEqual(report.state,'no-selection')
        self.assertGreater(dict(report.rejection_counts).get('fixed-overlap-not-exact-on-format-grid',0),0)
        for base,reason in ((F(0),'flat-source-step'),(F('.35'),'strict-short-base')):
            report=plan(step=step(base))
            self.assertEqual(report.reason,reason)
            self.assertTrue(report.finite_family_complete)

    def test_strict_prior_sources_and_malformed_family_reject(self):
        with self.assertRaises(ValueError): plan(prior_sources=(replace(source()[0],execution_order=10),))
        with self.assertRaises(ValueError): family(overlap_percent=F(31))
        with self.assertRaises(ValueError): family(widths_mm=(F('.4'),F('.3')))


if __name__=='__main__': unittest.main()
