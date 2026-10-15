"""Versioned ADR-0062 tagged bytes, registered DTO fields, and ADR-0064 array tokens."""
from dataclasses import is_dataclass
from collections.abc import Mapping
from math import isfinite, prod
from adaptive_subedge.domain.numeric import finite_binary64
from typing import get_type_hints
from struct import pack

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint2, PrintPoint3, StructuralPathSegment, StructuralLoopReference
from adaptive_subedge.domain.metrics import ErrorMetrics, SupportCoverageMetrics, ConservativeSupportBounds, BidirectionalSurfaceErrorMetrics
from adaptive_subedge.domain.plan import (
    IdentityReference, SubEdgeSegment, SubEdgePath, InsertionAnchor,
    FinalSurfaceEnvelope, ChronologicalSupportEnvelope, PlanSemanticContent,
)
from adaptive_subedge.domain.settings import (ToolRadialKeepOut, ToolClearanceProfile, CandidateSegmentRegularityPolicy, PluginSettings,
    SurfaceCorrespondencePolicy, ErrorEstimatorConfig, MeshSectionPolicy, CandidateBeadBounds, SupportCoverageThresholds, SupportRefinementPolicy)

_FIELDS = {
    PrintPoint2: ("x_mm", "y_mm"),
    PrintPoint3: ("x_mm", "y_mm", "z_mm"),
    StructuralPathSegment: ("start", "end", "width_mm", "local_height_mm", "local_geometric_mm3_per_mm", "command_flow_modifier", "layer_index", "role"),
    StructuralLoopReference: ("loop_id", "points", "seam_gap_allowance_mm", "canonical_shape_hash"),
    ErrorMetrics: ("e_max_mm", "e_rms_mm", "e_p95_mm", "signed_mean_mm"),
    SupportCoverageMetrics: ("version", "required_coverage_ratio", "measured_coverage_ratio"),
    BidirectionalSurfaceErrorMetrics: ("e_max_pred_to_src_mm", "e_max_src_to_pred_mm", "e_p95_pred_to_src_mm", "e_p95_src_to_pred_mm", "e_rms_pred_to_src_mm", "e_rms_src_to_pred_mm"),
    ConservativeSupportBounds: ("supported_area_fraction_lower_bound",
        "minimum_contiguous_support_width_lower_bound_mm",
        "minimum_effective_height_lower_bound_mm",
        "maximum_effective_height_upper_bound_mm"),
    IdentityReference: ("identity_type", "schema_version", "canonical_encoding_version", "digest_hex"),
    SubEdgeSegment: ("start_xy", "end_xy", "command_z_mm", "local_support_z_mm", "effective_bead_height_mm", "width_mm", "geometric_mm3_per_mm", "commanded_mm3_per_mm", "requested_speed_mm_s"),
    SubEdgePath: ("path_id", "interval_id", "command_z_mm", "planned_seam_gap_mm", "execution_order", "segments", "support_dependency_path_ids"),
    InsertionAnchor: ("anchor_id", "structural_loop_ids", "layer_index", "boundary_signature"),
    FinalSurfaceEnvelope: ("structural_loop_ids", "candidate_path_ids"),
    ChronologicalSupportEnvelope: ("printed_prior_structural_loop_ids", "printed_prior_candidate_path_ids", "candidate_path_id"),
    PlanSemanticContent: ("plugin_version", "compatibility_descriptor_id", "source_geometry", "execution_config", "plugin_settings", "structural_reference_ids", "candidate_paths", "anchors", "error_metrics", "geometric_volume_mm3", "commanded_volume_mm3", "estimated_added_time_s", "injectable", "reason"),
    ToolRadialKeepOut: ("height_above_tip_mm", "radial_clearance_mm"),
    ToolClearanceProfile: ("profile_id", "version", "fixture_evidence_ref", "axial_height_mm", "radial_safety_margin_mm", "vertical_safety_margin_mm", "radial_keep_out"),
    CandidateSegmentRegularityPolicy: ("version", "fixture_evidence_ref", "min_candidate_segment_length_mm", "min_candidate_segment_time_s", "max_adjacent_commanded_volumetric_rate_step_mm3_s", "max_adjacent_width_step_mm", "max_adjacent_effective_height_step_mm"),
    SurfaceCorrespondencePolicy: ("version", "max_surface_correspondence_distance_mm", "min_surface_normal_dot",
        "interaction_neighborhood_expansion_mm", "interaction_neighborhood_tolerance_mm",
        "normal_ray_numeric_tolerance_mm", "normal_ray_numeric_policy_version",
        "closest_point_fallback_policy_version"),
    ErrorEstimatorConfig: ("version", "initial_error_sample_spacing_mm", "error_refinement_factor",
        "error_metric_convergence_mm", "max_error_refinement_levels",
        "closest_point_sign_numeric_tolerance_version", "surface_correspondence_policy"),
    SupportCoverageThresholds: ("min_support_area_fraction", "min_support_contact_width_mm"),
    SupportRefinementPolicy: ("initial_support_cell_size_mm", "support_refinement_factor",
        "support_metric_convergence_fraction", "support_width_convergence_mm",
        "max_support_refinement_levels", "minimum_support_cell_size_mm"),
    CandidateBeadBounds: ("min_candidate_height_mm", "max_candidate_height_mm",
        "min_candidate_width_mm", "max_candidate_width_mm"),
    MeshSectionPolicy: ("version", "section_predicate_epsilon_mm", "coplanar_section_epsilon_mm",
        "mesh_section_join_tolerance_mm", "section_quantization_geometry_tolerance_mm",
        "section_stability_sampling_convergence_version"),
    PluginSettings: ("schema_version", "surface_error_tolerance_mm", "minimum_effective_bead_height_mm", "candidate_seam_gap_mm", "regularity_policy", "tool_clearance_profile", "physical_injection_requested"),
}
_ROOT_KEYS = frozenset(("identity_type", "schema_version", "canonical_encoding_version", "payload"))
_TYPES = frozenset(("subedge-plan", "execution-config", "plugin-settings", "source-geometry"))


def semantic_tree(value: object) -> object:
    """Versioned semantic projection, rejecting recursive input with a stable reason."""
    try:
        return _semantic_tree(value)
    except RecursionError as exc:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "cyclic or excessively deep semantic identity") from exc


def _semantic_tree(value: object) -> object:
    """Only explicitly registered dataclass fields and canonical primitives are accepted."""
    if value is None or type(value) in (str, bool, int, float):
        return value
    if type(value) in (tuple, list):
        return [_semantic_tree(v) for v in value]
    if type(value) is dict:
        if any(type(k) is not str for k in value):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "nonstring mapping key")
        return {k: _semantic_tree(v) for k, v in value.items()}
    registered = _FIELDS.get(type(value))
    if registered is not None and is_dataclass(value):
        # Annotated float DTO fields have IEEE-754 binary64 semantics regardless
        # of whether a caller wrote an integer literal (1) or float literal (1.0).
        hints = get_type_hints(type(value))
        normalized = {}
        for name in registered:
            item = getattr(value, name)
            if hints.get(name) is float and type(item) is int:
                try:
                    item = float(item)
                except OverflowError as exc:
                    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "float field outside binary64") from exc
            normalized[name] = _semantic_tree(item)
        return normalized
    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "unregistered identity object")


def canonical_bytes(value: object) -> bytes:
    """ADR-0062 exact grammar, with bounded, typed failures for recursive inputs."""
    try:
        return _canonical_bytes(value)
    except RecursionError as exc:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "cyclic or excessively deep canonical data") from exc


def _decimal_int_bytes(value: int) -> bytes:
    """Portable integer decimal encoding even when Python's str-digit cap is enabled."""
    try:
        return str(value).encode("ascii")
    except ValueError:
        # Python 3.11+ permits the decimal-digit cap as low as 640.
        # Use sub-640 chunks so fallback conversions remain legal under
        # the strictest permitted cap, without altering canonical bytes.
        negative = value < 0
        remaining = abs(value)
        digits_per_chunk = 100
        chunk_base = 10 ** digits_per_chunk
        chunks = []
        while remaining >= chunk_base:
            remaining, lower = divmod(remaining, chunk_base)
            chunks.append(str(lower).zfill(digits_per_chunk))
        token = ("-" if negative else "") + str(remaining) + "".join(reversed(chunks))
        return token.encode("ascii")


def _canonical_bytes(value: object) -> bytes:
    """Exact tagged encoding; normal inputs retain byte-identical results."""
    if value is None:
        return b"n"
    if type(value) is bool:
        return b"b1" if value else b"b0"
    if type(value) is int:
        return b"i" + _decimal_int_bytes(value) + b";"
    if type(value) is float:
        if not isfinite(value):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "nonfinite identity float")
        return b"f" + (0.0 if value == 0 else value).hex().encode("ascii") + b";"
    if type(value) is str:
        try:
            payload = value.encode("utf-8")
        except UnicodeError as exc:
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid UTF-8 text") from exc
        return b"s" + str(len(payload)).encode("ascii") + b":" + payload
    if type(value) in (tuple, list):
        return b"l" + str(len(value)).encode("ascii") + b"[" + b"".join(_canonical_bytes(x) for x in value) + b"]"
    if type(value) is dict:
        if any(type(k) is not str for k in value):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "nonstring mapping key")
        return b"m" + str(len(value)).encode("ascii") + b"{" + b"".join(_canonical_bytes(k) + _canonical_bytes(value[k]) for k in sorted(value)) + b"}"
    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "undeclared canonical type")


def identity_root(identity_type: str, payload: object, *, schema_version: str = "1", canonical_encoding_version: str = "1") -> dict[str, object]:
    if type(identity_type) is not str or identity_type not in _TYPES or type(schema_version) is not str or schema_version != "1" or type(canonical_encoding_version) is not str or canonical_encoding_version != "1":
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unrecognized identity root")
    return {"identity_type": identity_type, "schema_version": schema_version, "canonical_encoding_version": canonical_encoding_version, "payload": semantic_tree(payload)}


def validate_root(root: object, expected_type: str) -> None:
    if type(root) is not dict or any(type(key) is not str for key in root) or frozenset(root) != _ROOT_KEYS or type(expected_type) is not str or expected_type not in _TYPES or type(root["identity_type"]) is not str or root["identity_type"] != expected_type or type(root["schema_version"]) is not str or root["schema_version"] != "1" or type(root["canonical_encoding_version"]) is not str or root["canonical_encoding_version"] != "1":
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "invalid typed identity root")


def canonical_array_token(dtype: str, shape: tuple[int, ...], values_c_order: tuple[int | float, ...]) -> dict[str, object]:
    """Logical C-order elements explicitly supplied; no raw native ndarray bytes."""
    if type(dtype) is not str or dtype not in ("i64", "f64") or type(shape) is not tuple or len(shape) > 0xFFFFFFFF or any(type(x) is not int or not 0 <= x <= (1 << 64)-1 for x in shape):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid array schema/shape")
    if type(values_c_order) is not tuple or len(values_c_order) != prod(shape):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "shape/value mismatch")
    def framed_chunks():
        # Equivalent to ADR-0062 binary array framing; no full array byte copy.
        yield b"ASE_ARRAY_V1\0" + dtype.encode("ascii") + pack(">I", len(shape))
        for dimension in shape:
            yield pack(">Q", dimension)
        for value in values_c_order:
            if dtype == "i64":
                if type(value) is not int or not -(1 << 63) <= value < (1 << 63):
                    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid signed i64")
                yield pack(">q", value)
            else:
                if not finite_binary64(value):
                    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid finite f64")
                try:
                    yield pack(">d", 0.0 if value == 0 else value)
                except (OverflowError, ValueError) as exc:
                    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "out-of-range f64") from exc

    # Hash framing stays in the one application owner; avoid a full buffer copy.
    from adaptive_subedge.application.hashing import domain_digest_chunks
    return {"array_schema_version": "ASE_ARRAY_V1", "dtype": dtype, "shape": list(shape),
            "digest_hex": domain_digest_chunks("array", framed_chunks())}


def validate_array_token(token: object) -> None:
    if type(token) is not dict or any(type(key) is not str for key in token) or frozenset(token) != frozenset(("array_schema_version", "dtype", "shape", "digest_hex")) or type(token.get("array_schema_version")) is not str or token.get("array_schema_version") != "ASE_ARRAY_V1" or type(token.get("dtype")) is not str or token.get("dtype") not in ("i64", "f64"):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "unknown array token")
    dims, digest = token["shape"], token["digest_hex"]
    if type(dims) is not list or len(dims) > 0xFFFFFFFF or any(type(x) is not int or not 0 <= x <= (1 << 64)-1 for x in dims):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid array token shape")
    if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid array token digest")
