"""Exact planar difference values; construction grants no geometry authority."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .mesh_section import MeshSectionLoop


def _require(condition, message):
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


def _turn(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def _on_segment(a, b, p):
    return (_turn(a, b, p) == 0
            and min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def _intersects(a, b, c, d):
    ab_c, ab_d, cd_a, cd_b = _turn(a, b, c), _turn(a, b, d), _turn(c, d, a), _turn(c, d, b)
    return (ab_c*ab_d < 0 and cd_a*cd_b < 0
            or _on_segment(a, b, c) or _on_segment(a, b, d)
            or _on_segment(c, d, a) or _on_segment(c, d, b))


def _cell_area(cell):
    _require(type(cell) is tuple and len(cell) >= 3
             and all(type(p) is tuple and len(p) == 2
                     and all(type(v) is Fraction for v in p) for p in cell),
             "exact polygon coordinate tuples required")
    _require(len(set(cell)) == len(cell) and cell[0] == min(cell),
             "unique vertices and canonical first vertex required")
    size = len(cell)
    area2 = sum((cell[i][0]*cell[(i+1) % size][1]
                 - cell[i][1]*cell[(i+1) % size][0] for i in range(size)), Fraction(0))
    _require(area2 > 0, "positive CCW polygon area required")
    for i, a in enumerate(cell):
        b = cell[(i+1) % size]
        for j, point in enumerate(cell):
            if j not in (i, (i+1) % size):
                _require(_turn(a, b, point) > 0, "strict convex cell required")
        for j in range(i+1, size):
            if j == (i+1) % size or (j+1) % size == i:
                continue
            _require(not _intersects(a, b, cell[j], cell[(j+1) % size]),
                     "nonadjacent cell edges cannot intersect")
    return area2/2


@dataclass(frozen=True, slots=True)
class ConvexSectionDifference:
    state: str
    reason: str
    lower_z_mm: Fraction
    upper_z_mm: Fraction
    lower_section: MeshSectionLoop | None
    upper_section: MeshSectionLoop | None
    cells_xy_mm: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    area_mm2: Fraction | None

    def __post_init__(self):
        reasons = {
            "complete": ("difference-derived", "empty-difference"),
            "incomplete": ("cancelled", "resource-limit"),
            "rejected": ("empty-mesh", "unused-vertex", "degenerate-bounds",
                         "degenerate-triangle", "duplicate-triangle", "nonmanifold-edge",
                         "inconsistent-winding", "disconnected-shell", "nonmanifold-vertex",
                         "zero-signed-volume", "self-intersection", "coplanar-facet",
                         "ambiguous-join", "non-simple-graph", "multiple-loops", "zero-area",
                         "empty-section", "nonconvex-section", "non-nested-sections"),
        }
        _require(type(self.state) is str and self.state in reasons
                 and type(self.reason) is str and self.reason in reasons[self.state],
                 "invalid section difference disposition")
        _require(type(self.lower_z_mm) is Fraction and type(self.upper_z_mm) is Fraction
                 and self.lower_z_mm < self.upper_z_mm and type(self.cells_xy_mm) is tuple,
                 "exact ordered section heights and cells required")
        if self.state != "complete":
            _require(self.lower_section is None and self.upper_section is None
                     and not self.cells_xy_mm and self.area_mm2 is None,
                     "partial difference geometry forbidden")
            return
        _require(type(self.lower_section) is MeshSectionLoop
                 and type(self.upper_section) is MeshSectionLoop
                 and self.lower_section.command_z_mm == self.lower_z_mm
                 and self.upper_section.command_z_mm == self.upper_z_mm
                 and type(self.area_mm2) is Fraction,
                 "complete difference requires matching exact sections and area")
        if self.reason == "empty-difference":
            _require(not self.cells_xy_mm and self.area_mm2 == 0,
                     "empty difference cannot contain cells or positive area")
            return
        _require(bool(self.cells_xy_mm) and self.area_mm2 > 0,
                 "derived difference requires positive cells and area")
        area = sum((_cell_area(cell) for cell in self.cells_xy_mm), Fraction(0))
        _require(area == self.area_mm2, "cell area sum must match declared area")
