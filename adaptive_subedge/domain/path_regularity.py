"""Numerical regularity diagnostics without physical or execution authority."""
from dataclasses import dataclass

from .errors import ContractError, ReasonCode


@dataclass(frozen=True, slots=True)
class PathRegularityResult:
    state: str
    reason: str
    offending_segment_indices: tuple[int, ...]

    def __post_init__(self):
        indices = self.offending_segment_indices
        if (type(self.state) is not str or type(self.reason) is not str
                or type(indices) is not tuple
                or any(type(i) is not int or i < 0 for i in indices)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid regularity disposition or indices")
        valid = (self.state == "complete" and self.reason == "regular" and not indices
                 or self.state == "incomplete" and self.reason in ("cancelled", "resource-limit")
                 and not indices)
        if self.state == "rejected":
            if self.reason in ("segment-length", "segment-time"):
                valid = len(indices) == 1
            elif self.reason in ("adjacent-rate-step", "adjacent-width-step", "adjacent-height-step"):
                valid = len(indices) == 2 and indices[1] == indices[0]+1
        if not valid:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid closed regularity result")
