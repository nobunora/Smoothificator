"""Immutable numerical coverage reports; not physical support authorization."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .geometry import PrintPoint2
from .numeric import finite_binary64


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


@dataclass(frozen=True, slots=True)
class SupportFootprint:
    start: PrintPoint2
    end: PrintPoint2
    width_mm: float
    command_z_mm: float
    execution_order: int

    def __post_init__(self):
        _require(type(self.start) is PrintPoint2 and type(self.end) is PrintPoint2,
                 "exact footprint endpoints required")
        _require(finite_binary64(self.width_mm) and float(self.width_mm) > 0
                 and finite_binary64(self.command_z_mm), "invalid footprint dimensions")
        _require((float(self.start.x_mm), float(self.start.y_mm)) !=
                 (float(self.end.x_mm), float(self.end.y_mm)), "positive footprint length required")
        _require(type(self.execution_order) is int and self.execution_order >= 0,
                 "nonnegative footprint order required")


@dataclass(frozen=True, slots=True)
class SupportCoverageSnapshot:
    supported_area_fraction_lower_bound: Fraction
    minimum_contiguous_support_width_lower_bound_mm: Fraction
    minimum_effective_height_lower_bound_mm: Fraction | None
    maximum_effective_height_upper_bound_mm: Fraction | None
    unresolved_area_fraction: Fraction
    leaf_count: int

    def __post_init__(self):
        area, width, unknown = (self.supported_area_fraction_lower_bound,
                                self.minimum_contiguous_support_width_lower_bound_mm,
                                self.unresolved_area_fraction)
        _require(all(type(x) is Fraction for x in (area, width, unknown)),
                 "exact coverage quantities required")
        _require(0 <= area <= 1 and 0 <= unknown <= 1 and area + unknown <= 1 and width >= 0,
                 "invalid coverage quantities")
        lower, upper = self.minimum_effective_height_lower_bound_mm, self.maximum_effective_height_upper_bound_mm
        _require((lower is None and upper is None) or
                 (type(lower) is Fraction and type(upper) is Fraction and lower <= upper),
                 "paired ordered height bounds required")
        _require(type(self.leaf_count) is int and self.leaf_count > 0, "positive leaf count required")


@dataclass(frozen=True, slots=True)
class AdaptiveSupportResult:
    state: str
    reason: str
    metrics: SupportCoverageSnapshot | None
    levels_completed: int
    cells_evaluated: int

    def __post_init__(self):
        reasons = {"numerically-supported": ("converged",),
                   "numerically-rejected": ("thresholds-failed",),
                   "incomplete": ("max-levels", "resource-limit", "cancelled", "coordinate-range")}
        _require(type(self.state) is str and self.state in reasons
                 and type(self.reason) is str and self.reason in reasons[self.state],
                 "invalid adaptive disposition")
        _require(type(self.levels_completed) is int and self.levels_completed >= 0
                 and type(self.cells_evaluated) is int and self.cells_evaluated >= 0,
                 "invalid adaptive counters")
        _require((self.metrics is None and self.levels_completed == 0) or
                 (type(self.metrics) is SupportCoverageSnapshot and self.levels_completed > 0),
                 "only completed-pass metrics may be reported")
        if self.state != "incomplete":
            _require(self.metrics is not None and self.levels_completed >= 2
                     and self.metrics.unresolved_area_fraction == 0,
                     "complete converged coverage required")
            if self.state == "numerically-supported":
                _require(self.metrics.minimum_effective_height_lower_bound_mm is not None,
                         "supported height evidence required")
