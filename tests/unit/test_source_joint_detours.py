"""Localized original-joint recipes are applied before numeric freezing."""
from dataclasses import asdict
from fractions import Fraction as F
import json
import unittest

from tests.unit.test_source_contour_intents import contour, proposal
from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.exponential_top_fixture import ROOT
from tools.supplemental_z_hop import policy_from_slice
from tools.prepare_source_contour_intents import (
    ContourConstructionPolicy, ContourProposalError, SourceJointContourProposal, SourceJointDetour,
)


class SourceJointDetourTests(unittest.TestCase):
    def test_empty_default_exact_serialization_and_identity_parity(self):
        self.assertEqual(asdict(proposal()), asdict(proposal(joint_detours=())))

    def test_existing_six_factory_receipts_serialize_exactly_unchanged(self):
        folder = ROOT/'artifacts/revolved-exponential-derived5000-9-seam0-v2-research'
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        profile = read_sliced_profile(project, source, include_motion_caps=True)
        policy = policy_from_slice(profile, CandidateBeadBounds(.08, .18, .25, .45), xyz_places=3, e_places=5)
        by_line = {str(r['line']): r for r in json.loads((folder/'nominal-model-rows.json').read_bytes())}
        references = json.loads((ROOT/'artifacts/source-contour-intent-review/six-groups-seven-paths.UNVERIFIED.json').read_bytes())['proposals']
        self.assertEqual(len(references), 6)
        for reference in references:
            path = reference['frozen_emission']['path']
            rows = [by_line[line] for line in reference['source_segment_ids']]
            original = tuple(ExactNominalTopSegment(str(r['line']), tuple(map(F, r['start'])), tuple(map(F, r['end'])),
                F(r['width']), F(r['height']), 'structural') for r in rows)
            current = proposal(source_sha256=profile.source_sha256, project_sha256=profile.project_sha256,
                contour=original, path_id=path['path_id'], floor_z_mm=F(path['floor_z_mm']),
                upper_z_mm=F(reference['upper_z_mm']), width_mm=F(path['width_mm']), height_mm=F(path['height_mm']),
                remaining_height_mm=F(reference['remaining_height_mm']), inward_offset_mm=F(reference['inward_offset_mm']),
                minimum_segment_mm=F(reference['minimum_segment_mm']), emission_policy=policy,
                construction_policy=ContourConstructionPolicy(**reference['construction_policy']))
            self.assertEqual(json.loads(json.dumps(asdict(current), default=str)), reference)

    def test_both_orientations_translation_nonzero_joint_and_provenance(self):
        for points in (((0, 0), (1, 0), (1, 1), (0, 1)), ((0, 1), (1, 1), (1, 0), (0, 0))):
            source = contour(points)
            recipe = (SourceJointDetour('source-2', F('.2')),)
            result = proposal(contour=source, inward_offset_mm=F('.1'), joint_detours=recipe)
            self.assertIs(type(result), SourceJointContourProposal)
            self.assertIn((*source[2].start_xyz_mm[:2], F('3.08')), result.frozen_emission.path.points_mm)
            self.assertEqual({w.direction for w in result.waypoints}, {'before', 'after'})
            self.assertEqual(result.source_segment_ids, tuple(s.segment_id for s in source))
            self.assertFalse(result.accepted)
            shifted = contour(tuple((x+10, y-4) for x, y in points))
            moved = proposal(contour=shifted, inward_offset_mm=F('.1'), joint_detours=recipe)
            self.assertEqual(tuple((p[0]-10, p[1]+4, p[2]) for p in moved.frozen_emission.path.points_mm),
                             result.frozen_emission.path.points_mm)
            changed = proposal(contour=source, inward_offset_mm=F('.1'),
                joint_detours=(SourceJointDetour('source-2', F('.25')),))
            self.assertNotEqual(result.construction_identity, changed.construction_identity)

    def test_invalid_joint_locality_overlap_and_protected_short_edges(self):
        for recipes in ([SourceJointDetour('source-0', F('.2'))],
                (SourceJointDetour('missing', F('.2')),), (SourceJointDetour('source-0', F(0)),),
                (SourceJointDetour('source-0', .2),),
                (SourceJointDetour('source-0', F('.2')),)*2,
                (SourceJointDetour('source-0', F(3)),),
                (SourceJointDetour('source-0', F('.6')), SourceJointDetour('source-1', F('.6')))):
            with self.subTest(recipes=recipes), self.assertRaises(ContourProposalError):
                proposal(inward_offset_mm=F('.1'), joint_detours=recipes)
        with self.assertRaisesRegex(ContourProposalError, 'protected'):
            proposal(inward_offset_mm=F('.1'), minimum_segment_mm=F('.3'),
                     joint_detours=(SourceJointDetour('source-0', F('.2')),))

    def test_disjoint_multiple_joint_neighborhoods_and_wrapping_reject(self):
        recipes = (SourceJointDetour('source-0', F('.2')), SourceJointDetour('source-2', F('.2')))
        result = proposal(inward_offset_mm=F('.1'), joint_detours=recipes)
        self.assertEqual(len(result.waypoints), 4)
        self.assertEqual(len(result.joint_replacements), 2)
        for joint in ((F(0), F(0)), (F(1), F(1))):
            self.assertIn((*joint, F('3.08')), result.frozen_emission.path.points_mm)
        with self.assertRaises(ContourProposalError):
            proposal(joint_detours=(SourceJointDetour('source-0', F(5)),))

    def test_initial_regularization_retains_selected_original_joint_and_limits_reject(self):
        source = contour(((0, 0), (F('.01'), 0), (1, 0), (1, 1), (0, 1)))
        retained = proposal(contour=source, minimum_segment_mm=F('.05'),
            joint_detours=(SourceJointDetour('source-1', F('.2')),))
        self.assertIn((F('.01'), F(0), F('3.08')), retained.frozen_emission.path.points_mm)
        self.assertEqual(retained.removed_vertices[0].original_vertex_index, 0)
        self.assertEqual(retained.initial_removed_vertex_count, 1)
        before = next(w for w in retained.waypoints if w.direction == 'before')
        self.assertEqual(before.walked_source_segment_ids, ('source-0', 'source-4'))
        self.assertEqual(before.source_segment_id, 'source-4')
        with self.assertRaisesRegex(ContourProposalError, 'vertex budget'):
            proposal(construction_policy=ContourConstructionPolicy(9, 5, 4096, 1000),
                     joint_detours=(SourceJointDetour('source-0', F('.2')),))
        with self.assertRaises(ContourProposalError):
            proposal(cancelled=lambda: True, joint_detours=(SourceJointDetour('source-0', F('.2')),))


if __name__ == '__main__':
    unittest.main()
