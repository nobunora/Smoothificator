"""Frozen planned geometry and explicit identity data; no final G-code coordinates/E."""
from dataclasses import dataclass
from .numeric import finite_binary64
from .errors import ContractError, ReasonCode
from .geometry import PrintPoint2
from .metrics import ErrorMetrics


def _valid_ids(values: object, *, required: bool = False) -> bool:
    return (type(values) is tuple
            and (not required or bool(values))
            and all(type(v) is str and bool(v) for v in values)
            and len(set(values)) == len(values))


@dataclass(frozen=True, slots=True)
class IdentityReference:
    identity_type: str
    schema_version: str
    canonical_encoding_version: str
    digest_hex: str

    def __post_init__(self) -> None:
        if not all(type(x) is str and x for x in (self.identity_type, self.schema_version, self.canonical_encoding_version)):
            raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "invalid identity reference")
        if type(self.digest_hex) is not str or len(self.digest_hex) != 64 or any(c not in "0123456789abcdef" for c in self.digest_hex):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "full lowercase SHA-256 identity required")


@dataclass(frozen=True, slots=True)
class SubEdgeSegment:
    start_xy: PrintPoint2
    end_xy: PrintPoint2
    command_z_mm: float
    local_support_z_mm: float
    effective_bead_height_mm: float
    width_mm: float
    geometric_mm3_per_mm: float
    commanded_mm3_per_mm: float
    requested_speed_mm_s: float

    def __post_init__(self) -> None:
        vals = (self.command_z_mm, self.local_support_z_mm, self.effective_bead_height_mm, self.width_mm, self.geometric_mm3_per_mm, self.commanded_mm3_per_mm, self.requested_speed_mm_s)
        if type(self.start_xy) is not PrintPoint2 or type(self.end_xy) is not PrintPoint2 or any(not finite_binary64(x) for x in vals) or any(x <= 0 for x in vals[2:]):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid candidate segment")
        if self.start_xy == self.end_xy or self.width_mm < self.effective_bead_height_mm:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "degenerate/non-printable candidate segment")


@dataclass(frozen=True, slots=True)
class SubEdgePath:
    path_id: str
    interval_id: str
    command_z_mm: float
    planned_seam_gap_mm: float
    execution_order: int
    segments: tuple[SubEdgeSegment, ...]
    support_dependency_path_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.path_id) is not str or not self.path_id or type(self.interval_id) is not str or not self.interval_id or not finite_binary64(self.command_z_mm) or not finite_binary64(self.planned_seam_gap_mm) or self.planned_seam_gap_mm < 0 or type(self.execution_order) is not int or self.execution_order < 0:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid candidate path metadata")
        if type(self.segments) is not tuple or not self.segments or any(type(s) is not SubEdgeSegment or s.command_z_mm != self.command_z_mm for s in self.segments):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "path must consist of same-Z immutable segments")
        if not _valid_ids(self.support_dependency_path_ids) or self.path_id in self.support_dependency_path_ids:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid dependency metadata")
        if any(left.end_xy != right.start_xy for left, right in zip(self.segments, self.segments[1:])):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "candidate path segment discontinuity")


@dataclass(frozen=True, slots=True)
class InsertionAnchor:
    anchor_id: str
    structural_loop_ids: tuple[str, ...]
    layer_index: int
    boundary_signature: str

    def __post_init__(self) -> None:
        if type(self.anchor_id) is not str or not self.anchor_id or not _valid_ids(self.structural_loop_ids, required=True) or type(self.boundary_signature) is not str or not self.boundary_signature or type(self.layer_index) is not int or self.layer_index < 1:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid insertion anchor")


@dataclass(frozen=True, slots=True)
class FinalSurfaceEnvelope:
    structural_loop_ids: tuple[str, ...]
    candidate_path_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _valid_ids(self.structural_loop_ids) or not _valid_ids(self.candidate_path_ids):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid immutable final surface references")


@dataclass(frozen=True, slots=True)
class ChronologicalSupportEnvelope:
    printed_prior_structural_loop_ids: tuple[str, ...]
    printed_prior_candidate_path_ids: tuple[str, ...]
    candidate_path_id: str

    def __post_init__(self) -> None:
        if (not _valid_ids(self.printed_prior_structural_loop_ids)
                or not _valid_ids(self.printed_prior_candidate_path_ids)
                or type(self.candidate_path_id) is not str or not self.candidate_path_id):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid chronological support references")


@dataclass(frozen=True, slots=True)
class PlanSemanticContent:
    plugin_version: str
    compatibility_descriptor_id: str
    source_geometry: IdentityReference
    execution_config: IdentityReference
    plugin_settings: IdentityReference
    structural_reference_ids: tuple[str, ...]
    candidate_paths: tuple[SubEdgePath, ...]
    anchors: tuple[InsertionAnchor, ...]
    error_metrics: ErrorMetrics
    geometric_volume_mm3: float
    commanded_volume_mm3: float
    estimated_added_time_s: float
    injectable: bool
    reason: str

    def __post_init__(self) -> None:
        if type(self.plugin_version) is not str or not self.plugin_version or type(self.compatibility_descriptor_id) is not str or not self.compatibility_descriptor_id or any(type(x) is not tuple for x in (self.structural_reference_ids, self.candidate_paths, self.anchors)):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid immutable plan content")
        if any(type(x) is not str or not x for x in self.structural_reference_ids):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid structural identity")
        if any(type(x) is not SubEdgePath for x in self.candidate_paths) or any(type(x) is not InsertionAnchor for x in self.anchors):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "unknown nested plan DTO")
        if len({p.path_id for p in self.candidate_paths}) != len(self.candidate_paths):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "duplicate candidate path id")
        # Static chronological metadata checks only: the engine will prove
        # the actual geometric contact/support before declaring injectability.
        if not _valid_ids(self.structural_reference_ids):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "duplicate/invalid structural reference")
        if len({p.execution_order for p in self.candidate_paths}) != len(self.candidate_paths):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "duplicate candidate execution order")
        by_id = {p.path_id: p for p in self.candidate_paths}
        for candidate in self.candidate_paths:
            for dependency_id in candidate.support_dependency_path_ids:
                dependency = by_id.get(dependency_id)
                if (dependency is None
                        or dependency.execution_order >= candidate.execution_order
                        or dependency.command_z_mm >= candidate.command_z_mm):
                    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "future/unknown/same-Z required candidate support")
        if len({anchor.anchor_id for anchor in self.anchors}) != len(self.anchors):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "duplicate insertion anchor")
        if any(not set(anchor.structural_loop_ids).issubset(self.structural_reference_ids) for anchor in self.anchors):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "anchor refers to undeclared structural loop")
        if not all(isinstance(i, IdentityReference) for i in (self.source_geometry, self.execution_config, self.plugin_settings)):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "missing typed plan identity")
        if not isinstance(self.error_metrics, ErrorMetrics) or type(self.injectable) is not bool or not isinstance(self.reason, str):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid plan outcome/metrics")
        for v in (self.geometric_volume_mm3, self.commanded_volume_mm3, self.estimated_added_time_s):
            if not finite_binary64(v) or v < 0:
                raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid plan volume/time")


@dataclass(frozen=True, slots=True)
class SubEdgePlan:
    content: PlanSemanticContent
    plan_hash: str
    plan_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.content, PlanSemanticContent) or type(self.plan_hash) is not str or self.plan_id != self.plan_hash or len(self.plan_hash) != 64 or any(c not in "0123456789abcdef" for c in self.plan_hash):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid plan identity")
