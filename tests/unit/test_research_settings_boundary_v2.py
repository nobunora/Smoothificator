"""Four research-only frozen Settings semantics; no fixture calibration claim."""
from dataclasses import FrozenInstanceError, replace
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import (
    PluginSettings, ToolClearanceProfile, ToolRadialKeepOut,
    CandidateSegmentRegularityPolicy
)
from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree
from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from tests.unit.test_estimator_settings import estimator


class ResearchSettingsBoundaryV2(unittest.TestCase):
    def test_curve_heights_ordered_but_radius_need_not_be_monotonic(self):
        # Physical radiator shape is fixture-defined, not a guessed monotonic rule.
        profile = ToolClearanceProfile(
            "research-profile", "1", "synthetic-evidence", 12., .1, .2,
            (ToolRadialKeepOut(0, .6), ToolRadialKeepOut(4., 1.2),
             ToolRadialKeepOut(8., .9), ToolRadialKeepOut(12., 1.1)))
        self.assertEqual(len(profile.radial_keep_out), 4)
        with self.assertRaises(FrozenInstanceError):
            profile.radial_keep_out = ()
        with self.assertRaises(ContractError):
            replace(profile, radial_keep_out=tuple(reversed(profile.radial_keep_out)))

    def test_profile_requires_tip_start_and_sorted_bounded_height(self):
        profile = ToolClearanceProfile(
            "research-profile", "1", "synthetic-evidence", 12., .1, .2,
            (ToolRadialKeepOut(0, .6), ToolRadialKeepOut(8., .9)))
        for points in (
            (ToolRadialKeepOut(1., .6), ToolRadialKeepOut(8., .9)),
            (ToolRadialKeepOut(0, .6), ToolRadialKeepOut(0, .9)),
            (ToolRadialKeepOut(0, .6), ToolRadialKeepOut(13., .9)),
            (ToolRadialKeepOut(8., .9), ToolRadialKeepOut(0, .6)),
        ):
            with self.subTest(heights=tuple(p.height_above_tip_mm for p in points)), self.assertRaises(ContractError):
                replace(profile, radial_keep_out=points)

    def test_regularity_policy_evidence_identity_changes_v1_fingerprint(self):
        policy = CandidateSegmentRegularityPolicy("research-v1", None, .02, .001, 1., .01, .01)
        s = PluginSettings("1", .05, .08, .01, policy)
        evidence = replace(policy, fixture_evidence_ref="synthetic-not-physical-evidence")
        changed = replace(s, regularity_policy=evidence)
        self.assertNotEqual(fingerprint_plugin_settings(s), fingerprint_plugin_settings(changed))
        with self.assertRaises(ContractError):
            replace(policy, fixture_evidence_ref=[])
        self.assertEqual(s.physical_injection_requested, False)

    def test_standalone_estimator_is_canonical_but_not_registered_as_v1_settings(self):
        config = estimator()
        base = canonical_bytes(semantic_tree(config))
        modified = replace(config, max_error_refinement_levels=config.max_error_refinement_levels+1)
        self.assertNotEqual(base, canonical_bytes(semantic_tree(modified)))
        with self.assertRaises(ContractError) as ctx:
            fingerprint_plugin_settings(config)
        self.assertEqual(ctx.exception.reason, ReasonCode.INVALID_CANONICAL_VALUE)


if __name__ == "__main__":
    unittest.main()
