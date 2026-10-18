"""Whole-cell contact regression tests, including gaps between sample points."""
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from tools.audit_top_contact_cells import audit_strip


def bead(identifier, left, right, z="2.2"):
    return ExactNominalTopSegment(identifier, (F(left), F(0), F(z)),
                                  (F(right), F(0), F(z)), F("0.4"), F("0.2"), "structural")


class TopContactCellsTests(unittest.TestCase):
    def test_closed_strip_has_continuous_nominal_intersection(self):
        result = audit_strip(ExactTopCellXY(F(0), F(1), F("-.05"), F(".05")),
                             (bead("base", "0", "1"),), F("2.14"))
        self.assertEqual(result["state"], "nominal-strip-intersection-proven")
        self.assertFalse(result["printable_authorized"])

    def test_narrow_unsampled_axial_gap_is_not_certified(self):
        result = audit_strip(ExactTopCellXY(F(0), F(1), F("-.01"), F(".01")),
                             (bead("left", "0", ".501"), bead("right", ".502", "1")),
                             F("2.14"), max_depth=18)
        self.assertEqual(result["state"], "gap-proven")
        self.assertGreater(result["leaf_counts"]["gap"], 0)

    def test_cell_upper_bound_detects_round_side_gap(self):
        result = audit_strip(ExactTopCellXY(F(0), F(1), F(".199"), F(".2")),
                             (bead("base", "0", "1"),), F("2.198"))
        self.assertEqual(result["state"], "gap-proven")

    def test_resource_budget_does_not_claim_contact(self):
        result = audit_strip(ExactTopCellXY(F(0), F(1), F("-.05"), F(".05")),
                             (bead("left", "0", ".6"), bead("right", ".4", "1")),
                             F("2.14"), max_cells=1)
        self.assertEqual(result["state"], "unresolved")

    def test_discarded_low_sources_still_bound_gap_witness(self):
        result = audit_strip(ExactTopCellXY(F(0), F(1), F("-.05"), F(".05")),
                             (bead("low", "0", "1", "2"),), F("2.14"))
        self.assertEqual(result["state"], "gap-proven")
        self.assertEqual(result["gap_witnesses"][0]["top_upper_mm"], "2")


if __name__ == "__main__":
    unittest.main()
