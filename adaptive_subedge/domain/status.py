"""Stable immutable attempt-state data; mutable state belongs to application store."""
from dataclasses import dataclass
from enum import Enum
from .errors import ContractError, ReasonCode


class AttemptState(str, Enum):
    STARTED = "started"
    VALIDATED = "validated"
    EMITTED_TEMP = "emitted-temp"
    SANITY_PASS = "sanity-pass"
    COMMITTED = "committed"
    SKIPPED = "skipped"
    FAILED = "failed"
    FATAL = "fatal"


@dataclass(frozen=True, slots=True)
class InjectionAttemptRecord:
    attempt_id: str
    selected_plan_hash: str | None
    source_working_file_identity: str
    state: AttemptState
    reason: ReasonCode | None = None

    def __post_init__(self) -> None:
        if (type(self.attempt_id) is not str or not self.attempt_id
                or type(self.source_working_file_identity) is not str or not self.source_working_file_identity
                or type(self.state) is not AttemptState):
            raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "invalid immutable attempt record")
        if self.selected_plan_hash is not None:
            digest = self.selected_plan_hash
            if (type(digest) is not str or len(digest) != 64
                    or any(ch not in "0123456789abcdef" for ch in digest)):
                raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "invalid selected plan identity")
        failure_states = (AttemptState.SKIPPED, AttemptState.FAILED, AttemptState.FATAL)
        if ((self.state in failure_states and type(self.reason) is not ReasonCode)
                or (self.state not in failure_states and self.reason is not None)):
            raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "attempt state/reason mismatch")


@dataclass(frozen=True, slots=True)
class AttemptRevision:
    """Runtime-only immutable history entry; never part of Plan identity."""
    revision: int
    record: InjectionAttemptRecord

    def __post_init__(self):
        if type(self.revision) is not int or self.revision < 0 or type(self.record) is not InjectionAttemptRecord:
            raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "invalid attempt revision")
