"""Opt-in construction coalescing preserves original source-solid identities."""
from fractions import Fraction as F
import unittest

from tests.unit.test_source_contour_intents import contour, proposal
from tools.prepare_source_contour_intents import CoalescedSourceContourProposal, SourceJointDetour


class SourceContourCoalescingTests(unittest.TestCase):
    def test_explicit_exact_codirectional_removal_with_original_provenance(self):
        source = contour(((0, 0), (F('.5'), 0), (1, 0), (1, 1), (0, 1)))
        with self.assertRaises(ValueError):
            proposal(contour=source, inward_offset_mm=F('.1'))
        result = proposal(contour=source, inward_offset_mm=F('.1'), coalesce_collinear_source_vertices=True)
        self.assertIs(type(result), CoalescedSourceContourProposal)
        self.assertEqual(result.coalesced_source_vertex_indices, (1,))
        self.assertEqual(result.source_segment_ids, tuple(s.segment_id for s in source))
        self.assertEqual(result.removed_vertices[0].source_segment_id, 'source-1')
        self.assertEqual(result.removed_vertices[0].reason, 'exact-codirectional-source-vertex')
        self.assertEqual(len(result.frozen_emission.path.points_mm), 5)
        self.assertEqual(len(source), 5)
        self.assertNotEqual(result.construction_identity, proposal(inward_offset_mm=F('.1')).construction_identity)

    def test_selected_collinear_joint_rejects_and_reverse_or_nonexact_not_coalesced(self):
        source = contour(((0, 0), (F('.5'), 0), (1, 0), (1, 1), (0, 1)))
        with self.assertRaisesRegex(ValueError, 'selected source joint'):
            proposal(contour=source, inward_offset_mm=F('.1'), coalesce_collinear_source_vertices=True,
                     joint_detours=(SourceJointDetour('source-1', F('.2')),))
        tiny_turn = contour(((0, 0), (F('.5'), F('.001')), (1, 0), (1, 1), (0, 1)))
        result = proposal(contour=tiny_turn, inward_offset_mm=F('.01'), coalesce_collinear_source_vertices=True)
        self.assertEqual(result.coalesced_source_vertex_indices, ())
        reverse = contour(((0, 0), (1, 0), (F('.5'), 0), (1, 1), (0, 1)))
        with self.assertRaises(ValueError):
            proposal(contour=reverse, inward_offset_mm=F('.1'), coalesce_collinear_source_vertices=True)
        with self.assertRaises(ValueError):
            proposal(coalesce_collinear_source_vertices=1)


if __name__ == '__main__':
    unittest.main()
