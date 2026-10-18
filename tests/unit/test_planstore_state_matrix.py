"""ADR-0065 in-process store lifetime and atomic current-epoch selection matrix."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier
import unittest

from adaptive_subedge.application.plan_store import PlanSnapshot, PlanStore
from adaptive_subedge.domain.errors import ContractError
from tests.unit.test_stores import plan


class PlanStoreStateMatrix(unittest.TestCase):
    def test_old_generation_survives_new_publication_without_implicit_latest_gate(self):
        store = PlanStore(4)
        early = plan(3000, injectable=True)
        late = plan(3001, injectable=True)
        first = store.publish(early)
        store.publish(late)
        eligible = store.eligible(store.snapshot())
        self.assertEqual([x.plan_hash for x in eligible], [early.plan_hash, late.plan_hash])
        self.assertEqual(first.analysis_generation_id, 1)

    def test_retained_snapshot_survives_capacity_one_eviction_only_until_reset(self):
        store = PlanStore(1)
        first = plan(3010, injectable=True)
        second = plan(3011, injectable=True)
        store.publish(first)
        held = store.snapshot()
        store.publish(second)
        self.assertEqual(store.eligible(held), (first,))
        self.assertEqual(store.eligible(store.snapshot()), (second,))
        store.reset()
        self.assertEqual(store.eligible(held), ())

    def test_same_plan_republished_many_times_is_one_candidate_with_new_generation(self):
        store = PlanStore(3)
        semantic = plan(3020, injectable=True)
        ids = [store.publish(semantic).analysis_generation_id for _ in range(30)]
        self.assertEqual(ids, list(range(1, 31)))
        snap = store.snapshot()
        self.assertEqual(len(snap.candidates), 1)
        self.assertEqual(snap.candidates[0].analysis_generation_id, 30)
        self.assertEqual(store.eligible(snap), (semantic,))

    def test_copied_or_cross_session_snapshot_is_never_authoritative(self):
        store = PlanStore(3)
        original = plan(3030, injectable=True)
        store.publish(original)
        snap = store.snapshot()
        copied = replace(snap)
        forged = PlanSnapshot(snap.plugin_session_epoch, snap.candidates)
        other = PlanStore(3)
        other.publish(original)
        self.assertEqual(store.eligible(snap), (original,))
        self.assertEqual(store.eligible(copied), ())
        self.assertEqual(store.eligible(forged), ())
        self.assertEqual(other.eligible(snap), ())

    def test_concurrent_snapshots_have_unique_immutable_candidates(self):
        store = PlanStore(6)
        plans = tuple(plan(3040 + i, injectable=True) for i in range(30))
        gate = Barrier(6)
        def worker(chunk):
            gate.wait()
            snapshots = []
            for candidate in chunk:
                store.publish(candidate)
                snap = store.snapshot()
                self.assertEqual(len(snap.candidates),
                                 len({x.plan.plan_hash for x in snap.candidates}))
                self.assertLessEqual(len(snap.candidates), 6)
                self.assertTrue(all(x.plugin_session_epoch == snap.plugin_session_epoch
                                    for x in snap.candidates))
                snapshots.append(snap)
            return snapshots
        chunks = [plans[i::6] for i in range(6)]
        with ThreadPoolExecutor(max_workers=6) as pool:
            histories = list(pool.map(worker, chunks))
        self.assertEqual(sum(map(len, histories)), 30)
        self.assertEqual(len(store.snapshot().candidates), 6)


if __name__ == "__main__":
    unittest.main()
