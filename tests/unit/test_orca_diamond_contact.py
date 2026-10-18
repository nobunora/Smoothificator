"""Renderer-specific contact bounds must not reuse stadium top geometry."""
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from tools.audit_orca_diamond_contact import query_diamond_cell
from tools.audit_top_contact_cells import audit_strip


def source():
    return ExactNominalTopSegment("base", (F(0), F(0), F("2.2")),
                                  (F(1), F(0), F("2.2")), F(".4"), F(".2"), "structural")


class OrcaDiamondContactTests(unittest.TestCase):
    def query(self, cell, sources=None):
        return query_diamond_cell(cell, sources or (source(),), max_sources=1000,
                                  sqrt_fraction_bits=128, cancelled=lambda: False)

    def test_diamond_top_uses_linear_sides(self):
        bounds = self.query(ExactTopCellXY(F(".1"), F(".9"), F(".1"), F(".15")))
        self.assertEqual(bounds.top_z_lower_mm, F("2.125"))
        self.assertEqual(bounds.top_z_upper_mm, F("2.15"))

    def test_axial_cap_can_only_contribute_upper_bound(self):
        bounds = self.query(ExactTopCellXY(F("1.01"), F("1.02"), F("-.01"), F(".01")))
        self.assertEqual(bounds.state, "unresolved-partial")
        self.assertEqual(bounds.top_z_upper_mm, F("2.2"))
        self.assertIsNone(bounds.top_z_lower_mm)

    def test_source_beyond_pointed_cap_cannot_hide_a_gap(self):
        bounds = self.query(ExactTopCellXY(F("1.3"), F("1.4"), F("-.01"), F(".01")))
        self.assertEqual(bounds.state, "absent")
        self.assertIsNone(bounds.top_z_upper_mm)

    def test_diamond_gap_is_not_promoted_by_stadium_assumption(self):
        result = audit_strip(ExactTopCellXY(F(".1"), F(".9"), F(".15"), F(".151")),
                             (source(),), F("2.14"), query_cell=query_diamond_cell)
        self.assertEqual(result["state"], "gap-proven")
        self.assertFalse(result["printable_authorized"])

    def test_central_strip_intersection_is_bounded_over_its_area(self):
        result = audit_strip(ExactTopCellXY(F(".1"), F(".9"), F("-.01"), F(".01")),
                             (source(),), F("2.19"), query_cell=query_diamond_cell)
        self.assertEqual(result["state"], "nominal-strip-intersection-proven")

    def test_cancelled_or_source_limit_has_no_bounds(self):
        cell = ExactTopCellXY(F(".1"), F(".9"), F("-.01"), F(".01"))
        bounds = query_diamond_cell(cell, (source(),), max_sources=1,
                                    sqrt_fraction_bits=128, cancelled=lambda: True)
        self.assertEqual(bounds.state, "incomplete")
        self.assertIsNone(bounds.top_z_upper_mm)
        bounds = query_diamond_cell(cell, (source(),), max_sources=0,
                                    sqrt_fraction_bits=128, cancelled=lambda: False)
        self.assertEqual(bounds.reason, "resource-limit")


if __name__ == "__main__":
    unittest.main()
