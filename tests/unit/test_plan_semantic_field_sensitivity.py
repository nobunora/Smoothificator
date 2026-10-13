"""ADR-0064: declared semantic plan data affect hash; no emission or physical print."""
from dataclasses import replace
import unittest

from adaptive_subedge.application.hashing import create_plan, typed_identity
from tests.unit.test_plan_dependencies import content as plan_content, path as candidate_path


def digest(content):
    return create_plan(content).plan_hash


class PlanSemanticFieldSensitivityTests(unittest.TestCase):
    def test_plugin_metadata_reason_and_injectability_affect_hash(self):
        original = plan_content()
        initial = digest(original)
        cases = (
            ("plugin_version", "0.5.1"),
            ("compatibility_descriptor_id", "alternate-research-descriptor"),
            ("reason", "different-analysis-diagnostic"),
            ("injectable", True),
        )
        for field, value in cases:
            with self.subTest(field=field):
                self.assertNotEqual(digest(replace(original, **{field: value})), initial)

    def test_each_volume_and_time_measurement_is_semantic(self):
        original = plan_content()
        expected = digest(original)
        for field, amount in (
            ("geometric_volume_mm3", 0.1),
            ("commanded_volume_mm3", 0.2),
            ("estimated_added_time_s", 1.0),
        ):
            with self.subTest(field=field):
                changed = replace(original, **{field: amount})
                self.assertNotEqual(digest(changed), expected)
        self.assertEqual(digest(original), expected)

    def test_segment_flow_width_speed_and_seam_are_semantic(self):
        baseline = candidate_path("one", 0.2, 0)
        original = plan_content(paths=(baseline,))
        reference = digest(original)
        original_segment = baseline.segments[0]
        segment_changes = (
            ("width_mm", 0.5),
            ("commanded_mm3_per_mm", 0.025),
            ("geometric_mm3_per_mm", 0.035),
            ("requested_speed_mm_s", 20.0),
        )
        for field, changed in segment_changes:
            with self.subTest(field=field):
                segment = replace(original_segment, **{field: changed})
                candidate = replace(baseline, segments=(segment,))
                self.assertNotEqual(digest(replace(original, candidate_paths=(candidate,))), reference)
        altered_gap = replace(baseline, planned_seam_gap_mm=0.02)
        self.assertNotEqual(digest(replace(original, candidate_paths=(altered_gap,))), reference)

    def test_each_typed_source_execution_settings_reference_is_semantic(self):
        baseline = plan_content()
        reference = digest(baseline)
        for field, identity_type in (
            ("source_geometry", "source-geometry"),
            ("execution_config", "execution-config"),
            ("plugin_settings", "plugin-settings"),
        ):
            with self.subTest(field=field):
                changed = replace(baseline, **{field: typed_identity(
                    identity_type, {"fixture": "changed-for-identity-only"})})
                self.assertNotEqual(digest(changed), reference)


if __name__ == "__main__":
    unittest.main()
