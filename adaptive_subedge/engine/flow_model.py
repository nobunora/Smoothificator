"""Nominal cross-section arithmetic; no solid, support proof or print authority."""
from math import pi

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.numeric import finite_binary64
from adaptive_subedge.domain.settings import CandidateBeadBounds


def _scalar(value: object, name: str, *, positive: bool = True) -> float:
    if not finite_binary64(value) or (positive and value <= 0):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, f"invalid {name}")
    return float(value)


def _bounds(bounds: object) -> None:
    if type(bounds) is not CandidateBeadBounds:
        raise ContractError(ReasonCode.INVALID_SETTING, "exact candidate bead bounds required")


def _bounded_height(height: float, bounds: CandidateBeadBounds) -> None:
    if not float(bounds.min_candidate_height_mm) <= height <= float(bounds.max_candidate_height_mm):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "height outside candidate bounds")


def candidate_geometric_line_flow(
    height_mm: float, width_mm: float, *, bounds: CandidateBeadBounds,
) -> float:
    """Return a candidate stadium area in mm³/mm, within explicit research bounds."""
    _bounds(bounds)
    height = _scalar(height_mm, "candidate height")
    width = _scalar(width_mm, "candidate width")
    _bounded_height(height, bounds)
    if width < height or not float(bounds.min_candidate_width_mm) <= width <= float(bounds.max_candidate_width_mm):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "width outside candidate stadium/bounds")
    return _scalar(height * (width - height * (1 - pi / 4)), "candidate geometric line flow")


def bead_width_from_geometric_flow(
    height_mm: float, geometric_mm3_per_mm: float,
) -> float:
    """Invert nominal area; candidate admission must separately apply candidate bounds."""
    height = _scalar(height_mm, "bead height")
    geometric_flow = _scalar(geometric_mm3_per_mm, "geometric line flow")
    width = _scalar(geometric_flow / height + height * (1 - pi / 4), "derived bead width")
    if width < height:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "derived width below stadium height")
    return width


def zaa_local_bead(
    nominal_height_mm: float, nominal_geometric_mm3_per_mm: float,
    relative_z_offset_mm: float,
) -> tuple[float, float, float]:
    """Return local height, geometric line flow and derived width for structural ZAA."""
    nominal_height = _scalar(nominal_height_mm, "nominal height")
    nominal_flow = _scalar(nominal_geometric_mm3_per_mm, "nominal geometric line flow")
    offset = _scalar(relative_z_offset_mm, "relative Z offset", positive=False)
    local_height = _scalar(nominal_height + offset, "local ZAA height")
    ratio = _scalar(local_height / nominal_height, "ZAA height ratio")
    local_flow = _scalar(nominal_flow * ratio, "local ZAA geometric line flow")
    width = bead_width_from_geometric_flow(local_height, local_flow)
    return local_height, local_flow, width


def effective_candidate_height(
    command_z_mm: float, local_support_z_mm: float, *, bounds: CandidateBeadBounds,
) -> float:
    """Subtract declared support Z; this does not establish that support exists."""
    _bounds(bounds)
    command_z = _scalar(command_z_mm, "command Z", positive=False)
    support_z = _scalar(local_support_z_mm, "local support Z", positive=False)
    height = _scalar(command_z - support_z, "effective candidate height")
    _bounded_height(height, bounds)
    return height


def commanded_external_line_flow(
    geometric_mm3_per_mm: float, *, print_flow_ratio: float,
    filament_flow_ratio: float, set_other_flow_ratios: bool,
    outer_wall_flow_ratio: float,
) -> float:
    """Apply external-role command multipliers without altering nominal bead geometry."""
    if type(set_other_flow_ratios) is not bool:
        raise ContractError(ReasonCode.INVALID_SETTING, "exact flow enablement bool required")
    geometric_flow = _scalar(geometric_mm3_per_mm, "geometric line flow")
    print_ratio = _scalar(print_flow_ratio, "print flow ratio")
    filament_ratio = _scalar(filament_flow_ratio, "filament flow ratio")
    outer_ratio = _scalar(outer_wall_flow_ratio, "outer wall flow ratio")
    after_print = _scalar(geometric_flow * print_ratio, "print-adjusted line flow")
    after_filament = _scalar(after_print * filament_ratio, "filament-adjusted line flow")
    return _scalar(after_filament * (outer_ratio if set_other_flow_ratios else 1.0),
                   "commanded external line flow")
