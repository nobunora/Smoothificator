"""Sufficient exact nominal zero-height tip-disc sweep/material classifications."""
from dataclasses import dataclass, field
from fractions import Fraction as F

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from adaptive_subedge.engine.support_cell import _sqrt_bounds, query_exact_nominal_bead_projection, query_exact_nominal_top_point
from tools.provisional_tool_geometry import ProvisionalPlanarTip, swept_planar_disc_bounds


@dataclass(frozen=True)
class PlanarTipSweepPolicy:
    max_axis_queries: int
    max_coordinate_bits: int
    sqrt_fraction_bits: int
    max_point_queries: int = 32

    def __post_init__(self):
        if any(type(v) is not int or v < 1 for v in (self.max_axis_queries, self.max_coordinate_bits, self.sqrt_fraction_bits, self.max_point_queries)):
            raise ValueError('explicit positive exact sweep query/bit limits required')
        if self.sqrt_fraction_bits > 4096:
            raise ValueError('bounded kernel sqrt precision required')


@dataclass(frozen=True)
class PlanarTipSweepReport:
    material_segment_id: str
    geometry_identity: str
    policy: PlanarTipSweepPolicy
    state: str
    reason: str
    axis_queries: int
    separating_axis: tuple[F, F, F] | None
    strict_margin: F | None
    boundary_or_penetration_witness_xyz_mm: tuple[F, F, F] | None
    point_queries: int = 0
    physical_authority: bool = field(default=False, init=False)


def _closest_xy_parameters(a, b, c, d):
    """Exact closest centerline witnesses for two finite planar segments."""
    u, v = tuple(y-x for x, y in zip(a, b)), tuple(y-x for x, y in zip(c, d))
    dot = lambda x, y: sum(p*q for p, q in zip(x, y))
    clamp = lambda t: max(F(0), min(F(1), t))
    uu, vv = dot(u, u), dot(v, v)
    pairs = []
    for t in (F(0), F(1)):
        point = tuple(x+t*dx for x, dx in zip(a, u))
        pairs.append((t, clamp(dot(tuple(x-y for x, y in zip(point, c)), v)/vv)))
    if uu:
        for s in (F(0), F(1)):
            point = tuple(x+s*dx for x, dx in zip(c, v))
            pairs.append((clamp(dot(tuple(x-y for x, y in zip(point, a)), u)/uu), s))
        uv = dot(u, v)
        determinant = uu*vv-uv*uv
        if determinant:
            w = tuple(x-y for x, y in zip(a, c))
            t = (uv*dot(v, w)-vv*dot(u, w))/determinant
            s = (uu*dot(v, w)-uv*dot(u, w))/determinant
            if 0 <= t <= 1 and 0 <= s <= 1:
                pairs.append((t, s))
    def distance(pair):
        t, s = pair
        return sum((a[i]+t*u[i]-c[i]-s*v[i])**2 for i in (0, 1))
    t, s = min(pairs, key=distance)
    return t, s, distance((t, s))


def audit_provisional_tip_sweep(start, end, geometry, material, *, policy, cancelled, proposed_axes=(), proposed_top_witnesses=()):
    """Convex whole-sweep bounds; exact contact needs a real intersection witness.

    Strict projection separation proves exclusion. A global top-plane bound plus
    a point shared with the source's centerline top proves boundary contact.
    A disk-interior witness on the bead's interior center plane proves nominal
    penetration. Other unresolved cases stay unknown; no proximity tolerance.
    """
    if (type(material) is not ExactNominalTopSegment or type(policy) is not PlanarTipSweepPolicy
            or not callable(cancelled) or type(proposed_axes) is not tuple or type(proposed_top_witnesses) is not tuple):
        raise ValueError('exact nominal material, immutable sweep policy and explicit cancellation required')
    envelope = swept_planar_disc_bounds(start, end, geometry)
    if any(type(axis) is not tuple or len(axis) != 3 or any(type(v) is not F for v in axis)
           or axis == (F(0),)*3 for axis in proposed_axes):
        raise ValueError('exact nonzero proposed separating axes required')
    if any(type(p) is not tuple or len(p) != 3 or any(type(v) is not F for v in p) for p in proposed_top_witnesses):
        raise ValueError('exact immutable proposed top witnesses required')
    count, points = 0, 0

    def stopped():
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('exact bool sweep cancellation required')
        return answer

    def report(state, reason, axis=None, margin=None, witness=None):
        return PlanarTipSweepReport(material.segment_id, geometry.identity, policy, state, reason, count, axis, margin, witness, points)

    coordinates = (*start, *end, geometry.radius_mm, *material.start_xyz_mm, *material.end_xyz_mm, material.width_mm, material.height_mm)
    if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > policy.max_coordinate_bits for v in coordinates):
        return report('unknown', 'coordinate-bit-limit')
    if stopped():
        return report('unknown', 'cancelled')
    if len(proposed_axes) > policy.max_axis_queries:
        return report('unknown', 'proposed-axis-resource-limit')
    if len(proposed_top_witnesses) > policy.max_point_queries:
        return report('unknown', 'proposed-point-resource-limit')
    if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > policy.max_coordinate_bits for p in proposed_top_witnesses for v in p):
        return report('unknown', 'proposed-point-bit-limit')
    radius = material.width_mm/2
    lower = tuple(min(a, b)-(radius if i < 2 else material.height_mm) for i, (a, b) in enumerate(zip(material.start_xyz_mm, material.end_xyz_mm)))
    upper = tuple(max(a, b)+(radius if i < 2 else 0) for i, (a, b) in enumerate(zip(material.start_xyz_mm, material.end_xyz_mm)))
    for i in range(3):
        margin = max(lower[i]-envelope.upper_xyz_mm[i], envelope.lower_xyz_mm[i]-upper[i])
        if margin > 0:
            return report('strictly-separated', 'conservative-full-sweep-box', tuple(F(i == j) for j in range(3)), margin)
    # Boundary status requires both a whole-sweep nonpenetration plane and an
    # exact common point, never just equality of interval endpoints.
    if material.start_xyz_mm[2] == material.end_xyz_mm[2]:
        top = material.start_xyz_mm[2]
        if min(start[2], end[2]) >= top and top in (start[2], end[2]):
            if start[2] == end[2]:
                t, s, distance = _closest_xy_parameters(start[:2], end[:2], material.start_xyz_mm[:2], material.end_xyz_mm[:2])
            else:
                t = F(0) if start[2] == top else F(1)
                point = start if t == 0 else end
                _, s, distance = _closest_xy_parameters(point[:2], point[:2], material.start_xyz_mm[:2], material.end_xyz_mm[:2])
            if distance <= geometry.radius_mm**2:
                witness = tuple(material.start_xyz_mm[i]+s*(material.end_xyz_mm[i]-material.start_xyz_mm[i]) for i in (0, 1))+(top,)
                return report('boundary-contact', 'global-top-plane-and-exact-shared-point', witness=witness)
            for witness in proposed_top_witnesses:
                if stopped():
                    return report('unknown', 'cancelled')
                if witness[2] != top:
                    continue
                if start[2] == end[2]:
                    delta = tuple(b-a for a, b in zip(start[:2], end[:2]))
                    length_squared = sum(v*v for v in delta)
                    t = max(F(0), min(F(1), sum((w-a)*d for w, a, d in zip(witness[:2], start[:2], delta))/length_squared)) if length_squared else F(0)
                else:
                    t = (witness[2]-start[2])/(end[2]-start[2])
                if not 0 <= t <= 1 or sum((witness[i]-start[i]-t*(end[i]-start[i]))**2 for i in (0, 1)) > geometry.radius_mm**2:
                    continue
                proof = query_exact_nominal_top_point(witness[0], witness[1], (material,), max_sources=1,
                    max_coordinate_bits=policy.max_coordinate_bits, sqrt_fraction_bits=policy.sqrt_fraction_bits, cancelled=cancelled)
                points += 1
                if (proof.state == 'full-bounded' and proof.top_z_lower_mm == witness[2]
                        and proof.top_z_upper_mm == witness[2]):
                    return report('boundary-contact', 'global-top-plane-and-public-exact-top-witness', witness=witness)
                if proof.state == 'incomplete':
                    return report('unknown', 'point-query-incomplete')
        candidates = {F(0), F(1, 2), F(1)}
        if start[2] != end[2]:
            middle = top-material.height_mm/2
            t = (middle-start[2])/(end[2]-start[2])
            if 0 <= t <= 1:
                candidates.add(t)
        for t in candidates:
            point = tuple(a+t*(b-a) for a, b in zip(start, end))
            _, s, distance = _closest_xy_parameters(point[:2], point[:2], material.start_xyz_mm[:2], material.end_xyz_mm[:2])
            if top-material.height_mm < point[2] < top and 0 < s < 1 and distance < geometry.radius_mm**2:
                witness = tuple(material.start_xyz_mm[i]+s*(material.end_xyz_mm[i]-material.start_xyz_mm[i]) for i in (0, 1))+(point[2],)
                return report('positive-penetration', 'exact-disc-interior-and-material-interior-witness', witness=witness)
    axes = list(proposed_axes)+[(F(1), F(0), F(0)), (F(0), F(1), F(0)), (F(0), F(0), F(1))]
    normals = [(material.end_xyz_mm[1]-material.start_xyz_mm[1], material.start_xyz_mm[0]-material.end_xyz_mm[0]),
               (end[1]-start[1], start[0]-end[0]),
               ((material.start_xyz_mm[0]+material.end_xyz_mm[0]-start[0]-end[0])/2,
                (material.start_xyz_mm[1]+material.end_xyz_mm[1]-start[1]-end[1])/2)]
    for nx, ny in normals:
        if nx == ny == 0:
            continue
        length = _sqrt_bounds(nx*nx+ny*ny, policy.sqrt_fraction_bits)[1]
        for ratio in (F(0), F(1, 4), F(1, 2), F(1), F(2), F(4), F(8), F(16), F(32)):
            for sign in (1, -1):
                axes.append((nx, ny, sign*length*ratio))
    seen = set()
    for axis in axes:
        if (type(axis) is not tuple or len(axis) != 3 or any(type(v) is not F for v in axis) or axis == (F(0),)*3):
            raise ValueError('exact nonzero proposed separating axes required')
        if axis in seen:
            continue
        seen.add(axis)
        if stopped():
            return report('unknown', 'cancelled')
        if count >= policy.max_axis_queries:
            return report('unknown', 'axis-query-limit')
        if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > policy.max_coordinate_bits for v in axis):
            return report('unknown', 'axis-bit-limit')
        bead = query_exact_nominal_bead_projection(material, axis, max_coordinate_bits=policy.max_coordinate_bits,
            sqrt_fraction_bits=policy.sqrt_fraction_bits, cancelled=cancelled)
        count += 1
        if bead.state != 'bounded':
            return report('unknown', 'bead-projection-incomplete')
        radial_upper = _sqrt_bounds(axis[0]**2+axis[1]**2, policy.sqrt_fraction_bits)[1]*geometry.radius_mm
        endpoints = tuple(sum(a*b for a, b in zip(point, axis)) for point in (start, end))
        sweep_lower, sweep_upper = min(endpoints)-radial_upper, max(endpoints)+radial_upper
        margin = max(bead.lower_dot_units-sweep_upper, sweep_lower-bead.upper_dot_units)
        if margin > 0:
            return report('strictly-separated', 'exact-whole-swept-disc-projection', axis, margin)
    return report('unknown', 'no-sufficient-exact-certificate')
