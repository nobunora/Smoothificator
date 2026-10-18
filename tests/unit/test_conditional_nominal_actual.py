"""Actual pinned branch-free body, separately conditional from physical state."""
from collections import Counter
from dataclasses import asdict, replace
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import unittest
from zipfile import ZipFile

from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.conditional_nominal_body import (
    ASSUMPTION_NAMES, DeclaredNominalAssumption, NominalEntryContext, NominalMotionEnvelope,
    interpret_nominal_body, pin_nominal_producer,
)
from tools.conditional_nominal_copy import (
    ConditionalInsertion, ConditionalPathInput, associate_derived_path, compose_conditional_nominal_copy,
    propose_nominal_body_anchor,
)
from tools.exponential_top_fixture import ROOT
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.prepare_source_contour_intents import ContourConstructionPolicy, prepare_source_contour_proposal
from tools.supplemental_z_hop import policy_from_slice


ACTUAL_FOLDER = ROOT/'artifacts/branch-free-seam0-nominal-research/original-slice'


def actual_inputs():
    source = (ACTUAL_FOLDER/'plate_1.gcode').read_bytes()
    project = (ACTUAL_FOLDER/'sliced.3mf').read_bytes()
    producer = (ROOT/'artifacts/runtime/orca-nightly/OrcaSlicer/orca-slicer.exe').read_bytes()
    lines = source.splitlines(keepends=True)
    if (not lines[1244].startswith(b'M981 S1 P20000') or lines[1245] != b'M106 S0\n'
            or not lines[20796].startswith(b'M981 S0 P20000')):
        raise ValueError('pinned producer body boundary evidence changed')
    descriptor = pin_nominal_producer(source, project, producer,
        expected_source_sha256='f917caf88191253f22004d47545daa4e6f78f4b4132d61529101271e4d3ba288',
        expected_project_sha256='6fe38676704d886a0aa82b1179343629ff612ccb55e2ee534811d1011008e567',
        expected_producer_sha256='480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba',
        body_start_offset=sum(map(len, lines[:1245])), body_end_offset=sum(map(len, lines[:20796])),
        expected_object_token='AQAAAAAAAAA=', fan_channels=(0,))
    statements = (
        'Assume retained opaque manufacturer prefix completed normally, including M981; no startup interpretation or physical validation.',
        'Assume saved single-tool/source machine coordinate frame; homing/mesh/tool semantics remain unverified.',
        'Assume millimeters/absoluteXYZ/linear relativeE/disabled volumetric semantics; absent M200 is not interpreted as evidence.',
        'Declare ordinary physical debt0 and logicalE0 only as conditional nominal startup reference; actual debt unknown. XYZ/feed remain unknown.',
        'Assume file/runtime speed and flow100 percent; no live override measurement.',
        'Assume the one bitmap object is not cancelled across all31 repeated scopes; no guaranteed support if that premise fails.',
    )
    state = MachineState(millimetres=True, absolute_xyz=True, relative_e=True, logical_e_mm=F(0),
        retraction_debt_mm=F(0), volumetric_disabled=True, speed_override_100=True, flow_override_100=True)
    entry = NominalEntryContext(state, tuple(DeclaredNominalAssumption(name, statement, descriptor.prefix_sha256)
        for name, statement in zip(ASSUMPTION_NAMES, statements)))
    motion = NominalMotionEnvelope(descriptor.source_sha256, descriptor.project_sha256, descriptor.profile_identity,
        F(6000), F(9), F(5000), F(9), F(5000), F(9), 'classic-jerk', descriptor.prefix_sha256,
        'Opaque prefix last M204 S6000 and M205 X9 Y9; saved external-wall acceleration5000/jerk9 verified separately.',
        'Declare M204 S acceleration, isotropic classic XY jerk, M106 fan-only and M73/M991 notification-only effects; no firmware verification.')
    return source, project, producer, descriptor, entry, motion


def actual_sample(inputs, trace):
    source, project, producer, descriptor, entry, motion = inputs
    original_recipe_path = ROOT/'artifacts/source-contour-intent-review/six-groups-seven-paths.UNVERIFIED.json'
    recipe_bytes = original_recipe_path.read_bytes()
    reference = json.loads(recipe_bytes)['proposals'][1]
    reference_path = reference['frozen_emission']['path']
    floor = F(reference_path['floor_z_mm'])
    points = tuple(tuple(map(F, point)) for point in reference_path['points_mm'])
    material = tuple(e for e in trace.events if e.command in ('G0', 'G1') and e.feature == 'Outer wall'
        and e.scope_after is not None and e.deposited_filament_mm is not None and e.deposited_filament_mm > 0
        and e.before.xyz_mm[2] == floor and e.after.xyz_mm[2] == floor and e.before.xyz_mm[:2] != e.after.xyz_mm[:2])
    by_xy = {}
    for event in material:
        by_xy.setdefault((event.before.xyz_mm[:2], event.after.xyz_mm[:2]), []).append(event)
    matched = []
    for a, b in zip(points, points[1:]):
        options = by_xy.get((a[:2], b[:2]), ())
        if len(options) != 1:
            raise ValueError('frozen source-follow recipe is not uniquely rebound to actual derived-source geometry')
        matched.append(options[0])
    profile = read_sliced_profile(project, source, include_motion_caps=True)
    with ZipFile(ACTUAL_FOLDER/'sliced.3mf') as archive:
        saved = json.loads(archive.read('Metadata/project_settings.config'))
    contour = tuple(ExactNominalTopSegment(f'actual-source-{e.line_number}', e.before.xyz_mm, e.after.xyz_mm,
        F(saved['outer_wall_line_width']), F(saved['layer_height']), 'structural') for e in matched)
    bounds = CandidateBeadBounds(.08, .18, .25, .45)
    policy = policy_from_slice(profile, bounds, xyz_places=3, e_places=5)
    actual_feed_cap = min(e.after.feed_mm_min for e in material)/60
    policy = replace(policy, candidate_speed_mm_s=min(policy.candidate_speed_mm_s, actual_feed_cap))
    upper = floor+profile.setting('layer_height').number()
    proposal = prepare_source_contour_proposal(source_sha256=descriptor.source_sha256,
        project_sha256=descriptor.project_sha256, contour=contour, path_id='derived-source-follow-sample',
        floor_z_mm=floor, upper_z_mm=upper, width_mm=F(reference_path['width_mm']),
        height_mm=F(reference_path['height_mm']), remaining_height_mm=F(reference['remaining_height_mm']),
        inward_offset_mm=F(0), minimum_segment_mm=F(0), emission_policy=policy,
        construction_policy=ContourConstructionPolicy(9, 1000, 4096, 1000000), cancelled=lambda: False)
    if proposal.frozen_emission.path.points_mm != points:
        raise ValueError('freshly reconstructed source-follow geometry differs from recipe')
    last_floor_material = max(e.line_number for e in trace.events if e.command in ('G0', 'G1')
        and e.deposited_filament_mm is not None and e.deposited_filament_mm > 0 and e.after.xyz_mm[2] == floor)
    opening = next(e for e in trace.events if e.command == 'M624' and e.line_number > last_floor_material)
    anchor = propose_nominal_body_anchor(*inputs, opening.byte_offset+len(opening.raw))
    if anchor.eligibility_issues:
        raise ValueError(f'actual conditional anchor not eligible: {anchor.eligibility_issues}')
    original_source = (ROOT/'artifacts/revolved-exponential-derived5000-9-seam0-v2-research/original-slice/plate_1.gcode').read_bytes()
    original_project = (ROOT/'artifacts/revolved-exponential-derived5000-9-seam0-v2-research/original-slice/sliced.3mf').read_bytes()
    evidence = json.dumps({'statement': 'Exact XY recipe/source-contour comparison only; no old acceptance transferred. Feed cap freshly recomputed.',
        'new_source_sha256': descriptor.source_sha256, 'new_project_sha256': descriptor.project_sha256,
        'original_recipe_sha256': sha256(recipe_bytes).hexdigest(), 'matched_source_lines': [e.line_number for e in matched],
        'old_source_sha256': sha256(original_source).hexdigest(), 'declared_nominal_source_width_setting': saved['outer_wall_line_width'],
        'declared_nominal_source_height_setting': saved['layer_height'], 'actual_source_min_feed_mm_min': str(actual_feed_cap*60)},
        sort_keys=True, separators=(',', ':')).encode('ascii')
    association = associate_derived_path(trace, descriptor, proposal.frozen_emission, original_recipe=recipe_bytes,
        original_inputs=(original_source, original_project), geometry_evidence=evidence,
        matched_source_lines=tuple(sorted(e.line_number for e in matched)))
    path_input = ConditionalPathInput(proposal.frozen_emission, association, recipe_bytes,
                                    (original_source, original_project), evidence)
    return ConditionalInsertion(anchor, (path_input,), upper, policy), proposal, evidence


class ActualConditionalBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = actual_inputs()
        cls.trace = interpret_nominal_body(*cls.inputs)

    def test_every_actual_body_line_and_typed_command_is_accounted_without_m981(self):
        source, _, _, descriptor, _, _ = self.inputs
        self.assertEqual(len(self.trace.events), 19551)
        self.assertEqual(b''.join(e.raw for e in self.trace.events), source[descriptor.body_start_offset:descriptor.body_end_offset])
        counts = Counter(e.command for e in self.trace.events)
        self.assertEqual(counts, {None: 905, 'G1': 18073, 'M106': 10, 'M73': 76, 'M991': 31,
                                  'M204': 394, 'M624': 31, 'M625': 31})
        self.assertEqual(self.trace.events[0].line_number, 1246)
        self.assertEqual(self.trace.events[-1].line_number, 20796)
        self.assertTrue(source[descriptor.body_end_offset:].startswith(b'M981 S0'))
        self.assertIsNotNone(trace_linear_execution(source).failure)

    def test_fresh_actual_sample_source_association_conditional_anchor_and_copy(self):
        insertion, proposal, evidence = actual_sample(self.inputs, self.trace)
        result = compose_conditional_nominal_copy(*self.inputs, (insertion,))
        self.assertEqual(len(proposal.frozen_emission.path.points_mm), 66)
        self.assertEqual(len(insertion.paths[0].association.matched_source_lines), 65)
        self.assertEqual(insertion.anchor.object_scope.predicate, 'object_not_cancelled')
        span = result.insertion_spans[0]
        self.assertEqual(result.output_bytes[:span.output_start]+result.output_bytes[span.output_end:], self.inputs[0])
        self.assertFalse(result.printable_authorized)
        self.assertFalse(result.runtime_injection_authorized)

    def test_refrozen_reassociated_source_owned_policy_changes_reject(self):
        insertion, _, _ = actual_sample(self.inputs, self.trace)
        original = insertion.paths[0]
        changes = {'z_hop_mm': F('.001'), 'filament_diameter_mm': F('2.85'),
            'printable_height_mm': insertion.policy.printable_height_mm+1,
            'xy_speed_mm_s': insertion.policy.xy_speed_mm_s/2,
            'z_speed_mm_s': insertion.policy.z_speed_mm_s/2,
            'retract_speed_mm_s': insertion.policy.retract_speed_mm_s/2,
            'deretract_speed_mm_s': insertion.policy.deretract_speed_mm_s/2,
            'max_volume_mm3_s': insertion.policy.max_volume_mm3_s/2,
            'print_flow_ratio': insertion.policy.print_flow_ratio/2,
            'filament_flow_ratio': insertion.policy.filament_flow_ratio/2,
            'other_flow_enabled': not insertion.policy.other_flow_enabled,
            'outer_flow_ratio': insertion.policy.outer_flow_ratio/2}
        for field, changed in changes.items():
            with self.subTest(field=field):
                policy = replace(insertion.policy, **{field: changed})
                frozen = freeze_numeric_emission(original.frozen_emission.path, policy)
                association = associate_derived_path(self.trace, self.inputs[3], frozen,
                    original_recipe=original.original_recipe, original_inputs=original.original_inputs,
                    geometry_evidence=original.geometry_evidence,
                    matched_source_lines=original.association.matched_source_lines)
                path_input = replace(original, frozen_emission=frozen, association=association)
                with self.assertRaisesRegex(ValueError, 'saved source profile'):
                    compose_conditional_nominal_copy(*self.inputs,
                        (replace(insertion, paths=(path_input,), policy=policy),))

    def test_lower_candidate_speed_remains_profile_bound_and_legal(self):
        insertion, _, _ = actual_sample(self.inputs, self.trace)
        original = insertion.paths[0]
        policy = replace(insertion.policy, candidate_speed_mm_s=insertion.policy.candidate_speed_mm_s/2)
        frozen = freeze_numeric_emission(original.frozen_emission.path, policy)
        association = associate_derived_path(self.trace, self.inputs[3], frozen,
            original_recipe=original.original_recipe, original_inputs=original.original_inputs,
            geometry_evidence=original.geometry_evidence,
            matched_source_lines=original.association.matched_source_lines)
        composed = compose_conditional_nominal_copy(*self.inputs,
            (replace(insertion, paths=(replace(original, frozen_emission=frozen, association=association),), policy=policy),))
        self.assertFalse(composed.printable_authorized)
