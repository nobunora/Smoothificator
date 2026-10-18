"""Whole-top coverage and read-only cuboid representation regressions."""
from fractions import Fraction as F
import hashlib
import unittest

from tools.audit_layered_preview_overlap import source_segments
from tools.build_cuboid_top_review import build_scene, top_hatch, WIDTH_MM, ROOT


class CuboidTopReviewTests(unittest.TestCase):
    def test_hatch_covers_closed_full_rectangle_without_transverse_gaps(self):
        bounds = (F("119.6"),F("131.6"),F(80),F(100))
        rows = top_hatch(bounds,F(3))
        self.assertEqual(len(rows),59)
        self.assertEqual(rows[0][1]-WIDTH_MM/2,bounds[2])
        self.assertEqual(rows[-1][1]+WIDTH_MM/2,bounds[3])
        for a,b in zip(rows,rows[1:]):
            self.assertTrue(0<b[1]-a[1]<=WIDTH_MM)
        self.assertTrue(all((a,b,z)==(bounds[0],bounds[1],F("3.08")) for a,y,b,z in rows))

    def test_invalid_rectangle_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"bounds"):
            top_hatch((F(1),F(0),F(0),F(20)),F(3))

    def test_bbl_comment_tags_require_explicit_source_identity(self):
        source = b'G90\nM83\n; Z_HEIGHT: 3\n; LINE_WIDTH: 0.4\nG1 X1 Y2 Z3\nG1 X2 E0.1\n'
        with self.assertRaisesRegex(ValueError,"unpinned"):
            source_segments(source)
        rows = source_segments(source,expected_sha256=hashlib.sha256(source).hexdigest())
        self.assertEqual(rows[0][:6],(3.,1.,2.,2.,2.,.4))
        altered = source+b'G91\n'
        with self.assertRaisesRegex(ValueError,"motion mode"):
            source_segments(altered,expected_sha256=hashlib.sha256(altered).hexdigest())

    def test_actual_cuboid_scene_has_all_layers_and_no_machine_programs(self):
        path = ROOT/'artifacts/cuboid-top-review/original-slice/plate_1.gcode'
        if not path.is_file():
            self.skipTest("local offline cuboid slice is not distributed")
        source = path.read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        content,manifest = build_scene(source,digest)
        self.assertEqual(manifest["candidate_count"],59)
        self.assertEqual(manifest["layer_count"],16)
        self.assertFalse(manifest["printable_authorized"])
        self.assertFalse(manifest["shape_improvement_verified"])
        self.assertIn('; Z_HEIGHT: 3.08',content)
        self.assertEqual(content.count('; FEATURE: Custom'),59)
        self.assertEqual(manifest["original_segment_count"],len(source_segments(source,expected_sha256=digest)))
        baseline = source_segments(source,expected_sha256=digest)
        rendered = source_segments(content.encode('ascii'),expected_sha256=hashlib.sha256(content.encode('ascii')).hexdigest())
        shift_x,shift_y = map(F,manifest['viewer_xy_translation_exact_mm'])
        self.assertEqual(len(rendered),len(baseline)+59)
        for original,shown in zip(baseline,rendered):
            self.assertEqual(original[0],shown[0])
            for index,shift in ((1,shift_x),(2,shift_y),(3,shift_x),(4,shift_y)):
                self.assertAlmostEqual(original[index]+float(shift),shown[index],places=8)
        commands = {line.split()[0] for line in content.splitlines() if line and not line.startswith(';')}
        self.assertLessEqual(commands,{'G21','G90','M83','G92','G1'})
        with self.assertRaisesRegex(ValueError,"unpinned"):
            build_scene(source+b'x',digest)


if __name__ == '__main__':
    unittest.main()
