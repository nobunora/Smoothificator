"""Line-relative offset limits, envelope rejection and unchanged source."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
import unittest

from tools.analyze_thickness_z_offsets import ROOT, bounded_offset
from tools.audit_layered_preview_overlap import source_segments
from tools.build_uniform_z_review import build_bounded


class ThicknessZOffsetTests(unittest.TestCase):
    def test_offset_is_based_on_line_height_not_slicer_layer_height(self):
        self.assertEqual(bounded_offset(F('.05'),F('-.1')),F('-.005'))
        self.assertEqual(bounded_offset(F('.18'),F('.1')),F('.018'))
        self.assertEqual(bounded_offset(F('.05'),F(0)),0)

    def test_excessive_adjustments_are_rejected_without_clamping_silently(self):
        for fraction in (F('-.1000001'),F('.1000001'),F('-12.7')):
            with self.assertRaisesRegex(ValueError,'ten percent'):
                bounded_offset(F('.05'),fraction)

    def test_actual_sweep_and_bounded_representation(self):
        folder = ROOT/'artifacts/cuboid-tilt10-review'
        path = folder/'thickness-z-offsets.json'
        if not path.is_file():
            self.skipTest('local experiment not distributed')
        report = json.loads(path.read_text())
        self.assertEqual([v['offset_percent'] for v in report['variants']],[-10,-5,0,5,10])
        variant = report['variants'][0]
        self.assertEqual(len(variant['lines']),10)
        for row in variant['lines']:
            height,offset = F(row['height_exact_mm']),F(row['z_offset_exact_mm'])
            self.assertEqual(offset,-height/10)
            self.assertEqual(F(row['height_retained_fraction_exact']),F('.9'))
            self.assertTrue(row['target_rectangular_envelope_within_model'])
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        content,manifest = build_bounded(source,project,report)
        before = source_segments(source,expected_sha256=report['source_slice_sha256'])
        shown = source_segments(content.encode(),expected_sha256=hashlib.sha256(content.encode()).hexdigest())
        self.assertFalse(Counter(r[:6] for r in before)-Counter(r[:6] for r in shown))
        self.assertEqual(len(shown),len(before)+10)
        self.assertEqual(manifest['candidate_count'],10)
        self.assertFalse(manifest['useful_surface_interpolation_verified'])
        self.assertFalse(manifest['printable_authorized'])
        self.assertIn('+/-10%',content)
        for fraction in (F('.05'),F('.1')):
            with self.assertRaisesRegex(ValueError,'model'):
                build_bounded(source,project,report,fraction=fraction)
        with self.assertRaisesRegex(ValueError,'ten percent'):
            build_bounded(source,project,report,fraction=F('-.11'))
        altered = deepcopy(report)
        altered['variants'][0]['lines'][0]['z_offset_exact_mm']='-0.635'
        with self.assertRaisesRegex(ValueError,'geometry'):
            build_bounded(source,project,altered)


if __name__ == '__main__':
    unittest.main()
