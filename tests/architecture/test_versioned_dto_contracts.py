"""Phase 0.5 schema inclusion audit: new research DTOs cannot silently mutate v1."""
from dataclasses import fields
import unittest

from adaptive_subedge.application.serialization import _FIELDS, canonical_bytes, semantic_tree
from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import (
    PluginSettings, CandidateSegmentRegularityPolicy,
    SurfaceCorrespondencePolicy, ErrorEstimatorConfig, MeshSectionPolicy,
)


class VersionedDTOArchitectureTests(unittest.TestCase):
    def test_registered_research_dtos_have_exact_serializable_fields(self):
        for cls in (SurfaceCorrespondencePolicy, ErrorEstimatorConfig, MeshSectionPolicy):
            with self.subTest(cls=cls.__name__):
                self.assertIn(cls, _FIELDS)
                self.assertEqual(_FIELDS[cls], tuple(field.name for field in fields(cls)))

    def test_plugin_settings_v1_fields_have_not_silently_expanded(self):
        expected = (
            "schema_version", "surface_error_tolerance_mm",
            "minimum_effective_bead_height_mm", "candidate_seam_gap_mm",
            "regularity_policy", "tool_clearance_profile",
            "physical_injection_requested",
        )
        self.assertEqual(tuple(f.name for f in fields(PluginSettings)), expected)
        self.assertEqual(_FIELDS[PluginSettings], expected)
        self.assertNotIn(ErrorEstimatorConfig, (f.type for f in fields(PluginSettings)))
        self.assertNotIn(SurfaceCorrespondencePolicy, (f.type for f in fields(PluginSettings)))
        self.assertNotIn(MeshSectionPolicy, (f.type for f in fields(PluginSettings)))

    def test_incomplete_v2_cannot_be_mislabeled_as_v1_settings_fingerprint(self):
        from adaptive_subedge.application.serialization import identity_root
        from adaptive_subedge.domain.settings import ErrorEstimatorConfig, SurfaceCorrespondencePolicy
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(ErrorEstimatorConfig)
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(SurfaceCorrespondencePolicy)
        with self.assertRaises(ContractError):
            identity_root("plugin-settings", {"partial": 1}, schema_version="2")
        with self.assertRaises(ContractError):
            identity_root("plugin-settings", {"partial": 1}, canonical_encoding_version="2")

    def test_versioned_research_values_not_implicitly_part_of_v1(self):
        from adaptive_subedge.domain.settings import MeshSectionPolicy
        from adaptive_subedge.application.serialization import identity_root, validate_root
        baseline = PluginSettings("1", 0.05, 0.08, 0.01,
            CandidateSegmentRegularityPolicy("research", None, 0.01, 0.001, 1.0, 0.01, 0.01))
        identity = fingerprint_plugin_settings(baseline)
        metadata = identity_root("plugin-settings", baseline)
        self.assertEqual(set(metadata), {"identity_type", "schema_version", "canonical_encoding_version", "payload"})
        self.assertEqual(metadata["schema_version"], "1")
        self.assertEqual(identity.schema_version, "1")
        self.assertNotIn("mesh_section_policy", metadata["payload"])
        self.assertNotIn("error_estimator_config", metadata["payload"])
        validate_root(metadata, "plugin-settings")
        with self.assertRaises(ContractError):
            validate_root({**metadata, "undocumented": 1}, "plugin-settings")

    def test_physical_enablement_stays_disallowed(self):
        policy = CandidateSegmentRegularityPolicy("research-only", None, 0.01, 0.001, 1.0, 0.01, 0.01)
        settings = PluginSettings("1", 0.05, 0.08, 0.01, policy)
        self.assertEqual(settings.schema_version, "1")
        self.assertTrue(canonical_bytes(semantic_tree(settings)))
        self.assertEqual(fingerprint_plugin_settings(settings),
                         fingerprint_plugin_settings(PluginSettings("1", 0.05, 0.08, 0.01, policy)))
        with self.assertRaises(ContractError) as ctx:
            settings.require_physical_injection()
        self.assertEqual(ctx.exception.reason, ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
