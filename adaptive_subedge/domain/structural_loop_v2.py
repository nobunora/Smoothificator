"""Immutable loop metadata with local checks, never geometric matching proof."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .geometry import PrintPoint3
from .numeric import finite_binary64


def _require(valid: bool, message: str) -> None:
    if not valid:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


def _coordinates(points: object) -> tuple[tuple[float, float, float], ...]:
    _require(type(points) is tuple and len(points) >= 3,
             "at least three immutable points required")
    _require(all(type(point) is PrintPoint3 for point in points),
             "exact PrintPoint3 values required")
    coordinates = tuple((float(p.x_mm), float(p.y_mm), float(p.z_mm)) for p in points)
    _require(len(set(coordinates)) == len(coordinates), "distinct points required")
    return coordinates


def _noncollinear(anchors: tuple[tuple[float, float, float], ...]) -> bool:
    # Subtract only after conversion: even finite binary64 differences can overflow.
    a = tuple(Fraction(value) for value in anchors[0])
    b = tuple(Fraction(value) for value in anchors[1])
    u = tuple(right - left for left, right in zip(a, b))
    for point in anchors[2:]:
        v = tuple(Fraction(value) - origin for value, origin in zip(point, a))
        if any(u[i] * v[j] != u[j] * v[i] for i, j in ((0, 1), (0, 2), (1, 2))):
            return True
    return False


@dataclass(frozen=True, slots=True)
class StructuralLoopReferenceV2:
    loop_id: str
    points: tuple[PrintPoint3, ...]
    seam_gap_allowance_mm: float
    loop_length_mm: float
    bounds_print_space_mm: tuple[float, float, float, float, float, float]
    coordinate_frame: str
    winding_orientation: str
    winding_policy_version: str
    material_side_policy_version: str
    matching_anchor_points_print_space_mm: tuple[PrintPoint3, ...]
    anchor_predicate_version: str
    shape_canonicalization_version: str
    canonical_shape_hash: str

    def __post_init__(self) -> None:
        text = (self.loop_id, self.coordinate_frame, self.winding_orientation,
                self.winding_policy_version, self.material_side_policy_version,
                self.anchor_predicate_version, self.shape_canonicalization_version,
                self.canonical_shape_hash)
        _require(all(type(value) is str and bool(value.strip()) for value in text),
                 "nonblank exact loop metadata strings required")
        _require(self.coordinate_frame == "centered_printobject_mm_v1"
                 and self.winding_policy_version == "declared_xy_winding_v1"
                 and self.anchor_predicate_version == "exact_binary64_cross_product_v1",
                 "unknown loop frame or predicate vocabulary")
        _require(self.winding_orientation in ("unknown", "cw_xy", "ccw_xy"),
                 "unknown winding declaration")
        _require(len(self.canonical_shape_hash) == 64
                 and all(c in "0123456789abcdef" for c in self.canonical_shape_hash),
                 "full lowercase SHA-256 shape digest required")
        _require(finite_binary64(self.seam_gap_allowance_mm) and self.seam_gap_allowance_mm >= 0,
                 "invalid seam gap allowance")
        _require(finite_binary64(self.loop_length_mm) and self.loop_length_mm > 0,
                 "invalid declared loop length")
        points = _coordinates(self.points)
        anchors = _coordinates(self.matching_anchor_points_print_space_mm)
        bounds = self.bounds_print_space_mm
        _require(type(bounds) is tuple and len(bounds) == 6
                 and all(finite_binary64(value) for value in bounds), "invalid loop bounds")
        bounds = tuple(float(value) for value in bounds)
        expected = tuple(value for axis in range(3)
                         for value in (min(p[axis] for p in points), max(p[axis] for p in points)))
        _require(bounds == expected, "bounds must equal point extrema")
        _require(all(bounds[2 * axis] <= point[axis] <= bounds[2 * axis + 1]
                     for point in anchors for axis in range(3)), "anchor outside loop bounds")
        _require(_noncollinear(anchors), "matching anchors are collinear")
