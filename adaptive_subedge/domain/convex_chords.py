"""Unscored exact planar proposals, not feasible paths or execution permission."""
from dataclasses import dataclass
from fractions import Fraction

from .errors import ContractError, ReasonCode
from .mesh_section import MeshSectionLoop, MeshSectionResult


def _require(condition, message):
    if not condition:
        raise ContractError(ReasonCode.INVALID_GEOMETRY, message)


@dataclass(frozen=True, slots=True)
class ChordProposal:
    position_mm: Fraction
    state: str
    reason: str
    start_xy_mm: tuple[Fraction, Fraction] | None
    end_xy_mm: tuple[Fraction, Fraction] | None

    def __post_init__(self):
        _require(type(self.position_mm) is Fraction and type(self.state) is str
                 and type(self.reason) is str, "exact chord position and disposition required")
        if self.state == "proposed":
            _require(self.reason == "unscored", "chord proposals cannot assert feasibility")
            for endpoint in (self.start_xy_mm, self.end_xy_mm):
                _require(type(endpoint) is tuple and len(endpoint) == 2
                         and all(type(x) is Fraction for x in endpoint), "exact XY endpoints required")
            _require(self.start_xy_mm != self.end_xy_mm, "nonzero chord required")
        else:
            _require(self.state == "rejected" and self.reason in (
                "empty-footprint", "insufficient-span", "centerline-contact", "centerline-outside"),
                "invalid chord rejection")
            _require(self.start_xy_mm is None and self.end_xy_mm is None,
                     "rejected chord endpoints forbidden")


@dataclass(frozen=True, slots=True)
class ConvexChordProposalSet:
    state: str
    reason: str
    command_z_mm: Fraction
    axis: str
    width_mm: Fraction
    proposals: tuple[ChordProposal, ...]

    def __post_init__(self):
        _require(type(self.state) is str and type(self.reason) is str
                 and type(self.command_z_mm) is Fraction
                 and type(self.axis) is str and self.axis in ("X", "Y")
                 and type(self.width_mm) is Fraction and self.width_mm > 0
                 and type(self.proposals) is tuple, "invalid exact chord set metadata")
        if self.state != "complete":
            _require(not self.proposals, "partial chord sets forbidden")
            if self.state == "incomplete":
                _require(self.reason in ("resource-limit", "cancelled", "ray-directions-exhausted",
                                         "classification-inconsistent"), "invalid incomplete chord set")
            else:
                _require(self.state == "rejected", "invalid chord set state")
                if self.reason not in ("empty-section", "nonconvex-section"):
                    MeshSectionResult("rejected", self.reason, None)
            return
        _require(self.reason == "proposals-evaluated" and bool(self.proposals)
                 and all(type(row) is ChordProposal for row in self.proposals),
                 "completed set requires exact nonempty rows")
        running = 0 if self.axis == "X" else 1
        previous = None
        for row in self.proposals:
            _require(previous is None or previous < row.position_mm,
                     "unique ascending chord positions required")
            previous = row.position_mm
            if row.state == "proposed":
                start, end = row.start_xy_mm, row.end_xy_mm
                _require(start[running] < end[running]
                         and start[1-running] == end[1-running] == row.position_mm,
                         "chord endpoints must follow their declared axis and position")


@dataclass(frozen=True, slots=True)
class ConvexChordPreview:
    section: MeshSectionLoop | None
    proposals: ConvexChordProposalSet

    def __post_init__(self):
        _require(type(self.proposals) is ConvexChordProposalSet, "exact proposal set required")
        if self.proposals.state == "complete":
            _require(type(self.section) is MeshSectionLoop
                     and self.section.command_z_mm == self.proposals.command_z_mm,
                     "completed preview requires its source section")
        else:
            _require(self.section is None, "failed preview cannot retain partial geometry")


@dataclass(frozen=True, slots=True)
class BandChordPreview:
    state: str
    reason: str
    section: MeshSectionLoop | None
    proposals: tuple[ChordProposal, ...]
    width_mm: Fraction | None
    command_z_mm: Fraction
    axis: str
    common_running_interval: tuple[Fraction, Fraction] | None

    def __post_init__(self):
        _require(type(self.state) is str and type(self.reason) is str
                 and type(self.command_z_mm) is Fraction and type(self.axis) is str
                 and self.axis in ("X", "Y") and type(self.proposals) is tuple,
                 "invalid band preview metadata")
        if self.state != "complete":
            _require(self.section is None and not self.proposals and self.width_mm is None
                     and self.common_running_interval is None, "partial band geometry forbidden")
            if self.state == "rejected" and self.reason in (
                    "width-span-infeasible", "band-chord-rejected", "no-common-running-span"):
                return
            ConvexChordProposalSet(self.state, self.reason, self.command_z_mm,
                                   self.axis, Fraction(1), ())
            return
        _require(self.reason == "bands-proposed" and type(self.section) is MeshSectionLoop
                 and self.section.command_z_mm == self.command_z_mm,
                 "completed bands require same-Z source section")
        ConvexChordProposalSet("complete", "proposals-evaluated", self.command_z_mm,
                               self.axis, self.width_mm, self.proposals)
        _require(all(row.state == "proposed" for row in self.proposals),
                 "all bands must be proposed")
        for left, right in zip(self.proposals, self.proposals[1:]):
            _require(right.position_mm-left.position_mm == self.width_mm,
                     "band centers must partition contiguous equal widths")
        interval = self.common_running_interval
        _require(type(interval) is tuple and len(interval) == 2
                 and all(type(x) is Fraction for x in interval) and interval[0] < interval[1],
                 "positive exact common interval required")
        running = 0 if self.axis == "X" else 1
        expected = (max(row.start_xy_mm[running] for row in self.proposals),
                    min(row.end_xy_mm[running] for row in self.proposals))
        _require(interval == expected, "common interval must equal endpoint intersection")
