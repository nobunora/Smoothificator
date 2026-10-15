"""ADR-0064 exact content and derived full plan ID value types."""
from dataclasses import fields
import unittest

from adaptive_subedge.application.hashing import create_plan, verify_plan
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.plan import PlanSemanticContent, SubEdgePlan
from tests.unit.test_canonical import plan_content


class SubEdgePlanConstructionTests(unittest.TestCase):
    def test_valid_authoritative_plan_still_verifies(self):
        original = create_plan(plan_content())
        self.assertEqual(type(original.content), PlanSemanticContent)
        self.assertEqual(type(original.plan_hash), str)
        self.assertEqual(type(original.plan_id), str)
        self.assertEqual(original.plan_hash, original.plan_id)
        verify_plan(original)

    def test_declared_plan_content_must_be_exact_registered_dataclass(self):
        class ExtendedContent(PlanSemanticContent):
            pass
        semantic = plan_content()
        derived = ExtendedContent(**{field.name: getattr(semantic, field.name)
                                     for field in fields(semantic)})
        valid_hash = create_plan(semantic).plan_hash
        with self.assertRaises(ContractError) as err:
            SubEdgePlan(derived, valid_hash, valid_hash)
        self.assertEqual(err.exception.reason, ReasonCode.INVALID_CANONICAL_VALUE)

    def test_equal_str_subclass_plan_id_cannot_bypass_typed_contract(self):
        class DerivedHash(str):
            pass
        semantic = plan_content()
        valid_hash = create_plan(semantic).plan_hash
        with self.assertRaises(ContractError) as err:
            SubEdgePlan(semantic, valid_hash, DerivedHash(valid_hash))
        self.assertEqual(err.exception.reason, ReasonCode.INVALID_CANONICAL_VALUE)

    def test_hash_mismatch_still_rejected_during_explicit_verification(self):
        semantic = plan_content()
        invalid = SubEdgePlan(semantic, "0" * 64, "0" * 64)
        with self.assertRaises(ContractError):
            verify_plan(invalid)


if __name__ == "__main__":
    unittest.main()
