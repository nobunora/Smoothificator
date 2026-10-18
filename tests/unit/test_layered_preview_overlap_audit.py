"""Focused geometry tests for the read-only layered-preview conflict audit."""

import hashlib
import unittest
from unittest.mock import patch

from tools.audit_layered_preview_overlap import audit, centerline_distance, source_segments


SOURCE = b"M83\n;Z:2.4\n;WIDTH:0.4\nG0 X0 Y0 Z2.4\nG1 X2 Y0 E0.1\n"
DIGEST = hashlib.sha256(SOURCE).hexdigest()


def manifest():
    return {"source_gcode_sha256": DIGEST,
            "layers": [{"z_mm": 2.4, "candidate_segments": 1}],
            "candidate": {"scope": "top-surface-only", "display_z_mm": 2.4,
                          "true_interpolated_z_mm": 2.3, "display_width_mm": 0.4,
                          "segment_count": 1,
                          "segments": [{"start_xy_mm": [0, 0], "end_xy_mm": [2, 0]}]}}


class LayeredPreviewOverlapAuditTests(unittest.TestCase):
    def test_crossing_segment_has_zero_centerline_distance(self):
        self.assertEqual(centerline_distance((0, 1, 4, 1), (2, 0, 2, 2)), 0)

    def test_parallel_segment_uses_finite_separation(self):
        self.assertEqual(centerline_distance((0, 1, 4, 1), (0, 1.5, 4, 1.5)), 0.5)

    def test_nearby_short_segment_does_not_extrapolate(self):
        self.assertEqual(centerline_distance((0, 1, 4, 1), (5, 0, 5, 2)), 1)

    def test_overlapping_horizontal_segments_have_zero_distance(self):
        self.assertEqual(centerline_distance((0, 1, 4, 1), (2, 1, 6, 1)), 0)

    def test_degenerate_candidate_fails_closed(self):
        with self.assertRaises(ValueError):
            centerline_distance((1, 1, 1, 1), (0, 0, 2, 2))

    def test_unpinned_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unpinned source"):
            source_segments(b"G1 X1 Y1 E1\n")

    @patch("tools.audit_layered_preview_overlap.SOURCE_SHA256", DIGEST)
    def test_projected_overlapping_candidate_is_rejected_without_print_authorization(self):
        result = audit(SOURCE, manifest())
        self.assertEqual(result["state"], "rejected")
        self.assertEqual(result["reason"], "projected-Z-and-footprint-overlap")
        self.assertEqual(len(result["paths"]), 1)
        self.assertTrue(all(row["footprint_clearance_mm"] < 0 for row in result["paths"]))
        self.assertFalse(result["printable_authorized"])

    @patch("tools.audit_layered_preview_overlap.SOURCE_SHA256", DIGEST)
    def test_missing_candidate_segments_fail_closed(self):
        data = manifest()
        data["candidate"]["segments"].pop()
        with self.assertRaisesRegex(ValueError, "segment count mismatch"):
            audit(SOURCE, data)
        data["candidate"]["segments"] = []
        with self.assertRaisesRegex(ValueError, "segment count mismatch"):
            audit(SOURCE, data)


if __name__ == "__main__":
    unittest.main()
