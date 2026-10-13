"""Independent ADR-0062 v1 fingerprint reference; do not silently migrate schema 1."""
from dataclasses import replace
import hashlib
import unittest

from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import (
    CandidateSegmentRegularityPolicy, PluginSettings, ToolClearanceProfile, ToolRadialKeepOut,
)


def _golden_tree_bytes(value):
    """Independent test-only tagged-tree encoding from ADR-0062, NOT production serializer."""
    if value is None:
        return b"n"
    if type(value) is bool:
        return b"b1" if value else b"b0"
    if type(value) is int:
        return b"i" + str(value).encode("ascii") + b";"
    if type(value) is float:
        return b"f" + (0.0 if value == 0 else value).hex().encode("ascii") + b";"
    if type(value) is str:
        raw = value.encode("utf-8")
        return b"s" + str(len(raw)).encode("ascii") + b":" + raw
    if type(value) is list:
        return b"l" + str(len(value)).encode("ascii") + b"[" + b"".join(
            _golden_tree_bytes(x) for x in value) + b"]"
    if type(value) is dict:
        return b"m" + str(len(value)).encode("ascii") + b"{" + b"".join(
            _golden_tree_bytes(k) + _golden_tree_bytes(value[k]) for k in sorted(value)) + b"}"
    raise AssertionError("unsupported golden test value")


def v1_settings():
    policy = CandidateSegmentRegularityPolicy(
        "research-v1", None, 0.02, 0.001, 1.0, 0.01, 0.01)
    return PluginSettings("1", 0.05, 0.08, 0.01, policy)


class V1SettingsFingerprintGoldenTests(unittest.TestCase):
    def test_exact_v1_root_independently_encoded(self):
        settings = v1_settings()
        p = settings.regularity_policy
        nested_policy = {
            "version": p.version, "fixture_evidence_ref": None,
            "min_candidate_segment_length_mm": 0.02,
            "min_candidate_segment_time_s": 0.001,
            "max_adjacent_commanded_volumetric_rate_step_mm3_s": 1.0,
            "max_adjacent_width_step_mm": 0.01,
            "max_adjacent_effective_height_step_mm": 0.01,
        }
        root = {
            "identity_type": "plugin-settings",
            "schema_version": "1",
            "canonical_encoding_version": "1",
            "payload": {
                "schema_version": "1",
                "surface_error_tolerance_mm": 0.05,
                "minimum_effective_bead_height_mm": 0.08,
                "candidate_seam_gap_mm": 0.01,
                "regularity_policy": nested_policy,
                "tool_clearance_profile": None,
                "physical_injection_requested": False,
            },
        }
        expected = hashlib.sha256(
            b"AdaptiveSubEdgeCanonicalV1\0plugin-settings\0" +
            _golden_tree_bytes(root)).hexdigest()
        actual = fingerprint_plugin_settings(settings)
        self.assertEqual(actual.identity_type, "plugin-settings")
        self.assertEqual(actual.schema_version, "1")
        self.assertEqual(actual.canonical_encoding_version, "1")
        self.assertEqual(actual.digest_hex, expected)
        self.assertEqual(len(actual.digest_hex), 64)

    def test_v1_fingerprint_sensitive_to_every_declared_regularity_field(self):
        original = v1_settings()
        original_id = fingerprint_plugin_settings(original)
        changes = (
            ("version", "research-v2"),
            ("fixture_evidence_ref", "research-evidence-v1"),
            ("min_candidate_segment_length_mm", 0.03),
            ("min_candidate_segment_time_s", 0.002),
            ("max_adjacent_commanded_volumetric_rate_step_mm3_s", 2.0),
            ("max_adjacent_width_step_mm", 0.02),
            ("max_adjacent_effective_height_step_mm", 0.02),
        )
        for field, changed in changes:
            with self.subTest(field=field):
                policy = replace(original.regularity_policy, **{field: changed})
                new_settings = replace(original, regularity_policy=policy)
                self.assertNotEqual(
                    fingerprint_plugin_settings(new_settings).digest_hex,
                    original_id.digest_hex)

    def test_v1_fingerprint_distinguishes_research_hardware_profile(self):
        original = v1_settings()
        profile = ToolClearanceProfile(
            "research-tool", "1", "research-fixture-id",
            12.0, 0.1, 0.1, (ToolRadialKeepOut(0.0, 0.4),))
        candidate = replace(original, tool_clearance_profile=profile)
        self.assertNotEqual(fingerprint_plugin_settings(candidate),
                            fingerprint_plugin_settings(original))
        self.assertNotEqual(
            fingerprint_plugin_settings(replace(candidate,
                tool_clearance_profile=replace(profile, profile_id="different"))),
            fingerprint_plugin_settings(candidate))

    def test_proposed_version_does_not_activate_schema_two_or_injection(self):
        original = v1_settings()
        with self.assertRaises(ContractError) as ctx:
            replace(original, schema_version="2")
        self.assertEqual(ctx.exception.reason, ReasonCode.INVALID_SETTING)
        with self.assertRaises(ContractError):
            replace(original, physical_injection_requested=True)
        with self.assertRaises(ContractError):
            original.require_physical_injection()


if __name__ == "__main__":
    unittest.main()
