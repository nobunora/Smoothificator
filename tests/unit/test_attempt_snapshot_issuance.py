"""ADR-0065 process-local atomic eligible snapshot and independent attempt issuance."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import unittest

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState
from tests.unit.test_stores import plan


class AttemptSnapshotIssuanceTests(unittest.TestCase):
    def test_one_invocation_pairs_started_record_and_only_eligible_current_plans(self):
        store = PlanStore(3)
        status = InjectionAttemptStore()
        first = plan(10001, injectable=True)
        preview_only = plan(10002, injectable=False)
        store.publish(first)
        store.publish(preview_only)
        issued, attempt = store.begin_postprocess_attempt(status, "synthetic-working-copy")
        self.assertEqual([entry.plan.plan_hash for entry in issued.candidates], [first.plan_hash])
        self.assertEqual(store.eligible(issued), (first,))
        self.assertEqual(attempt.state, AttemptState.STARTED)
        self.assertIsNone(attempt.selected_plan_hash)
        self.assertEqual(status.snapshot(), (attempt,))
        self.assertEqual(attempt.source_working_file_identity, "synthetic-working-copy")

    def test_empty_current_epoch_still_records_unique_skippable_attempt(self):
        store = PlanStore(2)
        attempts = InjectionAttemptStore()
        one, first = store.begin_postprocess_attempt(attempts, "copy-one")
        two, second = store.begin_postprocess_attempt(attempts, "copy-two")
        self.assertEqual(one.candidates, ())
        self.assertEqual(two.candidates, ())
        self.assertNotEqual(first.attempt_id, second.attempt_id)
        self.assertEqual(store.eligible(one), ())
        self.assertEqual(store.eligible(two), ())
        self.assertEqual(len(attempts.snapshot()), 2)

    def test_rejected_file_identity_rolls_back_attempt_and_does_not_evict_plans(self):
        store, attempts = PlanStore(1), InjectionAttemptStore()
        published = store.publish(plan(10003, injectable=True))
        before = store.snapshot()
        for wrong in ([], {}, None, "", True, 4):
            with self.subTest(type=type(wrong).__name__), self.assertRaises(ContractError):
                store.begin_postprocess_attempt(attempts, wrong)
            self.assertEqual(attempts.snapshot(), ())
            self.assertEqual(store.eligible(before), (published.plan,))
            self.assertEqual(store.snapshot().candidates, (published,))

    def test_invalid_attempt_repository_type_fails_closed(self):
        store = PlanStore(1)
        store.publish(plan(10004, injectable=True))
        for bad in (None, {}, [], True):
            with self.subTest(type=type(bad).__name__), self.assertRaises(ContractError) as err:
                store.begin_postprocess_attempt(bad, "copy")
            self.assertEqual(err.exception.reason, ReasonCode.INVALID_STATE_TRANSITION)

    def test_retained_attempt_snapshot_survives_eviction_but_not_reset(self):
        store = PlanStore(1)
        status = InjectionAttemptStore()
        earlier = plan(10005, injectable=True)
        newer = plan(10006, injectable=True)
        store.publish(earlier)
        selected, attempt = store.begin_postprocess_attempt(status, "export-1")
        store.publish(newer)
        self.assertEqual(store.eligible(selected), (earlier,))
        self.assertEqual(store.eligible(store.snapshot()), (newer,))
        store.reset()
        self.assertEqual(store.eligible(selected), ())
        self.assertEqual(attempt.state, AttemptState.STARTED)
        self.assertEqual(status.snapshot(), (attempt,))

    def test_concurrent_unique_attempt_pairs_with_stable_frozen_snapshots(self):
        store = PlanStore(3)
        attempts = InjectionAttemptStore()
        candidates = [plan(10010+i, injectable=True) for i in range(3)]
        for candidate in candidates:
            store.publish(candidate)
        gate = Barrier(8)
        def worker(i):
            gate.wait()
            return store.begin_postprocess_attempt(attempts, "export-" + str(i))
        with ThreadPoolExecutor(max_workers=8) as executor:
            pairs = list(executor.map(worker, range(8)))
        self.assertEqual(len({record.attempt_id for _, record in pairs}), 8)
        self.assertEqual(len({record.source_working_file_identity for _, record in pairs}), 8)
        self.assertEqual(len(attempts.snapshot()), 8)
        for snapshot, record in pairs:
            self.assertEqual(len(snapshot.candidates), 3)
            self.assertEqual(store.eligible(snapshot), tuple(candidates))
            self.assertIs(record.state, AttemptState.STARTED)
            self.assertEqual(snapshot.plugin_session_epoch, store.plugin_session_epoch)


if __name__ == "__main__":
    unittest.main()
