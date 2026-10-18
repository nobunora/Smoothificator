"""ADR-0023/0062 v1 declared-field sensitivity; not a v2 migration test."""
from dataclasses import replace
import unittest

from adaptive_subedge.application.hashing import fingerprint_plugin_settings, typed_identity
from adaptive_subedge.domain.settings import (
    CandidateSegmentRegularityPolicy, PluginSettings, ToolClearanceProfile, ToolRadialKeepOut,
)


def configured_v1():
    regularity = CandidateSegmentRegularityPolicy("research", "research-fixture",
                                                   0.02, 0.001, 1.0, 0.01, 0.01)
    profile = ToolClearanceProfile("fixture-tool", "1", "evidence-id", 12.0, 0.1, 0.2,
                                   (ToolRadialKeepOut(0, 0.4), ToolRadialKeepOut(12, 1.4)))
    return PluginSettings("1", 0.05, 0.08, 0.01, regularity, profile)


class SettingsV1SensitivityTests(unittest.TestCase):
    def test_every_declared_tool_profile_field_changes_fingerprint(self):
        original = configured_v1()
        fp = fingerprint_plugin_settings(original)
        profile = original.tool_clearance_profile
        changes = {
            "profile_id": "different-tool",
            "version": "2",
            "fixture_evidence_ref": "evidence-remeasured",
            "axial_height_mm": 13.0,
            "radial_safety_margin_mm": 0.11,
            "vertical_safety_margin_mm": 0.21,
            "radial_keep_out": (ToolRadialKeepOut(0, 0.4), ToolRadialKeepOut(12, 1.41)),
        }
        for field, changed in changes.items():
            with self.subTest(field=field):
                settings = replace(original, tool_clearance_profile=replace(profile, **{field: changed}))
                self.assertNotEqual(fingerprint_plugin_settings(settings).digest_hex, fp.digest_hex)

    def test_top_level_v1_settings_field_changes_fingerprint(self):
        original = configured_v1()
        digest = fingerprint_plugin_settings(original).digest_hex
        for field, change in (("surface_error_tolerance_mm", 0.06),
                              ("minimum_effective_bead_height_mm", 0.09),
                              ("candidate_seam_gap_mm", 0.02)):
            with self.subTest(field=field):
                changed = replace(original, **{field: change})
                self.assertNotEqual(fingerprint_plugin_settings(changed).digest_hex, digest)
        self.assertEqual(fingerprint_plugin_settings(original).digest_hex, digest)

    def test_canonical_semantic_list_tuple_equivalent_but_ordered(self):
        a = typed_identity("source-geometry", {"polyline": (1, 2, 3)})
        b = typed_identity("source-geometry", {"polyline": [1, 2, 3]})
        changed = typed_identity("source-geometry", {"polyline": [3, 2, 1]})
        self.assertEqual(a, b)
        self.assertNotEqual(a, changed)


if __name__ == "__main__":
    unittest.main()
