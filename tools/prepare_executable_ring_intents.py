"""Quantization-aware immutable ring intents for offline research only."""
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from fractions import Fraction as F
from hashlib import sha256
import json
import re

from adaptive_subedge.domain.settings import CandidateBeadBounds
from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.build_triangle_rectangle_review import posed_intersection_area
from tools.exponential_top_fixture import ROOT
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.solve_triangle_rectangle import PackedRectangle
from tools.supplemental_z_hop import (
    HopPolicy, SupplementalPath, _validate_policy, compose_retracted_cycle, policy_from_slice, rounded,
)


SOURCE_SHA256 = '8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95'
PROJECT_SHA256 = '0f4d85b55a2c3e1f579cc013d722f755a657f17dadb840d8a020792099aa3d61'
MANIFEST_SHA256 = 'dbeabdef2570d25d9f9546443e9e0d3970ec17016f840c7d2ef1b6154278ecf0'


@dataclass(frozen=True)
class RingIntent:
    path: SupplementalPath
    radius_mm: F
    original_top_z_mm: F
    original_height_mm: F
    upper_z_mm: F
    original_chord_count: int
    selected_endpoint_indices: tuple[int, ...]
    rejected_divisors: tuple[tuple[int, str], ...]
    spill_fraction: F
    emitted_e_mm: tuple[F, ...]
    emitted_feed_mm_min: tuple[F, ...]
    minimum_emitted_width_mm: float
    maximum_emitted_width_mm: float
    maximum_volume_rate_mm3_s: float


@dataclass(frozen=True)
class RingIntents:
    source_sha256: str
    project_sha256: str
    manifest_sha256: str
    policy: HopPolicy
    radial_budget_mm: F
    settings_identity: tuple[tuple[str, str, str], ...]
    rings: tuple[RingIntent, ...]
    printable_authorized: bool = field(default=False, init=False)
    execution_verified: bool = field(default=False, init=False)


def radial_segment_in_band(start, end, center, radius, budget):
    """Exact squared radial envelope of a complete closed straight segment."""
    if any(type(pair) is not tuple or len(pair) != 2 for pair in (start, end, center)):
        raise ValueError('two-dimensional radial tuples required')
    if any(type(v) is not F for v in (*start, *end, *center, radius, budget)):
        raise ValueError('exact rational radial coordinates required')
    if radius <= 0 or budget < 0 or radius < budget:
        raise ValueError('positive radius and nonnegative bounded radial budget required')
    a = tuple(v - c for v, c in zip(start, center))
    b = tuple(v - c for v, c in zip(end, center))
    direction = tuple(y - x for x, y in zip(a, b))
    squared_length = sum(v*v for v in direction)
    if squared_length == 0:
        return False
    t = max(F(0), min(F(1), -sum(x*d for x, d in zip(a, direction))/squared_length))
    closest = sum((x+t*d)**2 for x, d in zip(a, direction))
    farthest = max(sum(v*v for v in a), sum(v*v for v in b))
    return closest >= (radius-budget)**2 and farthest <= (radius+budget)**2


def _emission(path, policy, center, radius, budget):
    points = tuple(tuple(rounded(v, policy.xyz_places) for v in point) for point in path.points_mm)
    for start, end in zip(points, points[1:]):
        if not radial_segment_in_band(start[:2], end[:2], center, radius, budget):
            raise ValueError('quantized segment outside exact radial band or collapsed')
    emitted = freeze_numeric_emission(path, policy)
    return (emitted.relative_e_mm, emitted.feed_mm_min, min(emitted.physical_width_mm),
            max(emitted.physical_width_mm), max(emitted.volume_rate_mm3_s))


def select_ring_chords(path, *, center, radius, budget, policy):
    """Largest legal divisor, preserving original phase and endpoint subset."""
    count = len(path.points_mm)-1
    rejected = []
    for divisor in range(count, 2, -1):
        if count % divisor:
            continue
        indices = tuple(range(0, count+1, count//divisor))
        selected = SupplementalPath(path.path_id, path.floor_z_mm, path.width_mm, path.height_mm,
                                    tuple(path.points_mm[index] for index in indices))
        try:
            emission = _emission(selected, policy, center, radius, budget)
        except ValueError as exc:
            rejected.append((divisor, str(exc)))
            continue
        return selected, indices, tuple(rejected), emission
    raise ValueError(f'no legal chord divisor: {rejected}')


def _unique_json(pairs):
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError(f'duplicate manifest key: {key}')
        fields[key] = value
    return fields


def prepare_ring_intents(project, source, manifest_bytes, *, expected_source_sha256=SOURCE_SHA256,
                         expected_project_sha256=PROJECT_SHA256, expected_manifest_sha256=MANIFEST_SHA256,
                         xyz_places=3, e_places=5, radial_budget_mm=F('.002')):
    hashes = tuple(sha256(content).hexdigest() for content in (source, project, manifest_bytes))
    if hashes != (expected_source_sha256, expected_project_sha256, expected_manifest_sha256):
        raise ValueError('source/project/manifest hash pin mismatch')
    manifest = json.loads(manifest_bytes, object_pairs_hook=_unique_json)
    profile = read_sliced_profile(project, source, include_motion_caps=True)
    if (manifest['source_slice_sha256'], manifest['placed_project_sha256']) != hashes[:2]:
        raise ValueError('manifest and source/project association mismatch')
    constraints = manifest['rectangle_constraints_exact_mm']
    min_width, max_width, remaining_min, max_height = (F(constraints[key]) for key in
        ('minimum_width', 'maximum_width', 'minimum_remaining_height', 'maximum_physical_height'))
    overlap = F(manifest['overlap_percent_exact'])/100
    if not 0 <= overlap <= F('.3'):
        raise ValueError('overlap outside 0..30 percent')
    if max_height > profile.setting('layer_height').number()*F(9, 10):
        raise ValueError('height cap exceeds saved layer-height90 percent')
    bounds = CandidateBeadBounds(float(remaining_min), float(max_height), float(min_width), float(max_width))
    policy = policy_from_slice(profile, bounds, xyz_places=xyz_places, e_places=e_places)
    _validate_policy(policy)
    center = tuple(F(str(v)) for v in manifest['center_mm'][:2])
    if len(center) != 2 or type(radial_budget_mm) is not F or radial_budget_mm <= 0:
        raise ValueError('exact center and positive radial budget required')
    triangles = {}
    for row in manifest['section_diagnostics']:
        floor = F(row['floor_z_exact_mm'])
        if floor in triangles:
            raise ValueError('duplicate source triangle floor')
        triangles[floor] = row
    segments = defaultdict(list)
    for segment in manifest['candidate_segments']:
        segments[segment['ring_id']].append(segment)
    rings, failures, seen = [], [], set()
    for ring in manifest['rings']:
        name = ring['id']
        if type(name) is not str or not re.fullmatch(r'[A-Za-z0-9_-]+', name):
            raise ValueError('safe ASCII ring ID required')
        if name in seen:
            raise ValueError('duplicate ring ID')
        seen.add(name)
        chords = sorted(segments.pop(name, ()), key=lambda s: s['chord_index'])
        count = ring['chord_count']
        if (type(count) is not int or count < 3 or any(type(s['chord_index']) is not int for s in chords)
                or [s['chord_index'] for s in chords] != list(range(1, count+1))):
            raise ValueError('incomplete or duplicate ring chord graph')
        def point(coords):
            if type(coords) is not list or len(coords) != 3:
                raise ValueError('XYZ chord endpoint required')
            return tuple(F(str(v)) for v in coords)
        points = (point(chords[0]['start_mm']),)+tuple(point(chord['end_mm']) for chord in chords)
        if points[-1] != points[0] or any(point(a['end_mm']) != point(b['start_mm']) for a, b in zip(chords, chords[1:])):
            raise ValueError('disconnected or unclosed ring graph')
        old_top, old_height, floor, radius, width = (F(ring[key]) for key in
            ('top_z_exact_mm', 'height_exact_mm', 'floor_z_exact_mm', 'radius_exact_mm', 'width_exact_mm'))
        if any(float(p[2]) != float(old_top) or any((v*10**9).denominator != 1 for v in p[:2]) for p in points):
            raise ValueError('source endpoints differ from nine-decimal XYZ intent')
        try:
            if old_top-floor != old_height*(1-overlap):
                raise ValueError('original ring height/top/overlap intent disagree')
            row = triangles[floor]
            upper, left, right = (F(row[key]) for key in ('upper_z_exact_mm', 'left_radius_exact_mm', 'right_radius_exact_mm'))
            base, rise = F(row['triangle_base_exact_mm']), F(row['triangle_height_exact_mm'])
            if base != right-left or rise != upper-floor or base <= 0 or rise <= 0:
                raise ValueError('source triangle dimensions disagree')
            top = rounded(old_top, xyz_places)
            height = (top-floor)/(1-overlap)
            if not (remaining_min <= top-floor and floor < top <= upper
                    and remaining_min/(1-overlap) <= height <= max_height and height <= width
                    and min_width <= width <= max_width):
                raise ValueError('grid height/remaining/width/ceiling bounds failed')
            a, b = radius-width/2-left, radius+width/2-left
            if not 0 <= a < b <= base:
                raise ValueError('rectangle outside source radial triangle span')
            rectangle = PackedRectangle(a, b, height, F(0))
            intersection = posed_intersection_area(base, rise, rectangle, top-height-floor)
            spill = 1-intersection/(width*height)
            if not 0 <= spill <= F('.5'):
                raise ValueError('per-rectangle radial spill exceeds50 percent')
            path = SupplementalPath(name, floor, width, height, tuple((p[0], p[1], top) for p in points))
            selected, indices, rejected, emission = select_ring_chords(path, center=center, radius=radius,
                budget=radial_budget_mm, policy=policy)
            rings.append(RingIntent(selected, radius, old_top, old_height, upper, count, indices,
                                    rejected, spill, *emission))
        except (ValueError, KeyError) as exc:
            failures.append((name, str(exc)))
    if segments:
        raise ValueError('orphan ring chords')
    if failures or not rings:
        raise ValueError(f'whole job rejected; ring failures: {failures}')
    if len(rings) != manifest['ring_count'] or len(rings) != manifest['planned_line_count']:
        raise ValueError('manifest ring counts disagree')
    identities = tuple((s.name, s.source_key, s.value) for s in profile.settings)
    return RingIntents(*hashes, policy, radial_budget_mm, identities, tuple(rings))


def synthetic_replay(intents):
    groups = defaultdict(list)
    for ring in intents.rings:
        groups[(ring.path.floor_z_mm, ring.upper_z_mm)].append(ring.path)
    receipts = []
    for (floor, upper), paths in sorted(groups.items()):
        anchor = MachineState((F(90), F(90), upper), True, True, True, F(1200), F(0), F('.8'), True, True, True)
        block = compose_retracted_cycle(anchor, tuple(paths), upper, intents.policy)
        replay = trace_linear_execution(block, initial_state=anchor)
        if replay.failure is not None or replay.final_state != anchor:
            raise ValueError('synthetic composer replay did not restore anchor')
        receipts.append({'floor_z_mm': str(floor), 'upper_z_mm': str(upper),
                         'synthetic_block_sha256': sha256(block).hexdigest(), 'exact_restore': True,
                         'real_anchor_verified': False})
    return receipts


def main():
    folder = ROOT/'artifacts/revolved-exponential-review'
    intents = prepare_ring_intents((folder/'original-slice/sliced.3mf').read_bytes(),
        (folder/'original-slice/plate_1.gcode').read_bytes(), (folder/'current-review.json').read_bytes())
    receipt = asdict(intents)
    receipt.update(scope='UNVERIFIED executable numeric intent research',
                   synthetic_replay=synthetic_replay(intents), real_source_anchor_verified=False,
                   support_verified=False, tool_clearance_verified=False)
    target = ROOT/'artifacts/revolved-exponential-execution/ring-intents.UNVERIFIED.json'
    with target.open('x', encoding='ascii') as stream:
        json.dump(receipt, stream, indent=2, default=str)
        stream.write('\n')
    print(json.dumps({'receipt': str(target), 'ring_count': len(intents.rings),
                      'chord_count': sum(len(r.path.points_mm)-1 for r in intents.rings),
                      'printable_authorized': False}))


if __name__ == '__main__':
    main()
