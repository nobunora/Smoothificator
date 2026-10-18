"""Explicit assumed planar tip disc; not measured or complete head geometry."""
from dataclasses import dataclass, field
from fractions import Fraction as F
from hashlib import sha256
import json


DEFAULT_ASSUMED_TOOL_DIAMETER_MM = F('.4')


@dataclass(frozen=True)
class ProvisionalPlanarTip:
    assumed_diameter_mm: F = DEFAULT_ASSUMED_TOOL_DIAMETER_MM
    model_version: str = field(default='provisional-planar-tip-disc-v1', init=False)

    def __post_init__(self):
        if type(self.assumed_diameter_mm) is not F or self.assumed_diameter_mm <= 0:
            raise ValueError('positive exact rational assumed diameter required')

    @property
    def radius_mm(self):
        return self.assumed_diameter_mm/2

    @property
    def identity(self):
        content = json.dumps({'model_version': self.model_version,
            'assumed_diameter_mm': str(self.assumed_diameter_mm)}, sort_keys=True,
            separators=(',', ':')).encode('ascii')
        return sha256(content).hexdigest()


@dataclass(frozen=True)
class SweptPlanarDiscBounds:
    start_xyz_mm: tuple[F, F, F]
    end_xyz_mm: tuple[F, F, F]
    lower_xyz_mm: tuple[F, F, F]
    upper_xyz_mm: tuple[F, F, F]
    geometry_identity: str


@dataclass(frozen=True)
class SweptPlanarPolylineBounds:
    point_count: int
    lower_xyz_mm: tuple[F, F, F]
    upper_xyz_mm: tuple[F, F, F]
    geometry_identity: str


def swept_planar_disc_bounds(start, end, geometry):
    """Conservative tip-disc sweep AABB with endpoint Z only; no axial height."""
    if type(geometry) is not ProvisionalPlanarTip:
        raise ValueError('immutable provisional planar tip required')
    for point in (start, end):
        if type(point) is not tuple or len(point) != 3 or any(type(v) is not F for v in point):
            raise ValueError('exact immutable XYZ endpoints required')
    radius = geometry.radius_mm
    lower = tuple(min(a, b)-(radius if axis < 2 else 0) for axis, (a, b) in enumerate(zip(start, end)))
    upper = tuple(max(a, b)+(radius if axis < 2 else 0) for axis, (a, b) in enumerate(zip(start, end)))
    return SweptPlanarDiscBounds(start, end, lower, upper, geometry.identity)


def swept_planar_polyline_bounds(points, geometry):
    """Union AABB of every closed or open polyline segment's assumed tip sweep."""
    if type(points) is not tuple or len(points) < 2:
        raise ValueError('immutable nonempty planar-tip polyline required')
    segments = tuple(swept_planar_disc_bounds(a, b, geometry) for a, b in zip(points, points[1:]))
    lower = tuple(min(segment.lower_xyz_mm[axis] for segment in segments) for axis in range(3))
    upper = tuple(max(segment.upper_xyz_mm[axis] for segment in segments) for axis in range(3))
    return SweptPlanarPolylineBounds(len(points), lower, upper, geometry.identity)
