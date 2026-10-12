"""Centered PrintObject slice-space value types; all coordinates are mm."""
from dataclasses import dataclass
from math import isfinite
from .errors import ContractError, ReasonCode


def _finite_mm(*values: float) -> None:
    if any(type(v) not in (int, float) or not isfinite(v) for v in values):
        raise ContractError(ReasonCode.INVALID_GEOMETRY, "non-finite/invalid millimeter coordinate")


@dataclass(frozen=True, slots=True)
class PrintPoint2:
    x_mm: float
    y_mm: float

    def __post_init__(self) -> None:
        _finite_mm(self.x_mm, self.y_mm)


@dataclass(frozen=True, slots=True)
class PrintPoint3:
    x_mm: float
    y_mm: float
    z_mm: float

    def __post_init__(self) -> None:
        _finite_mm(self.x_mm, self.y_mm, self.z_mm)


@dataclass(frozen=True, slots=True)
class StructuralPathSegment:
    start: PrintPoint3
    end: PrintPoint3
    width_mm: float
    local_height_mm: float
    local_geometric_mm3_per_mm: float
    command_flow_modifier: float
    layer_index: int
    role: str

    def __post_init__(self) -> None:
        _finite_mm(self.width_mm, self.local_height_mm, self.local_geometric_mm3_per_mm, self.command_flow_modifier)
        if min(self.width_mm, self.local_height_mm, self.local_geometric_mm3_per_mm, self.command_flow_modifier) <= 0:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid structural bead dimensions")
        if type(self.layer_index) is not int or self.layer_index < 0 or not self.role:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid structural layer/role")


@dataclass(frozen=True, slots=True)
class StructuralLoopReference:
    loop_id: str
    points: tuple[PrintPoint3, ...]
    seam_gap_allowance_mm: float
    canonical_shape_hash: str

    def __post_init__(self) -> None:
        _finite_mm(self.seam_gap_allowance_mm)
        if not self.loop_id or len(self.points) < 3 or self.seam_gap_allowance_mm < 0 or not self.canonical_shape_hash:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "incomplete structural loop reference")
        if type(self.points) is not tuple:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "structural points must be immutable")
