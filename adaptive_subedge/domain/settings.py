"""Validated plugin-owned Settings. Physical injection is not enabled in Phase 0.5."""
from dataclasses import dataclass
from .numeric import finite_binary64
from .errors import ContractError, ReasonCode


def _nonnegative_finite(value: float, field: str, *, positive: bool = False) -> None:
    if not finite_binary64(value) or value < 0 or (positive and value == 0):
        raise ContractError(ReasonCode.INVALID_SETTING, f"invalid {field}")


@dataclass(frozen=True, slots=True)
class ToolRadialKeepOut:
    height_above_tip_mm: float
    radial_clearance_mm: float

    def __post_init__(self) -> None:
        _nonnegative_finite(self.height_above_tip_mm, "tool height")
        _nonnegative_finite(self.radial_clearance_mm, "radial keep-out", positive=True)


@dataclass(frozen=True, slots=True)
class ToolClearanceProfile:
    profile_id: str
    version: str
    fixture_evidence_ref: str
    axial_height_mm: float
    radial_safety_margin_mm: float
    vertical_safety_margin_mm: float
    radial_keep_out: tuple[ToolRadialKeepOut, ...]

    def __post_init__(self) -> None:
        if not all((self.profile_id, self.version, self.fixture_evidence_ref)):
            raise ContractError(ReasonCode.INVALID_SETTING, "profile identity/evidence required")
        _nonnegative_finite(self.axial_height_mm, "axial height", positive=True)
        _nonnegative_finite(self.radial_safety_margin_mm, "radial safety margin")
        _nonnegative_finite(self.vertical_safety_margin_mm, "vertical safety margin")
        if type(self.radial_keep_out) is not tuple or not self.radial_keep_out or not all(isinstance(v, ToolRadialKeepOut) for v in self.radial_keep_out):
            raise ContractError(ReasonCode.INVALID_SETTING, "immutable keep-out curve required")
        levels = tuple(x.height_above_tip_mm for x in self.radial_keep_out)
        if levels[0] != 0 or levels[-1] > self.axial_height_mm or any(a >= b for a, b in zip(levels, levels[1:])):
            raise ContractError(ReasonCode.INVALID_SETTING, "keep-out curve must start at tip and increase")


@dataclass(frozen=True, slots=True)
class CandidateSegmentRegularityPolicy:
    version: str
    fixture_evidence_ref: str | None
    min_candidate_segment_length_mm: float
    min_candidate_segment_time_s: float
    max_adjacent_commanded_volumetric_rate_step_mm3_s: float
    max_adjacent_width_step_mm: float
    max_adjacent_effective_height_step_mm: float

    def __post_init__(self) -> None:
        if not self.version or self.fixture_evidence_ref == "":
            raise ContractError(ReasonCode.INVALID_SETTING, "invalid regularity policy version/evidence")
        for field in ("min_candidate_segment_length_mm", "min_candidate_segment_time_s", "max_adjacent_commanded_volumetric_rate_step_mm3_s", "max_adjacent_width_step_mm", "max_adjacent_effective_height_step_mm"):
            _nonnegative_finite(getattr(self, field), field, positive=field.startswith("min_"))


@dataclass(frozen=True, slots=True)
class PluginSettings:
    schema_version: str
    surface_error_tolerance_mm: float
    minimum_effective_bead_height_mm: float
    candidate_seam_gap_mm: float
    regularity_policy: CandidateSegmentRegularityPolicy
    tool_clearance_profile: ToolClearanceProfile | None = None
    physical_injection_requested: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != "1" or not isinstance(self.regularity_policy, CandidateSegmentRegularityPolicy):
            raise ContractError(ReasonCode.INVALID_SETTING, "unrecognized settings schema/policy")
        _nonnegative_finite(self.surface_error_tolerance_mm, "surface tolerance", positive=True)
        _nonnegative_finite(self.minimum_effective_bead_height_mm, "effective bead height", positive=True)
        _nonnegative_finite(self.candidate_seam_gap_mm, "seam gap")
        if type(self.physical_injection_requested) is not bool:
            raise ContractError(ReasonCode.INVALID_SETTING, "invalid injection flag")
        if self.physical_injection_requested:
            raise ContractError(ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED, "Phase 0.5 has no physical injection")

    def require_physical_injection(self) -> None:
        raise ContractError(ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED, "no printer-compatible fixture has been validated")
