"""One tools-owned numeric freeze for supplemental path research intents."""
from dataclasses import asdict, dataclass
from fractions import Fraction as F
from hashlib import sha256
import json
import math
import re

from adaptive_subedge.engine.flow_model import (
    bead_width_from_geometric_flow, candidate_geometric_line_flow, commanded_external_line_flow,
)
from tools.supplemental_z_hop import SupplementalPath, _validate_policy, rounded


@dataclass(frozen=True)
class FrozenSupplementalEmission:
    path: SupplementalPath
    policy_identity: str
    relative_e_mm: tuple[F, ...]
    feed_mm_min: tuple[F, ...]
    physical_width_mm: tuple[float, ...]
    volume_rate_mm3_s: tuple[float, ...]


def emission_policy_identity(policy):
    _validate_policy(policy)
    return sha256(json.dumps(asdict(policy), sort_keys=True, separators=(',', ':'), default=str).encode('ascii')).hexdigest()


def validate_supplemental_dimensions(floor_z_mm, width_mm, height_mm, remaining_height_mm, policy):
    """One exact admission owner for fixed planner height/overlap after XYZ freeze."""
    _validate_policy(policy)
    if any(type(v) is not F for v in (floor_z_mm, width_mm, height_mm, remaining_height_mm)):
        raise ValueError('exact supplemental dimensions required')
    bounds = policy.bounds
    if not (floor_z_mm >= 0 and F(str(bounds.min_candidate_height_mm)) <= remaining_height_mm
            <= height_mm <= min(width_mm, F(str(bounds.max_candidate_height_mm)))
            and F(str(bounds.min_candidate_width_mm)) <= width_mm <= F(str(bounds.max_candidate_width_mm))
            and 0 <= 1-remaining_height_mm/height_mm <= F('.3')):
        raise ValueError('width/height/remaining/overlap bounds failed')
    if (rounded(floor_z_mm, policy.xyz_places) != floor_z_mm
            or rounded(floor_z_mm+remaining_height_mm, policy.xyz_places) != floor_z_mm+remaining_height_mm):
        raise ValueError('floor/top must preserve planner dimensions on the XYZ grid')


def freeze_numeric_emission(path, policy):
    """Quantize XYZ then nearest E and downward-capped F; never optimize a path."""
    identity = emission_policy_identity(policy)
    if type(path) is not SupplementalPath or type(path.points_mm) is not tuple or len(path.points_mm) < 2:
        raise ValueError('immutable supplemental polyline required')
    if (any(type(v) is not F for v in (path.floor_z_mm, path.width_mm, path.height_mm))
            or type(path.path_id) is not str or not re.fullmatch('[A-Za-z0-9_-]+', path.path_id)):
        raise ValueError('exact dimensions and safe path identity required')
    for point in path.points_mm:
        if type(point) is not tuple or len(point) != 3 or any(type(v) is not F for v in point):
            raise ValueError('exact immutable XYZ required')
    if any(point[2] != path.points_mm[0][2] for point in path.points_mm):
        raise ValueError('original supplemental intent must have constant Z before quantization')
    validate_supplemental_dimensions(path.floor_z_mm, path.width_mm, path.height_mm,
                                    path.points_mm[0][2]-path.floor_z_mm, policy)
    points = tuple(tuple(rounded(v, policy.xyz_places) for v in point) for point in path.points_mm)
    if any(point[2] != points[0][2] for point in points):
        raise ValueError('constant-Z supplemental path required')
    qgeom = candidate_geometric_line_flow(float(path.height_mm), float(path.width_mm), bounds=policy.bounds)
    flow_arguments = dict(print_flow_ratio=float(policy.print_flow_ratio),
        filament_flow_ratio=float(policy.filament_flow_ratio), set_other_flow_ratios=policy.other_flow_enabled,
        outer_wall_flow_ratio=float(policy.outer_flow_ratio))
    qcmd = commanded_external_line_flow(qgeom, **flow_arguments)
    multiplier = commanded_external_line_flow(1.0, **flow_arguments)
    filament_area = math.pi*float(policy.filament_diameter_mm)**2/4
    amounts, feeds, widths, rates = [], [], [], []
    for start, end in zip(points, points[1:]):
        try:
            length = math.dist(tuple(map(float, start)), tuple(map(float, end)))
        except OverflowError as exc:
            raise ValueError('nonfinite geometry in numeric emission') from exc
        if not math.isfinite(length) or length <= 0:
            raise ValueError('collapsed/nonfinite quantized segment')
        amount = rounded(F(str(length*qcmd/filament_area)), policy.e_places)
        if amount <= 0:
            raise ValueError('nearest emitted E is zero')
        actual_qcmd = float(amount)*filament_area/length
        width = bead_width_from_geometric_flow(float(path.height_mm), actual_qcmd/multiplier)
        if not float(policy.bounds.min_candidate_width_mm) <= width <= float(policy.bounds.max_candidate_width_mm):
            raise ValueError('nearest E implies width outside bounds')
        speed = min(float(policy.candidate_speed_mm_s), float(policy.max_volume_mm3_s)/actual_qcmd)
        feed = F(math.floor(speed*60*1000), 1000)
        rate = actual_qcmd*float(feed)/60
        if feed <= 0 or rate > float(policy.max_volume_mm3_s):
            raise ValueError('emitted feed/volume-rate outside bounds')
        amounts.append(amount)
        feeds.append(feed)
        widths.append(width)
        rates.append(rate)
    frozen_path = SupplementalPath(path.path_id, path.floor_z_mm, path.width_mm, path.height_mm, points)
    return FrozenSupplementalEmission(frozen_path, identity, tuple(amounts), tuple(feeds), tuple(widths), tuple(rates))
