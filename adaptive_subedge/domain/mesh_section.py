"""Exact research plane sections, without material or quantization authority."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .mesh_topology import MeshTopologyResult


def _require(condition, message):
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


@dataclass(frozen=True, slots=True)
class MeshSectionVertex:
    source_vertex_ids: tuple[int, ...]
    edge_parameter: Fraction | None
    x_mm: Fraction
    y_mm: Fraction

    def __post_init__(self):
        ids = self.source_vertex_ids
        _require(type(ids) is tuple and len(ids) in (1, 2)
                 and all(type(i) is int and i >= 0 for i in ids)
                 and (len(ids) == 1 or ids[0] < ids[1]), "invalid section topology key")
        _require((len(ids) == 1 and self.edge_parameter is None)
                 or (len(ids) == 2 and type(self.edge_parameter) is Fraction
                     and 0 < self.edge_parameter < 1), "invalid edge interpolation parameter")
        _require(type(self.x_mm) is Fraction and type(self.y_mm) is Fraction,
                 "exact section coordinates required")


@dataclass(frozen=True, slots=True)
class MeshSectionLoop:
    command_z_mm: Fraction
    vertices: tuple[MeshSectionVertex, ...]

    def __post_init__(self):
        _require(type(self.command_z_mm) is Fraction and type(self.vertices) is tuple
                 and len(self.vertices) >= 3
                 and all(type(v) is MeshSectionVertex for v in self.vertices),
                 "exact section loop required")
        _require(len({v.source_vertex_ids for v in self.vertices}) == len(self.vertices),
                 "unique topology keys required; closure is implicit")


@dataclass(frozen=True, slots=True)
class MeshSectionResult:
    state: str
    reason: str
    loop: MeshSectionLoop | None

    def __post_init__(self):
        reasons = {"complete": ("section-loop",), "empty": ("no-crossing",),
                   "incomplete": ("cancelled", "resource-limit", "predicate-uncertain"),
                   "rejected": ("coplanar-facet", "ambiguous-join", "non-simple-graph",
                                "multiple-loops", "self-intersection", "zero-area")}
        _require(type(self.state) is str and self.state in reasons and type(self.reason) is str,
                 "invalid section disposition")
        if self.state == "rejected" and self.reason not in reasons[self.state]:
            # The topology owner validates its closed reason set.
            MeshTopologyResult("rejected", self.reason, None)
        else:
            _require(self.reason in reasons[self.state], "invalid section reason")
        _require((self.state == "complete" and type(self.loop) is MeshSectionLoop)
                 or (self.state != "complete" and self.loop is None), "only complete loops may escape")
