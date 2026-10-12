"""Stable expected failure categories for the Phase 0.5 contract."""
from enum import Enum


class ReasonCode(str, Enum):
    INVALID_SETTING = "invalid-setting"
    INVALID_GEOMETRY = "invalid-geometry"
    UNKNOWN_IDENTITY_SCHEMA = "unknown-identity-schema"
    INVALID_CANONICAL_VALUE = "invalid-canonical-value"
    STALE_PLAN = "stale-plan"
    AMBIGUOUS_PLAN = "ambiguous-plan"
    INVALID_STATE_TRANSITION = "invalid-state-transition"
    PHYSICAL_INJECTION_NOT_AUTHORIZED = "physical-injection-not-authorized"


class ContractError(ValueError):
    """Reject a contract violation without guessing a printer behavior."""

    def __init__(self, reason: ReasonCode, message: str):
        self.reason = reason
        super().__init__(message)
