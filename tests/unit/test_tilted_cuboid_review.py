"""Deficit-driven stair interpolation, separate from full-face hatch."""
from fractions import Fraction as F
import hashlib
import json
import math
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.audit_layered_preview_overlap import source_segments
from tools.build_tilted_cuboid_review import ROOT, baseline, sliced_top_face, step_candidates, slicer_height_limit
from tools.build_cuboid_top_review import prepare_fixture


def bead(identifier,z,y,width):
    return ExactNominalTopSegment(identifier,(F(0),F(y),F(z)),(F(20),F(y),F(z)),
                                 F(width),F('.2'),'structural')


class TiltedCuboidReviewTests(unittest.TestCase):
    def test_rectangle_fit_uses_width_edges_not_center_plane(self):
        sources = (bead('a','3','1','2'),bead('b','3.2','2.2','.4'))
        candidates,diagnostics = step_candidates((F(0),F(20),F(0),F(6)),F('.1'),F(3),sources,maximum_height=F('.18'))
        self.assertGreater(len(candidates),1)
        self.assertTrue(any(review['line_count']>1 for s,review in candidates))
        self.assertEqual(candidates[0][0].width_mm,F(1,3))
        first_group = [s for s,review in candidates if review['rectangle_id']==candidates[0][1]['rectangle_id']]
        self.assertEqual(sum((s.width_mm for s in first_group),F(0)),1)
        for segment,review in candidates:
            width,height = segment.width_mm,segment.height_mm
            self.assertTrue(F('.25') <= width <= F('.45'))
            self.assertTrue(F('.05') <= height <= F('.18'))
            low_y = segment.start_xyz_mm[1]-width/2
            self.assertLessEqual(segment.start_xyz_mm[2],F('.1')*low_y+3)
            self.assertEqual(review['whole_path_central_strip']['state'],'nominal-strip-intersection-proven')

    def test_positive_gap_can_still_have_no_feasible_rectangle(self):
        sources = (bead('a','3','.2','1'),bead('b','3.2','.7','.4'))
        candidates,diagnostics = step_candidates((F(0),F(20),F(0),F(6)),F('.18'),F(3),sources,maximum_height=F('.18'))
        self.assertEqual(candidates,[])
        self.assertEqual(diagnostics[0]['reason'],'no-feasible-2d-rectangle')
        self.assertGreater(diagnostics[0]['maximum_section_gap_mm'],0)
        self.assertLess(diagnostics[0]['maximum_height_at_minimum_width_mm'],.05)
        self.assertFalse(diagnostics[0]['actual_3d_nonexistence_proven'])

    def test_support_gap_does_not_emit_trimmed_fragments(self):
        short = ExactNominalTopSegment('a',(F(0),F(1),F(3)),
            (F(1),F(1),F(3)),F(2),F('.2'),'structural')
        candidates,diagnostics = step_candidates((F(0),F(20),F(0),F(6)),F('.1'),F(3),
                                               (short,bead('b','3.2','2.2','.4')),maximum_height=F('.18'))
        self.assertEqual(candidates,[])
        self.assertTrue(any(d['reason']=='2d-solution-requires-3d-support-reconstruction' for d in diagnostics))

    def test_subheight_gap_infill_preserved_but_audit_exclusion_requires_z_bound(self):
        source = b'G90\nM83\n; Z_HEIGHT: 0.4\n; LINE_WIDTH: 0.1\n; LAYER_HEIGHT: 0.2\n; FEATURE: Gap infill\nG1 X1 Y2 Z0.4\nG1 X2 E0.1\n'
        digest = hashlib.sha256(source).hexdigest()
        rows,exact,metadata,omitted = baseline(source,digest,F(2))
        self.assertEqual(len(rows),1)
        self.assertEqual(exact,())
        self.assertEqual(omitted[0]['maximum_z_mm'],.4)
        with self.assertRaisesRegex(ValueError,'audit domain'):
            baseline(source,digest,F('.4'))
        with self.assertRaisesRegex(ValueError,'unpinned'):
            baseline(source+b'x',digest,F(2))

    def test_invalid_fixture_angle_fails_before_writing(self):
        for angle in (float('nan'),-1,31):
            with self.assertRaises(ValueError):
                prepare_fixture(ROOT/'artifacts/cuboid-tilt10-review',tilt_degrees=angle)

    def test_maximum_height_tracks_slicer_setting_and_rejects_ambiguous_settings(self):
        for height in ('.20','.30'):
            source = f'; CONFIG_BLOCK_START\n; layer_height = {height}\n; CONFIG_BLOCK_END\n'.encode()
            configured,maximum = slicer_height_limit(source)
            self.assertEqual(configured,F(height))
            self.assertEqual(maximum,F(height)*F('.9'))
        for settings in ('','; layer_height = 0\n','; layer_height = .04\n',
                         '; layer_height = .2\n; layer_height = .3\n'):
            with self.assertRaises(ValueError):
                slicer_height_limit(f'; CONFIG_BLOCK_START\n{settings}; CONFIG_BLOCK_END\n'.encode())

    def test_actual_placed_model_and_retained_baseline(self):
        folder = ROOT/'artifacts/cuboid-tilt10-review'
        path = folder/'current-review.json'
        if not path.is_file():
            self.skipTest('local tilted cuboid review is not distributed')
        manifest = json.loads(path.read_text())
        bounds,slope,intercept = sliced_top_face((folder/'original-slice/sliced.3mf').read_bytes())
        self.assertAlmostEqual(math.degrees(math.atan(float(slope))),10,places=5)
        self.assertEqual(bounds[1]-bounds[0],20)
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        original = source_segments(source,expected_sha256=manifest['source_slice_sha256'])
        content = __import__('pathlib').Path(manifest['viewer_file']).read_bytes()
        shown = source_segments(content,expected_sha256=manifest['viewer_sha256'])
        # Insertion changes order: compare multisets of retained geometry.
        from collections import Counter
        expected = Counter(row[:6] for row in original)
        actual = Counter(row[:6] for row in shown)
        self.assertFalse(expected-actual)
        self.assertEqual(len(shown)-len(original),manifest['candidate_count'])
        self.assertEqual(manifest['original_layer_count'],25)
        self.assertEqual(manifest['candidate_count'],0)
        self.assertEqual(manifest['planned_line_count'],10)
        self.assertEqual(sum(d['reason']=='2d-rectangles-found' for d in manifest['section_diagnostics']),10)
        self.assertEqual(manifest['rectangle_constraints_mm'],
            {'minimum_width':.25,'maximum_width':.45,'minimum_height':.05,'maximum_height':.18})
        self.assertFalse(manifest['printable_authorized'])
        self.assertFalse(manifest['shape_improvement_verified'])
        for row in manifest['candidate_segments']:
            x,y,z = row['start_mm']
            self.assertLessEqual(z,float(slope)*(y-row['width_mm']/2)+float(intercept)+1e-9)
            self.assertTrue(.25 <= row['width_mm'] <= .45)
            self.assertTrue(.05 <= row['height_mm'] <= .18)
        commands = {l.split()[0] for l in content.decode().splitlines() if l and not l.startswith(';')}
        self.assertLessEqual(commands,{'G21','G90','M83','G92','G1'})


if __name__ == '__main__':
    unittest.main()
