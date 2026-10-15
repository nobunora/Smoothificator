"""Five ADR-0045/0050/0059/0063 value-contract boundaries, research-only."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import (
    CandidateSegmentRegularityPolicy, ErrorEstimatorConfig, MeshSectionPolicy,
    PluginSettings, SurfaceCorrespondencePolicy, ToolClearanceProfile, ToolRadialKeepOut,
)
from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree
from tests.unit.test_estimator_settings import estimator, correspondence
from tests.unit.test_mesh_section_policy import mesh_section_policy


class SettingsBoundaryMatrix(unittest.TestCase):
    def test_tool_radial_keepout_tip_height_and_clearance(self):
        tip = ToolRadialKeepOut(0, 0.4)
        self.assertEqual(tip.height_above_tip_mm, 0)
        with self.assertRaises(FrozenInstanceError):
            tip.radial_clearance_mm = 1.0
        for field, value in (
            ("height_above_tip_mm", -0.001),
            ("height_above_tip_mm", math.nan),
            ("radial_clearance_mm", 0),
            ("radial_clearance_mm", math.inf),
            ("radial_clearance_mm", True),
        ):
            with self.subTest(field=field), self.assertRaises(ContractError) as err:
                replace(tip, **{field: value})
            self.assertEqual(err.exception.reason, ReasonCode.INVALID_SETTING)

    def test_profile_height_curve_order_and_identity_evidence(self):
        profile = ToolClearanceProfile(
            "tip-profile", "1", "research-evidence",
            12., .1, .2, (ToolRadialKeepOut(0, .4),
                          ToolRadialKeepOut(6, .7), ToolRadialKeepOut(12, 1.2)))
        self.assertEqual(len(profile.radial_keep_out), 3)
        for changed in (
            {"radial_keep_out": (ToolRadialKeepOut(0, .4), ToolRadialKeepOut(0, 1.2))},
            {"radial_keep_out": (ToolRadialKeepOut(0, .4), ToolRadialKeepOut(13, 1.2))},
            {"radial_keep_out": (ToolRadialKeepOut(1, .4),)},
            {"radial_keep_out": []}, {"profile_id": "  "},
            {"fixture_evidence_ref": None}, {"axial_height_mm": 0},
        ):
            with self.subTest(fields=tuple(changed)), self.assertRaises(ContractError):
                replace(profile, **changed)

    def test_regularity_research_limits_allow_zero_maxima_but_require_positive_minima(self):
        baseline = CandidateSegmentRegularityPolicy(
            "research", None, .02, .001, 0., 0., 0.)
        s = PluginSettings("1", .05, .08, .01, baseline)
        self.assertIsNone(s.tool_clearance_profile)
        for field, bad in (
            ("min_candidate_segment_length_mm", 0),
            ("min_candidate_segment_time_s", 0),
            ("max_adjacent_width_step_mm", -.001),
            ("max_adjacent_effective_height_step_mm", math.nan),
            ("fixture_evidence_ref", {}),
        ):
            with self.subTest(field=field), self.assertRaises(ContractError):
                replace(baseline, **{field: bad})
        self.assertNotEqual(fingerprint_plugin_settings(s),
                            fingerprint_plugin_settings(replace(s,
                                regularity_policy=replace(baseline, max_adjacent_width_step_mm=.02))))

    def test_surface_correspondence_normal_extrema_and_ray_version(self):
        policy = correspondence()
        for threshold in (-1., 1.):
            with self.subTest(threshold=threshold):
                self.assertEqual(replace(policy, min_surface_normal_dot=threshold).min_surface_normal_dot,
                                 threshold)
        with self.assertRaises(ContractError):
            replace(policy, min_surface_normal_dot=1.001)
        with self.assertRaises(ContractError):
            replace(policy, normal_ray_numeric_tolerance_mm=0)
        changed = replace(policy, normal_ray_numeric_policy_version="different-research-version")
        self.assertNotEqual(canonical_bytes(semantic_tree(policy)),
                            canonical_bytes(semantic_tree(changed)))

    def test_estimator_and_section_policy_explicit_versioned_bounds(self):
        e, section = estimator(), mesh_section_policy()
        self.assertEqual(e.max_error_refinement_levels, 4)
        with self.assertRaises(ContractError):
            replace(e, max_error_refinement_levels=True)
        with self.assertRaises(ContractError):
            replace(e, error_refinement_factor=1.0)
        with self.assertRaises(ContractError):
            replace(e, error_metric_convergence_mm=0)
        with self.assertRaises(ContractError):
            replace(section, coplanar_section_epsilon_mm=0)
        changed = replace(section, section_stability_sampling_convergence_version="new-fixture")
        self.assertNotEqual(canonical_bytes(semantic_tree(changed)),
                            canonical_bytes(semantic_tree(section)))


if __name__ == "__main__":
    unittest.main()
