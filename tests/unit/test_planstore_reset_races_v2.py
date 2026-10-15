"""Four ADR-0065 in-process reset/publication safety cases, no export binding."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier
import unittest

from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.domain.errors import ContractError
from tests.unit.test_stores import plan


class PlanStoreResetRacesV2(unittest.TestCase):
    def test_interleaved_reset_and_publish_never_mix_epochs_in_snapshot(self):
        store = PlanStore(4)
        plans = [plan(9100 + i, injectable=True) for i in range(24)]
        def publishing():
            for candidate in plans:
                store.publish(candidate)
        def resetting():
            for _ in range(12):
                store.reset()
        def observing():
            observed = []
            for _ in range(75):
                snapshot = store.snapshot()
                self.assertTrue(all(entry.plugin_session_epoch == snapshot.plugin_session_epoch
                                    for entry in snapshot.candidates))
                self.assertLessEqual(len(snapshot.candidates), 4)
                observed.append(snapshot)
            return observed
        with ThreadPoolExecutor(max_workers=3) as pool:
            publications = pool.submit(publishing)
            resets = pool.submit(resetting)
            observations = pool.submit(observing)
            publications.result()
            resets.result()
            snapshots = observations.result()
        self.assertEqual(len(snapshots), 75)
        current = store.plugin_session_epoch
        self.assertTrue(all(store.eligible(snap) == ()
             for snap in snapshots if snap.plugin_session_epoch != current))

    def test_no_cache_loaded_plan_without_current_epoch_publication(self):
        old = PlanStore(2)
        cache_like = plan(9200, injectable=True)
        old.publish(cache_like)
        old_snap = old.snapshot()
        fresh = PlanStore(2)
        self.assertEqual(fresh.snapshot().candidates, ())
        self.assertEqual(fresh.eligible(old_snap), ())
        self.assertEqual(old.eligible(old_snap), (cache_like,))

    def test_invalid_publication_does_not_evict_or_advance_at_capacity_one(self):
        store = PlanStore(1)
        original = plan(9300, injectable=True)
        published = store.publish(original)
        before = store.snapshot()
        malformed = replace(plan(9301, injectable=True), plan_hash="0"*64, plan_id="0"*64)
        with self.assertRaises(ContractError):
            store.publish(malformed)
        after = store.snapshot()
        self.assertEqual(store.eligible(after), (original,))
        self.assertEqual(after.candidates[0].analysis_generation_id,
                         published.analysis_generation_id)
        self.assertEqual(store.eligible(before), (original,))

    def test_repeatable_duplicate_retention_window_selects_distinct_current_hashes(self):
        store = PlanStore(3)
        values = [plan(9400+i, injectable=True) for i in range(4)]
        for idx in (0, 1, 2, 0, 3, 1, 3):
            store.publish(values[idx])
            entries = store.snapshot().candidates
            hashes = [e.plan.plan_hash for e in entries]
            self.assertLessEqual(len(entries), 3)
            self.assertEqual(len(hashes), len(set(hashes)))
        self.assertEqual([p.plan_hash for p in store.eligible(store.snapshot())],
                         [values[0].plan_hash, values[1].plan_hash, values[3].plan_hash])


if __name__ == "__main__":
    unittest.main()
