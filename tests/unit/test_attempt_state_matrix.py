"""Five ADR-0037 attempt-record state machine and fail-closed matrix checks."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
import unittest

from adaptive_subedge.application.execution_status import InjectionAttemptStore
from adaptive_subedge.domain.status import AttemptState, InjectionAttemptRecord
from adaptive_subedge.domain.errors import ContractError, ReasonCode


class AttemptStateMatrix(unittest.TestCase):
    def test_ordered_success_state_progression_is_monotonic_in_record_store(self):
        status = InjectionAttemptStore()
        started = status.begin(None, "synthetic-copy")
        states = (AttemptState.VALIDATED, AttemptState.EMITTED_TEMP,
                  AttemptState.SANITY_PASS, AttemptState.COMMITTED)
        for state in states:
            record = status.transition(started.attempt_id, state)
            self.assertIs(record.state, state)
            self.assertIsNone(record.reason)
        self.assertEqual(len(status.snapshot()), 1)
        with self.assertRaises(FrozenInstanceError):
            record.state = AttemptState.FAILED

    def test_terminal_failure_must_have_reason_and_cannot_be_reopened(self):
        for terminal in (AttemptState.SKIPPED, AttemptState.FAILED, AttemptState.FATAL):
            with self.subTest(terminal=terminal):
                status = InjectionAttemptStore()
                started = status.begin(None, "synthetic-copy")
                with self.assertRaises(ContractError):
                    status.transition(started.attempt_id, terminal)
                self.assertIs(status.snapshot()[0].state, AttemptState.STARTED)
                final = status.transition(started.attempt_id, terminal, ReasonCode.STALE_PLAN)
                self.assertIs(final.state, terminal)
                self.assertIs(final.reason, ReasonCode.STALE_PLAN)
                with self.assertRaises(ContractError):
                    status.transition(started.attempt_id, AttemptState.VALIDATED)

    def test_invalid_transition_preserves_original_immutable_record(self):
        status = InjectionAttemptStore()
        original = status.begin(None, "export-copy")
        for state, reason in ((AttemptState.COMMITTED, None),
                              (AttemptState.VALIDATED, ReasonCode.STALE_PLAN),
                              (AttemptState.EMITTED_TEMP, None)):
            with self.subTest(state=state), self.assertRaises(ContractError):
                status.transition(original.attempt_id, state, reason)
            self.assertIs(status.snapshot()[0], original)
        with self.assertRaises(ContractError):
            status.transition("missing-attempt", AttemptState.VALIDATED)
        self.assertEqual(len(status.snapshot()), 1)

    def test_invalid_begin_inputs_do_not_publish_attempt_record(self):
        status = InjectionAttemptStore()
        invalid = ((None, ""), ("f" * 63, "source"), ("g" * 64, "source"),
                   (None, []), (None, None), (None, 0))
        for digest, source in invalid:
            with self.subTest(digest_type=type(digest).__name__,
                              source_type=type(source).__name__), self.assertRaises(ContractError):
                status.begin(digest, source)
            self.assertEqual(status.snapshot(), ())

    def test_parallel_attempts_do_not_share_identity_or_terminal_reason(self):
        status = InjectionAttemptStore()
        def worker(i):
            begin = status.begin(None, "export-" + str(i))
            reason = ReasonCode.STALE_PLAN
            final = status.transition(begin.attempt_id, AttemptState.SKIPPED, reason)
            return (final.attempt_id, final.source_working_file_identity, final.reason)
        with ThreadPoolExecutor(max_workers=8) as executor:
            records = list(executor.map(worker, range(80)))
        self.assertEqual(len({x[0] for x in records}), 80)
        self.assertEqual(len({x[1] for x in records}), 80)
        self.assertTrue(all(x[2] is ReasonCode.STALE_PLAN for x in records))
        self.assertEqual(len(status.snapshot()), 80)


if __name__ == "__main__":
    unittest.main()
