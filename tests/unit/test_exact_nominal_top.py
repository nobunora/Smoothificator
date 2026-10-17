"""Exact nominal bead tops are research bounds, not printable authority."""
import unittest
from fractions import Fraction as F

from adaptive_subedge.domain.convex_chords import ChordProposal
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY, NominalSupportSegment
from adaptive_subedge.engine.support_cell import (
    _segment_top_bounds, _segment_top_bounds_exact,
    exact_top_segment_from_chord, exact_top_segment_from_structural,
    query_exact_nominal_top_cell, query_exact_nominal_top_point,
)


class ExactTopTests(unittest.TestCase):
    def setUp(self):
        self.segment = ExactNominalTopSegment("a", (F(0), F(0), F(1)),
                                              (F(1), F(0), F(1)), F(2, 3), F(2, 3), "candidate")
        self.settings = dict(max_sources=2, max_coordinate_bits=128,
                             sqrt_fraction_bits=16, cancelled=lambda: False)

    def point(self, x, y, sources=None, **changes):
        return query_exact_nominal_top_point(x, y, self.segment_tuple(sources),
                                             **(self.settings | changes))

    def segment_tuple(self, sources):
        return (self.segment,) if sources is None else sources

    def test_exact_chord_endpoint_and_outer_side(self):
        proposal = ChordProposal(F(0), "proposed", "unscored",
                                 (F(1, 3), F(0)), (F(4, 3), F(0)))
        segment = exact_top_segment_from_chord(proposal, segment_id="c",
                                               command_z_mm=F(2), width_mm=F(2, 3), height_mm=F(2, 3))
        self.assertEqual(segment.start_xyz_mm[0], F(1, 3))
        self.assertEqual(segment.end_xyz_mm[0], F(4, 3))
        self.assertEqual(self.point(F(1, 3), F(1, 3), (segment,)).state, "full-bounded")
        self.assertEqual(self.point(F(1, 3) - F(1, 10**20), F(0), (segment,)).state, "absent")
        self.assertEqual(self.point(F(1, 3), F(1, 3) + F(1, 10**20), (segment,)).state, "absent")

    def test_max_union_and_negative_top(self):
        lower = ExactNominalTopSegment("b", (F(0), F(0), F(-1)),
                                       (F(1), F(0), F(-1)), F(2, 3), F(2, 3), "structural")
        self.assertEqual(self.point(F(1, 2), F(0), (lower,)).top_z_lower_mm, F(-1))
        self.assertEqual(self.point(F(1, 2), F(0), (lower, self.segment)).top_z_lower_mm, F(1))

    def test_cell_full_partial_absent(self):
        cell = ExactTopCellXY(F(1, 4), F(3, 4), F(-1, 10), F(1, 10))
        full = query_exact_nominal_top_cell(cell, (self.segment,), **self.settings)
        self.assertEqual((full.state, full.reason), ("full-bounded", "one-segment-covers-cell"))
        partial = query_exact_nominal_top_cell(ExactTopCellXY(F(3, 4), F(5, 4), F(-1, 10), F(1, 10)),
                                               (self.segment,), **self.settings)
        self.assertEqual(partial.state, "unresolved-partial")
        other = ExactNominalTopSegment("b", (F(1), F(0), F(1)), (F(2), F(0), F(1)),
                                       F(2, 3), F(2, 3), "candidate")
        joined = query_exact_nominal_top_cell(
            ExactTopCellXY(F(3, 4), F(5, 4), F(-1, 10), F(1, 10)),
            (self.segment, other), **self.settings)
        self.assertEqual(joined.state, "unresolved-partial")
        self.assertEqual(self.point(F(2), F(0)).state, "absent")

    def test_budget_and_cancel(self):
        self.assertEqual(self.point(F(0), F(0), max_sources=1).state, "full-bounded")
        self.assertEqual(self.point(F(0), F(0), max_coordinate_bits=1).reason, "resource-limit")
        self.assertEqual(self.point(F(0), F(0), cancelled=lambda: True).reason, "cancelled")
        second = ExactNominalTopSegment("b", self.segment.start_xyz_mm, self.segment.end_xyz_mm,
                                        self.segment.width_mm, self.segment.height_mm, "candidate")
        self.assertEqual(self.point(F(0), F(0), (self.segment, second), max_sources=1).reason,
                         "resource-limit")
        self.assertEqual(self.point(F(1, 257), F(0), max_coordinate_bits=8).reason,
                         "resource-limit")
        wide = ExactNominalTopSegment("wide", (F(0), F(0), F(1)),
                                      (F(1, 257), F(0), F(1)), F(1), F(1), "candidate")
        self.assertEqual(self.point(F(0), F(0), (wide,), max_coordinate_bits=8).reason,
                         "resource-limit")
        cell = ExactTopCellXY(F(0), F(1, 257), F(0), F(1))
        self.assertEqual(query_exact_nominal_top_cell(cell, (), **(self.settings | {"max_coordinate_bits": 8})).reason,
                         "resource-limit")
        with self.assertRaises(ContractError):
            self.point(F(0), F(0), (self.segment, self.segment))

    def test_precision_outward_encloses_irrational_top(self):
        tight = self.point(F(1, 2), F(1, 4), sqrt_fraction_bits=32)
        loose = self.point(F(1, 2), F(1, 4), sqrt_fraction_bits=4)
        self.assertLessEqual(loose.top_z_lower_mm, tight.top_z_lower_mm)
        self.assertGreaterEqual(loose.top_z_upper_mm, tight.top_z_upper_mm)
        self.assertLess(loose.top_z_lower_mm, loose.top_z_upper_mm)

    def test_cancellation_after_kernel_and_dto(self):
        calls = 0

        def cancel_after_kernel():
            nonlocal calls
            calls += 1
            return calls >= 4

        self.assertEqual(self.point(F(1, 2), F(0), cancelled=cancel_after_kernel).reason, "cancelled")
        calls = 0

        def cancel_after_result():
            nonlocal calls
            calls += 1
            return calls >= 6

        self.assertEqual(self.point(F(1, 2), F(0), cancelled=cancel_after_result).reason, "cancelled")

    def test_structural_adapter_sloped_binary64(self):
        source = NominalSupportSegment("s", PrintPoint3(0.1, 0., 1.), PrintPoint3(1., 0., 2.),
                                       0.4, 0.2, "structural", 0)
        exact = exact_top_segment_from_structural(source)
        self.assertEqual(exact.start_xyz_mm[0], F(0.1))
        self.assertEqual(exact.end_xyz_mm[2], F(2.0))
        self.assertEqual(self.point(F(1), F(0), (exact,)).top_z_lower_mm, F(2))
        corners = ((F(1, 2), F(1, 20)),)
        self.assertEqual(_segment_top_bounds(source, corners, 16),
                         _segment_top_bounds_exact(exact, corners, 16))

    def test_bad_geometry(self):
        for width, height in ((F(1, 10), F(2, 10)), (F(0), F(0))):
            with self.assertRaises(ContractError):
                ExactNominalTopSegment("a", (F(0), F(0), F(0)), (F(1), F(0), F(0)),
                                       width, height, "candidate")
        with self.assertRaises(ContractError):
            ExactNominalTopSegment("a", (F(0), F(0), F(0)), (F(1), F(0), F(1)),
                                   F(1), F(1), "candidate")
        with self.assertRaises(ContractError):
            ExactNominalTopSegment("", (F(0), F(0), F(0)), (F(1), F(0), F(0)),
                                   F(1), F(1), "candidate")
        rejected = ChordProposal(F(0), "rejected", "empty-footprint", None, None)
        with self.assertRaises(ContractError):
            exact_top_segment_from_chord(rejected, segment_id="r", command_z_mm=F(0),
                                         width_mm=F(1), height_mm=F(1))


if __name__ == "__main__":
    unittest.main()
