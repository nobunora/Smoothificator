"""Four ADR-0065 in-process PlanStore interleavings; no Orca invocation binding."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from dataclasses import replace
from threading import Barrier
import unittest

from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.domain.errors import ContractError
from tests.unit.test_stores import plan


class PlanStoreInterleavingsV1(unittest.TestCase):
    def test_snapshot_taken_before_reset_is_invalid_even_if_same_plan_republished(self):
        store = PlanStore(4)
        original = plan(8100, injectable=True)
        store.publish(original)
        previous = store.snapshot()
        old_epoch = previous.plugin_session_epoch
        store.reset()
        store.publish(plan(8100, injectable=True))
        current = store.snapshot()
        self.assertNotEqual(old_epoch, current.plugin_session_epoch)
        self.assertEqual(store.eligible(previous), ())
        self.assertEqual(store.eligible(current), (original,))
        with self.assertRaises(FrozenInstanceError):
            current.plugin_session_epoch = old_epoch

    def test_failed_publish_cannot_evict_existing_plan_at_capacity_one(self):
        store = PlanStore(1)
        valid = plan(8110, injectable=True)
        original = store.publish(valid)
        snapshot = store.snapshot()
        invalid = replace(valid, plan_hash="0"*64, plan_id="0"*64)
        with self.assertRaises(ContractError):
            store.publish(invalid)
        after = store.snapshot()
        self.assertEqual(store.eligible(after), (valid,))
        self.assertEqual(after.candidates[0].analysis_generation_id,
                         original.analysis_generation_id)
        self.assertEqual(store.eligible(snapshot), (valid,))

    def test_parallel_mixed_preview_and_injectable_plans_keep_selection_filter(self):
        store = PlanStore(24)
        items = [plan(8200+i, injectable=(i % 3 == 0)) for i in range(24)]
        with ThreadPoolExecutor(max_workers=6) as pool:
            entries = list(pool.map(store.publish, items))
        self.assertEqual(len({x.analysis_generation_id for x in entries}),24)
        snap = store.snapshot()
        self.assertEqual(len(snap.candidates),24)
        approved = store.eligible(snap)
        self.assertEqual(len(approved),8)
        self.assertTrue(all(x.content.injectable for x in approved))

    def test_concurrent_equal_hash_republication_never_creates_duplicate_semantics(self):
        store = PlanStore(3)
        source = plan(8300, injectable=True)
        barrier = Barrier(6)
        def task(index):
            barrier.wait()
            ids = []
            for _ in range(8):
                ids.append(store.publish(source).analysis_generation_id)
                self.assertLessEqual(len(store.snapshot().candidates),1)
            return ids
        with ThreadPoolExecutor(max_workers=6) as pool:
            histories = list(pool.map(task, range(6)))
        all_ids = [x for group in histories for x in group]
        self.assertEqual(sorted(all_ids), list(range(1,49)))
        self.assertEqual(store.eligible(store.snapshot()),(source,))


if __name__ == "__main__":
    unittest.main()
