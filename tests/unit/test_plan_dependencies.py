"""ADR-0032: immutable plan dependency metadata must be chronological and closed."""
import unittest
from dataclasses import replace

from adaptive_subedge.application.hashing import create_plan, typed_identity
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.geometry import PrintPoint2
from adaptive_subedge.domain.metrics import ErrorMetrics
from adaptive_subedge.domain.plan import (
    InsertionAnchor, PlanSemanticContent, SubEdgePath, SubEdgeSegment,
)


def path(path_id: str, z: float, order: int, dependencies=()):
    line = SubEdgeSegment(
        PrintPoint2(0.0, 0.0), PrintPoint2(1.0, 0.0),
        z, z - 0.1, 0.1, 0.4, 0.03, 0.03, 25.0,
    )
    return SubEdgePath(path_id, "interval", z, 0.01, order, (line,), dependencies)


def content(paths=(), anchors=(), structural_ids=("loop-A",)):
    return PlanSemanticContent(
        "0.5", "contract-fixture",
        typed_identity("source-geometry", {"fixture": "one"}),
        typed_identity("execution-config", {"fixture": "one"}),
        typed_identity("plugin-settings", {"fixture": "one"}),
        structural_ids, paths, anchors,
        ErrorMetrics(0.01, 0.01, 0.01, 0.0),
        0.0, 0.0, 0.0, False, "analysis-only",
    )


class DependencyContractTests(unittest.TestCase):
    def test_valid_prior_lower_candidate_support_hashes(self):
        lower = path("lower", 0.2, 0)
        upper = path("upper", 0.3, 1, ("lower",))
        plan = create_plan(content((lower, upper)))
        self.assertEqual(len(plan.plan_hash), 64)

    def test_valid_support_dependency_changes_authoritative_plan_identity(self):
        lower = path("lower", 0.2, 0)
        supported = path("upper", 0.3, 1, ("lower",))
        direct_structural = replace(supported, support_dependency_path_ids=())
        with_dependency = create_plan(content((lower, supported)))
        without_dependency = create_plan(content((lower, direct_structural)))
        self.assertNotEqual(with_dependency.plan_hash, without_dependency.plan_hash)
        self.assertEqual(with_dependency.plan_id, with_dependency.plan_hash)

    def test_execution_order_change_is_part_of_plan_identity(self):
        lower = path("lower", 0.2, 0)
        upper = path("upper", 0.3, 1, ("lower",))
        original = create_plan(content((lower, upper)))
        shifted = create_plan(content((
            replace(lower, execution_order=2),
            replace(upper, execution_order=3),
        )))
        self.assertNotEqual(original.plan_hash, shifted.plan_hash)

    def test_three_level_support_dependencies_remain_acyclic_and_hashable(self):
        lower = path("lower", 0.2, 0)
        middle = path("middle", 0.3, 1, ("lower",))
        upper = path("upper", 0.4, 2, ("middle",))
        result = create_plan(content((lower, middle, upper)))
        self.assertEqual(len(result.plan_hash), 64)

    def test_same_z_paths_without_required_support_are_valid(self):
        left = path("a", 0.2, 0)
        right = path("b", 0.2, 1)
        plan = create_plan(content((left, right)))
        self.assertEqual(len(plan.plan_hash), 64)
        with self.assertRaises(ContractError):
            content((left, replace(right, support_dependency_path_ids=("a",))))

    def test_missing_dependency_is_rejected(self):
        with self.assertRaises(ContractError):
            content((path("upper", 0.3, 1, ("absent",)),))

    def test_future_dependency_is_rejected(self):
        with self.assertRaises(ContractError):
            content((path("upper", 0.3, 0, ("lower",)), path("lower", 0.2, 1)))

    def test_same_z_required_support_is_rejected(self):
        with self.assertRaises(ContractError):
            content((path("a", 0.2, 0), path("b", 0.2, 1, ("a",))))

    def test_duplicate_candidate_orders_rejected(self):
        with self.assertRaises(ContractError):
            content((path("a", 0.2, 0), path("b", 0.3, 0)))

    def test_duplicate_structural_refs_and_anchor_id_rejected(self):
        with self.assertRaises(ContractError):
            content(structural_ids=("loop-A", "loop-A"))
        anchor = InsertionAnchor("a", ("loop-A",), 1, "supported-fixture")
        with self.assertRaises(ContractError):
            content(anchors=(anchor, anchor))

    def test_unknown_anchor_loop_rejected(self):
        anchor = InsertionAnchor("a", ("loop-not-listed",), 1, "supported-fixture")
        with self.assertRaises(ContractError):
            content(anchors=(anchor,))


if __name__ == "__main__":
    unittest.main()
