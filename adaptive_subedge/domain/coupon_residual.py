"""Research-only exact bounds on one planar coupon's vertical top residual."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .support_cell import ExactTopCellXY


@dataclass(frozen=True, slots=True)
class VerticalResidualInterval:
    lower_mm: Fraction
    upper_mm: Fraction

    def __post_init__(self):
        if (type(self.lower_mm) is not Fraction or type(self.upper_mm) is not Fraction
                or not 0 <= self.lower_mm <= self.upper_mm):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "ordered residual interval required")


@dataclass(frozen=True, slots=True)
class CouponVerticalComparison:
    state: str
    reason: str
    source_mesh_id: str
    baseline_slice_id: str
    rectangle: ExactTopCellXY | None
    target_plane_abc: tuple[Fraction, Fraction, Fraction] | None
    baseline_max_residual: VerticalResidualInterval | None
    augmented_max_residual: VerticalResidualInterval | None
    leaf_count: int

    def __post_init__(self):
        reasons = {
            "complete": ("certified-reduction", "certified-nonreduction", "interval-overlap"),
            "incomplete": ("cancelled", "resource-limit", "coverage-unresolved"),
            "rejected": ("target-unresolved",),
        }
        if (type(self.state) is not str or self.state not in reasons
                or type(self.reason) is not str or self.reason not in reasons[self.state]
                or type(self.source_mesh_id) is not str or not self.source_mesh_id.strip()
                or type(self.baseline_slice_id) is not str or not self.baseline_slice_id.strip()
                or type(self.leaf_count) is not int or self.leaf_count < 0):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid coupon comparison identity or state")
        if self.state == "complete":
            if (self.leaf_count == 0 or type(self.rectangle) is not ExactTopCellXY
                    or type(self.target_plane_abc) is not tuple or len(self.target_plane_abc) != 3
                    or any(type(x) is not Fraction for x in self.target_plane_abc)
                    or type(self.baseline_max_residual) is not VerticalResidualInterval
                    or type(self.augmented_max_residual) is not VerticalResidualInterval):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "complete coupon bounds required")
            baseline, augmented = self.baseline_max_residual, self.augmented_max_residual
            if ((self.reason == "certified-reduction" and not augmented.upper_mm < baseline.lower_mm)
                    or (self.reason == "certified-nonreduction" and not augmented.lower_mm >= baseline.upper_mm)
                    or (self.reason == "interval-overlap" and
                        (augmented.upper_mm < baseline.lower_mm or augmented.lower_mm >= baseline.upper_mm))):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "comparison label exceeds bounds")
        elif (self.rectangle is not None or self.target_plane_abc is not None
              or self.baseline_max_residual is not None or self.augmented_max_residual is not None):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "partial coupon geometry forbidden")
