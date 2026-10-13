"""ADR-0037/0065 deterministic injected UUID collision resilience."""
import unittest
from unittest.mock import patch
from uuid import UUID

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState
from tests.unit.test_stores import plan


class AttemptUuidCollisionTests(unittest.TestCase):
    def test_duplicate_generated_id_rejected_without_overwriting_original_record(self):
        attempts = InjectionAttemptStore()
        fixed = UUID(int=42)
        with patch("adaptive_subedge.application.execution_status.uuid4", return_value=fixed):
            original = attempts.begin(None, "original-working-file")
            with self.assertRaises(ContractError) as caught:
                attempts.begin(None, "other-working-file")
        self.assertEqual(caught.exception.reason, ReasonCode.INVALID_STATE_TRANSITION)
        self.assertEqual(attempts.snapshot(), (original,))
        self.assertIs(attempts.snapshot()[0], original)
        self.assertEqual(original.source_working_file_identity, "original-working-file")
        self.assertIs(original.state, AttemptState.STARTED)

    def test_unique_identity_still_permits_later_independent_attempt(self):
        attempts = InjectionAttemptStore()
        ids = (UUID(int=70), UUID(int=70), UUID(int=71))
        with patch("adaptive_subedge.application.execution_status.uuid4", side_effect=ids):
            first = attempts.begin(None, "first")
            with self.assertRaises(ContractError):
                attempts.begin(None, "duplicate-collision")
            second = attempts.begin(None, "second")
        self.assertEqual(attempts.snapshot(), (first, second))
        self.assertNotEqual(first.attempt_id, second.attempt_id)
        self.assertEqual((first.source_working_file_identity, second.source_working_file_identity),
                         ("first", "second"))

    def test_pair_creation_fails_atomically_on_attempt_id_collision(self):
        store, attempts = PlanStore(1), InjectionAttemptStore()
        fixture = plan(13101, injectable=True)
        store.publish(fixture)
        before = store.snapshot()
        epoch = store.plugin_session_epoch
        with patch("adaptive_subedge.application.execution_status.uuid4", return_value=UUID(int=99)):
            selected, original_attempt = store.begin_postprocess_attempt(attempts, "export-1")
            with self.assertRaises(ContractError) as ctx:
                store.begin_postprocess_attempt(attempts, "export-2")
        self.assertEqual(ctx.exception.reason, ReasonCode.INVALID_STATE_TRANSITION)
        self.assertEqual(attempts.snapshot(), (original_attempt,))
        self.assertEqual(store.plugin_session_epoch, epoch)
        self.assertEqual(store.eligible(selected), (fixture,))
        self.assertEqual(store.eligible(before), (fixture,))
        self.assertEqual(store.snapshot().candidates[0].plan, fixture)


if __name__ == "__main__":
    unittest.main()
