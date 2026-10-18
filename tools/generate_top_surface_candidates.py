"""Read-only, fixture-pinned geometry for a 3D review of the tilted coupon.

The output is a set of true-Z line segments, never a printable toolpath.
"""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
from fractions import Fraction
from zipfile import ZipFile
from xml.etree import ElementTree

from tools.audit_layered_preview_overlap import _point_distance, centerline_distance, source_segments
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from adaptive_subedge.engine.support_cell import query_exact_nominal_top_point


ROOT = Path(__file__).resolve().parents[1]
MODEL_SHA256 = "6b17c12a81ea54a0bfb8545713c2119e7d6604b6ee9abfbbdc23b73e883eebc4"
STL_SHA256 = "d785d15dba5e3675215abd4f98cb0c7d227e90caa1d1d424709eba8f11cf5b7a"
SLICE_SHA256 = "499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e"
# Pinned Orca CLI fixture: the 3MF build center (90,90) is placed at bed (125,125).
PLATE_OFFSET_MM = (35.0, 35.0)
REVIEW_BEADS = ((2.22, 0.4, 0.08), (2.26, 0.4, 0.08),
                (2.30, 0.4, 0.10), (2.34, 0.4, 0.14),
                (2.38, 0.4, 0.18), (2.28, 0.3, 0.08),
                (2.28, 0.34, 0.19))
MIN_EFFECTIVE_HEIGHT_MM = 0.08
EDGE_INSET_MM = 0.3


def _pinned(path: Path, digest: str) -> bytes:
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError(f"fixture identity mismatch: {path.name}")
    return content


def _top_face(model: bytes) -> tuple[tuple[float, ...], float, float, float]:
    with ZipFile(BytesIO(model)) as archive:
        main = ElementTree.fromstring(archive.read("3D/3dmodel.model"))
        part = ElementTree.fromstring(
            archive.read("3D/Objects/offline-coupon.stl_1.model"))
    item = main.find(".//{*}build/{*}item")
    if item is None:
        raise ValueError("missing 3MF build transform")
    matrix = tuple(float(word) for word in item.attrib["transform"].split())
    vertices = [tuple(float(node.attrib[axis]) for axis in "xyz")
                for node in part.findall(".//{*}vertices/{*}vertex")]
    if len(matrix) != 12 or len(vertices) != 8 or not all(
            math.isfinite(number) for number in (*matrix, *(v for p in vertices for v in p))):
        raise ValueError("unsupported coupon mesh or transform")
    top_z = max(vertex[2] for vertex in vertices)
    top = [vertex for vertex in vertices if vertex[2] == top_z]
    if (len(top) != 4 or any(abs(matrix[index]) > 1e-10 for index in (1, 2, 3, 6))
            or matrix[0] <= 0 or matrix[4] <= 0 or matrix[5] >= -1e-6
            or matrix[7] <= 0 or matrix[8] <= 0):
        raise ValueError("unsupported top plane")
    xs = sorted({vertex[0] for vertex in top})
    ys = sorted({vertex[1] for vertex in top})
    if len(xs) != 2 or len(ys) != 2 or len(part.findall(".//{*}triangle")) != 12:
        raise ValueError("unsupported coupon top footprint")
    return matrix, top_z, xs[0], xs[1]


def _exact_source_top_probe(source: bytes, structural: tuple[tuple[float, ...], ...],
                            x_min: float, x_max: float, y_mm: float, width_mm: float,
                            candidate_z_mm: float) -> float:
    """Sample nominal lower top, detecting valleys hidden by XY footprints."""
    heights = {}
    height = None
    for line_number, line in enumerate(source.decode("ascii").splitlines(), 1):
        if line.startswith(";HEIGHT:"):
            height = float(line[8:])
        heights[line_number] = height
    fraction = lambda value: Fraction(str(value))
    exact_sources = []
    for z, x1, y1, x2, y2, width, line_number in structural:
        if z >= candidate_z_mm:
            continue
        source_height = heights[line_number]
        if source_height is None or width < source_height:
            raise ValueError("unsupported source bead height")
        exact_sources.append(ExactNominalTopSegment(
            str(line_number), (fraction(x1), fraction(y1), fraction(z)),
            (fraction(x2), fraction(y2), fraction(z)), fraction(width),
            fraction(source_height), "structural"))
    sources = tuple(exact_sources)
    minimum_top = candidate_z_mm
    for x_index in range(95):
        x_mm = x_min + (x_max-x_min)*x_index/94
        for y_offset_mm in (-width_mm/2, 0, width_mm/2):
            query = query_exact_nominal_top_point(
                fraction(x_mm), fraction(y_mm+y_offset_mm), sources,
                max_sources=1000, max_coordinate_bits=4096, sqrt_fraction_bits=128,
                cancelled=lambda: False)
            if query.state != "full-bounded" or query.top_z_lower_mm is None:
                raise ValueError("nominal lower top remains unproven")
            minimum_top = min(minimum_top, float(query.top_z_lower_mm))
    return minimum_top


def generate(model: bytes, stl: bytes, source: bytes) -> dict[str, object]:
    if hashlib.sha256(model).hexdigest() != MODEL_SHA256:
        raise ValueError("unpinned 3MF")
    if hashlib.sha256(stl).hexdigest() != STL_SHA256:
        raise ValueError("unpinned STL")
    if hashlib.sha256(source).hexdigest() != SLICE_SHA256:
        raise ValueError("unpinned Orca slice")
    matrix, top_local_z, min_local_x, max_local_x = _top_face(model)
    structural = source_segments(source)
    if not structural:
        raise ValueError("empty source slice")
    # 3MF's twelve entries are three column vectors followed by translation.
    # The fixture has an X-axis tilt, so each fixed-Z top-face intersection is
    # a horizontal segment. Inset both X ends to keep its footprint in the mesh.
    left_x = matrix[0] * min_local_x + matrix[6] * top_local_z + matrix[9] + PLATE_OFFSET_MM[0] + EDGE_INSET_MM
    right_x = matrix[0] * max_local_x + matrix[6] * top_local_z + matrix[9] + PLATE_OFFSET_MM[0] - EDGE_INSET_MM
    if not left_x < right_x or abs((left_x + right_x) / 2 - 125) > 1e-6:
        raise ValueError("coupon slice frame mismatch")
    segments = []
    for index, (z_mm, width_mm, bead_height_mm) in enumerate(REVIEW_BEADS, 1):
        local_y = (z_mm - matrix[8] * top_local_z - matrix[11]) / matrix[5]
        if not -5 + EDGE_INSET_MM < local_y < 5 - EDGE_INSET_MM:
            raise ValueError("candidate outside top face")
        y_mm = matrix[4] * local_y + matrix[7] * top_local_z + matrix[10] + PLATE_OFFSET_MM[1]
        # Only later layer footprints are screened here; this is display
        # evidence, not a chronological nozzle or support clearance proof.
        later = [row for row in structural if row[0] > z_mm]
        if not later:
            raise ValueError("no higher source layer")
        nearest = min((centerline_distance((left_x, y_mm, right_x, y_mm), row[1:5])
                       - (width_mm + row[5]) / 2, row[6]) for row in later)
        support_z = []
        for x_index in range(21):
            x_mm = left_x + (right_x-left_x)*x_index/20
            for y_offset_mm in (-width_mm/2, 0, width_mm/2):
                below = [row[0] for row in structural if row[0] < z_mm and
                         _point_distance(x_mm, y_mm+y_offset_mm, *row[1:5]) <= row[5]/2]
                support_z.append(max(below) if below else None)
        unresolved_support = any(z is None for z in support_z)
        known_support = [z for z in support_z if z is not None]
        if not known_support:
            raise ValueError("no sampled lower support")
        effective_height_mm = z_mm - max(known_support)
        maximum_effective_height_mm = z_mm - min(known_support)
        status = ("unresolved-support" if unresolved_support else
                  "below-minimum-height" if effective_height_mm + 1e-9 < MIN_EFFECTIVE_HEIGHT_MM
                  else "higher-footprint-overlap" if nearest[0] <= 0
                  else "candidate-for-review")
        nominal_minimum_top = None
        if status == "candidate-for-review":
            nominal_minimum_top = _exact_source_top_probe(
                source, structural, left_x, right_x, y_mm, width_mm, z_mm)
            if nominal_minimum_top < z_mm - bead_height_mm - 1e-6:
                status = "nominal-support-valley"
            else:
                # Finite samples cannot prove contact over the entire bead.
                status = "continuous-contact-unverified"
        segments.append({"id": f"top-{index:02d}", "reason": "top-surface",
                         "start_mm": [round(left_x, 6), round(y_mm, 6), z_mm],
                         "end_mm": [round(right_x, 6), round(y_mm, 6), z_mm],
                         "width_mm": width_mm,
                         "bead_height_mm": bead_height_mm,
                         "sampled_support_top_z_mm": max(known_support),
                         "sampled_effective_height_mm": round(effective_height_mm, 6),
                         "sampled_effective_height_max_mm": round(maximum_effective_height_mm, 6),
                         "sampled_support_complete": not unresolved_support,
                         "sampled_nominal_minimum_top_z_mm": (
                             round(nominal_minimum_top, 6) if nominal_minimum_top is not None else None),
                         "minimum_effective_height_mm": MIN_EFFECTIVE_HEIGHT_MM,
                         "review_status": status,
                         "continuous_contact_verified": False,
                         "width_minimum_verified": width_mm >= 0.34,
                         "nearest_higher_footprint_clearance_mm": round(nearest[0], 6),
                         "nearest_higher_source_line": nearest[1],
                         "higher_footprint_overlap": nearest[0] <= 0})
    return {"schema": "smoothificator.offline_top_candidates.v1",
            "scope": "3d-review-only", "source_3mf_sha256": MODEL_SHA256,
            "source_stl_sha256": STL_SHA256, "source_slice_sha256": SLICE_SHA256,
            "frame": {"source": "3MF build transform + pinned Orca plate offset",
                      "plate_offset_xy_mm": list(PLATE_OFFSET_MM),
                      "top_local_z_mm": top_local_z, "transform_3mf": list(matrix)},
            "printable_authorized": False, "segments": segments}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=ROOT / "artifacts/fixtures/offline-coupon.3mf")
    parser.add_argument("--stl", type=Path, default=ROOT / "artifacts/fixtures/offline-coupon.stl")
    parser.add_argument("--slice", type=Path, default=ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/geometry-review/top-surface-candidates.json")
    args = parser.parse_args()
    result = generate(_pinned(args.model, MODEL_SHA256), _pinned(args.stl, STL_SHA256),
                      _pinned(args.slice, SLICE_SHA256))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
