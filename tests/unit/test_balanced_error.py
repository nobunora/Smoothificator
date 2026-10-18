"""Balanced over/under error, exact interval packing and numerical fixture QA."""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import math
import unittest

from tools.optimize_top_error import (
    ROOT, Proposal, bead_top, source_grid, metrics, apply_proposals, best_nonoverlapping, search,
)
from tools.build_balanced_error_review import build
from tools.audit_layered_preview_overlap import source_segments


class BalancedErrorTests(unittest.TestCase):
    def test_stadium_top_has_real_thickness_and_round_sides(self):
        self.assertEqual(bead_top(0,.4,.2,1),1)
        self.assertAlmostEqual(bead_top(.2,.4,.2,1),.9)
        self.assertEqual(bead_top(.201,.4,.2,1),-math.inf)

    def test_excess_is_penalized_equally_to_shortage(self):
        report = metrics([[.9,1.1]],[0],0,1)
        self.assertAlmostEqual(report['mean_absolute_vertical_mm'],.1)
        self.assertAlmostEqual(report['mean_shortage_mm'],.05)
        self.assertAlmostEqual(report['mean_excess_mm'],.05)

    def test_interval_solver_can_prefer_two_lines_over_one_greedy_wide_line(self):
        def p(y,w,gain):
            return Proposal('0',F(y),F(w),F('.05'),F(0),F('.05'),gain)
        chosen = best_nonoverlapping([p(1,2,10),p('.5',1,6),p('1.5',1,6)])
        self.assertEqual(len(chosen),2)
        self.assertEqual(sum(p.gain for p in chosen),12)

    def test_source_raster_matches_horizontal_nominal_bead(self):
        xs,ys,grid = source_grid(((1.,0.,0.,2.,0.,1.,1),),{1:('wall',F('.2'))},
                                (F(0),F(2),F('-.4'),F('.4')),2,2)
        self.assertTrue(all(z==1 for row in grid for z in row))
        with self.assertRaisesRegex(ValueError,'unevaluable'):
            apply_proposals([[None]],[1],[0],[Proposal('0',F(0),F(1),F('.1'),F(0),F(1),0)],F(0),F(2))

    def test_synthetic_error_optimizer_uses_midpoint_and_reduces_error(self):
        bounds = tuple(map(F,(0,2,0,2)))
        xs = [(i+.5)/4 for i in range(8)]
        ys = [(j+.5)/40 for j in range(80)]
        grid = [[0.]*8 for y in ys]
        groups = [{'rectangle_exact_mm':['.5','1','0','.05']}]
        chosen,uniform,count = search(grid,xs,ys,bounds,F('.1'),F(0),groups,F('.18'))
        before = metrics(grid,ys,F('.1'),F(0))
        after = metrics(apply_proposals(grid,xs,ys,chosen,F('.3'),F('1.7')),ys,F('.1'),F(0))
        self.assertLess(after['mean_absolute_vertical_mm'],before['mean_absolute_vertical_mm'])
        self.assertGreater(count,0)
        for p in chosen:
            self.assertLessEqual(abs(p.z-F('.1')*p.y),p.height/10)
            self.assertLessEqual(abs(p.fraction),F('.1'))

    def test_actual_balanced_hypotheses_preserve_baseline_and_midpoint_limits(self):
        folder = ROOT/'artifacts/cuboid-tilt10-review'
        path = folder/'balanced-error-optimization.json'
        if not path.is_file():
            self.skipTest('local actual model not distributed')
        report = json.loads(path.read_text())
        self.assertTrue(report['validation_improves_previous'])
        new = report['validation_comparison']['optimized_balanced']['mean_absolute_vertical_mm']
        old = report['validation_comparison']['previous_inscribed']['mean_absolute_vertical_mm']
        self.assertLess(new,old)
        self.assertEqual(report['chosen_line_count'],20)
        self.assertGreater(max(F(p['height_exact_mm']) for p in report['selected']),F('.05'))
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        content,manifest = build(source,project,report)
        before = source_segments(source,expected_sha256=report['source_slice_sha256'])
        after = source_segments(content.encode(),expected_sha256=hashlib.sha256(content.encode()).hexdigest())
        self.assertEqual(len(after),len(before)+20)
        self.assertFalse(Counter(r[:6] for r in before)-Counter(r[:6] for r in after))
        self.assertFalse(manifest['printable_authorized'])
        self.assertFalse(manifest['global_continuous_minimum_proven'])
        self.assertFalse(manifest['shape_improvement_verified'])
        self.assertIn('BALANCED',content)
        with self.assertRaisesRegex(ValueError,'source-bound'):
            build(source+b'x',project,report)


if __name__=='__main__':
    unittest.main()
