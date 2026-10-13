"""Four ADR-0037 terminal-state races and historical immutable attempt records."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import unittest

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState


class AttemptAtomicRacesV1(unittest.TestCase):
    def test_three_terminal_competitors_commit_exactly_one_result(self):
        status = InjectionAttemptStore()
        started = status.begin(None, "synthetic-export")
        gate = Barrier(3)
        def complete(state):
            gate.wait()
            try:
                return status.transition(started.attempt_id, state, ReasonCode.STALE_PLAN)
            except ContractError:
                return None
        with ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(complete,
                (AttemptState.SKIPPED, AttemptState.FATAL, AttemptState.FAILED)))
        winners = [x for x in results if x is not None]
        self.assertEqual(len(winners),1)
        self.assertEqual(status.snapshot(),tuple(winners))
        with self.assertRaises(ContractError):
            status.transition(started.attempt_id, AttemptState.COMMITTED)

    def test_each_nonterminal_step_permits_reasoned_failure_without_success_leak(self):
        for stages in ((), (AttemptState.VALIDATED,),
                       (AttemptState.VALIDATED,AttemptState.EMITTED_TEMP),
                       (AttemptState.VALIDATED,AttemptState.EMITTED_TEMP,AttemptState.SANITY_PASS)):
            with self.subTest(stages=stages):
                status = InjectionAttemptStore()
                first = status.begin(None, "synthetic")
                for state in stages:
                    status.transition(first.attempt_id,state)
                final = status.transition(first.attempt_id,AttemptState.FAILED,ReasonCode.STALE_PLAN)
                self.assertEqual(final.state,AttemptState.FAILED)
                self.assertEqual(final.reason,ReasonCode.STALE_PLAN)
                self.assertEqual(len(status.snapshot()),1)

    def test_snapshot_before_update_preserves_previous_immutable_record(self):
        status = InjectionAttemptStore()
        original = status.begin(None,"synthetic-export")
        before = status.snapshot()
        advanced = status.transition(original.attempt_id,AttemptState.VALIDATED)
        after = status.snapshot()
        self.assertIs(before[0],original)
        self.assertIs(after[0],advanced)
        self.assertEqual(before[0].state,AttemptState.STARTED)
        self.assertEqual(after[0].state,AttemptState.VALIDATED)
        self.assertIsNot(before[0],after[0])

    def test_invalid_future_transition_does_not_advance_or_mutate_reason(self):
        status = InjectionAttemptStore()
        first = status.begin(None, "attempt-source")
        advanced = status.transition(first.attempt_id,AttemptState.VALIDATED)
        for bad_state,bad_reason in ((AttemptState.SANITY_PASS,None),
                                     (AttemptState.VALIDATED,None),
                                     (AttemptState.EMITTED_TEMP,ReasonCode.STALE_PLAN)):
            with self.subTest(state=bad_state,reason=bad_reason),self.assertRaises(ContractError):
                status.transition(first.attempt_id,bad_state,bad_reason)
            self.assertIs(status.snapshot()[0],advanced)
            self.assertIsNone(advanced.reason)


if __name__=="__main__":
    unittest.main()
