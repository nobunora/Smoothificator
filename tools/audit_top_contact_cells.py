"""Fixture-only continuous nominal contact audit; never authorizes a path.

Closed rectangles cover the requested strip without gaps. Each rectangle is
bounded over its entire area, rather than certified by its sampled vertices.
"""
from __future__ import annotations

from fractions import Fraction
import json
from typing import Callable

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from adaptive_subedge.engine.support_cell import _sqrt_bounds, query_exact_nominal_top_cell
from tools.audit_layered_preview_overlap import source_segments
from tools.generate_top_surface_candidates import ROOT, SLICE_SHA256, _pinned


def lower_sources(source: bytes, command_z: Fraction) -> tuple[ExactNominalTopSegment, ...]:
    heights = {}
    height = None
    for number, line in enumerate(source.decode("ascii").splitlines(), 1):
        if line.startswith(";HEIGHT:"):
            height = Fraction(line[8:])
        heights[number] = height
    result = []
    for z, x1, y1, x2, y2, width, number in source_segments(source):
        if Fraction(str(z)) >= command_z:
            continue
        if heights[number] is None:
            raise ValueError("source bead height missing")
        result.append(ExactNominalTopSegment(
            str(number), tuple(Fraction(str(v)) for v in (x1, y1, z)),
            tuple(Fraction(str(v)) for v in (x2, y2, z)),
            Fraction(str(width)), heights[number], "structural"))
    return tuple(result)


def audit_strip(cell: ExactTopCellXY, sources: tuple[ExactNominalTopSegment, ...],
                bottom_z: Fraction, *, max_depth: int = 18, max_cells: int = 8191,
                query_cell: Callable = query_exact_nominal_top_cell,
                cancelled: Callable = lambda: False) -> dict:
    """Prove lower union reaches a constant bottom plane throughout a strip.

    This tests nominal intersection, allowing penetration. It does not prove
    shape improvement, bead deformation, or physical/chronological clearance.
    """
    if type(bottom_z) is not Fraction or not 0 <= max_depth <= 20 or max_cells < 1:
        raise ValueError("invalid bounded contact audit policy")
    pending = [(cell, 0)]
    # A stadium never rises above its maximum commanded Z. Sources strictly
    # below the target cannot establish contact; retain their global upper
    # bound when reporting a gap witness.
    relevant = tuple(s for s in sources if max(s.start_xyz_mm[2], s.end_xyz_mm[2]) >= bottom_z)
    omitted_upper = max((max(s.start_xyz_mm[2], s.end_xyz_mm[2]) for s in sources
                         if max(s.start_xyz_mm[2], s.end_xyz_mm[2]) < bottom_z), default=None)
    counts = {"reaches-bottom": 0, "gap": 0, "unresolved": 0}
    witnesses = []
    minimum_lower = None
    queried = 0
    while pending and queried < max_cells:
        if cancelled():
            break
        rectangle, depth = pending.pop()
        query = query_cell(
            rectangle, relevant, max_sources=1000, max_coordinate_bits=4096,
            sqrt_fraction_bits=128, cancelled=cancelled)
        queried += 1
        if query.top_z_lower_mm is not None and query.top_z_lower_mm >= bottom_z:
            counts["reaches-bottom"] += 1
            minimum_lower = (query.top_z_lower_mm if minimum_lower is None
                             else min(minimum_lower, query.top_z_lower_mm))
            continue
        if query.state == "absent" or (query.top_z_upper_mm is not None
                                      and query.top_z_upper_mm < bottom_z):
            counts["gap"] += 1
            if len(witnesses) < 8:
                upper_bounds = [v for v in (query.top_z_upper_mm, omitted_upper) if v is not None]
                witnesses.append({"xy_mm": [str(v) for v in (
                    rectangle.x_min_mm, rectangle.x_max_mm,
                    rectangle.y_min_mm, rectangle.y_max_mm)],
                    "top_upper_mm": str(max(upper_bounds)) if upper_bounds else None})
            continue
        if depth == max_depth or query.state == "incomplete":
            counts["unresolved"] += 1
            continue
        x0, x1, y0, y1 = (rectangle.x_min_mm, rectangle.x_max_mm,
                          rectangle.y_min_mm, rectangle.y_max_mm)
        if x1-x0 >= y1-y0:
            midpoint = (x0+x1)/2
            children = (ExactTopCellXY(x0, midpoint, y0, y1),
                        ExactTopCellXY(midpoint, x1, y0, y1))
        else:
            midpoint = (y0+y1)/2
            children = (ExactTopCellXY(x0, x1, y0, midpoint),
                        ExactTopCellXY(x0, x1, midpoint, y1))
        pending.extend((child, depth+1) for child in children)
    counts["unresolved"] += len(pending)
    return {"state": ("gap-proven" if counts["gap"] else "unresolved" if counts["unresolved"]
                      else "nominal-strip-intersection-proven"),
            "bottom_z_mm": str(bottom_z), "cells_queried": queried, "leaf_counts": counts,
            "minimum_certified_top_lower_mm": str(minimum_lower) if minimum_lower is not None else None,
            "gap_witnesses": witnesses, "printable_authorized": False}


def main() -> None:
    source = _pinned(ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode", SLICE_SHA256)
    plan = json.loads((ROOT / "artifacts/geometry-review/top-surface-candidates.json").read_text())
    row = next(row for row in plan["segments"] if row["id"] == "top-07")
    x0, y, z = (Fraction(str(v)) for v in row["start_mm"])
    x1 = Fraction(str(row["end_mm"][0]))
    width, height = Fraction(str(row["width_mm"])), Fraction(str(row["bead_height_mm"]))
    flat_half = (width-height)/2
    sources = lower_sources(source, z)
    central = audit_strip(ExactTopCellXY(x0, x1, y-flat_half, y+flat_half), sources, z-height)
    # Bound the stadium bottom over the outermost 0.001 mm strip.
    edge = Fraction("0.001")
    radius = height/2
    edge_plane = z-radius-_sqrt_bounds(radius**2-(radius-edge)**2, 128)[1]
    if not (0 < edge < radius and z-radius-edge_plane > 0
            and (z-radius-edge_plane)**2 >= radius**2-(radius-edge)**2):
        raise ValueError("edge lower-plane bound invalid for this fixture")
    edge_check = audit_strip(ExactTopCellXY(x0, x1, y+width/2-edge, y+width/2), sources, edge_plane)
    report = {"scope": "nominal-geometry-only", "candidate_id": row["id"],
              "source_slice_sha256": SLICE_SHA256,
              "candidate_mm": row, "central_flat_strip": central,
              "positive_y_rounded_edge": edge_check,
              "continuous_contact_verified": False, "printable_authorized": False,
              "limitations": "Strip intersection permits penetration; full footprint contact, shape error and nozzle clearance are not certified."}
    target = ROOT / "artifacts/geometry-review/top-07-contact-cells.json"
    target.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(target)
    print(json.dumps({"central": central, "edge": edge_check}, indent=2))


if __name__ == "__main__":
    main()
