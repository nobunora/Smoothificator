"""Standalone evidence vocabulary; construction is neither proof nor print permission."""
from dataclasses import dataclass

from .errors import ContractError, ReasonCode
from .metrics import BidirectionalSurfaceErrorMetrics
from .numeric import finite_binary64
from .plan import IdentityReference


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, message)


def _text(value: object) -> bool:
    return type(value) is str and bool(value.strip())


def _identity(value: object, kind: str, version: str) -> None:
    _require(type(value) is IdentityReference, "typed evidence identity required")
    _require((value.identity_type, value.schema_version, value.canonical_encoding_version)
             == (kind, version, "1"), "unsupported evidence identity schema")


@dataclass(frozen=True, slots=True)
class TimeEstimateAvailable:
    tag: str
    estimated_added_time_s: float
    predictor_model_version: str
    resolved_execution_config: IdentityReference
    evidence_reference: str

    def __post_init__(self):
        _require(type(self.tag) is str and self.tag == "available", "available time tag required")
        _require(finite_binary64(self.estimated_added_time_s) and self.estimated_added_time_s >= 0,
                 "finite nonnegative time required")
        _require(_text(self.predictor_model_version) and self.predictor_model_version != "unavailable_v1",
                 "available model identity required")
        _identity(self.resolved_execution_config, "execution-config", "1")
        _require(_text(self.evidence_reference), "time evidence reference required")


@dataclass(frozen=True, slots=True)
class TimeEstimateUnavailable:
    tag: str
    reason: str
    missing_dependency_ids: tuple[str, ...]

    def __post_init__(self):
        _require(type(self.tag) is str and self.tag == "unavailable", "unavailable time tag required")
        _require(type(self.reason) is str and self.reason in (
            "time-model-unavailable", "missing-execution-config", "missing-model-evidence"),
            "declared unavailable-time reason required")
        ids = self.missing_dependency_ids
        _require(type(ids) is tuple and bool(ids) and all(_text(x) for x in ids),
                 "immutable missing-dependency identities required")
        _require(len(set(ids)) == len(ids), "duplicate missing dependency")


@dataclass(frozen=True, slots=True)
class ErrorConvergenceEvidence:
    state: str
    estimator_policy: IdentityReference
    refinement_count: int
    evidence_reference: str | None
    reason: str | None

    def __post_init__(self):
        _require(type(self.state) is str and self.state in ("unknown", "converged", "failed"),
                 "declared convergence state required")
        _identity(self.estimator_policy, "plugin-settings", "2")
        _require(type(self.refinement_count) is int and self.refinement_count >= 0,
                 "nonnegative exact refinement count required")
        _require(self.evidence_reference is None or _text(self.evidence_reference),
                 "invalid convergence reference")
        if self.state == "unknown":
            _require(self.refinement_count == 0 and self.evidence_reference is None and self.reason is None,
                     "unknown convergence cannot claim evidence")
        elif self.state == "converged":
            _require(self.refinement_count >= 1 and _text(self.evidence_reference) and self.reason is None,
                     "convergence evidence and refinement required")
        else:
            _require(type(self.reason) is str and self.reason in (
                "refinement-budget-exhausted", "missing-error-evidence", "invalid-error-domain"),
                "declared convergence failure required")


@dataclass(frozen=True, slots=True)
class DirectionalErrorEvidence:
    metrics: BidirectionalSurfaceErrorMetrics
    pred_to_src: ErrorConvergenceEvidence
    src_to_pred: ErrorConvergenceEvidence

    def __post_init__(self):
        _require(type(self.metrics) is BidirectionalSurfaceErrorMetrics,
                 "directional metrics required")
        _require(type(self.pred_to_src) is ErrorConvergenceEvidence
                 and type(self.src_to_pred) is ErrorConvergenceEvidence,
                 "separate directional convergence records required")
        _require(self.pred_to_src.estimator_policy == self.src_to_pred.estimator_policy,
                 "directional estimator policies differ")
