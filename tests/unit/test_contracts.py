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

    def test_settings_identity_types_are_strict_and_immutable(self):
        policy = research_policy()
        invalid_policies = (
            lambda: CandidateSegmentRegularityPolicy(1, None, .02, .001, 1, .01, .01),
            lambda: CandidateSegmentRegularityPolicy("r", {"mutable": True}, .02, .001, 1, .01, .01),
            lambda: CandidateSegmentRegularityPolicy("r", "  ", .02, .001, 1, .01, .01),
            lambda: CandidateSegmentRegularityPolicy("  ", None, .02, .001, 1, .01, .01),
        )
        for make in invalid_policies:
            with self.subTest(make=make), self.assertRaises(ContractError):
                make()
        with self.assertRaises(ContractError):
            PluginSettings("1", .05, .08, .01, policy, tool_clearance_profile={"mutable": True})
        with self.assertRaises(ContractError):
            PluginSettings(1, .05, .08, .01, policy)
        for value in ([1], {"mutable": True}, "  "):
            with self.subTest(value=value), self.assertRaises(ContractError):
                ToolClearanceProfile("profile", "1", value, 12., .1, .1,
                                     (ToolRadialKeepOut(0, .4),))
        with self.assertRaises(ContractError):
            ToolClearanceProfile("profile", "1", "evidence", 12., .1, .1,
                                 ({"mutable": True},))
        good = ToolClearanceProfile("profile", "1", "fixture:measured", 12., .1, .1,
                                    (ToolRadialKeepOut(0, .4),))
        self.assertIs(PluginSettings("1", .05, .08, .01, policy, good).tool_clearance_profile, good)

    def test_tool_profile_is_only_explicit_value_model(self):
        profile = ToolClearanceProfile("tool-a", "1", "measurement://fixture-a",
            12.0, 0.1, 0.2, (ToolRadialKeepOut(0, 0.4), ToolRadialKeepOut(12, 1.4)))
        self.assertEqual(profile.radial_keep_out[-1].height_above_tip_mm, 12)
        with self.assertRaises(ContractError):
            ToolClearanceProfile("tool-a", "1", "evidence", 12.0, .1, .2, (ToolRadialKeepOut(1, .4),))

    def test_nested_plan_payload_validation(self):
        from adaptive_subedge.domain.plan import PlanSemanticContent
        from adaptive_subedge.domain.metrics import ErrorMetrics
        from adaptive_subedge.application.hashing import typed_identity
        sr = typed_identity("source-geometry", {"mesh": 1})
        ex = typed_identity("execution-config", {"flow": 1.0})
        pl = typed_identity("plugin-settings", {"policy": "research"})
        with self.assertRaises(ContractError):
            PlanSemanticContent("0.5", "research", sr, ex, pl, (), ("not-a-path",),
                                (), ErrorMetrics(.01, .01, .01, 0.0), 0.0, 0.0, 0.0,
                                False, "analysis-only")

    def test_rejects_mutable_nested_immutables(self):
        from adaptive_subedge.domain.geometry import StructuralLoopReference, PrintPoint3
        from adaptive_subedge.domain.plan import InsertionAnchor, FinalSurfaceEnvelope, ChronologicalSupportEnvelope
        with self.assertRaises(ContractError):
            FinalSurfaceEnvelope(["live-list"], ())
        with self.assertRaises(ContractError):
            ChronologicalSupportEnvelope((), [], "candidate")
        with self.assertRaises(ContractError):
            InsertionAnchor("anchor", (["not-hashable"],), 2, "layer")
        with self.assertRaises(ContractError):
            StructuralLoopReference("l", (PrintPoint3(0, 0, 0), "wrong", PrintPoint3(1, 0, 0)), 0, "shape")
        with self.assertRaises(ContractError):
            SubEdgePath("p", "interval", .2, 0, 0,
                (SubEdgeSegment(PrintPoint2(0, 0), PrintPoint2(1, 0), .2, .1, .1, .4, .03, .029, 30),),
                (["bad-id"],))

    def test_huge_ints_fail_with_typed_contract_error(self):
        from adaptive_subedge.domain.metrics import ErrorMetrics
        giant = 10 ** 400
        checks = (
            lambda: PrintPoint2(giant, 0),
            lambda: ErrorMetrics(giant, .01, .01, 0),
            lambda: PluginSettings("1", giant, .08, .01, research_policy()),
            lambda: CandidateSegmentRegularityPolicy("r", None, giant, .001, 1., .01, .01),
        )
        for factory in checks:
            with self.subTest(factory=factory), self.assertRaises(ContractError):
                factory()

    def test_structural_segment_rejects_mutable_fields(self):
        from adaptive_subedge.domain.geometry import PrintPoint3, StructuralPathSegment
        start, end = PrintPoint3(0, 0, 0), PrintPoint3(1, 0, 0)
        with self.assertRaises(ContractError):
            StructuralPathSegment([0, 0, 0], end, .4, .2, .03, 1., 0, "outer")
        with self.assertRaises(ContractError):
            StructuralPathSegment(start, end, .4, .2, .03, 1., 0, {"mutable": True})
        valid = StructuralPathSegment(start, end, .4, .2, .03, 1., 0, "outer")
        self.assertIs(valid.start, start)

    def test_plan_identity_labels_reject_mutable_values(self):
        from dataclasses import replace
        from tests.unit.test_canonical import plan_content
        plan = plan_content()
        for wrong in ([1], {"mutable": True}, True):
            with self.subTest(wrong=wrong), self.assertRaises(ContractError):
                replace(plan, compatibility_descriptor_id=wrong)
            with self.subTest(version=wrong), self.assertRaises(ContractError):
                replace(plan, plugin_version=wrong)

    def test_candidate_point_type_must_match_registered_serializer(self):
        from adaptive_subedge.domain.geometry import PrintPoint2
        class ExtendedPoint(PrintPoint2):
            pass
        a, b = ExtendedPoint(0, 0), PrintPoint2(1, 0)
        with self.assertRaises(ContractError):
            SubEdgeSegment(a, b, .2, .1, .1, .4, .03, .029, 30)

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
