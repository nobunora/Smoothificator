"""Bounded Custom-only viewer representation; never executable-plan output."""
from fractions import Fraction
import math
import re


class ViewerSceneError(ValueError):
    """Closed diagnostic codes; never host configuration values."""


MAX_BYTES = 2_097_152
GRID = 10**12
EXCLUDED = ("host", "api", "password", "token", "secret", "user", "device",
            "url", "gcode", "notes", "credential")


def _validate_key(key):
    if type(key) is not str:
        raise ViewerSceneError("invalid-config-key-type")
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", key) is None:
        if not key:
            raise ViewerSceneError("invalid-config-key-grammar-empty")
        for index, character in enumerate(key):
            pattern = r"[A-Za-z]" if index == 0 else r"[A-Za-z0-9_]"
            if re.fullmatch(pattern, character) is None:
                raise ViewerSceneError(
                    f"invalid-config-key-grammar-len{len(key)}-index{index}-ord{ord(character)}")


def _config(rows):
    if type(rows) is not tuple:
        raise ViewerSceneError("invalid-viewer-config")
    retained = {}
    for row in rows:
        if type(row) is not tuple or len(row) != 2:
            raise ViewerSceneError("invalid-viewer-config")
        key, value = row
        if type(key) is not str:
            raise ViewerSceneError("invalid-config-key-type")
        if any(token in key.lower() for token in EXCLUDED):
            continue
        _validate_key(key)
        if key in retained:
            raise ViewerSceneError("invalid-config-key-duplicate")
        if type(value) is not str or any(c in value for c in "\r\n\0"):
            raise ViewerSceneError("invalid-config-value")
        if not value.isascii():
            continue
        retained[key] = value
    if len(retained) < 80:
        raise ViewerSceneError("insufficient-viewer-config")
    if any(key not in retained for key in ("printer_model", "filament_diameter", "extruder_offset")):
        raise ViewerSceneError("missing-viewer-config")
    try:
        diameters = tuple(float(v) for v in retained["filament_diameter"].split(","))
        offsets = tuple(tuple(float(v) for v in pair.split("x"))
                        for pair in retained["extruder_offset"].split(","))
    except ValueError:
        raise ViewerSceneError("invalid-viewer-geometry") from None
    if (not diameters or any(not math.isfinite(d) or d <= 0 for d in diameters)
            or not offsets or any(len(pair) != 2 or any(not math.isfinite(v) for v in pair)
                                  for pair in offsets)):
        raise ViewerSceneError("invalid-viewer-geometry")
    if any(v != 0 for pair in offsets for v in pair):
        raise ViewerSceneError("unsupported-extruder-offset")
    if not retained["printer_model"]:
        raise ViewerSceneError("invalid-printer-model")
    return tuple(sorted(retained.items())), diameters[0]


def copy_viewer_config(bundle):
    """UI callback only: values are Orca opt_serialize strings, not JSON values."""
    keys = tuple(bundle.full_config_keys())
    if len(keys) > 10000:
        raise ViewerSceneError("viewer-config-limit")
    rows = []
    size = 0
    for key in keys:
        if type(key) is not str:
            raise ViewerSceneError("invalid-config-key-type")
        if any(token in key.lower() for token in EXCLUDED):
            continue
        _validate_key(key)
        value = bundle.full_config_value(key)
        if type(value) is not str:
            raise ViewerSceneError("invalid-config-value")
        size += len(key.encode("utf-8")) + len(value.encode("utf-8"))
        if size > MAX_BYTES:
            raise ViewerSceneError("viewer-config-limit")
        rows.append((key, value))
    return _config(tuple(rows))[0]


def _fraction(value):
    return value if type(value) is Fraction else Fraction(float(value))


def _decimal(ticks):
    sign = "-" if ticks < 0 else ""
    whole, part = divmod(abs(ticks), GRID)
    return f"{sign}{whole}.{part:012d}"


def _width_ticks(width, minimum, maximum, height):
    lower = max(_fraction(minimum), _fraction(height)) * GRID
    upper = _fraction(maximum) * GRID
    lo, hi = -(-lower.numerator // lower.denominator), upper.numerator // upper.denominator
    if lo > hi:
        raise ViewerSceneError("width-grid-infeasible")
    exact = width * GRID
    floor = exact.numerator // exact.denominator
    nearest = floor + (exact - floor > Fraction(1, 2))
    return min(hi, max(lo, nearest))


def render_scene(preview, request, config):
    if preview.state != "complete" or not preview.proposals or preview.width_mm is None:
        raise ViewerSceneError("complete-band-preview-required")
    if preview.axis != request.axis or preview.command_z_mm != _fraction(request.z_mm):
        raise ViewerSceneError("preview-request-mismatch")
    rows, diameter = _config(config)
    width_ticks = _width_ticks(preview.width_mm, request.minimum_width_mm,
                               request.maximum_width_mm, request.display_height_mm)
    height_ticks = round(_fraction(request.display_height_mm) * GRID)
    z_ticks = round(preview.command_z_mm * GRID)
    if height_ticks <= 0 or z_ticks == 0 or width_ticks < height_ticks:
        raise ViewerSceneError("unrepresentable-viewer-geometry")
    width, height = width_ticks / GRID, height_ticks / GRID
    if width > max(2.0, 4 * height):
        raise ViewerSceneError("native-width-clamp")
    area = width * height + (math.pi / 4 - 1) * height * height
    filament_area = math.pi * (diameter / 2)**2
    if not all(math.isfinite(v) and v > 0 for v in (area, filament_area)):
        raise ViewerSceneError("invalid-viewer-extrusion")
    bbl = dict(rows)["printer_model"].startswith("Bambu Lab")
    role = "; FEATURE: Custom" if bbl else ";TYPE:Custom"
    height_tag = "; LAYER_HEIGHT: " if bbl else ";HEIGHT:"
    width_tag = "; LINE_WIDTH: " if bbl else ";WIDTH:"
    layer = "; CHANGE_LAYER" if bbl else ";LAYER_CHANGE"
    lines = ["; generated by OrcaSlicer compatible Smoothificator viewer representation",
             "; SMOOTHIFICATOR RESEARCH - PRINT UNVALIDATED - VIEW ONLY",
             "; Rounded display approximation, no certified coverage or physical authority",
             "; Custom-only layer labels may differ from commanded Z",
             "; CONFIG_BLOCK_START"]
    lines.extend(f"; {key} = {value}" for key, value in rows)
    lines.extend(("; CONFIG_BLOCK_END", "G21", "G90", "M83", "G92 E0", layer))
    for index, proposal in enumerate(preview.proposals):
        if proposal.state != "proposed":
            raise ViewerSceneError("complete-band-preview-required")
        first = tuple(round(v * GRID) for v in proposal.start_xy_mm)
        last = tuple(round(v * GRID) for v in proposal.end_xy_mm)
        length = math.hypot((last[0]-first[0])/GRID, (last[1]-first[1])/GRID)
        if not math.isfinite(length) or length <= 0:
            raise ViewerSceneError("collapsed-viewer-extrusion")
        e = length * area / filament_area
        if not math.isfinite(e) or e <= 0:
            raise ViewerSceneError("invalid-viewer-extrusion")
        e_ticks = round(Fraction(e) * GRID)
        if e_ticks <= 0:
            raise ViewerSceneError("unrepresentable-viewer-extrusion")
        lines.append(f"G1 X{_decimal(first[0])} Y{_decimal(first[1])} Z{_decimal(z_ticks)} F1200")
        if index == 0:
            # Custom before the first G1 triggers Orca's start-code Z override.
            lines.extend((role, height_tag+_decimal(height_ticks), width_tag+_decimal(width_ticks)))
        lines.append(f"G1 X{_decimal(last[0])} Y{_decimal(last[1])} E{_decimal(e_ticks)} F1200")
    content = "\n".join(lines)+"\n"
    if not content.isascii() or len(content) > MAX_BYTES:
        raise ViewerSceneError("viewer-output-limit")
    return content
