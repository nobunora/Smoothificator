"""Dimensioned geometric error metrics; no estimator implementation."""
from dataclasses import dataclass
from .numeric import finite_binary64
from .errors import ContractError, ReasonCode


@dataclass(frozen=True, slots=True)
class ErrorMetrics:
    e_max_mm: float
    e_rms_mm: float
    e_p95_mm: float
    signed_mean_mm: float

    def __post_init__(self) -> None:
        values = (self.e_max_mm, self.e_rms_mm, self.e_p95_mm, self.signed_mean_mm)
        if any(not finite_binary64(v) for v in values) or min(values[:3]) < 0:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid error metric")
        # Both bidirectional summary RMS and p95 are bounded by the largest
        # directional maximum. This checks DTO coherence, not convergence.
        if (self.e_rms_mm > self.e_max_mm or self.e_p95_mm > self.e_max_mm
                or abs(self.signed_mean_mm) > self.e_max_mm):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "error summary exceeds maximum")


@dataclass(frozen=True, slots=True)
class SupportCoverageMetrics:
    version: str
    required_coverage_ratio: float
    measured_coverage_ratio: float

    def __post_init__(self) -> None:
        if type(self.version) is not str or not self.version.strip() or any(not finite_binary64(v) or not (0 <= v <= 1) for v in (self.required_coverage_ratio, self.measured_coverage_ratio)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid normalized coverage")


@dataclass(frozen=True, slots=True)
class ConservativeSupportBounds:
    """ADR-0058 lower/upper support evidence only; no pass/fail decision."""

    supported_area_fraction_lower_bound: float
    minimum_contiguous_support_width_lower_bound_mm: float
    minimum_effective_height_lower_bound_mm: float
    maximum_effective_height_upper_bound_mm: float

    def __post_init__(self) -> None:
        fraction = self.supported_area_fraction_lower_bound
        if not finite_binary64(fraction) or not 0 <= fraction <= 1:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid conservative support area")
        values = (
            self.minimum_contiguous_support_width_lower_bound_mm,
            self.minimum_effective_height_lower_bound_mm,
            self.maximum_effective_height_upper_bound_mm,
        )
        if any(not finite_binary64(v) or v < 0 for v in values):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid conservative support dimensions")
        if self.minimum_effective_height_lower_bound_mm > self.maximum_effective_height_upper_bound_mm:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "inverted conservative support height bounds")
