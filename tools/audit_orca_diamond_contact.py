"""Research bounds for Orca's diamond preview, separate from nominal beads.

Source: Orca 86905a8a libvgcode Shaders.hpp / ViewerImpl.cpp. Upper bounds
include the maximum half-width axial cap extension conservatively. Lower
bounds require the source's finite axial body.
"""
from __future__ import annotations

from fractions import Fraction as F
import json

from adaptive_subedge.domain.support_cell import ExactNominalTopBounds, ExactTopCellXY
from adaptive_subedge.engine.support_cell import _sqrt_bounds
from tools.audit_top_contact_cells import audit_strip, lower_sources
from tools.generate_top_surface_candidates import ROOT, SLICE_SHA256, _pinned


def query_diamond_cell(cell, sources, **policy):
    if policy["cancelled"]():
        return ExactNominalTopBounds("incomplete", "cancelled", None, None)
    if len(sources) > policy["max_sources"]:
        return ExactNominalTopBounds("incomplete", "resource-limit", None, None)
    corners = [(x, y) for x in (cell.x_min_mm, cell.x_max_mm)
               for y in (cell.y_min_mm, cell.y_max_mm)]
    lower = upper = None
    for source in sources:
        x0, y0, z = source.start_xyz_mm
        x1, y1, z1 = source.end_xyz_mm
        if z != z1:
            raise ValueError("preview diagnostic requires horizontal source")
        dx, dy = x1-x0, y1-y0
        squared = dx*dx+dy*dy
        length_lower, length_upper = _sqrt_bounds(squared, policy["sqrt_fraction_bits"])
        if length_lower == 0:
            return ExactNominalTopBounds("incomplete", "resource-limit", None, None)
        parameters = [((x-x0)*dx+(y-y0)*dy)/squared for x, y in corners]
        if ((max(parameters) < 0 and -max(parameters)*length_lower > source.width_mm/2)
                or (min(parameters) > 1 and (min(parameters)-1)*length_lower > source.width_mm/2)):
            continue
        crosses = [(x-x0)*dy-(y-y0)*dx for x, y in corners]
        cross_min = F(0) if min(crosses) <= 0 <= max(crosses) else min(abs(c) for c in crosses)
        cross_max = max(abs(c) for c in crosses)
        distance_lower, distance_upper = cross_min/length_upper, cross_max/length_lower
        if distance_lower > source.width_mm/2:
            continue
        source_upper = z-source.height_mm*distance_lower/source.width_mm
        upper = source_upper if upper is None else max(upper, source_upper)
        if min(parameters) >= 0 and max(parameters) <= 1 and distance_upper <= source.width_mm/2:
            source_lower = z-source.height_mm*distance_upper/source.width_mm
            lower = source_lower if lower is None else max(lower, source_lower)
    if upper is None:
        return ExactNominalTopBounds("absent", "disjoint", None, None)
    if lower is None:
        return ExactNominalTopBounds("unresolved-partial", "union-coverage-unproven", None, upper)
    return ExactNominalTopBounds("full-bounded", "one-segment-covers-cell", lower, upper)


def audit_candidate(source: bytes, row: dict, *, max_cells: int = 8191) -> dict:
    x0, y, z = (F(str(v)) for v in row["start_mm"])
    x1 = F(str(row["end_mm"][0]))
    width, height = F(str(row["width_mm"])), F(str(row["bead_height_mm"]))
    half_strip = F("0.01")
    # A diamond's bottom rises linearly off center. This plane bounds the
    # highest candidate bottom throughout the central 0.02-mm strip.
    bottom_upper = z-height+height*half_strip/width
    sources = lower_sources(source, z)
    strip = audit_strip(ExactTopCellXY(x0, x1, y-half_strip, y+half_strip), sources,
                        bottom_upper, query_cell=query_diamond_cell, max_cells=max_cells)
    # A witness near the sampled valley; closed area upper bound is stronger
    # than a single floating-point sample, and includes all source caps.
    witness = ExactTopCellXY(F("129.6106"), F("129.6108"), y-F("0.000001"), y+F("0.000001"))
    bounds = query_diamond_cell(witness, sources, max_sources=1000,
                               sqrt_fraction_bits=128, cancelled=lambda: False)
    gap_lower = None if bounds.top_z_upper_mm is None else z-height-bounds.top_z_upper_mm
    return {"candidate": row, "central_strip_width_mm": "0.02", "central_strip": strip,
            "witness_xy_mm": [str(v) for v in (witness.x_min_mm, witness.x_max_mm,
                                                witness.y_min_mm, witness.y_max_mm)],
            "witness_support_upper_mm": str(bounds.top_z_upper_mm),
            "witness_gap_lower_mm": str(gap_lower),
            "witness_gap_proven": gap_lower is not None and gap_lower > 0,
            "printable_authorized": False,
            "limitations": "Preview central-strip intersection only; permits penetration; no shape or tool-clearance proof."}


def main():
    source = _pinned(ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode", SLICE_SHA256)
    plan = json.loads((ROOT / "artifacts/geometry-review/top-surface-candidates.json").read_text())
    current = next(row for row in plan["segments"] if row["id"] == "top-07")
    previous = dict(current, bead_height_mm=0.14)
    report = {"source_slice_sha256": SLICE_SHA256, "renderer_source_commit": "86905a8a20d5887f3b13017e66cd897766334bd3",
              "previous": audit_candidate(source, previous, max_cells=512), "current": audit_candidate(source, current)}
    target = ROOT / "artifacts/geometry-review/orca-diamond-contact.json"
    target.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(target)
    for key in ("previous", "current"):
        print(key, report[key]["central_strip"]["state"], report[key]["witness_gap_proven"])


if __name__ == "__main__":
    main()
