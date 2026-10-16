"""Nominal support query vocabulary; local bounds are not print authorization."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .geometry import PrintPoint3
from .numeric import finite_binary64


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


@dataclass(frozen=True, slots=True)
class SupportCellXY:
    x_min_mm: float
    x_max_mm: float
    y_min_mm: float
    y_max_mm: float

    def __post_init__(self):
        _require(all(finite_binary64(x) for x in
                     (self.x_min_mm, self.x_max_mm, self.y_min_mm, self.y_max_mm)),
                 "finite support cell coordinates required")
        _require(float(self.x_min_mm) < float(self.x_max_mm)
                 and float(self.y_min_mm) < float(self.y_max_mm),
                 "positive binary64 support cell extents required")


@dataclass(frozen=True, slots=True)
class NominalSupportSegment:
    segment_id: str
    start: PrintPoint3
    end: PrintPoint3
    width_mm: float
    height_mm: float
    source_kind: str
    execution_order: int

    def __post_init__(self):
        _require(type(self.segment_id) is str and bool(self.segment_id.strip()),
                 "nonblank segment identity required")
        _require(type(self.start) is PrintPoint3 and type(self.end) is PrintPoint3,
                 "exact immutable support endpoints required")
        _require(finite_binary64(self.width_mm) and finite_binary64(self.height_mm),
                 "finite support dimensions required")
        _require(float(self.width_mm) >= float(self.height_mm) > 0,
                 "support stadium requires width >= height > 0")
        _require((float(self.start.x_mm), float(self.start.y_mm))
                 != (float(self.end.x_mm), float(self.end.y_mm)),
                 "nonzero support XY length required")
        _require(type(self.source_kind) is str and self.source_kind in ("structural", "candidate"),
                 "invalid support source kind")
        _require(type(self.execution_order) is int and self.execution_order >= 0,
                 "nonnegative support execution order required")
        if self.source_kind == "candidate":
            _require(float(self.start.z_mm) == float(self.end.z_mm),
                     "candidate support must have constant command Z")


@dataclass(frozen=True, slots=True)
class SupportCellQueryPolicy:
    version: str
    sqrt_fraction_bits: int
    max_source_segments: int

    def __post_init__(self):
        if not (type(self.version) is str and self.version == "nominal_bead_cell_bounds_v1"
                and type(self.sqrt_fraction_bits) is int and 1 <= self.sqrt_fraction_bits <= 4096
                and type(self.max_source_segments) is int and self.max_source_segments >= 1):
            raise ContractError(ReasonCode.INVALID_SETTING, "invalid explicit support query policy")


@dataclass(frozen=True, slots=True)
class SupportCellQueryResult:
    state: str
    top_z_lower_mm: Fraction | None
    top_z_upper_mm: Fraction | None
    effective_height_lower_mm: Fraction | None
    effective_height_upper_mm: Fraction | None
    reason: str

    def __post_init__(self):
        allowed = {
            "proven-supported": ("height-within-bounds",),
            "proven-unsupported": ("disjoint", "height-outside-bounds"),
            "unresolved": ("coverage-unresolved", "height-unresolved", "resource-limit"),
        }
        _require(type(self.state) is str and self.state in allowed
                 and type(self.reason) is str and self.reason in allowed[self.state],
                 "invalid support query outcome")
        bounds = (self.top_z_lower_mm, self.top_z_upper_mm,
                  self.effective_height_lower_mm, self.effective_height_upper_mm)
        _require(all(x is None or type(x) is Fraction for x in bounds),
                 "exact rational support bounds required")
        if self.reason in ("disjoint", "resource-limit"):
            _require(all(x is None for x in bounds), "empty outcome cannot claim bounds")
            return
        _require(self.top_z_upper_mm is not None and self.effective_height_lower_mm is not None,
                 "upper top and lower height bounds required")
        _require((self.top_z_lower_mm is None) == (self.effective_height_upper_mm is None),
                 "paired full-coverage bounds required")
        if self.top_z_lower_mm is not None:
            _require(self.top_z_lower_mm <= self.top_z_upper_mm
                     and self.effective_height_lower_mm <= self.effective_height_upper_mm,
                     "inverted support bounds")
        if self.reason in ("height-within-bounds", "height-unresolved"):
            _require(self.top_z_lower_mm is not None, "full-coverage bounds required")
        if self.reason == "coverage-unresolved":
            _require(self.top_z_lower_mm is None, "coverage remains unproven")
