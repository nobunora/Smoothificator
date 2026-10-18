"""Supplied-interval geometry evidence, without execution permission."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .mesh_section import MeshSectionResult


@dataclass(frozen=True, slots=True)
class SectionStabilityResult:
    state: str
    reason: str
    z_lower_mm: Fraction
    z_upper_mm: Fraction
    maximum_boundary_displacement_upper_bound_mm: Fraction | None

    def __post_init__(self):
        if (type(self.state) is not str or type(self.reason) is not str
                or type(self.z_lower_mm) is not Fraction
                or type(self.z_upper_mm) is not Fraction
                or self.z_lower_mm >= self.z_upper_mm):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid stability interval or disposition")
        bound = self.maximum_boundary_displacement_upper_bound_mm
        if (self.state, self.reason) in (("complete", "stable"),
                                        ("incomplete", "displacement-unproven")):
            if type(bound) is not Fraction or bound < 0:
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact nonnegative bound required")
            return
        if bound is not None:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "partial stability bound forbidden")
        if self.state == "incomplete" and self.reason in (
                "cancelled", "resource-limit", "topology-event-unproven"):
            return
        if self.state != "rejected":
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid stability disposition")
        if self.reason != "non-simple-section":
            MeshSectionResult("rejected", self.reason, None)
