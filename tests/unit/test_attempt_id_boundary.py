"""ADR-0037 expected typed failure for malformed attempt IDs at store boundary."""
import unittest

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState


class AttemptIdBoundary(unittest.TestCase):
    def test_nonhashable_and_wrong_attempt_ids_fail_with_stable_reason(self):
        class Subclass(str):
            pass
        store = InjectionAttemptStore()
        first = store.begin(None, "synthetic-file")
        for bad in ([], {}, set(), None, 0, True, b"abc", "", Subclass(first.attempt_id)):
            with self.subTest(bad_type=type(bad).__name__), self.assertRaises(ContractError) as caught:
                store.transition(bad, AttemptState.VALIDATED)
            self.assertEqual(caught.exception.reason, ReasonCode.INVALID_STATE_TRANSITION)
            self.assertEqual(store.snapshot(), (first,))

    def test_unknown_valid_string_id_fails_with_same_stable_reason(self):
        store = InjectionAttemptStore()
        started = store.begin(None, "synthetic-file")
        with self.assertRaises(ContractError) as caught:
            store.transition("unknown-otherwise-valid-id", AttemptState.VALIDATED)
        self.assertEqual(caught.exception.reason, ReasonCode.INVALID_STATE_TRANSITION)
        self.assertEqual(store.snapshot(), (started,))

    def test_valid_identical_attempt_id_still_transitions_without_reason(self):
        store = InjectionAttemptStore()
        started = store.begin(None, "synthetic-file")
        updated = store.transition(started.attempt_id, AttemptState.VALIDATED)
        self.assertEqual(updated.attempt_id, started.attempt_id)
        self.assertEqual(updated.state, AttemptState.VALIDATED)
        self.assertIsNone(updated.reason)
        self.assertEqual(store.snapshot(), (updated,))


if __name__ == "__main__":
    unittest.main()
