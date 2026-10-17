"""Restricted planar coupon comparison remains a bounded research receipt."""
import unittest
from fractions import Fraction as F
from unittest.mock import patch

from adaptive_subedge.domain.coupon_residual import CouponVerticalComparison, VerticalResidualInterval
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.planar_cell_top import PlanarCellTopCoverage
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from adaptive_subedge.engine import coupon_residual as engine
from adaptive_subedge.engine.coupon_residual import compare_planar_coupon_vertical_residual
from tests.unit.test_section_difference import frustum


CELL = ExactTopCellXY(F(3, 2), F(5, 2), F(7, 4), F(9, 4))


def line(identity, z, kind, y=F(2)):
    return ExactNominalTopSegment(identity, (F(0), y, z), (F(4), y, z),
                                  F(2), F(1), kind)


class CouponResidualTests(unittest.TestCase):
    def compare(self, structural=None, candidate=None, **change):
        options = dict(source_mesh_id="mesh", baseline_slice_id="slice",
                       max_vertices=100, max_triangles=100, max_mesh_pair_checks=1000,
                       max_cell_vertices=20, max_centroid_tests=100,
                       max_facet_clip_tests=1000, max_sources=4,
                       max_coordinate_bits=128, sqrt_fraction_bits=32,
                       max_refinement_depth=0, max_leaf_cells=1,
                       cancelled=lambda: False)
        return compare_planar_coupon_vertical_residual(
            frustum(), CELL, (line("s", F(0), "structural"),) if structural is None else structural,
            (line("c", F(1), "candidate"),) if candidate is None else candidate,
            **(options | change))

    def test_exact_reduction_and_overbuild(self):
        reduced = self.compare()
        self.assertEqual((reduced.state, reduced.reason, reduced.leaf_count,
                          reduced.target_plane_abc),
                         ("complete", "certified-reduction", 1, (F(0), F(0), F(1))))
        self.assertGreater(reduced.baseline_max_residual.lower_mm,
                           reduced.augmented_max_residual.upper_mm)
        overbuilt = self.compare(candidate=(line("c", F(3), "candidate"),))
        self.assertEqual((overbuilt.state, overbuilt.reason),
                         ("complete", "certified-nonreduction"))

    def test_uncovered_or_unresolved_does_not_publish_score(self):
        outcome = self.compare(structural=(line("s", F(0), "structural", F(4)),))
        self.assertEqual((outcome.state, outcome.reason, outcome.leaf_count,
                          outcome.baseline_max_residual),
                         ("incomplete", "coverage-unresolved", 1, None))

    def test_preflight_coordinate_limit_before_certificate(self):
        with patch("adaptive_subedge.engine.coupon_residual.certify_planar_cell_top") as certificate:
            result = self.compare(max_coordinate_bits=2)
            self.assertEqual((result.state, result.reason, result.leaf_count),
                             ("incomplete", "resource-limit", 0))
            certificate.assert_not_called()

    def test_cancellation_and_source_identity(self):
        cancelled = self.compare(cancelled=lambda: True)
        self.assertEqual((cancelled.state, cancelled.reason, cancelled.leaf_count),
                         ("incomplete", "cancelled", 0))
        with self.assertRaises(ContractError):
            self.compare(candidate=(line("s", F(1), "candidate"),))

    def test_source_permutation_keeps_bounds_and_exact_refinement(self):
        structural = (line("s", F(0), "structural"),
                      line("t", F(-1), "structural"))
        candidates = (line("c", F(1), "candidate"),
                      line("d", F(1, 2), "candidate"))
        first = self.compare(structural=structural, candidate=candidates,
                             max_refinement_depth=1, max_leaf_cells=4)
        second = self.compare(structural=tuple(reversed(structural)),
                              candidate=tuple(reversed(candidates)),
                              max_refinement_depth=1, max_leaf_cells=4)
        self.assertEqual(first, second)

    def test_one_bit_over_budget_cancels_before_certificate(self):
        calls = 0

        def cancellation():
            nonlocal calls
            calls += 1
            return calls >= 5

        with patch("adaptive_subedge.engine.coupon_residual.certify_planar_cell_top") as certificate:
            result = self.compare(max_coordinate_bits=2, cancelled=cancellation)
            self.assertEqual((result.state, result.reason), ("incomplete", "cancelled"))
            certificate.assert_not_called()

    def test_dto_rejects_favorable_label_without_disjoint_bounds(self):
        with self.assertRaises(ContractError):
            CouponVerticalComparison("complete", "certified-reduction", "mesh", "slice", CELL,
                                     (F(0), F(0), F(1)), VerticalResidualInterval(F(0), F(1)),
                                     VerticalResidualInterval(F(0), F(1)), 1)

    def test_known_target_rejection_and_unknown_reason(self):
        outside = ExactTopCellXY(F(5), F(6), F(5), F(6))
        options = dict(source_mesh_id="mesh", baseline_slice_id="slice",
                       max_vertices=100, max_triangles=100, max_mesh_pair_checks=1000,
                       max_cell_vertices=20, max_centroid_tests=100,
                       max_facet_clip_tests=1000, max_sources=2,
                       max_coordinate_bits=128, sqrt_fraction_bits=16,
                       max_refinement_depth=0, max_leaf_cells=1,
                       cancelled=lambda: False)
        result = engine.compare_planar_coupon_vertical_residual(
            frustum(), outside, (line("s", F(0), "structural"),),
            (line("c", F(1), "candidate"),), **options)
        self.assertEqual((result.state, result.reason, result.leaf_count),
                         ("rejected", "target-unresolved", 0))
        with patch.object(engine, "certify_planar_cell_top", return_value=PlanarCellTopCoverage(
                "rejected", "empty-mesh", None, None, None, None, None)):
            self.assertEqual(engine.compare_planar_coupon_vertical_residual(
                frustum(), CELL, (line("s", F(0), "structural"),),
                (line("c", F(1), "candidate"),), **options).reason, "target-unresolved")
        with patch.object(engine, "certify_planar_cell_top") as certificate:
            certificate.return_value.state = "rejected"
            certificate.return_value.reason = "future-reason"
            with self.assertRaises(ContractError):
                engine.compare_planar_coupon_vertical_residual(
                    frustum(), CELL, (line("s", F(0), "structural"),),
                    (line("c", F(1), "candidate"),), **options)

    def test_equal_curved_tops_overlap_and_leaf_budget(self):
        structural = ExactNominalTopSegment("s", (F(0), F(2), F(0)),
                                            (F(4), F(2), F(0)), F(1), F(1), "structural")
        candidate = ExactNominalTopSegment("c", (F(0), F(2), F(0)),
                                           (F(4), F(2), F(0)), F(1), F(1), "candidate")
        zero = self.compare(structural=(structural,), candidate=(candidate,))
        self.assertEqual((zero.state, zero.reason, zero.leaf_count),
                         ("complete", "interval-overlap", 1))
        depth = self.compare(structural=(structural,), candidate=(candidate,),
                             max_refinement_depth=1, max_leaf_cells=4)
        self.assertEqual((depth.state, depth.reason, depth.leaf_count),
                         ("complete", "interval-overlap", 4))
        budget = self.compare(structural=(structural,), candidate=(candidate,),
                              max_refinement_depth=1, max_leaf_cells=3)
        self.assertEqual((budget.state, budget.reason, budget.leaf_count),
                         ("complete", "interval-overlap", 1))

    def test_cancellation_after_prior_leaf_discards_intervals(self):
        structural = ExactNominalTopSegment("s", (F(0), F(2), F(0)),
                                            (F(4), F(2), F(0)), F(1), F(1), "structural")
        candidate = ExactNominalTopSegment("c", (F(0), F(2), F(0)),
                                           (F(4), F(2), F(0)), F(1), F(1), "candidate")
        original = engine.query_exact_nominal_top_cell
        calls = 0
        cancelled = False

        def query(*args, **kwargs):
            nonlocal calls, cancelled
            calls += 1
            answer = original(*args, **kwargs)
            if calls == 3:
                cancelled = True
            return answer

        with patch.object(engine, "query_exact_nominal_top_cell", side_effect=query):
            result = self.compare(structural=(structural,), candidate=(candidate,),
                                  max_refinement_depth=1, max_leaf_cells=4,
                                  cancelled=lambda: cancelled)
        self.assertEqual((result.state, result.reason, result.leaf_count,
                          result.baseline_max_residual),
                         ("incomplete", "cancelled", 1, None))


if __name__ == "__main__":
    unittest.main()
