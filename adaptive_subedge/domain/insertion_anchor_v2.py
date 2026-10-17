"""Standalone research anchor vocabulary; not matching or execution evidence."""
from dataclasses import dataclass

from .errors import ContractError, ReasonCode
from .numeric import finite_binary64


@dataclass(frozen=True, slots=True)
class InsertionAnchorV2:
    anchor_id: str
    structural_loop_ids: tuple[str, ...]
    layer_index: int
    boundary_signature: str
    target_structural_interval_id: str
    boundary_signature_schema_version: str
    matching_tolerance_mm: float
    matching_profile_id: str

    def __post_init__(self) -> None:
        text_fields = (self.anchor_id, self.boundary_signature,
                       self.target_structural_interval_id,
                       self.boundary_signature_schema_version,
                       self.matching_profile_id)
        if any(type(value) is not str or not value.strip() for value in text_fields):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "nonblank anchor identifiers required")
        if (type(self.structural_loop_ids) is not tuple or not self.structural_loop_ids
                or any(type(value) is not str or not value.strip()
                       for value in self.structural_loop_ids)):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "immutable nonblank loop identifiers required")
        if len(set(self.structural_loop_ids)) != len(self.structural_loop_ids):
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "duplicate anchor loop identifier")
        if type(self.layer_index) is not int or self.layer_index < 1:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "anchor layer must be an integer >=1")
        if self.boundary_signature_schema_version != "opaque_boundary_signature_v1":
            raise ContractError(ReasonCode.UNKNOWN_IDENTITY_SCHEMA, "unsupported boundary signature vocabulary")
        if not finite_binary64(self.matching_tolerance_mm) or self.matching_tolerance_mm <= 0:
            raise ContractError(ReasonCode.INVALID_GEOMETRY, "finite positive matching tolerance required")
