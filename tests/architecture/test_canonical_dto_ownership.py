"""ADR-0049/0064 exact DTO field registry and runtime-derived identity boundaries."""
from dataclasses import fields, is_dataclass
import unittest

from adaptive_subedge.application.serialization import _FIELDS, semantic_tree
from adaptive_subedge.application.plan_store import PlanSnapshot, PublishedPlan
from adaptive_subedge.domain.plan import PlanSemanticContent, SubEdgePlan
from adaptive_subedge.domain.status import InjectionAttemptRecord, AttemptState
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.application.hashing import create_plan
from tests.unit.test_canonical import plan_content


class CanonicalDtoOwnershipTests(unittest.TestCase):
    def test_all_registered_dtos_have_exact_whitelisted_fields_and_are_frozen(self):
        self.assertTrue(_FIELDS)
        for cls, registered in _FIELDS.items():
            with self.subTest(cls=cls.__name__):
                self.assertTrue(is_dataclass(cls))
                self.assertTrue(cls.__dataclass_params__.frozen)
                self.assertEqual(registered, tuple(f.name for f in fields(cls)))
                self.assertEqual(len(registered), len(set(registered)))

    def test_derived_and_runtime_dtos_never_enter_canonical_projection(self):
        plan = create_plan(plan_content())
        attempt = InjectionAttemptRecord("synthetic-attempt", plan.plan_hash,
                                         "synthetic-file", AttemptState.STARTED)
        snapshot = PlanSnapshot("synthetic-epoch", ())
        for value in (plan, attempt, snapshot):
            with self.subTest(dto=type(value).__name__), self.assertRaises(ContractError):
                semantic_tree(value)
        for cls in (SubEdgePlan, InjectionAttemptRecord, PublishedPlan, PlanSnapshot):
            self.assertNotIn(cls, _FIELDS)

    def test_plan_semantic_projection_contains_all_authorized_fields_only(self):
        content = plan_content()
        tree = semantic_tree(content)
        self.assertEqual(set(tree), set(_FIELDS[PlanSemanticContent]))
        for forbidden in ("plan_hash", "plan_id", "analysis_generation_id",
                          "injection_attempt_id", "machine_z_mm", "final_emitted_e",
                          "plugin_session_epoch", "attempt_state"):
            self.assertNotIn(forbidden, tree)
        for required in ("source_geometry", "execution_config", "plugin_settings",
                         "candidate_paths", "anchors", "injectable", "reason",
                         "error_metrics", "geometric_volume_mm3",
                         "commanded_volume_mm3", "estimated_added_time_s"):
            self.assertIn(required, tree)


if __name__ == "__main__":
    unittest.main()
