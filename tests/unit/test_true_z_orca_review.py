"""Research viewer input contract; no printable G-code permission."""

import unittest

from tools.build_true_z_orca_review import _candidate_rows, SCHEMA


def plan():
    return {"schema": SCHEMA, "source_slice_sha256": "source",
            "segments": [{"id": "upper-1", "reason": "top-surface",
                          "start_mm": [120, 125, 2.3], "end_mm": [130, 125, 2.3],
                          "width_mm": 0.4,
                          "bead_height_mm": 0.1,
                          "nearest_higher_footprint_clearance_mm": 0.2,
                          "higher_footprint_overlap": False,
                          "sampled_effective_height_mm": 0.1,
                          "sampled_support_top_z_mm": 2.2,
                          "sampled_nominal_minimum_top_z_mm": 2.2,
                          "continuous_contact_verified": True,
                          "sampled_support_complete": True,
                          "minimum_effective_height_mm": 0.08,
                          "review_status": "candidate-for-review"}]}


class TrueZOrcaReviewTests(unittest.TestCase):
    def test_true_z_is_retained(self):
        rows = _candidate_rows(plan(), "source")
        self.assertEqual(rows[0][0], 2.3)
        self.assertEqual(rows[0][1:5], (120, 125, 130, 125))

    def test_projected_or_sloped_z_is_rejected(self):
        data = plan()
        data["segments"][0]["end_mm"][2] = 2.4
        with self.assertRaisesRegex(ValueError, "true-Z"):
            _candidate_rows(data, "source")

    def test_non_top_or_printable_plan_is_rejected(self):
        data = plan()
        data["segments"][0]["reason"] = "underside"
        with self.assertRaisesRegex(ValueError, "top-surface"):
            _candidate_rows(data, "source")
        data = plan()
        data["printable_authorized"] = True
        with self.assertRaisesRegex(ValueError, "unauthorized"):
            _candidate_rows(data, "source")

    def test_source_mismatch_and_duplicate_identity_rejected(self):
        data = plan()
        with self.assertRaisesRegex(ValueError, "unauthorized"):
            _candidate_rows(data, "other")
        data["segments"].append(dict(data["segments"][0]))
        with self.assertRaisesRegex(ValueError, "true-Z"):
            _candidate_rows(data, "source")

    def test_overlapping_higher_layer_candidate_is_excluded(self):
        data = plan()
        data["segments"].append({"id": "upper-2", "reason": "top-surface",
                                 "start_mm": [120, 124, 2.34], "end_mm": [130, 124, 2.34],
                                 "width_mm": 0.4,
                                 "bead_height_mm": 0.14,
                                 "nearest_higher_footprint_clearance_mm": -0.1,
                                 "higher_footprint_overlap": True,
                                 "sampled_effective_height_mm": 0.14,
                                 "sampled_support_top_z_mm": 2.2,
                                 "sampled_nominal_minimum_top_z_mm": None,
                                 "continuous_contact_verified": False,
                                 "sampled_support_complete": True,
                                 "minimum_effective_height_mm": 0.08,
                                 "review_status": "higher-footprint-overlap"})
        self.assertEqual(len(_candidate_rows(data, "source")), 1)

    def test_thin_bead_is_excluded(self):
        data = plan()
        data["segments"][0]["sampled_effective_height_mm"] = 0.02
        data["segments"][0]["sampled_support_top_z_mm"] = 2.28
        data["segments"][0]["bead_height_mm"] = 0.08
        data["segments"][0]["review_status"] = "below-minimum-height"
        with self.assertRaisesRegex(ValueError, "no height-and-footprint review candidates"):
            _candidate_rows(data, "source")

    def test_nominal_support_valley_excludes_floating_bead(self):
        data = plan()
        data["segments"][0]["sampled_nominal_minimum_top_z_mm"] = 2.16131
        data["segments"][0]["review_status"] = "nominal-support-valley"
        with self.assertRaisesRegex(ValueError, "no height-and-footprint review candidates"):
            _candidate_rows(data, "source")
        data["segments"][0]["review_status"] = "candidate-for-review"
        with self.assertRaisesRegex(ValueError, "classification mismatch"):
            _candidate_rows(data, "source")

    def test_sampled_contact_cannot_enable_green_viewer_line(self):
        data = plan()
        data["segments"][0]["continuous_contact_verified"] = False
        data["segments"][0]["review_status"] = "continuous-contact-unverified"
        with self.assertRaisesRegex(ValueError, "no height-and-footprint review candidates"):
            _candidate_rows(data, "source")

    def test_effective_height_must_match_support_top(self):
        data = plan()
        data["segments"][0]["sampled_support_top_z_mm"] = 2.1
        with self.assertRaisesRegex(ValueError, "invalid true-Z"):
            _candidate_rows(data, "source")


if __name__ == "__main__":
    unittest.main()
