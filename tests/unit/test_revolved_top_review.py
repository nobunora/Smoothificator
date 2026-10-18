"""Closed revolution, radial step extraction and complete native ring evidence."""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import math
import unittest

from tools.revolved_exponential_fixture import (
    REVIEW_FOLDER, ANGULAR_PANELS, PANELS, mesh, placed_geometry,
)
from tools.build_revolved_top_review import build, positive_ray_interval, ring_vertices, RING_SEGMENTS
from tools.evaluate_revolved_surface import triangle_height, target_at_xy
from tools.audit_layered_preview_overlap import source_segments


class RevolvedTopTests(unittest.TestCase):
    def test_revolved_mesh_is_closed_and_oriented(self):
        vertices,faces = mesh()
        directed = Counter((a,b) for face in faces for a,b in zip(face,face[1:]+face[:1]))
        self.assertTrue(all(n==directed[(b,a)]==1 for (a,b),n in directed.items()))
        self.assertEqual(len(vertices),2+(PANELS+1)*ANGULAR_PANELS)
        self.assertAlmostEqual(vertices[1][2],3)
        outer = vertices[2+(PANELS-1)*ANGULAR_PANELS]
        self.assertAlmostEqual(math.hypot(*outer[:2]),12)
        self.assertGreater(outer[2],6)

    def test_positive_ray_uses_finite_flat_cap_footprint(self):
        lo,hi = positive_ray_interval((1,95,80,95,100,.4,1),(90,90,3))
        self.assertAlmostEqual(lo,4.8,places=12)
        self.assertAlmostEqual(hi,5.2,places=12)
        self.assertIsNone(positive_ray_interval((1,80,95,100,95,.4,1),(90,90,3)))

    def test_rings_are_closed_constant_z_with_bounded_chord_error(self):
        points = ring_vertices((90.,90.,3.),F(10),F('3.12'))
        self.assertEqual(len(points),RING_SEGMENTS+1)
        self.assertEqual(points[0],points[-1])
        self.assertEqual(len(set(points[:-1])),RING_SEGMENTS)
        self.assertTrue(all(p[2]==F('3.12') for p in points))
        for x,y,z in points:
            self.assertAlmostEqual(math.hypot(float(x)-90,float(y)-90),10,places=8)
        self.assertLess(12*(1-math.cos(math.pi/RING_SEGMENTS)),.002)

    def test_actual_triangle_height_is_barycentric(self):
        value = triangle_height((0,0,0),(1,0,1),(0,1,0),.25,.25)
        self.assertEqual(value,(.25,1.))
        self.assertIsNone(triangle_height((0,0,0),(1,0,1),(0,1,0),1,1))

    def test_actual_revolution_preview_preserves_originals_and_constraints(self):
        folder = REVIEW_FOLDER
        if not (folder/'current-review.json').is_file():
            self.skipTest('local actual revolution fixture not distributed')
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        receipt = json.loads((folder/'slice-receipt.json').read_text())
        content,manifest = build(source,project,receipt)
        self.assertEqual(manifest['ring_count'],30)
        self.assertEqual(manifest['candidate_count'],30*RING_SEGMENTS)
        self.assertEqual(manifest['excluded_step_count'],4)
        for ring in manifest['rings']:
            self.assertTrue(F('.25')<=F(ring['width_exact_mm'])<=F('.45'))
            self.assertTrue(F('.08')<=F(ring['height_exact_mm'])<=F('.18'))
            self.assertEqual(ring['bottom_z_exact_mm'],ring['floor_z_exact_mm'])
            self.assertLessEqual(F(ring['spill_fraction_exact']),F('.5'))
            self.assertFalse(ring['whole_ring_contact_verified'])
        old = source_segments(source,expected_sha256=receipt['source_slice_sha256'])
        new = source_segments(content.encode(),expected_sha256=hashlib.sha256(content.encode()).hexdigest())
        self.assertFalse(Counter(r[:6] for r in old)-Counter(r[:6] for r in new))
        self.assertEqual(len(new),len(old)+manifest['candidate_count'])
        self.assertFalse(manifest['printable_authorized'])
        self.assertFalse(manifest['whole_ring_contact_verified'])
        self.assertFalse(manifest['annular_volume_optimum_proven'])
        with self.assertRaisesRegex(ValueError,'pinned'):
            build(source+b'x',project,receipt)
        with self.assertRaises(ValueError):
            build(source,project,receipt,overlap_percent=F(31))

    def test_placed_target_and_angle_report(self):
        folder = REVIEW_FOLDER
        if not (folder/'angle-errors.json').is_file():
            self.skipTest('local actual revolution metrics not distributed')
        center,top,vertices = placed_geometry((folder/'original-slice/sliced.3mf').read_bytes())
        radii = [float(r) for r,z in top]
        for j in (0,ANGULAR_PANELS//4,ANGULAR_PANELS//2):
            vertex = vertices[2+127*ANGULAR_PANELS+j]
            z,slope = target_at_xy(center,radii,vertices,*vertex[:2])
            self.assertAlmostEqual(z,vertex[2],places=6)
            self.assertGreater(slope,0)
        self.assertIsNone(target_at_xy(center,radii,vertices,center[0]+13,center[1]))
        report = json.loads((folder/'angle-errors.json').read_text())
        self.assertEqual(len(report['fine']['source_covered_only_angle_bins']),8)
        for row in report['fine']['source_covered_only_angle_bins']:
            self.assertGreater(row['before']['count'],0)
            self.assertEqual(row['before']['count'],row['after']['count'])
            self.assertTrue(math.isfinite(row['after']['mae_vertical_mm']))


if __name__=='__main__':
    unittest.main()
