"""Focused geometry tests for the read-only layered-preview conflict audit."""

import json
from pathlib import Path
import unittest

from tools.audit_layered_preview_overlap import audit, centerline_distance, source_segments


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode"
MANIFEST = ROOT / "artifacts/layered-viewer/smoothificator-0f17b22cd4744c848b2e427bae9bf4bc.VIEW_ONLY.json"


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

    def test_pinned_viewer_is_rejected_without_print_authorization(self):
        result = audit(SOURCE.read_bytes(), json.loads(MANIFEST.read_text(encoding="utf-8")))
        self.assertEqual(result["state"], "rejected")
        self.assertEqual(result["reason"], "projected-Z-and-footprint-overlap")
        self.assertEqual(len(result["paths"]), 7)
        self.assertTrue(all(row["footprint_clearance_mm"] < 0 for row in result["paths"]))
        self.assertFalse(result["printable_authorized"])

    def test_missing_candidate_segments_fail_closed(self):
        source = SOURCE.read_bytes()
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["candidate"]["segments"].pop()
        with self.assertRaisesRegex(ValueError, "segment count mismatch"):
            audit(source, manifest)
        manifest["candidate"]["segments"] = []
        with self.assertRaisesRegex(ValueError, "segment count mismatch"):
            audit(source, manifest)


if __name__ == "__main__":
    unittest.main()
