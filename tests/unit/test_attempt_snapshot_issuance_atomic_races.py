"""ADR-0065 adversarial in-process atomic-pair tests; no Orca filesystem integration."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import unittest
from unittest.mock import patch

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState
from tests.unit.test_stores import plan


class AtomicAttemptIssuanceRaces(unittest.TestCase):
    def test_reset_waits_until_attempt_pair_is_fully_published(self):
        store, attempts = PlanStore(2), InjectionAttemptStore()
        store.publish(plan(11001, injectable=True))
        begin_entered, release_begin = Event(), Event()
        reset_finished = Event()
        real_begin = attempts.begin
        def paused_begin(plan_hash, identity):
            begin_entered.set()
            if not release_begin.wait(4):
                raise AssertionError("bounded test gate never released")
            return real_begin(plan_hash, identity)
        with patch.object(attempts, "begin", side_effect=paused_begin):
            with ThreadPoolExecutor(max_workers=2) as executor:
                pairing = executor.submit(store.begin_postprocess_attempt, attempts, "working-file")
                try:
                    self.assertTrue(begin_entered.wait(4))
                    def reset():
                        value = store.reset()
                        reset_finished.set()
                        return value
                    reset_future = executor.submit(reset)
                    # The lock cannot be acquired while attempt record creation is paused.
                    self.assertFalse(store._lock.acquire(blocking=False))
                    self.assertFalse(reset_finished.is_set())
                finally:
                    release_begin.set()
                issued, record = pairing.result(timeout=4)
                reset_future.result(timeout=4)
        self.assertEqual(record.state, AttemptState.STARTED)
        self.assertEqual(len(issued.candidates), 1)
        self.assertEqual(store.eligible(issued), ())
        self.assertEqual(attempts.snapshot(), (record,))

    def test_failed_pair_creation_releases_lock_and_has_no_record_or_epoch_change(self):
        store, attempts = PlanStore(2), InjectionAttemptStore()
        published = store.publish(plan(11002, injectable=True))
        epoch_before = store.plugin_session_epoch
        with patch.object(attempts, "begin", side_effect=ContractError(
            ReasonCode.INVALID_STATE_TRANSITION, "synthetic rejection")):
            with self.assertRaises(ContractError):
                store.begin_postprocess_attempt(attempts, "working-file")
        self.assertEqual(store.plugin_session_epoch, epoch_before)
        self.assertEqual(store.snapshot().candidates, (published,))
        self.assertEqual(attempts.snapshot(), ())
        # A subsequent valid call is not blocked by a prior failure.
        issued, record = store.begin_postprocess_attempt(attempts, "working-file")
        self.assertEqual(store.eligible(issued), (published.plan,))
        self.assertIs(record.state, AttemptState.STARTED)

    def test_two_distinct_stores_do_not_accept_each_others_issued_snapshot(self):
        first, second = PlanStore(1), PlanStore(1)
        attempts = InjectionAttemptStore()
        same_plan = plan(11003, injectable=True)
        first.publish(same_plan)
        second.publish(same_plan)
        snap_one, attempt_one = first.begin_postprocess_attempt(attempts, "one")
        snap_two, attempt_two = second.begin_postprocess_attempt(attempts, "two")
        self.assertEqual(first.eligible(snap_one), (same_plan,))
        self.assertEqual(second.eligible(snap_two), (same_plan,))
        self.assertEqual(first.eligible(snap_two), ())
        self.assertEqual(second.eligible(snap_one), ())
        self.assertNotEqual(attempt_one.attempt_id, attempt_two.attempt_id)


if __name__ == "__main__":
    unittest.main()
