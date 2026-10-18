"""Curved fixture topology, independent geometry and angle-bin evidence."""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import math
import unittest

from tools.exponential_top_fixture import ROOT, REVIEW_FOLDER, PANELS, angle_radians, profile, mesh, placed_profile, target_at
from tools.evaluate_curved_surface import compare, summarize
from tools.build_triangle_rectangle_review import build
from tools.audit_layered_preview_overlap import source_segments


class ExponentialTopTests(unittest.TestCase):
    def test_angles_are_exponential_and_integral_is_stable(self):
        self.assertAlmostEqual(math.degrees(angle_radians(0)),0)
        self.assertAlmostEqual(math.degrees(angle_radians(12)),40)
        self.assertAlmostEqual(math.degrees(angle_radians(6)),40/3)
        a,b = profile(),profile(2*PANELS)
        self.assertLess(abs(a[-1][1]-b[-1][1]),1e-8)
        self.assertTrue(all(z1>z0 for (_,z0),(_,z1) in zip(a,a[1:])))
        for invalid in (0,1,4097,256.0):
            with self.assertRaises(ValueError):
                profile(invalid)

    def test_closed_oriented_mesh_has_no_boundary_edges(self):
        vertices,faces = mesh()
        edges = Counter((min(a,b),max(a,b)) for f in faces for a,b in zip(f,f[1:]+f[:1]))
        directed = Counter((a,b) for f in faces for a,b in zip(f,f[1:]+f[:1]))
        self.assertTrue(all(count==2 for count in edges.values()))
        self.assertTrue(all(directed[(a,b)]==directed[(b,a)] for a,b in directed))
        self.assertEqual(len(vertices),4*(PANELS+1))

    def test_piecewise_target_and_domain_guard(self):
        top = ((F(84),F(3)),(F(85),F('3.2')),(F(86),F('3.6')))
        self.assertEqual(target_at(top,F('84.5')),(F('3.1'),F('.2')))
        self.assertEqual(target_at(top,F(86)),(F('3.6'),F('.4')))
        with self.assertRaises(ValueError):
            target_at(top,F('83.9'))

    def test_angle_metrics_penalize_excess_and_preserve_missing_mask(self):
        top = ((F(0),F(1)),(F(1),F('1.2')))
        bins = compare([[1.,None]],[[1.2,None]],[.5],top)
        row = bins[2]
        self.assertEqual(row['before']['count'],1)
        self.assertEqual(row['after']['missing_source_count'],1)
        self.assertAlmostEqual(row['before']['mae_vertical_mm'],.1)
        self.assertAlmostEqual(row['after']['mae_vertical_mm'],.1)
        self.assertAlmostEqual(row['after']['mean_excess_mm'],.1)
        self.assertIsNone(summarize([],0)['mae_vertical_mm'])

    def test_actual_curve_preserves_source_and_reports_actual_mesh_errors(self):
        folder = REVIEW_FOLDER
        if not (folder/'angle-errors.json').is_file():
            self.skipTest('local curved fixture not distributed')
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        current = json.loads((folder/'current-review.json').read_text())
        bounds,top = placed_profile(project)
        self.assertEqual(bounds[:2],(80,100))
        content,manifest = build(source,project,curved_top=True,
            expected_source_sha256=current['source_slice_sha256'],
            expected_project_sha256=current['placed_project_sha256'])
        self.assertNotIn('target_plane_z_equals_by_plus_c_exact',manifest)
        self.assertGreater(manifest['candidate_count'],0)
        excluded = [s for s in manifest['section_diagnostics'] if s['status']=='excluded-short-step-base']
        self.assertGreater(len(excluded),0)
        self.assertEqual(manifest['step_applicability']['excluded_step_count'],len(excluded))
        for step in excluded:
            self.assertLess(F(step['triangle_base_exact_mm'])**2,2*F('.25')**2)
            self.assertEqual(step['line_count'],0)
        rejected_floors = {s['lower_z_exact_mm'] for s in excluded}
        self.assertTrue(all(c['terrace_z_exact_mm'] not in rejected_floors
                            for c in manifest['candidate_segments']))
        self.assertFalse(manifest['printable_authorized'])
        before = source_segments(source,expected_sha256=current['source_slice_sha256'])
        after = source_segments(content.encode(),expected_sha256=hashlib.sha256(content.encode()).hexdigest())
        self.assertFalse(Counter(r[:6] for r in before)-Counter(r[:6] for r in after))
        self.assertEqual(len(after),len(before)+manifest['candidate_count'])
        errors = json.loads((folder/'angle-errors.json').read_text())
        for row in errors['fine']['source_covered_only_angle_bins']:
            self.assertGreater(row['before']['count'],0)
            self.assertEqual(row['before']['count'],row['after']['count'])
            self.assertTrue(math.isfinite(row['after']['mae_vertical_mm']))
        steep = errors['fine']['source_covered_only_angle_bins'][-1]
        self.assertEqual(steep['before']['mae_vertical_mm'],steep['after']['mae_vertical_mm'])
        step = manifest['section_diagnostics'][1]
        low = F(step['lower_z_exact_mm'])
        a,b = F(step['left_edge_exact_mm']),F(step['right_edge_exact_mm'])
        self.assertAlmostEqual(float(target_at(top,a)[0]-low),-.1,places=3)
        self.assertAlmostEqual(float(target_at(top,b)[0]-low),.1,places=3)


if __name__ == '__main__':
    unittest.main()
