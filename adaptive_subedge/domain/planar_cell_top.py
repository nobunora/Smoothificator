"""Exact planar top coverage receipt; construction is not a mesh proof."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode


@dataclass(frozen=True, slots=True)
class PlanarCellTopCoverage:
    state: str
    reason: str
    cell_xy_mm: tuple[tuple[Fraction, Fraction], ...] | None
    plane_a: Fraction | None
    plane_b: Fraction | None
    plane_c_mm: Fraction | None
    area_mm2: Fraction | None

    def __post_init__(self):
        reasons = {
            "complete": ("planar-top-covered",),
            "incomplete": ("cancelled", "resource-limit"),
            "rejected": ("empty-mesh", "unused-vertex", "degenerate-bounds",
                         "degenerate-triangle", "duplicate-triangle", "nonmanifold-edge",
                         "inconsistent-winding", "disconnected-shell", "nonmanifold-vertex",
                         "zero-signed-volume", "self-intersection", "no-top-facing-facet",
                         "ambiguous-top-plane", "above-top-plane", "uncovered-top"),
        }
        if (type(self.state) is not str or self.state not in reasons
                or type(self.reason) is not str or self.reason not in reasons[self.state]):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "invalid planar top disposition")
        fields = (self.plane_a, self.plane_b, self.plane_c_mm, self.area_mm2)
        if self.state != "complete":
            if self.cell_xy_mm is not None or any(field is not None for field in fields):
                raise ContractError(ReasonCode.INVALID_GEOMETRY, "partial top geometry forbidden")
            return
        cell = self.cell_xy_mm
        if (type(cell) is not tuple or len(cell) < 3
                or any(type(point) is not tuple or len(point) != 2
                       or any(type(v) is not Fraction for v in point) for point in cell)
                or len(set(cell)) != len(cell) or cell[0] != min(cell)
                or any(type(field) is not Fraction for field in fields)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "exact complete planar top required")
        area2 = sum((cell[i][0]*cell[(i+1) % len(cell)][1]
                     - cell[i][1]*cell[(i+1) % len(cell)][0]
                     for i in range(len(cell))), Fraction(0))
        if area2 <= 0 or self.area_mm2 != area2/2:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "top cell area mismatch")
