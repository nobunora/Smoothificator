"""Frozen DTO, fixture evidence and defensive validation."""
import unittest
from dataclasses import FrozenInstanceError
from adaptive_subedge.domain.geometry import PrintPoint2, PrintPoint3
from adaptive_subedge.domain.plan import SubEdgeSegment, SubEdgePath
from adaptive_subedge.domain.settings import (
    CandidateSegmentRegularityPolicy, PluginSettings, ToolClearanceProfile, ToolRadialKeepOut,
)
from adaptive_subedge.domain.errors import ContractError, ReasonCode


def research_policy():
    return CandidateSegmentRegularityPolicy("research-1", None, .02, .001, 1.0, .01, .01)


class ContractTests(unittest.TestCase):
    def test_frozen_points_and_coordinate_gate(self):
        p = PrintPoint2(1.0, 2.0)
        with self.assertRaises(FrozenInstanceError):
            p.x_mm = 3.0
        with self.assertRaises(ContractError):
            PrintPoint3(0.0, float("nan"), 1.0)

    def test_settings_reject_nonfinite_and_physical(self):
        self.assertIsNone(PluginSettings("1", .05, .08, .01, research_policy()).tool_clearance_profile)
        with self.assertRaises(ContractError):
            PluginSettings("1", float("nan"), .08, .01, research_policy())
        with self.assertRaises(ContractError) as e:
            PluginSettings("1", .05, .08, .01, research_policy(), physical_injection_requested=True)
        self.assertEqual(e.exception.reason, ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED)
        with self.assertRaises(ContractError):
            CandidateSegmentRegularityPolicy("r", None, -.01, .001, 1.0, .01, .01)

    def test_tool_profile_is_only_explicit_value_model(self):
        profile = ToolClearanceProfile("tool-a", "1", "measurement://fixture-a",
            12.0, 0.1, 0.2, (ToolRadialKeepOut(0, 0.4), ToolRadialKeepOut(12, 1.4)))
        self.assertEqual(profile.radial_keep_out[-1].height_above_tip_mm, 12)
        with self.assertRaises(ContractError):
            ToolClearanceProfile("tool-a", "1", "evidence", 12.0, .1, .2, (ToolRadialKeepOut(1, .4),))

    def test_candidate_constant_z_and_local_flow(self):
        a = PrintPoint2(0, 0)
        b = PrintPoint2(1, 0)
        seg = SubEdgeSegment(a, b, .2, .1, .1, .4, .03, .029, 30)
        self.assertEqual(SubEdgePath("p", "interval", .2, .01, 0, (seg,)).segments[0], seg)
        with self.assertRaises(ContractError):
            SubEdgePath("p", "interval", .3, .01, 0, (seg,))
        with self.assertRaises(ContractError):
            SubEdgeSegment(a, a, .2, .1, .1, .4, .03, .029, 30)


if __name__ == "__main__":
    unittest.main()
