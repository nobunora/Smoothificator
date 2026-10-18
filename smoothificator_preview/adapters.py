"""UI-thread copies of live Orca model bindings; no live views escape."""
from dataclasses import dataclass
from math import isfinite
from numbers import Integral

from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from .limits import FRAME, MAX_TRIANGLES, MAX_VERTICES


@dataclass(frozen=True, slots=True)
class ModelSnapshot:
    mesh: IndexedTriangleMesh
    name: str
    frame: str = FRAME


def _matrix(binding):
    if tuple(binding.shape) != (4, 4):
        raise ValueError("invalid-matrix-shape")
    matrix = tuple(tuple(float(binding[i, j]) for j in range(4)) for i in range(4))
    if (any(not isfinite(v) for row in matrix for v in row)
            or matrix[3] != (0, 0, 0, 1)):
        raise ValueError("invalid-affine-matrix")
    return matrix


def copy_model(model):
    """Call only in Orca's Script/UI callback, before dispatching a worker."""
    if model.object_count() != 1:
        raise ValueError("one-model-object-required")
    obj = model.object(0)
    if obj.instance_count() != 1 or obj.volume_count() != 1:
        raise ValueError("one-instance-and-volume-required")
    instance, volume = obj.instance(0), obj.volume(0)
    if not instance.is_printable() or not volume.is_model_part():
        raise ValueError("printable-model-part-required")
    mesh = volume.mesh()
    nv, nt = mesh.vertex_count(), mesh.triangle_count()
    if not (0 < nv <= MAX_VERTICES and 0 < nt <= MAX_TRIANGLES):
        raise ValueError("resource-limit")
    # Orca returns NumPy matrix copies; indexed mesh access needs no arrays.
    instance_matrix, volume_matrix = _matrix(instance.matrix()), _matrix(volume.matrix())
    transform = tuple(tuple(sum(instance_matrix[i][k]*volume_matrix[k][j]
                                for k in range(4)) for j in range(4)) for i in range(4))
    vertices = []
    for index in range(nv):
        source = tuple(float(v) for v in mesh.vertex(index))
        if len(source) != 3 or any(not isfinite(v) for v in source):
            raise ValueError("invalid-source-vertex")
        point = (*source, 1.0)
        vertices.append(PrintPoint3(*(sum(transform[i][k]*point[k] for k in range(4))
                                      for i in range(3))))
    triangles = []
    for index in range(nt):
        triangle = tuple(mesh.triangle(index))
        if (len(triangle) != 3 or any(isinstance(v, bool) or not isinstance(v, Integral)
                                     or not 0 <= v < nv for v in triangle)):
            raise ValueError("invalid-triangle-index")
        triangles.append(tuple(int(v) for v in triangle))
    return ModelSnapshot(IndexedTriangleMesh(tuple(vertices), tuple(triangles)), str(obj.name)[:256])
