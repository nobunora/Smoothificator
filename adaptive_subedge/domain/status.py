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
        if not self.attempt_id or not self.source_working_file_identity or not isinstance(self.state, AttemptState):
            raise ContractError(ReasonCode.INVALID_STATE_TRANSITION, "invalid attempt record")
