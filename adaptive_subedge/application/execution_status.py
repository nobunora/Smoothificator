"""One monotonic attempt-record store (ADR-0037); no plan-owned mutable status."""
from dataclasses import replace
from threading import RLock
from uuid import uuid4

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState, InjectionAttemptRecord, AttemptRevision

_FORWARD = {
    AttemptState.STARTED: AttemptState.VALIDATED,
    AttemptState.VALIDATED: AttemptState.EMITTED_TEMP,
    AttemptState.EMITTED_TEMP: AttemptState.SANITY_PASS,
    AttemptState.SANITY_PASS: AttemptState.COMMITTED,
}
_TERMINAL = frozenset((AttemptState.COMMITTED, AttemptState.SKIPPED, AttemptState.FAILED, AttemptState.FATAL))


class InjectionAttemptStore:
    def __init__(self, *, max_attempts: int | None = None, max_revisions_per_attempt: int | None = None):
        if not (max_attempts is None and max_revisions_per_attempt is None):
            if (type(max_attempts) is not int or max_attempts < 1
                    or type(max_revisions_per_attempt) is not int or max_revisions_per_attempt < 1):
                raise ContractError(ReasonCode.INVALID_SETTING, "both positive retention capacities required")
        self._lock = RLock()
        self._records: dict[str, InjectionAttemptRecord] = {}
        self._max_attempts = max_attempts
        self._max_revisions = max_revisions_per_attempt
        self._histories: dict[str, tuple[AttemptRevision, ...]] = {}
        self._issuance_sequence = 0

    def begin(self, plan_hash: str | None, source_working_file_identity: str) -> InjectionAttemptRecord:
        with self._lock:
            generated_id = uuid4().hex
            sequence = self._issuance_sequence + 1
            attempt_id = generated_id if self._max_attempts is None else f"{generated_id}:{sequence}"
            record = InjectionAttemptRecord(attempt_id, plan_hash, source_working_file_identity, AttemptState.STARTED)
            if record.attempt_id in self._records:
                raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "duplicate attempt identity")
            if self._max_attempts is not None:
                if any(key.rpartition(":")[0] == generated_id for key in self._records):
                    raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "duplicate retained attempt UUID")
                victim = None
                if len(self._records) >= self._max_attempts:
                    victim = next((key for key, value in self._records.items() if value.state in _TERMINAL), None)
                    if victim is None:
                        raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "attempt capacity occupied by active work")
                # Prepare all fallible allocations before publishing or evicting.
                records, histories = self._records.copy(), self._histories.copy()
                if victim is not None:
                    del records[victim]
                    del histories[victim]
                records[record.attempt_id] = record
                histories[record.attempt_id] = (AttemptRevision(0, record),)
                self._records, self._histories = records, histories
                self._issuance_sequence = sequence
                return record
            self._records[record.attempt_id] = record
            return record

    def transition(self, attempt_id: str, state: AttemptState, reason: ReasonCode | None = None) -> InjectionAttemptRecord:
        if type(attempt_id) is not str or not attempt_id:
            raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "valid attempt identity required")
        with self._lock:
            previous = self._records.get(attempt_id)
            if previous is None or not isinstance(state, AttemptState) or previous.state in _TERMINAL:
                raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "unknown or terminal attempt")
            if state in (AttemptState.SKIPPED, AttemptState.FAILED, AttemptState.FATAL):
                if not isinstance(reason, ReasonCode):
                    raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "failed/skipped attempt requires stable reason")
            elif _FORWARD.get(previous.state) != state or reason is not None:
                raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "state transition not monotonic")
            result = replace(previous, state=state, reason=reason)
            if self._max_attempts is not None:
                old_history = self._histories[attempt_id]
                entry = AttemptRevision(old_history[-1].revision + 1, result)
                records, histories = self._records.copy(), self._histories.copy()
                records[attempt_id] = result
                histories[attempt_id] = (old_history + (entry,))[-self._max_revisions:]
                self._records, self._histories = records, histories
                return result
            self._records[attempt_id] = result
            return result

    def snapshot(self) -> tuple[InjectionAttemptRecord, ...]:
        with self._lock:
            return tuple(self._records.values())

    def history(self, attempt_id: str) -> tuple[AttemptRevision, ...]:
        if type(attempt_id) is not str or not attempt_id:
            raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "valid attempt identity required")
        with self._lock:
            return self._histories.get(attempt_id, ())
