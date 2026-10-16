"""Numerical mesh predicates, not reusable execution permission receipts."""
from dataclasses import dataclass

from .errors import ContractError, ReasonCode
from .mesh_topology import MeshTopologyResult


def _require(condition, message):
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


@dataclass(frozen=True, slots=True)
class MeshEmbeddingResult:
    state: str
    reason: str

    def __post_init__(self):
        _require(type(self.state) is str and type(self.reason) is str,
                 "exact embedding disposition strings required")
        if self.state == "complete":
            _require(self.reason == "embedded", "invalid embedding completion")
        elif self.state == "rejected" and self.reason == "self-intersection":
            pass
        else:
            _require(self.state in ("rejected", "incomplete"), "invalid embedding state")
            MeshTopologyResult(self.state, self.reason, None)


@dataclass(frozen=True, slots=True)
class MeshPointClassification:
    state: str
    reason: str
    classification: str | None

    def __post_init__(self):
        _require(type(self.state) is str and type(self.reason) is str,
                 "exact classification disposition strings required")
        if self.state == "complete":
            _require(self.reason == "classified" and type(self.classification) is str
                     and self.classification in ("inside", "outside", "boundary"),
                     "invalid point classification")
        else:
            _require(self.classification is None, "incomplete classification cannot escape")
            if self.state == "incomplete" and self.reason == "ray-directions-exhausted":
                return
            MeshEmbeddingResult(self.state, self.reason)


@dataclass(frozen=True, slots=True)
class MeshSegmentClassification:
    state: str
    reason: str
    classification: str | None

    def __post_init__(self):
        _require(type(self.state) is str and type(self.reason) is str,
                 "exact segment disposition strings required")
        if self.state == "complete":
            _require(self.reason == "classified" and type(self.classification) is str
                     and self.classification in ("strictly-inside", "strictly-outside", "boundary-contact"),
                     "invalid segment classification")
        else:
            _require(self.classification is None, "partial segment classification forbidden")
            if self.state == "incomplete" and self.reason == "classification-inconsistent":
                return
            MeshPointClassification(self.state, self.reason, None)
