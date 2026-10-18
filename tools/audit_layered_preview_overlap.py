"""Read-only audit of one pinned, display-only Orca top-surface probe.

This deliberately cannot authorize printing: it identifies direct footprint
conflicts in the fixture and rejects viewer-Z projection as execution intent.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re


SOURCE_SHA256 = "499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e"
WORD = re.compile(r"([XYZEF])([+-]?(?:\d+(?:\.\d*)?|\.\d+))")


def source_segments(source: bytes, *, expected_sha256: str | None = None) -> tuple[tuple[float, ...], ...]:
    if expected_sha256 is None:
        expected_sha256 = SOURCE_SHA256
    if hashlib.sha256(source).hexdigest() != expected_sha256:
        raise ValueError("unpinned source G-code")
    x = y = z = 0.0
    layer_z = None
    width = None
    segments = []
    for line_number, raw in enumerate(source.decode("ascii").splitlines(), 1):
        line = raw.strip()
        if line == "G91" or line.startswith("M82") or line.startswith(("G2 ", "G3 ")):
            raise ValueError("unsupported source motion mode")
        if line.startswith("G92") and any(key in line for key in ("X", "Y", "Z")):
            raise ValueError("unsupported source origin remap")
        if line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":",1)[1])
        elif line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":",1)[1])
        elif line.startswith(";Z:"):
            layer_z = float(line[3:])
        elif line.startswith(";WIDTH:"):
            width = float(line[7:])
        elif line.startswith(("G0 ", "G1 ")):
            words = {key: float(value) for key, value in WORD.findall(line.split(";", 1)[0])}
            next_x, next_y, next_z = words.get("X", x), words.get("Y", y), words.get("Z", z)
            if (line.startswith("G1 ") and words.get("E", 0) > 0 and layer_z is not None
                    and (next_x != x or next_y != y)):
                if width is None or not math.isfinite(width) or width <= 0 or abs(next_z - layer_z) > 1e-6:
                    raise ValueError("unsupported source extrusion")
                segments.append((layer_z, x, y, next_x, next_y, width, line_number))
            x, y, z = next_x, next_y, next_z
    return tuple(segments)


def _point_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    length_squared = dx * dx + dy * dy
    if length_squared <= 0:
        raise ValueError("degenerate segment")
    fraction = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_squared))
    return math.hypot(px - ax - fraction * dx, py - ay - fraction * dy)


def centerline_distance(candidate: tuple[float, float, float, float],
                        structural: tuple[float, float, float, float]) -> float:
    ax, ay, bx, by = candidate
    cx, cy, dx, dy = structural
    if ay != by or ax >= bx:
        raise ValueError("probe candidate must be a positive horizontal segment")
    if cy != dy and min(cy, dy) <= ay <= max(cy, dy):
        crossing_x = cx + (ay - cy) * (dx - cx) / (dy - cy)
        if ax <= crossing_x <= bx:
            return 0.0
    if cy == dy == ay and max(ax, min(cx, dx)) <= min(bx, max(cx, dx)):
        return 0.0
    return min(_point_distance(ax, ay, cx, cy, dx, dy),
               _point_distance(bx, by, cx, cy, dx, dy),
               _point_distance(cx, cy, ax, ay, bx, by),
               _point_distance(dx, dy, ax, ay, bx, by))


def audit(source: bytes, manifest: dict[str, object]) -> dict[str, object]:
    candidate = manifest["candidate"]
    if not isinstance(candidate, dict) or candidate.get("scope") != "top-surface-only":
        raise ValueError("unsupported candidate manifest")
    if manifest.get("source_gcode_sha256") != SOURCE_SHA256:
        raise ValueError("source identity mismatch")
    segments = candidate.get("segments")
    count = candidate.get("segment_count")
    layers = manifest.get("layers")
    if (not isinstance(segments, list) or not segments or type(count) is not int
            or count != len(segments) or not isinstance(layers, list)
            or sum(layer.get("candidate_segments", 0) for layer in layers) != count):
        raise ValueError("candidate segment count mismatch")
    display_z = candidate["display_z_mm"]
    true_z = candidate["true_interpolated_z_mm"]
    width = candidate["display_width_mm"]
    if not all(type(value) in (int, float) and math.isfinite(value)
               for value in (display_z, true_z, width)) or width <= 0:
        raise ValueError("invalid candidate coordinates or width")
    structural = tuple(row for row in source_segments(source) if row[0] == display_z)
    if not structural:
        raise ValueError("missing display-layer structural extrusion")
    results = []
    for index, item in enumerate(segments):
        start = item["start_xy_mm"]
        end = item["end_xy_mm"]
        xy = (*start, *end)
        if not all(type(value) in (int, float) and math.isfinite(value) for value in xy):
            raise ValueError("invalid candidate path")
        nearest = min(((centerline_distance(xy, row[1:5]) - (width + row[5]) / 2,
                        row[6]) for row in structural), key=lambda pair: pair[0])
        results.append({"candidate_index": index, "footprint_clearance_mm": round(nearest[0], 6),
                        "nearest_source_line": nearest[1]})
    projected = true_z != display_z
    overlap = any(row["footprint_clearance_mm"] <= 0 for row in results)
    reason = ("projected-Z-and-footprint-overlap" if projected and overlap else
              "projected-Z" if projected else
              "footprint-overlap" if overlap else "other-safety-gates-unverified")
    return {"state": "rejected" if projected or overlap else "not-proven-safe",
            "reason": reason,
            "source_sha256": SOURCE_SHA256, "paths": results,
            "printable_authorized": False}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "artifacts/cli-midpoint-slice/plate_1.gcode"
    manifest = root / "artifacts/layered-viewer/smoothificator-0f17b22cd4744c848b2e427bae9bf4bc.VIEW_ONLY.json"
    result = audit(source.read_bytes(), json.loads(manifest.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
