"""Four v1 Settings contract isolation cases; proposed Settings v2 is not enabled."""
from dataclasses import fields, replace
import unittest

from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import (
    CandidateSegmentRegularityPolicy, ErrorEstimatorConfig, MeshSectionPolicy,
    PluginSettings, ToolClearanceProfile, ToolRadialKeepOut,
)
from tests.unit.test_v1_settings_field_sensitivity import configured_v1


class SettingsIdentityIsolationMatrix(unittest.TestCase):
    def test_semantic_v1_numeric_int_float_literals_have_identical_fingerprint(self):
        original = configured_v1()
        profile = original.tool_clearance_profile
        modified_profile = replace(profile,
            axial_height_mm=12, radial_keep_out=(ToolRadialKeepOut(0., .4),
                                                  ToolRadialKeepOut(12., 1.4)))
        modified_regular = replace(original.regularity_policy,
                                   max_adjacent_commanded_volumetric_rate_step_mm3_s=1)
        equivalent = replace(original, tool_clearance_profile=modified_profile,
                             regularity_policy=modified_regular)
        self.assertEqual(fingerprint_plugin_settings(original), fingerprint_plugin_settings(equivalent))
        self.assertEqual(canonical_bytes(semantic_tree(original)), canonical_bytes(semantic_tree(equivalent)))

    def test_version_string_subclasses_cannot_enter_any_v1_metadata(self):
        class Tagged(str):
            pass
        original = configured_v1()
        for operation in (
            lambda: replace(original, schema_version=Tagged("1")),
            lambda: replace(original.regularity_policy, version=Tagged("research")),
            lambda: replace(original.tool_clearance_profile, profile_id=Tagged("fixture-tool")),
            lambda: replace(original.tool_clearance_profile, version=Tagged("1")),
            lambda: replace(original.tool_clearance_profile,
                            fixture_evidence_ref=Tagged("evidence-id")),
        ):
            with self.subTest(operation=operation), self.assertRaises(ContractError):
                operation()

    def test_unknown_research_dtos_cannot_become_v1_settings_without_schema_review(self):
        original = configured_v1()
        wrong_settings = ({"schema_version": "1"}, ErrorEstimatorConfig, MeshSectionPolicy,
                          original.tool_clearance_profile, original.regularity_policy)
        for wrong in wrong_settings:
            with self.subTest(wrong=type(wrong).__name__), self.assertRaises(ContractError):
                fingerprint_plugin_settings(wrong)
        with self.assertRaises(ContractError):
            replace(original, tool_clearance_profile=original.regularity_policy)
        with self.assertRaises(ContractError):
            replace(original, regularity_policy=original.tool_clearance_profile)

    def test_declared_v1_fields_stay_exact_and_physical_enablement_fails_closed(self):
        original = configured_v1()
        self.assertEqual(tuple(f.name for f in fields(original)),
            ("schema_version", "surface_error_tolerance_mm",
             "minimum_effective_bead_height_mm", "candidate_seam_gap_mm",
             "regularity_policy", "tool_clearance_profile", "physical_injection_requested"))
        self.assertEqual(set(semantic_tree(original)), set(f.name for f in fields(original)))
        for bad in ("2", "", False):
            with self.subTest(version=bad), self.assertRaises(ContractError):
                replace(original, schema_version=bad)
        with self.assertRaises(ContractError) as caught:
            replace(original, physical_injection_requested=True)
        self.assertEqual(caught.exception.reason, ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
