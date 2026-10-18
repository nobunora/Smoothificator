"""JSON review of actual supplemental-to-supplemental hops; no G-code file."""
import argparse
from collections import defaultdict
from dataclasses import asdict
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

from adaptive_subedge.domain.settings import CandidateBeadBounds
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.provisional_tool_geometry import (
    DEFAULT_ASSUMED_TOOL_DIAMETER_MM, ProvisionalPlanarTip,
    swept_planar_disc_bounds, swept_planar_polyline_bounds,
)
from tools.supplemental_z_hop import (
    SupplementalPath, policy_from_slice, safe_ceiling, _ordered_paths, rounded, _text,
)


def review_hops(project, source, manifest_bytes, *, assumed_tool_diameter_mm=DEFAULT_ASSUMED_TOOL_DIAMETER_MM):
    geometry = ProvisionalPlanarTip(assumed_tool_diameter_mm)
    manifest = json.loads(manifest_bytes)
    profile = read_sliced_profile(project, source, include_motion_caps=True)
    if (profile.source_sha256 != manifest['source_slice_sha256']
            or profile.project_sha256 != manifest['placed_project_sha256']):
        raise ValueError('candidate manifest and source/project hashes differ')
    constraints = manifest['rectangle_constraints_exact_mm']
    bounds = CandidateBeadBounds(float(F(constraints['minimum_remaining_height'])),
        float(F(constraints['maximum_physical_height'])), float(F(constraints['minimum_width'])),
        float(F(constraints['maximum_width'])))
    policy = policy_from_slice(profile, bounds, xyz_places=3, e_places=5)
    segments = defaultdict(list)
    for segment in manifest['candidate_segments']:
        segments[segment['ring_id']].append(segment)
    groups = defaultdict(list)
    for ring in manifest['rings']:
        if ring['id'] not in segments:
            raise ValueError('missing or duplicate ring ID')
        chords = sorted(segments.pop(ring['id']), key=lambda s: s['chord_index'])
        if len(chords) != ring['chord_count'] or [s['chord_index'] for s in chords] != list(range(1,len(chords)+1)):
            raise ValueError('incomplete or duplicate ring chords')
        point = lambda coords: tuple(F(str(v)) for v in coords)
        for a,b in zip(chords,chords[1:]):
            if point(a['end_mm']) != point(b['start_mm']):
                raise ValueError('disconnected ring')
        points = (point(chords[0]['start_mm']),) + tuple(point(c['end_mm']) for c in chords)
        exact_top = F(ring['top_z_exact_mm'])
        if points[0] != points[-1] or any(float(p[2]) != float(exact_top) for p in points):
            raise ValueError('ring closure/top differs from manifest')
        # The viewer serializes float Z, while the same manifest retains exact
        # intended Z. Check float agreement, then retain that exact intent.
        points = tuple((p[0],p[1],exact_top) for p in points)
        floor = F(ring['floor_z_exact_mm'])
        groups[floor].append(SupplementalPath(ring['id'],floor,F(ring['width_exact_mm']),
                                             F(ring['height_exact_mm']),points))
    if segments:
        raise ValueError('orphan ring segments')
    upper_by_floor = {F(row['floor_z_exact_mm']): F(row['upper_z_exact_mm'])
                      for row in manifest['section_diagnostics']}
    batches, path_tip_bounds = [], []
    for floor, paths in sorted(groups.items()):
        upper = upper_by_floor[floor]
        ordered = _ordered_paths(tuple(paths), upper, policy)
        for path in ordered:
            quantized_points = tuple(tuple(rounded(v, policy.xyz_places) for v in point)
                                     for point in path.points_mm)
            path_tip_bounds.append({'path_id':path.path_id, 'floor_z_mm':floor,
                'quantized_centerline_sha256':sha256(json.dumps(quantized_points, default=str,
                    separators=(',', ':')).encode('ascii')).hexdigest(),
                'swept_tip_bounds':asdict(swept_planar_polyline_bounds(quantized_points, geometry))})
        ceiling = safe_ceiling(max(p.points_mm[0][2] for p in ordered), upper, policy)
        transitions = []
        for a,b in zip(ordered,ordered[1:]):
            start,end = a.points_mm[-1],b.points_mm[0]
            # This is the bridge AFTER retracting and BEFORE unretracting.
            # No real insertion anchor or complete print program is invented.
            commands = [f'G1 Z{_text(ceiling,3)} F{_text(policy.z_speed_mm_s*60,3)}',
                f'G1 X{_text(rounded(end[0],3),3)} Y{_text(rounded(end[1],3),3)} F{_text(policy.xy_speed_mm_s*60,3)}',
                f'G1 Z{_text(rounded(end[2],3),3)} F{_text(policy.z_speed_mm_s*60,3)}']
            quantized_start = tuple(rounded(v, policy.xyz_places) for v in start)
            quantized_end = tuple(rounded(v, policy.xyz_places) for v in end)
            raised = (*quantized_start[:2], ceiling)
            above_end = (*quantized_end[:2], ceiling)
            bridge_legs = [(quantized_start, raised), (raised, above_end), (above_end, quantized_end)]
            transitions.append({'from':a.path_id,'to':b.path_id,
                'start_mm':list(start),'end_mm':list(end),'safe_z_mm':ceiling,
                'required_state':'already retracted; unretract only after descent',
                'unverified_bridge_commands':commands,
                'provisional_tip_sweep_bounds': [asdict(swept_planar_disc_bounds(a, b, geometry))
                                                for a, b in bridge_legs]})
        batches.append({'floor_z_mm':floor,'upper_z_mm':upper,'safe_z_mm':ceiling,
            'order':[p.path_id for p in ordered], 'heights_mm':[p.height_mm for p in ordered],
            'transitions':transitions,'entry_exit_anchor_verified':False})
    manifest_hash = sha256(manifest_bytes).hexdigest()
    review_identity = sha256(json.dumps({'review_version':'supplemental-hop-planar-tip-v1',
        'source_sha256':profile.source_sha256, 'project_sha256':profile.project_sha256,
        'manifest_sha256':manifest_hash, 'geometry_identity':geometry.identity,
        'xyz_places':policy.xyz_places, 'e_places':policy.e_places}, sort_keys=True,
        separators=(',', ':')).encode('ascii')).hexdigest()
    saved_nozzle = profile.setting('nozzle_diameter').number()
    return {'scope':'supplemental-explicit-hop-review','printable_authorized':False,
        'physical_print_authorized':False, 'complete_head_verified':False,
        'tool_clearance_verified':False, 'review_identity':review_identity,
        'provisional_tool_geometry':{'model_version':geometry.model_version,
            'assumed_diameter_mm':geometry.assumed_diameter_mm, 'radius_mm':geometry.radius_mm,
            'identity':geometry.identity, 'measured':False},
        'saved_nozzle_diameter_mm':saved_nozzle,
        'assumed_vs_saved_nozzle_mismatch':geometry.assumed_diameter_mm != saved_nozzle,
        'diameter_comparison_note':'Assumed tip footprint and saved nozzle orifice are different quantities; inequality is not a profile error.',
        'surface_quality_improvement':'deferred by user; candidates unchanged',
        'source_sha256':profile.source_sha256,'project_sha256':profile.project_sha256,
        'manifest_sha256':manifest_hash,
        'profile_z_hop_mm':policy.z_hop_mm,'requested_xy_speed_mm_s':policy.xy_speed_mm_s,
        'requested_z_speed_mm_s':policy.z_speed_mm_s,'path_count':sum(len(v) for v in groups.values()),
        'batch_count':len(batches),'batches':batches,
        'supplemental_path_tip_bounds':path_tip_bounds,
        'limitations':['No actual source insertion anchor or file mutation.',
            'Assumed planar tip only: no axial head extension, obstacle query or collision certificate.',
            'Thin-first ordering and these bridges do not certify tool-body clearance.',
            'Entry/exit, extrusion formatting parity and unchanged downstream motion remain unverified.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder',type=Path,default=Path('artifacts/revolved-exponential-review'))
    parser.add_argument('--assumed-tool-diameter-mm', type=F, default=DEFAULT_ASSUMED_TOOL_DIAMETER_MM,
                        help=f'Positive provisional planar tip diameter in mm (default {float(DEFAULT_ASSUMED_TOOL_DIAMETER_MM):g}); not measured head geometry.')
    args = parser.parse_args()
    report = review_hops((args.folder/'original-slice/sliced.3mf').read_bytes(),
        (args.folder/'original-slice/plate_1.gcode').read_bytes(),
        (args.folder/'current-review.json').read_bytes(), assumed_tool_diameter_mm=args.assumed_tool_diameter_mm)
    print(json.dumps(report,indent=2,default=str))


if __name__ == '__main__':
    main()
