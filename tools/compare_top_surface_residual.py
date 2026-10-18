"""Compare a pinned offline candidate with the complete sliced baseline.

This fixture adapter does not generate a Plan or authorize printing. It uses
the physical nominal stadium model, never Orca's diamond display surrogate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
from io import BytesIO
import json
import math
from time import monotonic
from xml.etree import ElementTree
from zipfile import ZipFile

from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.coupon_residual import CouponVerticalComparison, VerticalResidualInterval
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from adaptive_subedge.engine.coupon_residual import compare_planar_coupon_vertical_residual
from tools.audit_layered_preview_overlap import source_segments
from tools.audit_top_contact_cells import audit_strip, lower_sources
from tools.build_true_z_orca_review import _candidate_rows
from tools.generate_top_surface_candidates import (
    MODEL_SHA256, PLATE_OFFSET_MM, ROOT, SLICE_SHA256, STL_SHA256, _pinned, _top_face,
)


def coupon_mesh(model: bytes) -> IndexedTriangleMesh:
    if hashlib.sha256(model).hexdigest() != MODEL_SHA256:
        raise ValueError("unpinned 3MF")
    matrix, _, _, _ = _top_face(model)
    with ZipFile(BytesIO(model)) as archive:
        part = ElementTree.fromstring(archive.read("3D/Objects/offline-coupon.stl_1.model"))
    vertices = []
    for node in part.findall(".//{*}vertices/{*}vertex"):
        x, y, z = (float(node.attrib[axis]) for axis in "xyz")
        vertices.append(PrintPoint3(
            matrix[0]*x+matrix[3]*y+matrix[6]*z+matrix[9]+PLATE_OFFSET_MM[0],
            matrix[1]*x+matrix[4]*y+matrix[7]*z+matrix[10]+PLATE_OFFSET_MM[1],
            matrix[2]*x+matrix[5]*y+matrix[8]*z+matrix[11]))
    faces = tuple(tuple(int(node.attrib[key]) for key in ("v1", "v2", "v3"))
                  for node in part.findall(".//{*}triangles/{*}triangle"))
    return IndexedTriangleMesh(tuple(vertices), faces)


def spatial_baseline(source: bytes, rectangle: ExactTopCellXY):
    """Discard only sources whose conservative XY bounds miss the rectangle.

    Later layers are deliberately retained. Truncating at candidate Z could
    manufacture a favorable score against material already scheduled later.
    """
    if hashlib.sha256(source).hexdigest() != SLICE_SHA256:
        raise ValueError("unpinned source slice")
    rows = source_segments(source)
    if len(rows) != 669:
        raise ValueError("unexpected complete baseline count")
    all_sources = lower_sources(source, F(str(max(row[0] for row in rows)))+1)
    if len(all_sources) != len(rows):
        raise ValueError("incomplete structural baseline")
    return all_sources, overlapping_sources(all_sources, rectangle)


def overlapping_sources(sources, rectangle):
    return tuple(s for s in sources if
        max(s.start_xyz_mm[0], s.end_xyz_mm[0])+s.width_mm/2 >= rectangle.x_min_mm and
        min(s.start_xyz_mm[0], s.end_xyz_mm[0])-s.width_mm/2 <= rectangle.x_max_mm and
        max(s.start_xyz_mm[1], s.end_xyz_mm[1])+s.width_mm/2 >= rectangle.y_min_mm and
        min(s.start_xyz_mm[1], s.end_xyz_mm[1])-s.width_mm/2 <= rectangle.y_max_mm)


def _interval(interval):
    return None if interval is None else {
        "lower_exact_mm": str(interval.lower_mm), "upper_exact_mm": str(interval.upper_mm),
        "lower_mm": float(interval.lower_mm), "upper_mm": float(interval.upper_mm)}


def dominant_baseline(rectangle, sources, cancelled):
    """Remove lower sources only after a whole-region dominance certificate."""
    if not sources:
        return sources, None
    highest = max(max(s.start_xyz_mm[2], s.end_xyz_mm[2]) for s in sources)
    upper = tuple(s for s in sources if min(s.start_xyz_mm[2], s.end_xyz_mm[2]) == highest)
    lower = tuple(s for s in sources if s not in upper)
    if not upper or not lower:
        return sources, None
    omitted_ceiling = max(max(s.start_xyz_mm[2], s.end_xyz_mm[2]) for s in lower)
    certificate = audit_strip(rectangle, upper, omitted_ceiling, max_depth=18,
                              max_cells=2047, cancelled=cancelled)
    if certificate["state"] == "nominal-strip-intersection-proven":
        return upper, certificate
    return sources, certificate


def compare_partitions(mesh, rectangle, structural, candidate, **policy):
    """A closed rational X partition avoids very thin whole-strip quadtrees.

    Every tile is independently certified by the unchanged comparison engine.
    Maxima of their interval bounds bound the maximum over the closed union.
    Leaf allocations sum to no more than the supplied global leaf budget.
    """
    count = min(32, policy["max_leaf_cells"])
    per_tile = policy["max_leaf_cells"]//count
    results = []
    for index in range(count):
        x0 = rectangle.x_min_mm+(rectangle.x_max_mm-rectangle.x_min_mm)*F(index,count)
        x1 = rectangle.x_min_mm+(rectangle.x_max_mm-rectangle.x_min_mm)*F(index+1,count)
        tile = ExactTopCellXY(x0,x1,rectangle.y_min_mm,rectangle.y_max_mm)
        result = compare_planar_coupon_vertical_residual(
            mesh, tile, overlapping_sources(structural,tile), candidate,
            **(policy | {"max_leaf_cells": per_tile}))
        results.append(result)
        if result.state != "complete":
            return CouponVerticalComparison(result.state,result.reason,policy["source_mesh_id"],
                policy["baseline_slice_id"],None,None,None,None,sum(r.leaf_count for r in results))
        if result.target_plane_abc != results[0].target_plane_abc:
            return CouponVerticalComparison("rejected","target-unresolved",policy["source_mesh_id"],
                policy["baseline_slice_id"],None,None,None,None,sum(r.leaf_count for r in results))
    if policy["cancelled"]():
        return CouponVerticalComparison("incomplete","cancelled",policy["source_mesh_id"],
            policy["baseline_slice_id"],None,None,None,None,sum(r.leaf_count for r in results))
    baseline = VerticalResidualInterval(max(r.baseline_max_residual.lower_mm for r in results),
                                         max(r.baseline_max_residual.upper_mm for r in results))
    augmented = VerticalResidualInterval(max(r.augmented_max_residual.lower_mm for r in results),
                                          max(r.augmented_max_residual.upper_mm for r in results))
    reason = ("certified-reduction" if augmented.upper_mm < baseline.lower_mm else
              "certified-nonreduction" if augmented.lower_mm >= baseline.upper_mm else "interval-overlap")
    return CouponVerticalComparison("complete",reason,policy["source_mesh_id"],policy["baseline_slice_id"],
        rectangle,results[0].target_plane_abc,baseline,augmented,sum(r.leaf_count for r in results))


def compare(model: bytes, stl: bytes, source: bytes, plan: dict, *,
            candidate_id: str = "top-07", max_leaf_cells: int = 4096,
            max_depth: int = 12, timeout_seconds: float = 45,
            cancelled=lambda: False) -> dict:
    if (type(max_leaf_cells) is not int or not 1 <= max_leaf_cells <= 4096
            or type(max_depth) is not int or not 0 <= max_depth <= 12
            or type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds)
            or not 0 < timeout_seconds <= 300 or not callable(cancelled)):
        raise ValueError("invalid bounded comparison policy")
    for content, digest, label in ((model, MODEL_SHA256, "3MF"), (stl, STL_SHA256, "STL"),
                                   (source, SLICE_SHA256, "slice")):
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f"unpinned {label}")
    if (plan.get("source_3mf_sha256") != MODEL_SHA256
            or plan.get("source_stl_sha256") != STL_SHA256
            or plan.get("scope") != "3d-review-only"):
        raise ValueError("candidate model identity mismatch")
    rows = _candidate_rows(plan, SLICE_SHA256, show_unverified=True)
    matches = [row for row in rows if row[6] == candidate_id]
    if len(matches) != 1:
        raise ValueError("candidate is not an eligible display hypothesis")
    z, x0, y0, x1, y1, width, identifier, height, status = matches[0]
    if y0 != y1 or not x0 < x1:
        raise ValueError("comparison requires a forward horizontal fixture line")
    candidate = ExactNominalTopSegment(
        identifier, tuple(F(str(v)) for v in (x0, y0, z)),
        tuple(F(str(v)) for v in (x1, y1, z)), F(str(width)), F(str(height)), "candidate")
    half_width = candidate.width_mm/2
    rectangle = ExactTopCellXY(F(str(x0)), F(str(x1)), F(str(y0))-half_width, F(str(y0))+half_width)
    mesh = coupon_mesh(model)
    complete, selected = spatial_baseline(source, rectangle)
    start = monotonic()
    timed_out = False

    def stop():
        nonlocal timed_out
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError("cancellation must return exact bool")
        timed_out = timed_out or monotonic()-start >= timeout_seconds
        return answer or timed_out

    evaluated, dominance = dominant_baseline(rectangle, selected, stop)
    result = compare_partitions(
        mesh, rectangle, evaluated, (candidate,), source_mesh_id=MODEL_SHA256,
        baseline_slice_id=SLICE_SHA256, max_vertices=8, max_triangles=12,
        max_mesh_pair_checks=1000, max_cell_vertices=4, max_centroid_tests=1000,
        max_facet_clip_tests=10000, max_sources=1000, max_coordinate_bits=4096,
        sqrt_fraction_bits=128, max_refinement_depth=max_depth,
        max_leaf_cells=max_leaf_cells, cancelled=stop)
    return {"schema": "smoothificator.offline_coupon_comparison.v1",
            "scope": "nominal-vertical-top-over-candidate-footprint-only",
            "source_3mf_sha256": MODEL_SHA256, "source_stl_sha256": STL_SHA256,
            "source_slice_sha256": SLICE_SHA256,
            "candidate_plan_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True,
                separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
            "coordinate_frame": "pinned_3mf_build_plus_orca_plate_offset_mm",
            "mesh_numeric_model": "exact binary64 transformed vertices",
            "bead_numeric_model": "exact decimal source coordinates; nominal stadium; flat axial caps",
            "candidate_id": identifier, "candidate_review_status": status,
            "candidate_start_mm": [x0, y0, z], "candidate_end_mm": [x1, y1, z],
            "width_mm": width, "height_mm": height,
            "rectangle_exact_mm": [str(v) for v in (rectangle.x_min_mm, rectangle.x_max_mm,
                                                     rectangle.y_min_mm, rectangle.y_max_mm)],
            "baseline_total_segments": len(complete), "baseline_spatial_segments": len(selected),
            "baseline_selected_source_ids": [s.segment_id for s in selected],
            "baseline_evaluated_segments": len(evaluated),
            "baseline_dominance_certificate": dominance,
            "baseline_higher_layers_truncated": False,
            "policy": {"max_leaf_cells": max_leaf_cells, "max_depth": max_depth,
                       "timeout_seconds": timeout_seconds, "x_partitions": min(32,max_leaf_cells)},
            "state": result.state, "reason": "deadline" if timed_out else result.reason,
            "leaf_count": result.leaf_count,
            "target_plane_exact_abc": None if result.target_plane_abc is None else [
                str(v) for v in result.target_plane_abc],
            "baseline_max_vertical_residual": _interval(result.baseline_max_residual),
            "augmented_max_vertical_residual": _interval(result.augmented_max_residual),
            "strict_local_reduction_verified": result.state == "complete" and result.reason == "certified-reduction",
            "printable_authorized": False, "full_surface_improvement_verified": False,
            "limitations": ["vertical top error only", "candidate footprint only; influence closure unproven",
                            "support and chronological nozzle clearance not established",
                            "reference geometry; not printer calibration or physical evidence"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-leaf-cells", type=int, default=4096)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--timeout-seconds", type=float, default=45)
    args = parser.parse_args()
    plan = json.loads((ROOT / "artifacts/geometry-review/top-surface-candidates.json").read_text(encoding="utf-8"))
    receipt = compare(_pinned(ROOT / "artifacts/fixtures/offline-coupon.3mf", MODEL_SHA256),
                      _pinned(ROOT / "artifacts/fixtures/offline-coupon.stl", STL_SHA256),
                      _pinned(ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode", SLICE_SHA256), plan,
                      max_leaf_cells=args.max_leaf_cells, max_depth=args.max_depth,
                      timeout_seconds=args.timeout_seconds)
    target = ROOT / "artifacts/geometry-review/top-surface-residual-comparison.json"
    target.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(target)
    print(json.dumps({key: receipt[key] for key in ("state", "reason", "leaf_count",
        "baseline_max_vertical_residual", "augmented_max_vertical_residual")}, indent=2))


if __name__ == "__main__":
    main()
