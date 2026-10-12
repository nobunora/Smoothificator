"""Dimensioned geometric error metrics; no estimator implementation."""
from dataclasses import dataclass
from math import isfinite
from .errors import ContractError, ReasonCode


@dataclass(frozen=True, slots=True)
class ErrorMetrics:
    e_max_mm: float
    e_rms_mm: float
    e_p95_mm: float
    signed_mean_mm: float

    def __post_init__(self) -> None:
        values = (self.e_max_mm, self.e_rms_mm, self.e_p95_mm, self.signed_mean_mm)
        if any(type(v) not in (int, float) or not isfinite(v) for v in values) or min(values[:3]) < 0:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid error metric")


@dataclass(frozen=True, slots=True)
class SupportCoverageMetrics:
    version: str
    required_coverage_ratio: float
    measured_coverage_ratio: float

    def __post_init__(self) -> None:
        if not self.version or any(type(v) not in (int, float) or not isfinite(v) or not (0 <= v <= 1) for v in (self.required_coverage_ratio, self.measured_coverage_ratio)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid normalized coverage")
