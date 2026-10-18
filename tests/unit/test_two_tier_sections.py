"""Exact finite stacked families, overlap union and incomplete budgets."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tools.solve_two_tier_rectangles import (
    TwoTierSectionPolicy, PosedSectionRectangle, TwoTierSectionBlock,
    solve_two_tier_section, section_block_error_area,
)


def policy(overlap=0):
    return TwoTierSectionPolicy(48, tuple(F(n,100) for n in range(8,19,2)), F(overlap),
        F('.25'), F('.45'), F('.08'), F('.18'), 2000000, 1000000, 1000000, 4096)


class TwoTierSectionTests(unittest.TestCase):
    def test_twenty_degree_family_improves_stronger_floor_comparator(self):
        report = solve_two_tier_section(F('.549495'), F('.2'), policy=policy(), cancelled=lambda: False)
        self.assertEqual(report.state, 'complete')
        self.assertTrue(report.finite_family_complete)
        self.assertTrue(any(b.upper is not None for b in report.blocks))
        self.assertLess(report.selected_error_area_mm2, report.floor_comparator_error_area_mm2)
        self.assertEqual(report.selected_from, 'finite-two-tier-family')
        summed = F('.549495')*F('.2')/2
        for block in report.blocks:
            summed += section_block_error_area(F('.549495'), F('.2'), block)-F('.549495')*F('.2')/2
        self.assertEqual(summed, report.selected_error_area_mm2)

    def test_shared_overlap_counted_once_against_independent_horizontal_strips(self):
        # Triangle y<=x on[0,1]. Parent[0,1]x[0,.5], child[.5,1]x[.4,.8].
        # union area .5+.2-.05=.65.
        block = TwoTierSectionBlock(PosedSectionRectangle(F(0),F(1),F(0),F('.5')),
            PosedSectionRectangle(F('.5'),F(1),F('.4'),F('.8')))
        # Child inside triangle: .2 minus upper-left triangle(.3*.3/2)=.155.
        # Shared .05 is fully inside; union inside=.375+.155-.05=.48.
        self.assertEqual(section_block_error_area(F(1), F(1), block), F('.19'))

    def test_overlap_minimum_pose_and_strict_top_are_real_constraints(self):
        for overlap in (0, 30):
            report = solve_two_tier_section(F('.55'), F('.2'), policy=policy(overlap), cancelled=lambda: False)
            self.assertEqual(report.state, 'complete')
            for block in report.blocks:
                support = F(0)
                for rectangle in (block.lower, block.upper):
                    if rectangle is None:
                        continue
                    height = rectangle.top_mm-rectangle.bottom_mm
                    self.assertGreaterEqual(rectangle.top_mm-support, F('.08'))
                    self.assertEqual(1-(rectangle.top_mm-support)/height, F(overlap,100))
                    self.assertLess(rectangle.top_mm, F('.2'))
                    support = rectangle.top_mm
        with self.assertRaises(ValueError):
            policy(31)

    def test_flat_short_base_cancel_limits_and_determinism(self):
        arguments = dict(policy=policy(), cancelled=lambda: False)
        self.assertEqual(solve_two_tier_section(F(0),F(0),**arguments).state, 'flat')
        self.assertEqual(solve_two_tier_section(F('.34641'),F('.2'),**arguments).state, 'excluded')
        for changes in (dict(cancelled=lambda: True), dict(policy=replace(policy(),max_candidates=1)),
                        dict(policy=replace(policy(),max_area_queries=1)), dict(policy=replace(policy(),max_events=1)),
                        dict(policy=replace(policy(),max_number_bits=2))):
            report = solve_two_tier_section(F('.55'),F('.2'),**dict(arguments,**changes))
            self.assertEqual(report.state,'incomplete')
            self.assertFalse(report.finite_family_complete)
            self.assertIsNone(report.selected_error_area_mm2)
        small = replace(policy(),grid_divisions=8)
        a = solve_two_tier_section(F('.55'),F('.2'),policy=small,cancelled=lambda:False)
        b = solve_two_tier_section(F('.55'),F('.2'),policy=small,cancelled=lambda:False)
        self.assertEqual(a,b)

    def test_height_pair_prefilter_cancels_and_spends_event_budget_before_quadratic_work(self):
        heights=tuple(F(800+n,10000) for n in range(100))
        settings=replace(policy(),physical_heights_mm=heights,grid_divisions=2,max_events=100)
        polls=0
        def cancel_second():
            nonlocal polls
            polls+=1
            return polls==2
        cancelled=solve_two_tier_section(F('.55'),F('.2'),policy=settings,cancelled=cancel_second)
        self.assertEqual((cancelled.state,cancelled.reason,cancelled.events,cancelled.height_pair_tests),
                         ('incomplete','cancelled',2,0))
        budgeted=solve_two_tier_section(F('.55'),F('.2'),policy=settings,cancelled=lambda:False)
        self.assertEqual(budgeted.reason,'event-limit')
        self.assertEqual(budgeted.height_pair_tests,0)
        self.assertFalse(budgeted.finite_family_complete)
        # With a larger budget the comparisons themselves are charged too.
        larger=replace(settings,max_events=400)
        partial=solve_two_tier_section(F('.55'),F('.2'),policy=larger,cancelled=lambda:False)
        self.assertEqual(partial.reason,'event-limit')
        self.assertGreater(partial.height_pair_tests,0)
        self.assertLessEqual(partial.height_pair_tests,400)


if __name__ == '__main__':
    unittest.main()
