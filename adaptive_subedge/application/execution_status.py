"""One monotonic attempt-record store (ADR-0037); no plan-owned mutable status."""
from dataclasses import replace
from threading import RLock
from uuid import uuid4

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.status import AttemptState, InjectionAttemptRecord

_FORWARD = {
    AttemptState.STARTED: AttemptState.VALIDATED,
    AttemptState.VALIDATED: AttemptState.EMITTED_TEMP,
    AttemptState.EMITTED_TEMP: AttemptState.SANITY_PASS,
    AttemptState.SANITY_PASS: AttemptState.COMMITTED,
}
_TERMINAL = frozenset((AttemptState.COMMITTED, AttemptState.SKIPPED, AttemptState.FAILED, AttemptState.FATAL))


class InjectionAttemptStore:
    def __init__(self):
        self._lock = RLock()
        self._records: dict[str, InjectionAttemptRecord] = {}

    def begin(self, plan_hash: str | None, source_working_file_identity: str) -> InjectionAttemptRecord:
        with self._lock:
            record = InjectionAttemptRecord(uuid4().hex, plan_hash, source_working_file_identity, AttemptState.STARTED)
            if record.attempt_id in self._records:
                raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "duplicate attempt identity")
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
            self._records[attempt_id] = result
            return result

    def snapshot(self) -> tuple[InjectionAttemptRecord, ...]:
        with self._lock:
            return tuple(self._records.values())
