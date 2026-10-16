"""Closed Plan-v2-root projection; standalone v2 evidence stays unregistered."""
from types import UnionType
from typing import get_args, get_origin, get_type_hints

from adaptive_subedge.domain.analysis_evidence import (
    TimeEstimateAvailable, TimeEstimateUnavailable, ErrorConvergenceEvidence,
    DirectionalErrorEvidence,
)
from adaptive_subedge.domain.insertion_anchor_v2 import InsertionAnchorV2
from adaptive_subedge.domain.structural_loop_v2 import StructuralLoopReferenceV2
from adaptive_subedge.domain.plan_v2 import (
    GeometryRegionReferenceV2, SupportReferenceV2, SurfaceBandV2,
    StructuralLoopContextV2, SegmentSupportIntentV2, SubEdgePathV2,
    PlannedTransitionV2, PlannedVolumesV2, ResearchPlanOutcomeV2, PlanSemanticContentV2,
)
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.numeric import finite_binary64
from .serialization import _FIELDS


PLAN_V2_FIELDS = {
    GeometryRegionReferenceV2: ("identity", "source_geometry", "coordinate_frame"),
    SupportReferenceV2: ("reference_id", "contributor_kind", "contributor_id"),
    SurfaceBandV2: ("surface_band_id", "source_geometry", "target_boundary_ref",
        "residual_error_region_ref", "chronological_support_reference_ids", "nesting_parent_band_id"),
    StructuralLoopContextV2: ("loop_id", "structural_interval_id", "layer_index",
        "execution_order", "maximum_path_z_mm"),
    SegmentSupportIntentV2: ("support_reference_ids", "settings_identity", "evidence_reference"),
    SubEdgePathV2: ("path", "surface_band_id", "insertion_anchor_id", "segment_support"),
    PlannedTransitionV2: ("from_path_id", "to_path_id", "kind", "policy_version"),
    PlannedVolumesV2: ("geometric_volume_mm3", "commanded_volume_mm3"),
    ResearchPlanOutcomeV2: ("injectable", "reason"),
    PlanSemanticContentV2: ("schema_version", "plugin_version", "compatibility_descriptor_id",
        "source_geometry", "execution_config", "plugin_settings", "geometry_regions",
        "support_references", "surface_bands", "structural_loops", "structural_loop_contexts",
        "candidate_paths", "anchors", "transitions", "directional_error", "added_time",
        "volumes", "analysis_outcome"),
    StructuralLoopReferenceV2: ("loop_id", "points", "seam_gap_allowance_mm", "loop_length_mm",
        "bounds_print_space_mm", "coordinate_frame", "winding_orientation", "winding_policy_version",
        "material_side_policy_version", "matching_anchor_points_print_space_mm",
        "anchor_predicate_version", "shape_canonicalization_version", "canonical_shape_hash"),
    InsertionAnchorV2: ("anchor_id", "structural_loop_ids", "layer_index", "boundary_signature",
        "target_structural_interval_id", "boundary_signature_schema_version",
        "matching_tolerance_mm", "matching_profile_id"),
    TimeEstimateAvailable: ("tag", "estimated_added_time_s", "predictor_model_version",
        "resolved_execution_config", "evidence_reference"),
    TimeEstimateUnavailable: ("tag", "reason", "missing_dependency_ids"),
    ErrorConvergenceEvidence: ("state", "estimator_policy", "refinement_count", "evidence_reference", "reason"),
    DirectionalErrorEvidence: ("metrics", "pred_to_src", "src_to_pred"),
}


def _plan_value(value, expected, *, decode):
    if get_origin(expected) is UnionType:
        for option in get_args(expected):
            try:
                return _plan_value(value, option, decode=decode)
            except ContractError:
                pass
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "unknown Plan union variant")
    if expected is type(None) and value is None:
        return None
    if get_origin(expected) is tuple:
        if type(value) is not (list if decode else tuple):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "closed Plan sequence required")
        arguments = get_args(expected)
        if len(arguments) != 2 or arguments[1] is not Ellipsis:
            if len(value) != len(arguments):
                raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "Plan tuple arity mismatch")
            values = [_plan_value(v, t, decode=decode) for v, t in zip(value, arguments)]
        else:
            values = [_plan_value(v, arguments[0], decode=decode) for v in value]
        return tuple(values) if decode else values
    names = PLAN_V2_FIELDS.get(expected, _FIELDS.get(expected))
    if names is not None:
        hints = get_type_hints(expected)
        if decode:
            if type(value) is not dict or any(type(k) is not str for k in value) or set(value) != set(names):
                raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "closed Plan object required")
            return expected(**{name: _plan_value(value[name], hints[name], decode=True) for name in names})
        if type(value) is not expected:
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "exact Plan DTO required")
        return {name: _plan_value(getattr(value, name), hints[name], decode=False) for name in names}
    if expected is float:
        if (type(value) is float or (not decode and type(value) is int)) and finite_binary64(value):
            return float(value)
    elif expected in (str, bool, int) and type(value) is expected:
        return value
    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid Plan scalar")


def project_plan_content_v2(content: PlanSemanticContentV2) -> dict:
    try:
        return _plan_value(content, PlanSemanticContentV2, decode=False)
    except RecursionError as exc:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "recursive Plan content") from exc


def validate_plan_projection_v2(payload: object) -> None:
    try:
        _plan_value(payload, PlanSemanticContentV2, decode=True)
    except RecursionError as exc:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "recursive Plan projection") from exc
