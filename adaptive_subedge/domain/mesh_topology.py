"""Indexed topology values; positive volume is not material-side proof."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .geometry import PrintPoint3


def _require(condition, message):
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


@dataclass(frozen=True, slots=True)
class IndexedTriangleMesh:
    vertices: tuple[PrintPoint3, ...]
    triangles: tuple[tuple[int, int, int], ...]

    def __post_init__(self):
        # Element validation belongs after the evaluator's resource preflight.
        _require(type(self.vertices) is tuple and type(self.triangles) is tuple,
                 "immutable mesh tuples required")


@dataclass(frozen=True, slots=True)
class OrientedMeshTopology:
    mesh: IndexedTriangleMesh
    oriented_triangles: tuple[tuple[int, int, int], ...]
    edges: tuple[tuple[int, int, int, int], ...]
    vertex_faces: tuple[tuple[int, ...], ...]
    input_signed_volume_six_mm3: Fraction
    globally_flipped: bool

    def __post_init__(self):
        _require(type(self.mesh) is IndexedTriangleMesh, "exact mesh required")
        vertices, faces = len(self.mesh.vertices), len(self.mesh.triangles)
        _require(type(self.oriented_triangles) is tuple and len(self.oriented_triangles) == faces,
                 "oriented face count mismatch")
        for row in self.oriented_triangles:
            _require(type(row) is tuple and len(row) == 3
                     and all(type(i) is int and 0 <= i < vertices for i in row)
                     and len(set(row)) == 3, "invalid oriented face")
        _require(type(self.edges) is tuple, "immutable edges required")
        previous = None
        for row in self.edges:
            _require(type(row) is tuple and len(row) == 4
                     and all(type(i) is int for i in row), "invalid edge row")
            a, b, c, d = row
            _require(0 <= a < b < vertices and 0 <= c < d < faces
                     and (previous is None or previous < (a, b)), "invalid canonical edge")
            previous = (a, b)
        _require(type(self.vertex_faces) is tuple and len(self.vertex_faces) == vertices,
                 "vertex incidence count mismatch")
        for row in self.vertex_faces:
            _require(type(row) is tuple and all(type(i) is int and 0 <= i < faces for i in row)
                     and tuple(sorted(set(row))) == row, "invalid vertex incidence")
        _require(type(self.input_signed_volume_six_mm3) is Fraction
                 and self.input_signed_volume_six_mm3 != 0
                 and type(self.globally_flipped) is bool
                 and self.globally_flipped == (self.input_signed_volume_six_mm3 < 0),
                 "invalid input volume or reversal")


@dataclass(frozen=True, slots=True)
class MeshTopologyResult:
    state: str
    reason: str
    topology: OrientedMeshTopology | None

    def __post_init__(self):
        reasons = {
            "complete": ("prepared",),
            "incomplete": ("cancelled", "resource-limit"),
            "rejected": ("empty-mesh", "unused-vertex", "degenerate-bounds",
                         "degenerate-triangle", "duplicate-triangle", "nonmanifold-edge",
                         "inconsistent-winding", "disconnected-shell", "nonmanifold-vertex",
                         "zero-signed-volume"),
        }
        _require(type(self.state) is str and self.state in reasons
                 and type(self.reason) is str and self.reason in reasons[self.state],
                 "invalid topology disposition")
        _require((self.state == "complete" and type(self.topology) is OrientedMeshTopology)
                 or (self.state != "complete" and self.topology is None),
                 "only complete topology may be published")
