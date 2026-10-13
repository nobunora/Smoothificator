"""Four ADR-0037 immutable attempt-record construction invariants."""
from dataclasses import FrozenInstanceError, replace
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState, InjectionAttemptRecord


class AttemptRecordContractMatrixV2(unittest.TestCase):
    def test_full_lowercase_selected_hash_or_none_is_required(self):
        valid = InjectionAttemptRecord("attempt-A", "0123456789abcdef" * 4,
                                       "working-copy", AttemptState.STARTED)
        self.assertEqual(len(valid.selected_plan_hash), 64)
        self.assertIsNone(replace(valid, selected_plan_hash=None).selected_plan_hash)
        for value in ("a"*63, "a"*65, "A"*64, "g"*64, 1, [], True):
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ContractError) as ctx:
                replace(valid, selected_plan_hash=value)
            self.assertEqual(ctx.exception.reason, ReasonCode.INVALID_STATE_TRANSITION)

    def test_working_file_and_attempt_ids_are_exact_nonempty_strings(self):
        record = InjectionAttemptRecord("attempt-B", None, "synthetic-export", AttemptState.STARTED)
        class Tagged(str):
            pass
        for field in ("attempt_id", "source_working_file_identity"):
            for invalid in ("", None, {}, [], Tagged("nonempty"), False):
                with self.subTest(field=field, invalid=type(invalid).__name__), self.assertRaises(ContractError):
                    replace(record, **{field: invalid})

    def test_terminal_states_require_stable_reason_and_other_states_forbid_it(self):
        record = InjectionAttemptRecord("attempt-C", None, "synthetic-export", AttemptState.STARTED)
        for state in (AttemptState.SKIPPED, AttemptState.FAILED, AttemptState.FATAL):
            with self.subTest(state=state):
                with self.assertRaises(ContractError):
                    replace(record, state=state)
                valid = replace(record, state=state, reason=ReasonCode.STALE_PLAN)
                self.assertEqual(valid.reason, ReasonCode.STALE_PLAN)
        for state in (AttemptState.STARTED, AttemptState.VALIDATED, AttemptState.EMITTED_TEMP,
                      AttemptState.SANITY_PASS, AttemptState.COMMITTED):
            with self.subTest(state=state), self.assertRaises(ContractError):
                replace(record, state=state, reason=ReasonCode.STALE_PLAN)

    def test_immutable_attempt_state_enum_cannot_be_replaced_by_string(self):
        record = InjectionAttemptRecord("attempt-D", None, "synthetic-export", AttemptState.STARTED)
        with self.assertRaises(FrozenInstanceError):
            record.state = AttemptState.FAILED
        for bad in (AttemptState.STARTED.value, "failed", None, 0):
            with self.subTest(bad_type=type(bad).__name__), self.assertRaises(ContractError):
                replace(record, state=bad)
        self.assertIs(record.state, AttemptState.STARTED)


if __name__ == "__main__":
    unittest.main()
