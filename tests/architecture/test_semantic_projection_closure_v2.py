"""Four v1 canonical content ownership checks: no status/derived identity leakage."""
from dataclasses import fields, replace
import unittest

from adaptive_subedge.application.hashing import create_plan, verify_plan, typed_identity
from adaptive_subedge.application.serialization import semantic_tree, _FIELDS, canonical_bytes
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.domain.plan import PlanSemanticContent, SubEdgePlan, IdentityReference
from adaptive_subedge.domain.metrics import ErrorMetrics
from adaptive_subedge.domain.status import AttemptState, InjectionAttemptRecord
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from tests.unit.test_canonical import plan_content


class SemanticProjectionClosureV2(unittest.TestCase):
    def test_content_is_exactly_declared_semantic_fields_without_derived_identity(self):
        source = plan_content()
        tree = semantic_tree(source)
        self.assertEqual(tuple(f.name for f in fields(source)), _FIELDS[PlanSemanticContent])
        self.assertEqual(set(tree), set(_FIELDS[PlanSemanticContent]))
        for key in ("plan_hash", "plan_id", "plugin_session_epoch",
                    "analysis_generation_id", "injection_attempt_id",
                    "source_working_file_identity", "final_machine_e"):
            self.assertNotIn(key, tree)
        plan = create_plan(source)
        self.assertEqual(plan.plan_hash, plan.plan_id)
        verify_plan(plan)

    def test_plan_runtime_and_derived_dtos_are_rejected_by_semantic_tree(self):
        source = plan_content()
        plan = create_plan(source)
        attempts = InjectionAttemptStore()
        record = attempts.begin(plan.plan_hash, "synthetic")
        store = PlanStore(1)
        published = store.publish(plan)
        snap = store.snapshot()
        for bad in (plan, record, published, snap):
            with self.subTest(dto=type(bad).__name__), self.assertRaises(ContractError):
                semantic_tree(bad)
        self.assertTrue(canonical_bytes(semantic_tree(source)))

    def test_separate_attempt_transitions_and_new_store_epoch_cannot_modify_plan_hash(self):
        original = plan_content()
        expected = create_plan(original).plan_hash
        attempts = InjectionAttemptStore()
        started = attempts.begin(expected, "synthetic")
        attempts.transition(started.attempt_id, AttemptState.VALIDATED)
        attempts.transition(started.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        store = PlanStore(2)
        store.publish(create_plan(original))
        snapshot = store.snapshot()
        store.reset()
        self.assertNotEqual(snapshot.plugin_session_epoch, store.plugin_session_epoch)
        store.publish(create_plan(original))
        self.assertEqual(create_plan(original).plan_hash, expected)
        self.assertEqual(len(attempts.snapshot()), 1)

    def test_subclassed_frozen_dto_not_registered_as_semantic_payload(self):
        class DerivedMetrics(ErrorMetrics):
            pass
        class DerivedIdentity(IdentityReference):
            pass
        source = plan_content()
        metrics = source.error_metrics
        extended_metrics = DerivedMetrics(metrics.e_max_mm, metrics.e_rms_mm,
                                          metrics.e_p95_mm, metrics.signed_mean_mm)
        with self.assertRaises(ContractError):
            semantic_tree(extended_metrics)
        with self.assertRaises(ContractError):
            replace(source, error_metrics=extended_metrics)
        ident = source.source_geometry
        extended_id = DerivedIdentity(ident.identity_type, ident.schema_version,
                                      ident.canonical_encoding_version, ident.digest_hex)
        with self.assertRaises(ContractError):
            replace(source, source_geometry=extended_id)


if __name__ == "__main__":
    unittest.main()
