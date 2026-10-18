"""ADR-0066 closed research Settings; no geometry, predictor or physical defaults."""
from dataclasses import dataclass

from .errors import ContractError, ReasonCode
from .settings import (
    CandidateBeadBounds, CandidateSegmentRegularityPolicy, ErrorEstimatorConfig,
    MeshSectionPolicy, SupportCoverageThresholds, SupportRefinementPolicy,
    ToolClearanceProfile, _nonnegative_finite,
)


def _literal(value: object, expected: str) -> None:
    if type(value) is not str or value != expected:
        raise ContractError(ReasonCode.INVALID_SETTING, "unsupported Settings v2 policy")


@dataclass(frozen=True, slots=True)
class SupportQueryNumericPolicy:
    version: str
    support_query_length_tolerance_mm: float

    def __post_init__(self):
        _literal(self.version, "support_query_length_v1")
        _nonnegative_finite(self.support_query_length_tolerance_mm, "support query tolerance", positive=True)


@dataclass(frozen=True, slots=True)
class ClassicJerkCorneringLimit:
    model_version: str
    max_subedge_jerk_mm_s: float

    def __post_init__(self):
        _literal(self.model_version, "classic_jerk_v1")
        _nonnegative_finite(self.max_subedge_jerk_mm_s, "classic jerk cap", positive=True)


@dataclass(frozen=True, slots=True)
class CandidateMotionLimits:
    max_candidate_speed_mm_s: float
    max_subedge_acceleration_mm_s2: float
    cornering_limit: ClassicJerkCorneringLimit

    def __post_init__(self):
        _nonnegative_finite(self.max_candidate_speed_mm_s, "speed cap", positive=True)
        _nonnegative_finite(self.max_subedge_acceleration_mm_s2, "acceleration cap", positive=True)
        if type(self.cornering_limit) is not ClassicJerkCorneringLimit:
            raise ContractError(ReasonCode.INVALID_SETTING, "classic jerk DTO required")


@dataclass(frozen=True, slots=True)
class DirectionalErrorWeights:
    pred_to_src_weight: float
    src_to_pred_weight: float

    def __post_init__(self):
        _nonnegative_finite(self.pred_to_src_weight, "prediction exploration weight")
        _nonnegative_finite(self.src_to_pred_weight, "source exploration weight")
        if self.pred_to_src_weight == 0 and self.src_to_pred_weight == 0:
            raise ContractError(ReasonCode.INVALID_SETTING, "positive exploration weight required")


@dataclass(frozen=True, slots=True)
class OptimizerCostPolicy:
    version: str
    quality_mode: str
    rank_mode: str
    complexity_counter_version: str
    search_priority_version: str
    time_estimator_model_version: str
    commanded_volume_accounting_version: str
    tie_break_version: str
    max_candidate_evaluations: int

    def __post_init__(self):
        for value, expected in (
            (self.version, "lexicographic_v1"),
            (self.quality_mode, "hard_bidirectional_max"),
            (self.rank_mode, "lex_complexity_time_commanded_volume"),
            (self.complexity_counter_version, "planned_intent_counts_v1"),
            (self.search_priority_version, "weighted_directional_p95_rational_v1"),
            (self.time_estimator_model_version, "unavailable_v1"),
            (self.commanded_volume_accounting_version, "commanded_volume_sum_v1"),
            (self.tie_break_version, "canonical_semantic_bytes_v1"),
        ):
            _literal(value, expected)
        if type(self.max_candidate_evaluations) is not int or self.max_candidate_evaluations < 1:
            raise ContractError(ReasonCode.INVALID_SETTING, "positive exact search budget required")


@dataclass(frozen=True, slots=True)
class CandidateExecutionPolicy:
    version: str
    ordering_policy_id: str

    def __post_init__(self):
        _literal(self.version, "candidate_execution_v1")
        _literal(self.ordering_policy_id, "chronological_dependency_first_v1")


@dataclass(frozen=True, slots=True)
class PluginSettingsV2:
    schema_version: str
    surface_error_tolerance_mm: float
    minimum_effective_bead_height_mm: float
    candidate_seam_gap_mm: float
    regularity_policy: CandidateSegmentRegularityPolicy
    tool_clearance_profile: ToolClearanceProfile | None
    candidate_bead_bounds: CandidateBeadBounds
    support_coverage_thresholds: SupportCoverageThresholds
    support_refinement_policy: SupportRefinementPolicy
    support_query_numeric_policy: SupportQueryNumericPolicy
    error_estimator_config: ErrorEstimatorConfig
    mesh_section_policy: MeshSectionPolicy
    candidate_motion_limits: CandidateMotionLimits
    directional_error_weights: DirectionalErrorWeights
    optimizer_cost_policy: OptimizerCostPolicy
    candidate_execution_policy: CandidateExecutionPolicy
    physical_injection_requested: bool

    def __post_init__(self):
        _literal(self.schema_version, "2")
        _nonnegative_finite(self.surface_error_tolerance_mm, "surface tolerance", positive=True)
        _nonnegative_finite(self.minimum_effective_bead_height_mm, "effective bead height", positive=True)
        _nonnegative_finite(self.candidate_seam_gap_mm, "seam gap")
        for value, expected in (
            (self.regularity_policy, CandidateSegmentRegularityPolicy),
            (self.candidate_bead_bounds, CandidateBeadBounds),
            (self.support_coverage_thresholds, SupportCoverageThresholds),
            (self.support_refinement_policy, SupportRefinementPolicy),
            (self.support_query_numeric_policy, SupportQueryNumericPolicy),
            (self.error_estimator_config, ErrorEstimatorConfig),
            (self.mesh_section_policy, MeshSectionPolicy),
            (self.candidate_motion_limits, CandidateMotionLimits),
            (self.directional_error_weights, DirectionalErrorWeights),
            (self.optimizer_cost_policy, OptimizerCostPolicy),
            (self.candidate_execution_policy, CandidateExecutionPolicy),
        ):
            if type(value) is not expected:
                raise ContractError(ReasonCode.INVALID_SETTING, "exact Settings v2 nested DTO required")
        if self.tool_clearance_profile is not None and type(self.tool_clearance_profile) is not ToolClearanceProfile:
            raise ContractError(ReasonCode.INVALID_SETTING, "exact hardware profile DTO required")
        if type(self.physical_injection_requested) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "boolean injection flag required")
        if self.physical_injection_requested:
            self.require_physical_injection()

    def require_physical_injection(self):
        raise ContractError(ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED, "Settings v2 is research only")
