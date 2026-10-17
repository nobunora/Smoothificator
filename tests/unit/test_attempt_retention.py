"""Bounded history, failure atomicity, stale IDs and concurrent record ownership."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from threading import Barrier
import unittest
from unittest.mock import patch
from uuid import UUID

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.application.serialization import semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState, AttemptRevision


def bounded(attempts=2, revisions=2):
    return InjectionAttemptStore(max_attempts=attempts, max_revisions_per_attempt=revisions)


class AttemptRetentionTests(unittest.TestCase):
    def test_capacities_are_explicit_positive_exact_integers(self):
        for a, r in ((None, 1), (1, None), (0, 2), (2, 0), (True, 2), (2, 1.), (-1, 2)):
            with self.subTest(a=a, r=r), self.assertRaises(ContractError):
                bounded(a, r)
        legacy = InjectionAttemptStore()
        record = legacy.begin(None, "source")
        self.assertEqual(legacy.history(record.attempt_id), ())
        self.assertEqual(len(record.attempt_id), 32)

    def test_pruned_revisions_keep_monotonic_numbers_and_old_snapshots(self):
        store = bounded(1, 2)
        first = store.begin(None, "source")
        held = store.history(first.attempt_id)
        for state in (AttemptState.VALIDATED, AttemptState.EMITTED_TEMP, AttemptState.SANITY_PASS, AttemptState.COMMITTED):
            store.transition(first.attempt_id, state)
        self.assertEqual(tuple(x.revision for x in store.history(first.attempt_id)), (3, 4))
        self.assertEqual(held[0].record.state, AttemptState.STARTED)
        with self.assertRaises(FrozenInstanceError):
            held[0].revision = 7
        with self.assertRaises(ContractError):
            semantic_tree(held[0])

    def test_evict_oldest_created_terminal_and_never_active(self):
        store = bounded(3, 1)
        first, active, third = [store.begin(None, str(i)) for i in range(3)]
        store.transition(third.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        store.transition(first.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        fourth = store.begin(None, "fourth")
        self.assertEqual(tuple(x.attempt_id for x in store.snapshot()), (active.attempt_id, third.attempt_id, fourth.attempt_id))
        self.assertEqual(store.history(first.attempt_id), ())

    def test_full_active_capacity_rejects_without_sequence_or_record_change(self):
        store = bounded(1, 2)
        first = store.begin(None, "first")
        before = store.history(first.attempt_id)
        with self.assertRaises(ContractError):
            store.begin(None, "blocked")
        self.assertEqual(store.snapshot(), (first,))
        self.assertEqual(store.history(first.attempt_id), before)
        store.transition(first.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        self.assertTrue(store.begin(None, "next").attempt_id.endswith(":2"))

    def test_duplicate_uuid_rejects_before_terminal_eviction(self):
        store = bounded(1, 2)
        with patch("adaptive_subedge.application.execution_status.uuid4", return_value=UUID(int=7)):
            first = store.begin(None, "first")
            terminal = store.transition(first.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
            held = store.history(first.attempt_id)
            with self.assertRaises(ContractError):
                store.begin(None, "collision")
        self.assertEqual(store.snapshot(), (terminal,))
        self.assertEqual(store.history(first.attempt_id), held)

    def test_evicted_uuid_recurrence_cannot_reuse_stale_full_id(self):
        store = bounded(1, 1)
        with patch("adaptive_subedge.application.execution_status.uuid4", side_effect=(UUID(int=1), UUID(int=2), UUID(int=1))):
            first = store.begin(None, "first")
            store.transition(first.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
            second = store.begin(None, "second")
            store.transition(second.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
            third = store.begin(None, "third")
        self.assertNotEqual(first.attempt_id, third.attempt_id)
        self.assertEqual(store.history(first.attempt_id), ())
        with self.assertRaises(ContractError):
            store.transition(first.attempt_id, AttemptState.VALIDATED)
        self.assertEqual(store.snapshot(), (third,))

    def test_failed_allocation_preserves_terminal_record_history_and_sequence(self):
        store = bounded(1, 2)
        first = store.begin(None, "first")
        terminal = store.transition(first.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        history = store.history(first.attempt_id)
        with patch("adaptive_subedge.application.execution_status.AttemptRevision", side_effect=RuntimeError("synthetic allocation failure")):
            with self.assertRaises(RuntimeError):
                store.begin(None, "next")
        self.assertEqual(store.snapshot(), (terminal,))
        self.assertEqual(store.history(first.attempt_id), history)
        self.assertTrue(store.begin(None, "next").attempt_id.endswith(":2"))

    def test_failed_transition_and_malformed_begin_preserve_history(self):
        store = bounded(1, 3)
        first = store.begin(None, "first")
        held = store.history(first.attempt_id)
        with self.assertRaises(ContractError):
            store.transition(first.attempt_id, AttemptState.COMMITTED)
        with self.assertRaises(ContractError):
            store.begin(None, "")
        with patch("adaptive_subedge.application.execution_status.AttemptRevision", side_effect=RuntimeError("synthetic")):
            with self.assertRaises(RuntimeError):
                store.transition(first.attempt_id, AttemptState.VALIDATED)
        self.assertEqual(store.history(first.attempt_id), held)
        self.assertEqual(store.snapshot(), (first,))
        for value in (None, "", 1, []):
            with self.assertRaises(ContractError):
                store.history(value)

    def test_atomic_plan_issuance_rolls_back_on_capacity_rejection(self):
        plans, attempts = PlanStore(1), bounded(1, 2)
        snapshot, record = plans.begin_postprocess_attempt(attempts, "first")
        with self.assertRaises(ContractError):
            plans.begin_postprocess_attempt(attempts, "second")
        self.assertEqual(tuple(plans._issued_snapshots), (snapshot,))
        self.assertEqual(attempts.snapshot(), (record,))

    def test_parallel_begin_never_exceeds_active_capacity(self):
        store, gate = bounded(3, 2), Barrier(12)
        def begin(i):
            gate.wait(timeout=5)
            try:
                return store.begin(None, str(i))
            except ContractError:
                return None
        with ThreadPoolExecutor(max_workers=12) as executor:
            results = list(executor.map(begin, range(12)))
        self.assertEqual(sum(x is not None for x in results), 3)
        self.assertEqual(len(store.snapshot()), 3)
        for record in store.snapshot():
            self.assertEqual(store.history(record.attempt_id), (AttemptRevision(0, record),))


if __name__ == "__main__":
    unittest.main()
