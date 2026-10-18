"""Continuous contact bounds distinguish lowering from useful surface fill."""
from fractions import Fraction as F
import json
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment, ExactTopCellXY
from tools.analyze_uniform_z_contact import minimum_support, ROOT
from tools.build_uniform_z_review import build
from tools.audit_layered_preview_overlap import source_segments


def bead(identifier,a,b,z):
    return ExactNominalTopSegment(identifier,(F(a),F(0),F(z)),(F(b),F(0),F(z)),
                                 F(1),F('.2'),'structural')


class UniformZContactTests(unittest.TestCase):
    def test_flat_source_certifies_entire_closed_strip(self):
        report = minimum_support(ExactTopCellXY(F(0),F(2),F('-.01'),F('.01')),
                                 (bead('a',0,2,3),))
        self.assertEqual(report['state'],'full-bounded')
        self.assertEqual(F(report['minimum_lower_exact_mm']),3)
        self.assertEqual(F(report['minimum_upper_exact_mm']),3)

    def test_valley_reaches_lower_layer_without_trimming_x(self):
        sources = (bead('left',0,'.9',3),bead('right','1.1',2,3),bead('base',0,2,'2.8'))
        report = minimum_support(ExactTopCellXY(F(0),F(2),F('-.01'),F('.01')),sources)
        self.assertEqual(report['state'],'full-bounded')
        self.assertEqual(F(report['minimum_lower_exact_mm']),F('2.8'))
        self.assertEqual(F(report['minimum_upper_exact_mm']),F('2.8'))

    def test_missing_coverage_does_not_claim_a_lower_bound(self):
        report = minimum_support(ExactTopCellXY(F(0),F(2),F('-.01'),F('.01')),
                                 (bead('short',0,'.5',3),),max_cells=63)
        self.assertEqual(report['state'],'unresolved')
        self.assertNotIn('minimum_lower_exact_mm',report)

    def test_budget_exhaustion_cannot_be_point_sample_success(self):
        report = minimum_support(ExactTopCellXY(F(0),F(2),F('-.01'),F('.01')),
            (bead('left',0,1,3),bead('right',1,2,3)),max_cells=1)
        self.assertEqual(report['state'],'unresolved')

    def test_actual_uniform_shift_respects_all_closed_strip_certificates(self):
        path = ROOT/'artifacts/cuboid-tilt10-review/uniform-z-contact.json'
        if not path.exists():
            self.skipTest('local contact experiment is not distributed')
        report = json.loads(path.read_text())
        self.assertEqual(report['state'],'bounded')
        shift = F(report['uniform_downward_shift_exact_mm'])
        self.assertEqual(len(report['lines']),10)
        for line in report['lines']:
            bottom,w,h = map(F,(line['bottom_exact_mm'],line['width_exact_mm'],line['height_exact_mm']))
            self.assertLessEqual(bottom-shift,F(line['nominal_support']['minimum_lower_exact_mm']))
            self.assertLessEqual(bottom-shift,
                                 F(line['diamond_support']['minimum_lower_exact_mm']))
        self.assertFalse(report['printable_authorized'])
        self.assertFalse(report['shape_improvement_verified'])

    def test_historical_excessive_drop_is_now_rejected(self):
        folder = ROOT/'artifacts/cuboid-tilt10-review'
        path = folder/'uniform-z-contact.json'
        if not path.exists():
            self.skipTest('local contact experiment is not distributed')
        report = json.loads(path.read_text())
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        with self.assertRaisesRegex(ValueError,'ten percent'):
            build(source,project,report)
        with self.assertRaisesRegex(ValueError,'source-bound'):
            build(source+b'x',project,report)
        with self.assertRaisesRegex(ValueError,'project'):
            build(source,project+b'x',report)



if __name__ == '__main__':
    unittest.main()
