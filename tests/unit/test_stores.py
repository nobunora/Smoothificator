"""ADR-0037/0065 current-session lifetime, dedup and monotonic attempts."""
import unittest
from concurrent.futures import ThreadPoolExecutor

from adaptive_subedge.application.plan_store import PlanStore
from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.application.hashing import create_plan, typed_identity, fingerprint_resolved_execution, fingerprint_plugin_settings
from adaptive_subedge.domain.plan import PlanSemanticContent
from adaptive_subedge.domain.metrics import ErrorMetrics
from adaptive_subedge.domain.settings import PluginSettings, CandidateSegmentRegularityPolicy
from adaptive_subedge.domain.status import AttemptState
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
