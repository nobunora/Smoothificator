"""Offline explicit Z-hop blocks. No source mutation or physical authorization."""
from dataclasses import dataclass
from fractions import Fraction as F
import math
import re

from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.engine.flow_model import (
    candidate_geometric_line_flow, commanded_external_line_flow,
)
from orca_plugin.gcode.linear_trace import MachineState


@dataclass(frozen=True)
class SupplementalPath:
    path_id: str
    floor_z_mm: F
    width_mm: F
    height_mm: F
    points_mm: tuple[tuple[F, F, F], ...]


@dataclass(frozen=True)
class HopPolicy:
    z_hop_mm: F
    printable_height_mm: F
    xy_speed_mm_s: F
    z_speed_mm_s: F
    retract_speed_mm_s: F
    deretract_speed_mm_s: F
    candidate_speed_mm_s: F
    filament_diameter_mm: F
    max_volume_mm3_s: F
    print_flow_ratio: F
    filament_flow_ratio: F
    other_flow_enabled: bool
    outer_flow_ratio: F
    bounds: CandidateBeadBounds
    xyz_places: int
    e_places: int


def rounded(value, places):
    """Exact rational decimal rounding, ties away from zero (research policy)."""
    scale = 10 ** places
    numerator, denominator = value.numerator, value.denominator
    quotient, remainder = divmod(abs(numerator) * scale, denominator)
    return F((-1 if numerator < 0 else 1) * (quotient + (2 * remainder >= denominator)), scale)


def _text(value, places):
    scaled = value * 10 ** places
    if scaled.denominator != 1:
        raise ValueError("restore/command value not exactly representable")
    integer = scaled.numerator
    digits = str(abs(integer)).zfill(places + 1)
    body = digits if places == 0 else digits[:-places] + "." + digits[-places:]
    return ("-" if integer < 0 else "") + body


def _validate_policy(policy):
    if type(policy) is not HopPolicy:
        raise ValueError("immutable HopPolicy required")
    for name in ("z_hop_mm", "printable_height_mm", "xy_speed_mm_s", "z_speed_mm_s",
                 "retract_speed_mm_s", "deretract_speed_mm_s", "candidate_speed_mm_s",
                 "filament_diameter_mm", "max_volume_mm3_s", "print_flow_ratio",
                 "filament_flow_ratio", "outer_flow_ratio"):
        value = getattr(policy, name)
        if type(value) is not F or value <= 0 or not math.isfinite(float(value)):
            raise ValueError(f"positive finite rational required: {name}")
    if type(policy.other_flow_enabled) is not bool or type(policy.bounds) is not CandidateBeadBounds:
        raise ValueError("exact flow flag and candidate bounds required")
    for places in (policy.xyz_places, policy.e_places):
        if type(places) is not int or not 0 <= places <= 9:
            raise ValueError("explicit decimal precision 0..9 required")


def _ordered_paths(paths, upper_z, policy):
    if type(paths) is not tuple or not paths or not all(type(p) is SupplementalPath for p in paths):
        raise ValueError("nonempty immutable candidate tuple required")
    if len({p.path_id for p in paths}) != len(paths):
        raise ValueError("duplicate path ID")
    floor = paths[0].floor_z_mm
    for path in paths:
        if type(path.path_id) is not str or not re.fullmatch(r"[A-Za-z0-9_-]+", path.path_id):
            raise ValueError("ASCII path ID required")
        if any(type(v) is not F for v in (path.floor_z_mm, path.width_mm, path.height_mm)):
            raise ValueError("exact candidate dimensions required")
        if path.floor_z_mm != floor or not F(0) <= floor < upper_z:
            raise ValueError("one original-layer batch required")
        if type(path.points_mm) is not tuple or len(path.points_mm) < 2:
            raise ValueError("immutable nonempty polyline required")
        for point in path.points_mm:
            if type(point) is not tuple or len(point) != 3 or any(type(v) is not F for v in point):
                raise ValueError("exact XYZ points required")
        top = path.points_mm[0][2]
        if not floor < top <= upper_z or any(p[2] != top for p in path.points_mm):
            raise ValueError("constant-Z candidate must remain below next source layer")
        remaining = top - floor
        overlap = 1 - remaining / path.height_mm if path.height_mm > 0 else F(-1)
        if not 0 <= overlap <= F('0.3'):
            raise ValueError("overlap outside 0..30 percent")
        if remaining < F(str(policy.bounds.min_candidate_height_mm)):
            raise ValueError("remaining height below configured minimum")
        candidate_geometric_line_flow(float(path.height_mm), float(path.width_mm), bounds=policy.bounds)
    return tuple(sorted(paths, key=lambda p: (p.height_mm, p.path_id)))


def safe_ceiling(saved_z, upper_z, policy):
    _validate_policy(policy)
    if any(type(z) is not F or z < 0 for z in (saved_z, upper_z)):
        raise ValueError("known nonnegative actual and target Z required")
    scale = 10 ** policy.xyz_places
    exact = (max(saved_z, upper_z) + policy.z_hop_mm) * scale
    ceiling = F(-(-exact.numerator // exact.denominator), scale)
    if ceiling > policy.printable_height_mm:
        raise ValueError("Z hop exceeds tool printable height; cannot clamp")
    return ceiling


def compose_retracted_cycle(anchor, paths, upper_z, policy):
    """Return an UNVERIFIED ASCII block for a fully specified offline fixture.

    No callers may infer print authority from this function. Real anchors,
    firmware/formatter equivalence and chronological clearance remain gates.
    """
    _validate_policy(policy)
    if type(anchor) is not MachineState or not all((anchor.millimetres, anchor.absolute_xyz,
            anchor.relative_e, anchor.volumetric_disabled, anchor.speed_override_100, anchor.flow_override_100)):
        raise ValueError("known supported modal anchor required")
    if any(type(v) is not bool for v in (anchor.millimetres, anchor.absolute_xyz,
            anchor.relative_e, anchor.volumetric_disabled, anchor.speed_override_100, anchor.flow_override_100)):
        raise ValueError("exact bool modal state required")
    if (type(anchor.xyz_mm) is not tuple or len(anchor.xyz_mm) != 3
            or any(type(v) is not F for v in (*anchor.xyz_mm, anchor.feed_mm_min,
                                             anchor.logical_e_mm, anchor.retraction_debt_mm))):
        raise ValueError("actual XYZ/feed/logical E/retraction anchor required")
    if anchor.feed_mm_min <= 0 or anchor.retraction_debt_mm <= 0:
        raise ValueError("positive saved feed and retraction required")
    ordered = _ordered_paths(paths, upper_z, policy)
    ceiling = safe_ceiling(anchor.xyz_mm[2], upper_z, policy)
    xyz = lambda value: _text(value, policy.xyz_places)
    eword = lambda value: _text(value, policy.e_places)
    for coordinate in anchor.xyz_mm:
        xyz(coordinate)
    debt = eword(anchor.retraction_debt_mm)
    logical = eword(anchor.logical_e_mm)
    saved_feed = _text(anchor.feed_mm_min, 3)
    feed = lambda mm_s: _text(mm_s * 60, 3)
    xy_feed, z_feed = feed(policy.xy_speed_mm_s), feed(policy.z_speed_mm_s)
    lines = ["; UNVERIFIED OFFLINE MOTION BLOCK - DO NOT PRINT", "; SUPPLEMENTAL_CYCLE_BEGIN"]
    area_filament = math.pi * float(policy.filament_diameter_mm) ** 2 / 4
    for path in ordered:
        points = tuple(tuple(rounded(v, policy.xyz_places) for v in p) for p in path.points_mm)
        if not paths[0].floor_z_mm < points[0][2] <= upper_z:
            raise ValueError("quantized candidate top outside original-layer interval")
        # Rounding must not defeat the remaining-height or overlap contracts.
        remaining = points[0][2] - path.floor_z_mm
        if (remaining < F(str(policy.bounds.min_candidate_height_mm))
                or not 0 <= 1 - remaining / path.height_mm <= F('.3')):
            raise ValueError("quantized Z violates height/overlap bounds")
        lines.extend((f"; PATH {path.path_id} HEIGHT {path.height_mm}",
            f"G1 Z{xyz(ceiling)} F{z_feed}",
            f"G1 X{xyz(points[0][0])} Y{xyz(points[0][1])} F{xy_feed}",
            f"G1 Z{xyz(points[0][2])} F{z_feed}",
            f"G1 E{debt} F{feed(policy.deretract_speed_mm_s)}"))
        qgeom = candidate_geometric_line_flow(float(path.height_mm), float(path.width_mm), bounds=policy.bounds)
        qcmd = commanded_external_line_flow(qgeom, print_flow_ratio=float(policy.print_flow_ratio),
            filament_flow_ratio=float(policy.filament_flow_ratio),
            set_other_flow_ratios=policy.other_flow_enabled, outer_wall_flow_ratio=float(policy.outer_flow_ratio))
        for a, b in zip(points, points[1:]):
            length = math.dist(tuple(map(float, a)), tuple(map(float, b)))
            if not math.isfinite(length) or length <= 0:
                raise ValueError("collapsed or nonfinite quantized segment")
            amount = rounded(F(str(length * qcmd / area_filament)), policy.e_places)
            if amount <= 0:
                raise ValueError("quantized E is zero")
            executed_q = float(amount) * area_filament / length
            speed = min(float(policy.candidate_speed_mm_s), float(policy.max_volume_mm3_s) / executed_q)
            # Floor F so decimal formatting cannot increase the volume cap.
            emitted_feed = F(math.floor(speed * 60 * 1000), 1000)
            if emitted_feed <= 0:
                raise ValueError("nonpositive quantized feed")
            lines.append(f"G1 X{xyz(b[0])} Y{xyz(b[1])} E{eword(amount)} F{_text(emitted_feed,3)}")
        lines.extend((f"G1 E-{debt} F{feed(policy.retract_speed_mm_s)}", f"G1 Z{xyz(ceiling)} F{z_feed}"))
    lines.extend((f"G1 X{xyz(anchor.xyz_mm[0])} Y{xyz(anchor.xyz_mm[1])} F{xy_feed}",
                  f"G1 Z{xyz(anchor.xyz_mm[2])} F{z_feed}", f"G92 E{logical}",
                  f"G1 F{saved_feed}", "; SUPPLEMENTAL_CYCLE_END"))
    return ("\n".join(lines) + "\n").encode("ascii")


def policy_from_slice(profile, bounds, *, xyz_places, e_places):
    """Conservative requested feeds; no claim about actual firmware timing."""
    number = lambda name: profile.setting(name).number()
    if (type(bounds) is not CandidateBeadBounds
            or F(str(bounds.max_candidate_height_mm)) > number('layer_height') * F(9,10)):
        raise ValueError("candidate height bound exceeds 90 percent of saved layer height")
    if number('use_firmware_retraction') != 0 or number('retract_restart_extra') != 0:
        raise ValueError("firmware retract/restart extra unsupported")
    xy = min(number('travel_speed'), number('conservative_machine_max_speed_x'),
             number('conservative_machine_max_speed_y'))
    requested_z = number('travel_speed_z') or number('travel_speed')
    z = min(requested_z, number('conservative_machine_max_speed_z'))
    return HopPolicy(number('z_hop'), number('effective_printable_height'), xy, z,
        number('retraction_speed'), number('deretraction_speed'), number('outer_wall_speed'),
        number('filament_diameter'), number('filament_max_volumetric_speed'),
        number('print_flow_ratio'), number('filament_flow_ratio'),
        bool(number('set_other_flow_ratios')), number('outer_wall_flow_ratio'), bounds,
        xyz_places, e_places)
