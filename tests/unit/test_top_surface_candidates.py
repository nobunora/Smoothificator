"""Fixture geometry checks for read-only tilted-coupon review segments."""

import unittest
from pathlib import Path

from tools.generate_top_surface_candidates import (MODEL_SHA256, ROOT, SLICE_SHA256,
                                                   STL_SHA256, _pinned, generate)
from tools.build_true_z_orca_review import build_review


class TopSurfaceCandidatesTests(unittest.TestCase):
    def setUp(self):
        fixture_paths = (ROOT / "artifacts/fixtures/offline-coupon.3mf",
                         ROOT / "artifacts/fixtures/offline-coupon.stl",
                         ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode")
        if not all(Path(path).is_file() for path in fixture_paths):
            self.skipTest("local SHA-pinned Orca geometry fixture is not distributed to CI")
        self.model = _pinned(ROOT / "artifacts/fixtures/offline-coupon.3mf", MODEL_SHA256)
        self.stl = _pinned(ROOT / "artifacts/fixtures/offline-coupon.stl", STL_SHA256)
        self.source = _pinned(ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode", SLICE_SHA256)

    def test_distinct_isocontours_lie_on_transformed_upward_face(self):
        review = generate(self.model, self.stl, self.source)
        matrix = review["frame"]["transform_3mf"]
        segments = review["segments"]
        self.assertEqual(len(segments), 6)
        self.assertEqual(len({row["start_mm"][2] for row in segments}), 6)
        self.assertFalse(review["printable_authorized"])
        for row in segments:
            self.assertEqual(row["reason"], "top-surface")
            start, end = row["start_mm"], row["end_mm"]
            self.assertEqual(start[1:], end[1:])
            self.assertGreater(start[0], 120.2)
            self.assertLess(end[0], 129.8)
            local_y = (start[1] - 35 - matrix[7] - matrix[10]) / matrix[4]
            self.assertLess(abs(matrix[5] * local_y + matrix[8] + matrix[11] - start[2]), 1e-5)
            self.assertLess(abs(local_y), 5)
        self.assertFalse(segments[0]["higher_footprint_overlap"])
        self.assertEqual(segments[0]["review_status"], "below-minimum-height")
        self.assertTrue(segments[-2]["higher_footprint_overlap"])
        self.assertEqual(segments[-1]["review_status"], "nominal-support-valley")
        self.assertAlmostEqual(segments[-1]["sampled_nominal_minimum_top_z_mm"], 2.16131, places=4)
        self.assertEqual(segments[-1]["sampled_effective_height_mm"], 0.08)
        self.assertEqual(segments[-1]["width_mm"], 0.3)
        self.assertFalse(segments[-1]["width_minimum_verified"])

    def test_source_identity_change_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unpinned 3MF"):
            generate(self.model + b"x", self.stl, self.source)
        with self.assertRaisesRegex(ValueError, "unpinned Orca slice"):
            generate(self.model, self.stl, self.source + b"x")

    def test_focused_orca_viewer_rejects_floating_true_z_candidate(self):
        review = generate(self.model, self.stl, self.source)
        with self.assertRaisesRegex(ValueError, "no height-and-footprint review candidates"):
            build_review(self.source, review, focus=True)


if __name__ == "__main__":
    unittest.main()
