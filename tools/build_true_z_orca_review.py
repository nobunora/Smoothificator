"""Build an offline Orca Preview scene at candidate true Z, never a print plan.

The input slice is hash-pinned. Output is an exclusive VIEW_ONLY artifact with
synthetic extrusion values so Orca can display both the original slice paths
and candidate paths in its standard layer preview. It is not for export.
"""

from __future__ import annotations

from collections import defaultdict
import argparse
import hashlib
import json
import math
from pathlib import Path
from uuid import uuid4

from smoothificator_preview.native_scene import _config
from tools.audit_layered_preview_overlap import SOURCE_SHA256, source_segments


SCHEMA = "smoothificator.offline_top_candidates.v1"
MAX_SEGMENTS = 128


def _number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _candidate_rows(plan: dict, source_sha256: str, *, show_unverified: bool = False) -> tuple[tuple, ...]:
    if (plan.get("schema") != SCHEMA or plan.get("source_slice_sha256") != source_sha256
            or plan.get("printable_authorized", False) is not False):
        raise ValueError("invalid or unauthorized candidate plan")
    segments = plan.get("segments")
    if not isinstance(segments, list) or not 0 < len(segments) <= MAX_SEGMENTS:
        raise ValueError("candidate count out of bounds")
    rows = []
    seen = set()
    for item in segments:
        if not isinstance(item, dict) or item.get("reason") != "top-surface":
            raise ValueError("only top-surface candidates may be displayed")
        identifier = item.get("id")
        start, end, width = item.get("start_mm"), item.get("end_mm"), item.get("width_mm")
        bead_height = item.get("bead_height_mm")
        clearance = item.get("nearest_higher_footprint_clearance_mm")
        overlap = item.get("higher_footprint_overlap")
        effective_height = item.get("sampled_effective_height_mm")
        minimum_height = item.get("minimum_effective_height_mm")
        support_top = item.get("sampled_support_top_z_mm")
        nominal_minimum_top = item.get("sampled_nominal_minimum_top_z_mm")
        contact_verified = item.get("continuous_contact_verified")
        status = item.get("review_status")
        support_complete = item.get("sampled_support_complete")
        if (type(identifier) is not str or not identifier or identifier in seen
                or not isinstance(start, list) or not isinstance(end, list)
                or len(start) != 3 or len(end) != 3
                or not all(type(v) in (int, float) and math.isfinite(v) for v in (*start, *end, width))
                or not 0 < width <= 2 or start[2] != end[2]
                or type(bead_height) not in (int, float) or not math.isfinite(bead_height)
                or not minimum_height <= bead_height <= min(width, 0.32)
                or type(clearance) not in (int, float) or not math.isfinite(clearance)
                or type(overlap) is not bool or overlap != (clearance <= 0)
                or type(effective_height) not in (int, float) or not math.isfinite(effective_height)
                or type(minimum_height) not in (int, float) or minimum_height <= 0
                or type(support_top) not in (int, float) or not math.isfinite(support_top)
                or type(contact_verified) is not bool
                or abs(effective_height - (start[2] - support_top)) > 1e-6
                or (nominal_minimum_top is not None and
                    (type(nominal_minimum_top) not in (int, float) or not math.isfinite(nominal_minimum_top)))
                or type(support_complete) is not bool
                or status not in ("unresolved-support", "below-minimum-height",
                                  "higher-footprint-overlap", "nominal-support-valley",
                                  "continuous-contact-unverified",
                                  "candidate-for-review")
                or math.hypot(end[0]-start[0], end[1]-start[1]) <= 0):
            raise ValueError("invalid true-Z candidate segment")
        expected_status = ("unresolved-support" if not support_complete else
                           "below-minimum-height" if effective_height + 1e-9 < minimum_height
                           else "higher-footprint-overlap" if overlap else
                           "nominal-support-valley" if (nominal_minimum_top is not None and
                                                        nominal_minimum_top < start[2] - bead_height - 1e-6)
                           else "continuous-contact-unverified" if not contact_verified
                           else "candidate-for-review")
        if status == "candidate-for-review" and nominal_minimum_top is None:
            raise ValueError("candidate requires exact nominal support probe")
        if status != expected_status:
            raise ValueError("candidate review classification mismatch")
        seen.add(identifier)
        if status == "candidate-for-review" or (show_unverified and status == "continuous-contact-unverified"
                and nominal_minimum_top is not None and nominal_minimum_top >= start[2] - bead_height - 1e-6
                and item.get("width_minimum_verified") is True):
            rows.append((float(start[2]), float(start[0]), float(start[1]),
                         float(end[0]), float(end[1]), float(width), identifier,
                         float(bead_height), status))
    if not rows:
        raise ValueError("no height-and-footprint review candidates")
    return tuple(rows)


def build_review(source: bytes, plan: dict, *, focus: bool = False,
                 show_unverified: bool = False) -> tuple[str, dict]:
    digest = hashlib.sha256(source).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("unpinned original Orca slice")
    original = source_segments(source)
    candidates = _candidate_rows(plan, digest, show_unverified=show_unverified)
    if focus:
        highest_candidate_z = max(row[0] for row in candidates)
        original = tuple(row for row in original if row[0] < highest_candidate_z)
    source_lines = source.decode("ascii").splitlines()
    start, end = source_lines.index("; CONFIG_BLOCK_START"), source_lines.index("; CONFIG_BLOCK_END")
    raw_config = dict(line[2:].split(" = ", 1) for line in source_lines[start+1:end]
                      if line.startswith("; ") and " = " in line)
    config, diameter = _config(tuple(raw_config.items()))
    filament_area = math.pi * (diameter / 2) ** 2
    role = ""
    roles = {}
    for line_number, line in enumerate(source_lines, 1):
        if line.startswith(";TYPE:"):
            role = line[6:]
        roles[line_number] = role
    by_z = defaultdict(list)
    for z, x1, y1, x2, y2, width, line_number in original:
        by_z[z].append((x1, y1, x2, y2, width, roles[line_number], line_number, None))
    existing_z = set(by_z)
    for z, x1, y1, x2, y2, width, identifier, bead_height, status in candidates:
        if z in existing_z:
            raise ValueError("candidate true Z coincides with an original layer")
        by_z[z].append((x1, y1, x2, y2, width, "Custom", identifier, bead_height))
    output = ["; generated by OrcaSlicer compatible Smoothificator viewer representation",
              "; Smoothificator offline 3D review - VIEW ONLY - PRINT UNVALIDATED",
              "; Candidate paths use true Z; original slice is unchanged",
              "; CONFIG_BLOCK_START"]
    output.extend(f"; {key} = {value}" for key, value in config)
    output.extend(("; CONFIG_BLOCK_END", "G21", "G90", "M83", "G92 E0"))
    layers = []
    sorted_z = sorted(by_z)
    for ordinal, z in enumerate(sorted_z):
        candidate_heights = {row[7] for row in by_z[z] if row[5] == "Custom"}
        if len(candidate_heights) > 1:
            raise ValueError("mixed candidate heights at one review Z")
        height = 0.2 if z in existing_z else candidate_heights.pop()
        if height <= 0:
            raise ValueError("nonpositive review layer height")
        output.extend((";LAYER_CHANGE", f";Z:{_number(z)}", f";HEIGHT:{_number(height)}"))
        candidate_count = 0
        for x1, y1, x2, y2, width, feature, provenance, bead_height in by_z[z]:
            if feature == "Custom":
                candidate_count += 1
            length = math.hypot(x2-x1, y2-y1)
            path_height = bead_height if bead_height is not None else height
            area = width * path_height + (math.pi / 4 - 1) * path_height * path_height
            extrusion = length * area / filament_area
            if not math.isfinite(extrusion) or extrusion <= 0:
                raise ValueError("invalid visual extrusion")
            output.extend((f"G1 X{_number(x1)} Y{_number(y1)} Z{_number(z)} F1200",
                           f";TYPE:{feature}", f";WIDTH:{_number(width)}",
                           f";HEIGHT:{_number(path_height)}",
                           f"G1 X{_number(x2)} Y{_number(y2)} E{_number(extrusion)} F1200"))
        layers.append({"ordinal": ordinal, "z_mm": z, "original_segments": len(by_z[z])-candidate_count,
                       "candidate_segments": candidate_count})
    content = "\n".join(output) + "\n"
    if not content.isascii() or len(content) > 2_097_152:
        raise ValueError("review scene exceeds bounded ASCII size")
    return content, {"state": "research-display-only", "source_slice_sha256": digest,
                     "candidate_ids": [row[6] for row in candidates],
                     "unverified_display": show_unverified,
                     "excluded_candidates": [
                         {"id": row["id"], "reason": row["review_status"]}
                         for row in plan["segments"] if row["id"] not in {item[6] for item in candidates}],
                     "layers": layers, "focus_lower_layers_only": focus,
                     "original_segments_displayed": len(original),
                     "printable_authorized": False,
                     "validation": "visual-Z-only; shape improvement and tool clearance unverified"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--focus", action="store_true", help="show original layers only through candidate Z")
    parser.add_argument("--show-unverified", action="store_true", help="show sampled-contact hypothesis in VIEW_ONLY scene")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "artifacts/cli-midpoint-slice/plate_1.gcode"
    plan_path = root / "artifacts/geometry-review/top-surface-candidates.json"
    content, manifest = build_review(source.read_bytes(), json.loads(plan_path.read_text(encoding="utf-8")),
                                     focus=args.focus, show_unverified=args.show_unverified)
    destination = root / "artifacts/geometry-review"
    destination.mkdir(parents=True, exist_ok=True)
    label = "UNVERIFIED_VIEW_ONLY" if args.show_unverified else "VIEW_ONLY"
    target = destination / f"smoothificator-{uuid4().hex}.{label}.gcode"
    with target.open("xb") as stream:
        stream.write(content.encode("ascii"))
    manifest["viewer_sha256"] = hashlib.sha256(content.encode("ascii")).hexdigest()
    manifest["viewer_file"] = str(target)
    target.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"viewer": str(target), "manifest": str(target.with_suffix(".json")),
                      "candidate_count": len(manifest["candidate_ids"]),
                      "layer_count": len(manifest["layers"]), "printable_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
