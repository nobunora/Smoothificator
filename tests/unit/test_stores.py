"""ADR-0037/0065 current-session lifetime, dedup and monotonic attempts."""
import unittest
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor

from adaptive_subedge.application.plan_store import PlanStore, PlanSnapshot
from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.hashing import create_plan, typed_identity, fingerprint_resolved_execution, fingerprint_plugin_settings
from adaptive_subedge.domain.plan import PlanSemanticContent
from adaptive_subedge.domain.metrics import ErrorMetrics
from adaptive_subedge.domain.settings import PluginSettings, CandidateSegmentRegularityPolicy
from adaptive_subedge.domain.status import AttemptState, InjectionAttemptRecord
from adaptive_subedge.domain.errors import ContractError, ReasonCode


def plan(seed, *, injectable=False):
    policy = CandidateSegmentRegularityPolicy("r", None, .01, .001, 1, .01, .01)
    settings = PluginSettings("1", .05, .08, .01, policy)
    return create_plan(PlanSemanticContent("0.5", "research",
        typed_identity("source-geometry", {"seed": seed}),
        fingerprint_resolved_execution({"x": 1}),
        fingerprint_plugin_settings(settings),
        (), (), (), ErrorMetrics(.01, .01, .01, 0.0), 0, 0, 0, injectable, "fixture-only"))


class StoreTests(unittest.TestCase):
    def test_bounded_dedup_and_old_generation(self):
        store = PlanStore(2)
        one, two, three = (plan(i, injectable=True) for i in (1, 2, 3))
        first = store.publish(one)
        store.publish(two)
        old_snapshot = store.snapshot()
        duplicate = store.publish(two)
        self.assertGreater(duplicate.analysis_generation_id, first.analysis_generation_id)
        self.assertEqual(len(store.snapshot().candidates), 2)
        store.publish(three)
        self.assertNotIn(one.plan_hash, [x.plan.plan_hash for x in store.snapshot().candidates])
        self.assertIn(one.plan_hash, [x.plan_hash for x in store.eligible(old_snapshot)])
        store.reset()
        self.assertEqual(store.eligible(old_snapshot), ())
        self.assertEqual(store.snapshot().candidates, ())

    def test_preview_only_plans_never_eligible(self):
        store = PlanStore(3)
        research = plan(8)
        executable_fixture = plan(9, injectable=True)
        store.publish(research)
        store.publish(executable_fixture)
        preview = store.snapshot()
        self.assertEqual(len(preview.candidates), 2)
        self.assertEqual([p.plan_hash for p in store.eligible(preview)], [executable_fixture.plan_hash])
        store.reset()
        self.assertEqual(store.eligible(preview), ())

    def test_only_store_issued_snapshot_is_executable(self):
        store = PlanStore(2)
        good = plan(100, injectable=True)
        store.publish(good)
        issued = store.snapshot()
        self.assertEqual(store.eligible(issued), (good,))
        # A copied or constructed snapshot has the same epoch and contents,
        # but was never atomically issued by this PlanStore.
        fabricated = PlanSnapshot(issued.plugin_session_epoch, issued.candidates)
        copied = replace(issued)
        self.assertEqual(store.eligible(fabricated), ())
        self.assertEqual(store.eligible(copied), ())
        # Retained issuance is valid even after the plan is evicted.
        store.publish(plan(101, injectable=True))
        store.publish(plan(102, injectable=True))
        self.assertEqual(store.eligible(issued), (good,))
        store.reset()
        self.assertEqual(store.eligible(issued), ())

    def test_attempts_parallel_unique_and_monotonic(self):
        status = InjectionAttemptStore()
        def attempt(i):
            started = status.begin(None, "export-" + str(i))
            finished = status.transition(started.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
            return (started.attempt_id, finished.state)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt, range(60)))
        self.assertEqual(len({attempt_id for attempt_id, _ in results}), 60)
        self.assertTrue(all(state is AttemptState.SKIPPED for _, state in results))
        self.assertEqual(len(status.snapshot()), 60)

    def test_rejects_malformed_attempt_identity_and_reason(self):
        with self.assertRaises(ContractError):
            InjectionAttemptRecord("id", "short", "source", AttemptState.STARTED)
        with self.assertRaises(ContractError):
            InjectionAttemptRecord("id", None, {"mutable": 1}, AttemptState.STARTED)
        with self.assertRaises(ContractError):
            InjectionAttemptRecord("id", None, "source", AttemptState.FAILED)
        with self.assertRaises(ContractError):
            InjectionAttemptRecord("id", None, "source", AttemptState.VALIDATED, ReasonCode.STALE_PLAN)
        valid_hash = "a" * 64
        self.assertEqual(InjectionAttemptRecord("id", valid_hash, "source", AttemptState.STARTED).selected_plan_hash,
                         valid_hash)

    def test_competing_same_attempt_transition_is_serialized(self):
        status = InjectionAttemptStore()
        attempt = status.begin(None, "source")
        def advance(_):
            try:
                status.transition(attempt.attempt_id, AttemptState.VALIDATED)
                return "advanced"
            except ContractError:
                return "rejected"
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(advance, range(2)))
        self.assertEqual(sorted(outcomes), ["advanced", "rejected"])
        self.assertEqual(status.snapshot()[0].state, AttemptState.VALIDATED)

    def test_concurrent_snapshots_remain_complete_and_bounded(self):
        store = PlanStore(5)
        plans = [plan(i, injectable=True) for i in range(24)]
        def publish_then_snapshot(candidate):
            item = store.publish(candidate)
            snapshot = store.snapshot()
            self.assertTrue(all(p.plugin_session_epoch == snapshot.plugin_session_epoch
                                for p in snapshot.candidates))
            self.assertEqual(len(snapshot.candidates),
                             len({p.plan.plan_hash for p in snapshot.candidates}))
            self.assertLessEqual(len(snapshot.candidates), 5)
            return item, snapshot
        with ThreadPoolExecutor(max_workers=8) as pool:
            histories = list(pool.map(publish_then_snapshot, plans))
        self.assertEqual(len({entry.analysis_generation_id for entry, _ in histories}), 24)
        self.assertTrue(all(len(snap.candidates) >= 1 for _, snap in histories))

    def test_cross_store_snapshot_cannot_claim_eligibility(self):
        first = PlanStore(2)
        second = PlanStore(2)
        chosen = plan(800, injectable=True)
        first.publish(chosen)
        second.publish(chosen)
        issued = first.snapshot()
        self.assertEqual(first.eligible(issued), (chosen,))
        self.assertEqual(second.eligible(issued), ())

    def test_terminal_failure_race_is_single_winner(self):
        from threading import Barrier
        status = InjectionAttemptStore()
        started = status.begin(None, "export-race")
        gate = Barrier(2)
        def terminate(state):
            gate.wait()
            try:
                status.transition(started.attempt_id, state, ReasonCode.STALE_PLAN)
                return "accepted"
            except ContractError:
                return "rejected"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(terminate, (AttemptState.SKIPPED, AttemptState.FAILED)))
        self.assertEqual(sorted(results), ["accepted", "rejected"])
        self.assertEqual(len(status.snapshot()), 1)
        self.assertIn(status.snapshot()[0].state, (AttemptState.SKIPPED, AttemptState.FAILED))

    def test_invalid_plan_store_capacity_is_rejected(self):
        for capacity in (0, -1, True, 1.5, "two"):
            with self.subTest(capacity=capacity), self.assertRaises(ContractError):
                PlanStore(capacity)

    def test_eviction_before_fresh_snapshot_is_not_recovered(self):
        store = PlanStore(2)
        oldest = plan(2000, injectable=True)
        middle = plan(2001, injectable=True)
        newest = plan(2002, injectable=True)
        store.publish(oldest)
        store.publish(middle)
        in_flight = store.snapshot()
        store.publish(newest)
        fresh = store.snapshot()
        self.assertEqual([x.plan_hash for x in store.eligible(in_flight)],
                         [oldest.plan_hash, middle.plan_hash])
        self.assertEqual([x.plan_hash for x in store.eligible(fresh)],
                         [middle.plan_hash, newest.plan_hash])
        self.assertNotIn(oldest.plan_hash, [x.plan_hash for x in store.eligible(fresh)])

    def test_dedup_refreshes_retention_without_duplicate_candidate(self):
        store = PlanStore(2)
        first = plan(2100, injectable=True)
        second = plan(2101, injectable=True)
        third = plan(2102, injectable=True)
        a = store.publish(first)
        store.publish(second)
        newest_first = store.publish(first)
        self.assertGreater(newest_first.analysis_generation_id, a.analysis_generation_id)
        store.publish(third)
        published = store.snapshot().candidates
        self.assertEqual([x.plan.plan_hash for x in published],
                         [first.plan_hash, third.plan_hash])
        self.assertEqual(len(store.eligible(store.snapshot())), 2)

    def test_epoch_reset_and_generation_are_separate_scopes(self):
        store = PlanStore(2)
        first = store.publish(plan(2200, injectable=True))
        old_epoch = first.plugin_session_epoch
        store.publish(plan(2201, injectable=True))
        store.reset()
        second = store.publish(plan(2200, injectable=True))
        self.assertNotEqual(old_epoch, second.plugin_session_epoch)
        self.assertEqual(first.analysis_generation_id, 1)
        self.assertEqual(second.analysis_generation_id, 1)
        self.assertEqual(first.plan.plan_hash, second.plan.plan_hash)

    def test_snapshot_registry_does_not_strongly_retain_abandoned_snapshots(self):
        import gc
        import weakref
        store = PlanStore(1)
        store.publish(plan(2300, injectable=True))
        captured = store.snapshot()
        ref = weakref.ref(captured)
        self.assertEqual(len(store.eligible(captured)), 1)
        del captured
        gc.collect()
        self.assertIsNone(ref())

    def test_parallel_publication_bounded(self):
        store = PlanStore(4)
        plans = [plan(i) for i in range(20)]
        with ThreadPoolExecutor(max_workers=5) as pool:
            entries = list(pool.map(store.publish, plans))
        self.assertEqual(len({e.analysis_generation_id for e in entries}), 20)
        self.assertEqual(len(store.snapshot().candidates), 4)

    def test_attempts_independent_and_monotonic(self):
        status = InjectionAttemptStore()
        a = status.begin(None, "export-A")
        b = status.begin(None, "export-B")
        self.assertNotEqual(a.attempt_id, b.attempt_id)
        status.transition(a.attempt_id, AttemptState.VALIDATED)
        status.transition(a.attempt_id, AttemptState.EMITTED_TEMP)
        status.transition(a.attempt_id, AttemptState.SANITY_PASS)
        status.transition(a.attempt_id, AttemptState.COMMITTED)
        status.transition(b.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        self.assertEqual({x.state for x in status.snapshot()}, {AttemptState.COMMITTED, AttemptState.SKIPPED})
        with self.assertRaises(ContractError):
            status.transition(a.attempt_id, AttemptState.SKIPPED, ReasonCode.STALE_PLAN)
        with self.assertRaises(ContractError):
            status.transition(b.attempt_id, AttemptState.VALIDATED)
        with self.assertRaises(ContractError):
            status.transition("missing", AttemptState.VALIDATED)


if __name__ == "__main__":
    unittest.main()
