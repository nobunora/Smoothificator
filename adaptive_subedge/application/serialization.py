"""Versioned ADR-0062 tagged bytes, registered DTO fields, and ADR-0064 array tokens."""
from dataclasses import is_dataclass
from collections.abc import Mapping
from math import isfinite, prod
from struct import pack

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint2, PrintPoint3, StructuralPathSegment, StructuralLoopReference
from adaptive_subedge.domain.metrics import ErrorMetrics, SupportCoverageMetrics
from adaptive_subedge.domain.plan import (
    IdentityReference, SubEdgeSegment, SubEdgePath, InsertionAnchor,
    FinalSurfaceEnvelope, ChronologicalSupportEnvelope, PlanSemanticContent,
)
from adaptive_subedge.domain.settings import ToolRadialKeepOut, ToolClearanceProfile, CandidateSegmentRegularityPolicy, PluginSettings

_FIELDS = {
    PrintPoint2: ("x_mm", "y_mm"),
    PrintPoint3: ("x_mm", "y_mm", "z_mm"),
    StructuralPathSegment: ("start", "end", "width_mm", "local_height_mm", "local_geometric_mm3_per_mm", "command_flow_modifier", "layer_index", "role"),
    StructuralLoopReference: ("loop_id", "points", "seam_gap_allowance_mm", "canonical_shape_hash"),
    ErrorMetrics: ("e_max_mm", "e_rms_mm", "e_p95_mm", "signed_mean_mm"),
    SupportCoverageMetrics: ("version", "required_coverage_ratio", "measured_coverage_ratio"),
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
    PluginSettings: ("schema_version", "surface_error_tolerance_mm", "minimum_effective_bead_height_mm", "candidate_seam_gap_mm", "regularity_policy", "tool_clearance_profile", "physical_injection_requested"),
}
_ROOT_KEYS = frozenset(("identity_type", "schema_version", "canonical_encoding_version", "payload"))
_TYPES = frozenset(("subedge-plan", "execution-config", "plugin-settings", "source-geometry"))


def semantic_tree(value: object) -> object:
    """Only explicitly registered dataclass fields and canonical primitives are accepted."""
    if value is None or type(value) in (str, bool, int, float):
        return value
    if type(value) in (tuple, list):
        return [semantic_tree(v) for v in value]
    if type(value) is dict:
        if any(type(k) is not str for k in value):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "nonstring mapping key")
        return {k: semantic_tree(v) for k, v in value.items()}
    registered = _FIELDS.get(type(value))
    if registered is not None and is_dataclass(value):
        return {name: semantic_tree(getattr(value, name)) for name in registered}
    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "unregistered identity object")


def canonical_bytes(value: object) -> bytes:
    """ADR-0062 exact tagged grammar; rejects undeclared or nonfinite values."""
    if value is None:
        return b"n"
    if type(value) is bool:
        return b"b1" if value else b"b0"
    if type(value) is int:
        return b"i" + str(value).encode("ascii") + b";"
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
        return b"l" + str(len(value)).encode("ascii") + b"[" + b"".join(canonical_bytes(x) for x in value) + b"]"
    if type(value) is dict:
        if any(type(k) is not str for k in value):
            raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "nonstring mapping key")
        return b"m" + str(len(value)).encode("ascii") + b"{" + b"".join(canonical_bytes(k) + canonical_bytes(value[k]) for k in sorted(value)) + b"}"
    raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "undeclared canonical type")


def identity_root(identity_type: str, payload: object, *, schema_version: str = "1", canonical_encoding_version: str = "1") -> dict[str, object]:
    if type(identity_type) is not str or identity_type not in _TYPES or type(schema_version) is not str or schema_version != "1" or canonical_encoding_version != "1":
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unrecognized identity root")
    return {"identity_type": identity_type, "schema_version": schema_version, "canonical_encoding_version": canonical_encoding_version, "payload": semantic_tree(payload)}


def validate_root(root: object, expected_type: str) -> None:
    if type(root) is not dict or frozenset(root) != _ROOT_KEYS or expected_type not in _TYPES or root["identity_type"] != expected_type or root["schema_version"] != "1" or root["canonical_encoding_version"] != "1":
        raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "invalid typed identity root")


def canonical_array_token(dtype: str, shape: tuple[int, ...], values_c_order: tuple[int | float, ...]) -> dict[str, object]:
    """Logical C-order elements explicitly supplied; no raw native ndarray bytes."""
    if dtype not in ("i64", "f64") or type(shape) is not tuple or len(shape) > 0xFFFFFFFF or any(type(x) is not int or not 0 <= x <= (1 << 64)-1 for x in shape):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid array schema/shape")
    if type(values_c_order) is not tuple or len(values_c_order) != prod(shape):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "shape/value mismatch")
    data = bytearray(b"ASE_ARRAY_V1\0" + dtype.encode("ascii") + pack(">I", len(shape)) + b"".join(pack(">Q", x) for x in shape))
    for v in values_c_order:
        if dtype == "i64":
            if type(v) is not int or not -(1 << 63) <= v < (1 << 63):
                raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid signed i64")
            data.extend(pack(">q", v))
        else:
            if type(v) not in (float, int) or not isfinite(v):
                raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid finite f64")
            try:
                data.extend(pack(">d", 0.0 if v == 0 else v))
            except (OverflowError, ValueError) as exc:
                raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "out-of-range f64") from exc
    # Delayed import avoids an import cycle; hashing remains the only digest owner.
    from adaptive_subedge.application.hashing import domain_digest
    return {"array_schema_version": "ASE_ARRAY_V1", "dtype": dtype, "shape": list(shape), "digest_hex": domain_digest("array", bytes(data))}


def validate_array_token(token: object) -> None:
    if type(token) is not dict or frozenset(token) != frozenset(("array_schema_version", "dtype", "shape", "digest_hex")) or token.get("array_schema_version") != "ASE_ARRAY_V1" or token.get("dtype") not in ("i64", "f64"):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "unknown array token")
    dims, digest = token["shape"], token["digest_hex"]
    if type(dims) is not list or len(dims) > 0xFFFFFFFF or any(type(x) is not int or not 0 <= x <= (1 << 64)-1 for x in dims):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid array token shape")
    if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, "invalid array token digest")
