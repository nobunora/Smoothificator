"""Pinned fixture comparison must retain provenance and uncertainty."""
import hashlib
import json
from fractions import Fraction as F
import unittest
from unittest.mock import patch
from itertools import chain, repeat

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from tools.compare_top_surface_residual import compare, compare_partitions, coupon_mesh, dominant_baseline, spatial_baseline
from tools.generate_top_surface_candidates import ROOT, MODEL_SHA256, STL_SHA256, SLICE_SHA256
from tools.render_top_surface_3d_review import comparison_summary
from tests.unit.test_section_difference import frustum


def reference_plan():
    return {"schema": "smoothificator.offline_top_candidates.v1", "scope": "3d-review-only",
            "source_3mf_sha256": MODEL_SHA256, "source_stl_sha256": STL_SHA256,
            "source_slice_sha256": SLICE_SHA256, "printable_authorized": False,
            "segments": [{"id": "top-07", "reason": "top-surface",
                "start_mm": [120.3,127.336335,2.28], "end_mm": [129.7,127.336335,2.28],
                "width_mm": .34, "bead_height_mm": .19,
                "minimum_effective_height_mm": .08, "sampled_effective_height_mm": .08,
                "sampled_support_top_z_mm": 2.2, "sampled_nominal_minimum_top_z_mm": 2.16131,
                "sampled_support_complete": True, "continuous_contact_verified": False,
                "review_status": "continuous-contact-unverified", "width_minimum_verified": True,
                "nearest_higher_footprint_clearance_mm": .018, "higher_footprint_overlap": False}]}


def receipt(plan):
    return {"schema": "smoothificator.offline_coupon_comparison.v1",
            "candidate_plan_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True,
                separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
            "source_3mf_sha256": MODEL_SHA256, "source_stl_sha256": STL_SHA256,
            "source_slice_sha256": SLICE_SHA256, "printable_authorized": False,
            "full_surface_improvement_verified": False, "baseline_higher_layers_truncated": False,
            "state": "complete", "reason": "certified-reduction", "strict_local_reduction_verified": True,
            "baseline_max_vertical_residual": {"lower_exact_mm": "1/10", "upper_exact_mm": "1/5"},
            "augmented_max_vertical_residual": {"lower_exact_mm": "1/100", "upper_exact_mm": "1/20"}}


class ComparisonDisplayTests(unittest.TestCase):
    def test_only_disjoint_intervals_report_local_reduction(self):
        plan = reference_plan()
        summary = comparison_summary(plan, receipt(plan))
        self.assertEqual(summary["state"], "complete")
        self.assertIn("この範囲", summary["text"])
        self.assertIn("0.100000", summary["text"])

    def test_changed_height_rejects_stale_comparison(self):
        plan = reference_plan()
        report = receipt(plan)
        plan["segments"][0]["bead_height_mm"] = .14
        self.assertEqual(comparison_summary(plan, report)["state"], "stale")

    def test_wrong_source_and_global_success_are_not_displayed(self):
        plan = reference_plan()
        for key, value in (("source_slice_sha256", "other"), ("printable_authorized", True),
                           ("full_surface_improvement_verified", True),
                           ("baseline_higher_layers_truncated", True)):
            report = receipt(plan)
            report[key] = value
            self.assertEqual(comparison_summary(plan, report)["state"], "stale")

    def test_favorable_label_cannot_override_overlapping_bounds(self):
        plan = reference_plan()
        report = receipt(plan)
        report["augmented_max_vertical_residual"]["upper_exact_mm"] = "3/20"
        self.assertEqual(comparison_summary(plan, report)["state"], "invalid")
        report["reason"] = "interval-overlap"
        report["strict_local_reduction_verified"] = False
        self.assertIn("未確定", comparison_summary(plan, report)["text"])

    def test_incomplete_comparison_never_displays_partial_scores(self):
        plan = reference_plan()
        report = receipt(plan)
        report.update(state="incomplete", reason="coverage-unresolved")
        summary = comparison_summary(plan, report)
        self.assertEqual(summary["state"], "incomplete")
        self.assertNotIn("0.100000", summary["text"])
        self.assertEqual(comparison_summary(plan, None)["state"], "missing")

    def test_malformed_or_unrepresentable_display_bounds_fail_closed(self):
        plan = reference_plan()
        self.assertEqual(comparison_summary(plan, [])["state"], "invalid")
        report = receipt(plan)
        report["baseline_max_vertical_residual"]["upper_exact_mm"] = "1"+"0"*500
        self.assertEqual(comparison_summary(plan, report)["state"], "invalid")


class BaselineDominanceTests(unittest.TestCase):
    def test_lower_paths_are_removed_only_with_full_area_top_bound(self):
        rectangle = ExactTopCellXY(F(0),F(1),F("-.05"),F(".05"))
        high = ExactNominalTopSegment("high", (F(0),F(0),F(2)), (F(1),F(0),F(2)), F(1),F(".2"),"structural")
        low = ExactNominalTopSegment("low", (F(0),F(0),F(1)), (F(1),F(0),F(1)), F(1),F(".2"),"structural")
        selected, proof = dominant_baseline(rectangle, (high,low), lambda: False)
        self.assertEqual(selected, (high,))
        self.assertEqual(proof["state"], "nominal-strip-intersection-proven")
        wider = ExactTopCellXY(F(0),F(1),F("-.7"),F(".7"))
        selected, proof = dominant_baseline(wider, (high,low), lambda: False)
        self.assertEqual(selected, (high,low))
        self.assertEqual(proof["state"], "gap-proven")

    def test_cancelled_dominance_retains_the_original_baseline(self):
        rectangle = ExactTopCellXY(F(0),F(1),F("-.05"),F(".05"))
        high = ExactNominalTopSegment("high", (F(0),F(0),F(2)), (F(1),F(0),F(2)), F(1),F(".2"),"structural")
        low = ExactNominalTopSegment("low", (F(0),F(0),F(1)), (F(1),F(0),F(1)), F(1),F(".2"),"structural")
        selected, proof = dominant_baseline(rectangle, (high,low), lambda: True)
        self.assertEqual(selected, (high,low))
        self.assertEqual(proof["state"], "unresolved")


class PartitionedComparisonTests(unittest.TestCase):
    def test_closed_partition_preserves_certified_maximum_and_global_leaf_budget(self):
        rectangle = ExactTopCellXY(F("1.5"),F("2.5"),F("1.75"),F("2.25"))
        structural = ExactNominalTopSegment("base",(F(0),F(2),F(0)),(F(4),F(2),F(0)),F(2),F(1),"structural")
        candidate = ExactNominalTopSegment("candidate",(F(0),F(2),F(1)),(F(4),F(2),F(1)),F(2),F(1),"candidate")
        result = compare_partitions(frustum(),rectangle,(structural,),(candidate,),
            source_mesh_id="analytic",baseline_slice_id="synthetic",max_vertices=100,
            max_triangles=100,max_mesh_pair_checks=1000,max_cell_vertices=20,
            max_centroid_tests=100,max_facet_clip_tests=1000,max_sources=4,
            max_coordinate_bits=256,sqrt_fraction_bits=32,max_refinement_depth=0,
            max_leaf_cells=4,cancelled=lambda:False)
        self.assertEqual((result.state,result.reason,result.leaf_count), ("complete","certified-reduction",4))
        self.assertEqual(result.rectangle,rectangle)
        self.assertEqual(result.baseline_max_residual.lower_mm,F(1))
        self.assertEqual(result.augmented_max_residual.upper_mm,F(0))


class PinnedTopSurfaceComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        paths = [ROOT / "artifacts/fixtures/offline-coupon.3mf",
                 ROOT / "artifacts/fixtures/offline-coupon.stl",
                 ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode"]
        if not all(path.is_file() for path in paths):
            raise unittest.SkipTest("local SHA-pinned fixtures are not distributed")
        cls.model, cls.stl, cls.source = (path.read_bytes() for path in paths)

    def run_comparison(self, **changes):
        return compare(self.model, self.stl, self.source, reference_plan(),
                       max_leaf_cells=1, max_depth=0, **changes)

    def test_complete_baseline_keeps_future_layers_and_all_source_ids(self):
        all_sources, selected = spatial_baseline(self.source, ExactTopCellXY(F(119),F(131),F(119),F(131)))
        self.assertEqual(len(all_sources), 669)
        self.assertEqual(len(selected), 669)
        self.assertEqual(max(s.start_xyz_mm[2] for s in selected), F(3))
        self.assertEqual(len({s.segment_id for s in selected}), 669)

    def test_pinned_mesh_and_incomplete_comparison_have_bound_identities(self):
        mesh = coupon_mesh(self.model)
        self.assertEqual((len(mesh.vertices),len(mesh.triangles)), (8,12))
        result = self.run_comparison()
        self.assertEqual((result["state"],result["reason"]), ("incomplete","coverage-unresolved"))
        self.assertEqual(result["baseline_total_segments"], 669)
        self.assertFalse(result["baseline_higher_layers_truncated"])
        self.assertIsNone(result["baseline_max_vertical_residual"])
        self.assertIsNone(result["augmented_max_vertical_residual"])
        self.assertFalse(result["strict_local_reduction_verified"])
        self.assertFalse(result["printable_authorized"])
        self.assertEqual(comparison_summary(reference_plan(), result)["state"], "incomplete")

    def test_cancellation_does_not_publish_scores(self):
        result = self.run_comparison(cancelled=lambda: True)
        self.assertEqual(result["reason"], "cancelled")
        self.assertIsNone(result["augmented_max_vertical_residual"])

    def test_deadline_is_distinct_from_user_cancellation(self):
        clock = chain([0], repeat(100))
        with patch("tools.compare_top_surface_residual.monotonic", side_effect=lambda: next(clock)):
            result = self.run_comparison()
        self.assertEqual(result["reason"], "deadline")
        self.assertIsNone(result["baseline_max_vertical_residual"])

    def test_mutated_inputs_and_print_permission_are_rejected(self):
        for model, stl, source in ((self.model+b"x", self.stl, self.source),
                                  (self.model,self.stl+b"x",self.source),
                                  (self.model,self.stl,self.source+b"x")):
            with self.assertRaisesRegex(ValueError,"unpinned"):
                compare(model,stl,source,reference_plan())
        plan = reference_plan()
        plan["printable_authorized"] = True
        with self.assertRaisesRegex(ValueError,"unauthorized"):
            compare(self.model,self.stl,self.source,plan)

    def test_invalid_budgets_and_missing_candidate_fail_before_analysis(self):
        for policy in ({"max_depth": True}, {"max_leaf_cells": 0}, {"timeout_seconds": float('nan')}):
            with self.assertRaisesRegex(ValueError,"policy"):
                compare(self.model,self.stl,self.source,reference_plan(),**policy)
        with self.assertRaisesRegex(ValueError,"eligible"):
            self.run_comparison(candidate_id="missing")


if __name__ == "__main__":
    unittest.main()
