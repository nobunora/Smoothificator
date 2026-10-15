"""Four ADR-0065 atomic in-process publication/attempt edge cases (no Orca hook)."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import patch
import unittest

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState
from tests.unit.test_stores import plan


class AttemptEpochMatrix(unittest.TestCase):
    def test_preview_only_snapshot_stays_empty_after_later_injectable_publication(self):
        store,attempts=PlanStore(2),InjectionAttemptStore()
        store.publish(plan(12001,injectable=False))
        first,record=store.begin_postprocess_attempt(attempts,"export-before")
        self.assertEqual(first.candidates,())
        newer=plan(12002,injectable=True)
        store.publish(newer)
        self.assertEqual(store.eligible(first),())
        second,record2=store.begin_postprocess_attempt(attempts,"export-after")
        self.assertEqual(store.eligible(second),(newer,))
        self.assertNotEqual(record.attempt_id,record2.attempt_id)

    def test_new_publication_waits_for_atomic_attempt_pair_issuance(self):
        store,attempts=PlanStore(3),InjectionAttemptStore()
        old=plan(12003,injectable=True)
        new=plan(12004,injectable=True)
        store.publish(old)
        entered,release=Event(),Event()
        real_begin=attempts.begin
        def paused(*args):
            entered.set()
            if not release.wait(4):
                raise AssertionError("test gate not released")
            return real_begin(*args)
        with patch.object(attempts,"begin",side_effect=paused):
            with ThreadPoolExecutor(max_workers=2) as executor:
                paired=executor.submit(store.begin_postprocess_attempt,attempts,"old-export")
                try:
                    self.assertTrue(entered.wait(4))
                    publish=executor.submit(store.publish,new)
                    self.assertFalse(store._lock.acquire(blocking=False))
                finally:
                    release.set()
                held,record=paired.result(timeout=4)
                publish.result(timeout=4)
        self.assertEqual(store.eligible(held),(old,))
        self.assertEqual(store.eligible(store.snapshot()),(old,new))
        self.assertIs(record.state,AttemptState.STARTED)

    def test_failed_pair_issuance_restores_weak_registry_and_keeps_existing_status(self):
        store,attempts=PlanStore(1),InjectionAttemptStore()
        old=plan(12005,injectable=True)
        store.publish(old)
        held,earlier=store.begin_postprocess_attempt(attempts,"earlier-file")
        count=len(store._issued_snapshots)
        with patch.object(attempts,"begin",side_effect=ContractError(
                ReasonCode.INVALID_STATE_TRANSITION,"synthetic reject")):
            with self.assertRaises(ContractError):
                store.begin_postprocess_attempt(attempts,"rejected-file")
        self.assertEqual(len(store._issued_snapshots),count)
        self.assertEqual(store.eligible(held),(old,))
        self.assertEqual(attempts.snapshot(),(earlier,))

    def test_new_generation_and_matching_plan_hash_do_not_change_previous_attempt(self):
        store,attempts=PlanStore(2),InjectionAttemptStore()
        original=plan(12006,injectable=True)
        first=store.publish(original)
        held,attempt=store.begin_postprocess_attempt(attempts,"export")
        nextgen=store.publish(original)
        self.assertGreater(nextgen.analysis_generation_id,first.analysis_generation_id)
        self.assertEqual(nextgen.plan.plan_hash,first.plan.plan_hash)
        self.assertEqual(store.eligible(held),(original,))
        self.assertEqual(store.eligible(store.snapshot()),(original,))
        self.assertEqual(attempts.snapshot(),(attempt,))


if __name__=="__main__":
    unittest.main()
