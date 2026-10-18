"""Generic proposal freezing and exact legacy emission parity regressions."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import json
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.exponential_top_fixture import ROOT
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.prepare_source_contour_intents import (
    ContourConstructionPolicy, ContourProposalError, prepare_source_contour_proposal,
)
from tests.unit.test_supplemental_z_hop import policy_fixture, path_fixture


def contour(points=((0, 0), (1, 0), (1, 1), (0, 1))):
    points = tuple(tuple(F(v) for v in p) for p in points)
    return tuple(ExactNominalTopSegment(f'source-{i}', (*a, F(3)), (*b, F(3)), F('.4'), F('.2'), 'structural')
                 for i, (a, b) in enumerate(zip(points, points[1:]+points[:1])))


def proposal(**changes):
    arguments = dict(source_sha256='1'*64, project_sha256='2'*64, contour=contour(), path_id='contour-proposal',
        floor_z_mm=F(3), upper_z_mm=F('3.2'), width_mm=F('.3'), height_mm=F('.08'),
        remaining_height_mm=F('.08'), inward_offset_mm=F(0), minimum_segment_mm=F(0),
        emission_policy=policy_fixture(), construction_policy=ContourConstructionPolicy(9, 100, 4096, 100000),
        cancelled=lambda: False)
    arguments.update(changes)
    return prepare_source_contour_proposal(**arguments)


class SourceContourIntentTests(unittest.TestCase):
    def test_zero_offset_minimum0_preserves_source_vertices_before_freezing(self):
        result = proposal()
        self.assertEqual(result.removed_vertices, ())
        self.assertEqual(result.frozen_emission.path.points_mm,
            ((F(0), F(0), F('3.08')), (F(1), F(0), F('3.08')), (F(1), F(1), F('3.08')),
             (F(0), F(1), F('3.08')), (F(0), F(0), F('3.08'))))
        for field in ('accepted', 'contact_verified', 'future_volume_verified', 'printable_authorized'):
            self.assertFalse(getattr(result, field))
        with self.assertRaises(FrozenInstanceError):
            result.accepted = True

    def test_inward_offset_both_orientations_and_translation(self):
        expected = {(F('.1'), F('.1')), (F('.9'), F('.1')), (F('.9'), F('.9')), (F('.1'), F('.9'))}
        for points in (((0, 0), (1, 0), (1, 1), (0, 1)), ((0, 1), (1, 1), (1, 0), (0, 0))):
            result = proposal(contour=contour(points), inward_offset_mm=F('.1'))
            self.assertEqual({p[:2] for p in result.frozen_emission.path.points_mm}, expected)
            translated = contour(tuple((x+10, y-4) for x, y in points))
            moved = proposal(contour=translated, inward_offset_mm=F('.1'))
            self.assertEqual({(p[0]-10, p[1]+4) for p in moved.frozen_emission.path.points_mm}, expected)

    def test_short_and_grid_duplicate_vertices_removed_only_before_freeze_with_provenance(self):
        for position, reason, minimum in ((F('.01'), 'declared-short-edge', F('.05')),
                                          (F('.0004'), 'grid-duplicate', F(0))):
            source = contour(((0, 0), (position, 0), (1, 0), (1, 1), (0, 1)))
            result = proposal(contour=source, minimum_segment_mm=minimum)
            self.assertEqual(len(result.removed_vertices), 1)
            self.assertEqual(result.removed_vertices[0].original_vertex_index, 1)
            self.assertEqual(result.removed_vertices[0].source_segment_id, 'source-1')
            self.assertEqual(result.removed_vertices[0].reason, reason)
            self.assertEqual(len(result.frozen_emission.path.points_mm), 5)
            self.assertEqual(len(source), 5)

    def test_nonsimple_disconnected_wrong_floor_and_unsupported_offsets_reject(self):
        cases = (dict(contour=contour(((0, 0), (1, 1), (0, 1), (1, 0)))),
                 dict(contour=contour(((0, 0), (F('.5'), 0), (1, 0), (1, 1), (0, 1))), inward_offset_mm=F('.1')),
                 dict(inward_offset_mm=F('.75')))
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ContourProposalError):
                proposal(**changes)
        source = contour()
        with self.assertRaises(ContourProposalError):
            proposal(contour=(replace(source[0], end_xyz_mm=(F('.9'), F(0), F(3))), *source[1:]))
        with self.assertRaises(ContourProposalError):
            proposal(contour=(replace(source[0], start_xyz_mm=(F(0), F(0), F('3.1'))), *source[1:]))
        concave = contour(((0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)))
        self.assertEqual(len(proposal(contour=concave).frozen_emission.path.points_mm), 7)
        self.assertEqual(len(proposal(contour=concave, inward_offset_mm=F('.1')).frozen_emission.path.points_mm), 7)

    def test_dimensions_remaining_overlap_height_cap_and_nearest_e_reject(self):
        for changes in (dict(remaining_height_mm=F('.079')), dict(height_mm=F('.18'), remaining_height_mm=F('.08')),
                        dict(height_mm=F('.181'), remaining_height_mm=F('.126')), dict(width_mm=F('.24')),
                        dict(remaining_height_mm=F('.0801'), height_mm=F('.0801')),
                        dict(upper_z_mm=F('3.05')), dict(inward_offset_mm=F(-1))):
            with self.subTest(changes=changes), self.assertRaises(ContourProposalError):
                proposal(**changes)
        with self.assertRaisesRegex(ValueError, 'E is zero'):
            proposal(emission_policy=replace(policy_fixture(), e_places=0))
        with self.assertRaisesRegex(ValueError, 'width outside'):
            freeze_numeric_emission(replace(path_fixture(), width_mm=F('.25'),
                points_mm=((F(0), F(0), F('3.08')), (F('.003'), F(0), F('3.08')))), policy_fixture())
        for invalid in (replace(path_fixture(), height_mm=F('.18')),
                        replace(path_fixture(), floor_z_mm=F('3.001')),
                        replace(path_fixture(), floor_z_mm=F('3.0001'))):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                freeze_numeric_emission(invalid, policy_fixture())
        base = path_fixture()
        varying = replace(base, points_mm=(base.points_mm[0],
            (*base.points_mm[1][:2], base.points_mm[1][2]+F('.0001')), base.points_mm[2]))
        with self.assertRaisesRegex(ValueError, 'before quantization'):
            freeze_numeric_emission(varying, policy_fixture())

    def test_resource_invalid_identity_types_and_cancellation(self):
        for settings in (ContourConstructionPolicy(9, 3, 4096, 10000),
                         ContourConstructionPolicy(9, 100, 1, 10000),
                         ContourConstructionPolicy(9, 100, 4096, 1)):
            with self.assertRaises(ContourProposalError) as failure:
                proposal(construction_policy=settings)
            self.assertEqual(failure.exception.reason, 'resource-limit')
        with self.assertRaises(ContourProposalError) as failure:
            proposal(cancelled=lambda: True)
        self.assertEqual(failure.exception.reason, 'cancelled')
        for changes in (dict(source_sha256='bad'), dict(path_id='bad\nM112'), dict(width_mm=.3),
                        dict(cancelled=lambda: 1), dict(contour=list(contour()))):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                proposal(**changes)
        huge = 10**400
        with self.assertRaisesRegex(ValueError, 'nonfinite geometry'):
            proposal(contour=contour(((huge, 0), (huge+1, 0), (huge+1, 1), (huge, 1))))

    def test_legacy_ring_numeric_tuples_match_existing_frozen_artifact_exactly(self):
        from tools.prepare_executable_ring_intents import prepare_ring_intents
        folder = ROOT/'artifacts/revolved-exponential-review'
        result = prepare_ring_intents((folder/'original-slice/sliced.3mf').read_bytes(),
            (folder/'original-slice/plate_1.gcode').read_bytes(), (folder/'current-review.json').read_bytes())
        old = json.loads((ROOT/'artifacts/revolved-exponential-execution/ring-intents.UNVERIFIED.json').read_bytes())
        self.assertEqual(len(result.rings), 30)
        self.assertEqual(len(old['rings']), 30)
        self.assertEqual(tuple(r.path.path_id for r in result.rings), tuple(r['path']['path_id'] for r in old['rings']))
        for current, reference in zip(result.rings, old['rings']):
            self.assertEqual(current.emitted_e_mm, tuple(map(F, reference['emitted_e_mm'])))
            self.assertEqual(current.emitted_feed_mm_min, tuple(map(F, reference['emitted_feed_mm_min'])))
            self.assertEqual(current.minimum_emitted_width_mm, reference['minimum_emitted_width_mm'])
            self.assertEqual(current.maximum_emitted_width_mm, reference['maximum_emitted_width_mm'])
            self.assertEqual(current.maximum_volume_rate_mm3_s, reference['maximum_volume_rate_mm3_s'])
