"""Closed-footprint structural top queries over the existing nominal bead model."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.support_cell import (
    NominalStructuralTopBounds, NominalSupportSegment, SupportCellQueryPolicy, SupportCellXY,
)
from adaptive_subedge.engine.support_cell import (
    query_nominal_structural_top_cell, query_nominal_structural_top_point,
)


def source(name="a", start=(0, 0, 1), end=(4, 0, 1), width=2, height=1, kind="structural"):
    return NominalSupportSegment(name, PrintPoint3(*start), PrintPoint3(*end), width, height, kind, 0)


class StructuralTopTests(unittest.TestCase):
    def setUp(self):
        self.policy = SupportCellQueryPolicy("nominal_bead_cell_bounds_v1", 32, 2)

    def point(self, x, y, sources=None, **changes):
        return query_nominal_structural_top_point(F(x), F(y),
            (source(),) if sources is None else sources,
            policy=changes.get("policy", self.policy),
            max_point_coordinate_bits=changes.get("bits", 64),
            cancelled=changes.get("cancelled", lambda: False))

    def cell(self, cell, sources=None, **changes):
        return query_nominal_structural_top_cell(cell,
            (source(),) if sources is None else sources,
            policy=changes.get("policy", self.policy),
            cancelled=changes.get("cancelled", lambda: False))

    def test_point_closed_flat_caps_side_and_absence(self):
        for x, y, top in ((2, 0, 1), (0, 0, 1), (4, 0, 1),
                          (2, 1, F(1, 2)), (0, 1, F(1, 2))):
            result = self.point(x, y)
            self.assertEqual((result.state, result.reason), ("full-bounded", "covered-point"))
            self.assertEqual((result.top_z_lower_mm, result.top_z_upper_mm), (top, top))
        for x, y in ((F(-1, 100), 0), (F(401, 100), 0), (2, F(101, 100))):
            self.assertEqual(self.point(x, y).state, "absent")
        circle = source(width=1, height=1)
        self.assertEqual(self.point(2, F(1, 2), (circle,)).top_z_upper_mm, F(1, 2))
        self.assertEqual(self.point(2, F(51, 100), (circle,)).state, "absent")

    def test_irrational_arc_enclosure_tightens(self):
        coarse = self.point(2, F(3, 4), policy=replace(self.policy, sqrt_fraction_bits=4))
        fine = self.point(2, F(3, 4), policy=replace(self.policy, sqrt_fraction_bits=32))
        self.assertLessEqual(coarse.top_z_lower_mm, fine.top_z_lower_mm)
        self.assertGreaterEqual(coarse.top_z_upper_mm, fine.top_z_upper_mm)
        self.assertLess(fine.top_z_lower_mm, fine.top_z_upper_mm)

    def test_union_max_and_order(self):
        low, high = source(), source("z", start=(0, 0, 2), end=(4, 0, 2))
        for pair in ((low, high), (high, low), (replace(high, segment_id="b"), low)):
            self.assertEqual(self.point(2, 0, pair).top_z_lower_mm, F(2))
        self.assertEqual(self.point(2, 0, (low, high)).top_z_upper_mm, F(2))

    def test_cell_full_partial_absent_and_seam_union(self):
        full = self.cell(SupportCellXY(1, 2, -0.25, 0.25))
        self.assertEqual((full.state, full.reason, full.top_z_lower_mm, full.top_z_upper_mm),
                         ("full-bounded", "one-segment-covers-cell", F(1), F(1)))
        partial = self.cell(SupportCellXY(-0.25, 0.25, -0.25, 0.25))
        self.assertEqual((partial.state, partial.reason, partial.top_z_lower_mm),
                         ("unresolved-partial", "union-coverage-unproven", None))
        self.assertIsNotNone(partial.top_z_upper_mm)
        self.assertEqual(self.cell(SupportCellXY(-2, -1, -1, 1)).state, "absent")
        left = source("left", end=(1, 0, 1))
        right = source("right", start=(1, 0, 1), end=(2, 0, 1))
        seam = self.cell(SupportCellXY(0.5, 1.5, -0.25, 0.25), (left, right))
        self.assertEqual((seam.state, seam.top_z_lower_mm), ("unresolved-partial", None))

    def test_count_and_point_bit_preflight(self):
        self.assertEqual(self.point(2, 0, (source(), source("b"))).state, "full-bounded")
        overflow = (None, None, None)
        self.assertEqual(self.point(2, 0, overflow).reason, "resource-limit")
        self.assertEqual(self.cell(SupportCellXY(0, 1, 0, 1), overflow).reason, "resource-limit")
        self.assertEqual(self.point(F(7), F(1, 4), (), bits=3).state, "absent")
        self.assertEqual(self.point(F(8), 0, (), bits=3).reason, "resource-limit")
        self.assertEqual(self.point(F(1, 8), 0, (), bits=3).reason, "resource-limit")
        self.assertEqual(self.point(F(8), 0, (), bits=3, cancelled=lambda: True).reason, "cancelled")

    def test_cancellation_before_during_and_after_publication(self):
        self.assertEqual(self.point(2, 0, cancelled=lambda: True).reason, "cancelled")
        count = 0
        def during():
            nonlocal count
            count += 1
            return count == 2
        self.assertEqual(self.point(2, 0, cancelled=during).reason, "cancelled")
        def after():
            nonlocal count
            count += 1
            return count == 4
        count = 0
        self.assertEqual(self.point(2, 0, cancelled=after).reason, "cancelled")
        with patch("adaptive_subedge.engine.support_cell.NominalStructuralTopBounds",
                   wraps=NominalStructuralTopBounds) as dto:
            self.point(2, 0)
            self.assertTrue(dto.called)

    def test_invalid_inputs_and_result_shape(self):
        for src in ((source(kind="candidate"),),
                    (source(start=(0, 0, 1), end=(4, 0, 2)),),
                    (source(), source())):
            with self.assertRaises(ContractError) as failure:
                self.point(2, 0, src)
            self.assertIs(failure.exception.reason, ReasonCode.INVALID_GEOMETRY)
        for kwargs in ({"bits": 0}, {"bits": True}, {"cancelled": None},
                       {"cancelled": lambda: 1}):
            with self.assertRaises(ContractError):
                self.point(2, 0, **kwargs)
        with self.assertRaises(ContractError):
            query_nominal_structural_top_point(2, F(0), (), policy=self.policy,
                max_point_coordinate_bits=64, cancelled=lambda: False)
        with self.assertRaises(ContractError):
            NominalStructuralTopBounds("full-bounded", "covered-point", None, F(1))
        with self.assertRaises(FrozenInstanceError):
            self.point(2, 0).state = "absent"


if __name__ == "__main__":
    unittest.main()
