"""Analytic optimum, constrained boundaries and actual source retention."""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import unittest

from tools.solve_triangle_rectangle import solve, spill_area, pack, PackedRectangle
from tools.build_triangle_rectangle_review import (
    ROOT, build, line_placement, posed_intersection_area, validate_dimensions, analysis_minimum_height,
    step_base_applicable,
)
from tools.audit_layered_preview_overlap import source_segments


POLICY = dict(minimum_width_mm=F('.25'),maximum_width_mm=F('.45'),
              minimum_height_mm=F('.05'),maximum_height_mm=F('.18'))


class TriangleRectangleTests(unittest.TestCase):
    def test_step_base_gate_is_exact_and_tracks_configured_minimum_width(self):
        self.assertFalse(step_base_applicable(F('.353553390593'),F('.25')))
        self.assertTrue(step_base_applicable(F('.353553390594'),F('.25')))
        self.assertFalse(step_base_applicable(F('.4'),F('.3')))
        self.assertTrue(step_base_applicable(F('.4'),F('.25')))
        with self.assertRaises(ValueError):
            step_base_applicable(F(0),F('.25'))
    def test_configured_dimensions_reject_invalid_policy(self):
        for a,b,h in ((F('.5'),F('.4'),F('.08')),(F(0),F('.45'),F('.08')),
                      (F('.25'),F('.45'),F('.19')),(F('.25'),F('.45'),F(0)),
                      (.25,F('.45'),F('.08'))):
            with self.assertRaises(ValueError):
                validate_dimensions(a,b,h,F('.18'))
        validate_dimensions(F('.25'),F('.45'),F('.08'),F('.18'))

    def test_overlap_zero_aligns_bottom_and_positive_penetrates(self):
        self.assertEqual(line_placement(F(3),F('.1'),F(0)),(F(3),F('3.1')))
        self.assertEqual(line_placement(F(3),F('.1'),F(5)),(F('2.995'),F('3.095')))
        self.assertEqual(line_placement(F(3),F('.1'),F(30)),(F('2.97'),F('3.07')))

    def test_overlap_rejects_nonexact_and_out_of_range_values(self):
        for overlap in (F('30.001'),F('-.001'),float('nan'),5.0,'5'):
            with self.assertRaises(ValueError):
                line_placement(F(3),F('.1'),overlap)
        self.assertEqual(line_placement(F(3),F('.05'),F(10))[0],F('2.995'))

    def test_analysis_minimum_compensates_effective_height_and_rejects_excess(self):
        h = analysis_minimum_height(F('.08'),F(30),F('.18'))
        self.assertEqual(h,F(4,35))
        self.assertEqual(h*F('.7'),F('.08'))
        self.assertGreater(h,F('.08')*F('1.3'))
        self.assertEqual(analysis_minimum_height(F('.08'),F(0),F('.18')),F('.08'))
        with self.assertRaisesRegex(ValueError,'exceeds'):
            analysis_minimum_height(F('.13'),F(30),F('.18'))
        self.assertEqual(analysis_minimum_height(F('.126'),F(30),F('.18')),F('.18'))

    def test_overlap_metrics_count_below_floor_spill(self):
        r = PackedRectangle(F('.5'),F(1),F('.1'),F(0))
        self.assertEqual(posed_intersection_area(F(1),F('.2'),r,F(0)),F('.05'))
        self.assertEqual(posed_intersection_area(F(1),F('.2'),r,F('-.01')),F('.045'))
        self.assertEqual(posed_intersection_area(F(1),F('.2'),r,F('-.2')),0)

    def test_unconstrained_analytic_optimum_and_exact_tiling(self):
        r = solve(F('1.134'),F('.2'),**POLICY)
        self.assertEqual(r.width_mm,F('.756'))
        self.assertEqual(r.height_mm,F(2,15))
        self.assertEqual(r.line_count,2)
        self.assertEqual(r.width_mm/r.line_count,F('.378'))
        self.assertEqual(r.spill_area_mm2/(r.width_mm*r.height_mm),F(1,8))
        self.assertEqual(r.error_area_mm2,F('1.134')*F('.2')/6)

    def test_height_cap_and_untileable_width_gap(self):
        r = solve(F(1),F('.2'),**dict(POLICY,maximum_height_mm=F('.08')))
        self.assertEqual(r.height_mm,F('.08'))
        self.assertEqual(r.width_mm,F('.8'))
        r = solve(F('.7'),F('.2'),**POLICY)
        # Unconstrained width 7/15 falls in the .45-to-.50 tiling gap.
        self.assertTrue(r.width_mm<=F('.45') or r.width_mm>=F('.50'))

    def test_solver_beats_independent_constrained_grid(self):
        for base,rise in ((F('.7'),F('.2')),(F('1.1'),F('.1'))):
            r = solve(base,rise,**POLICY)
            for k in range(25,int(base*100)+1):
                w = F(k,100)
                if not any(n*F('.25')<=w<=n*F('.45') for n in range(1,6)):
                    continue
                for j in range(50,int(min(rise,F('.18'))*1000)+1,5):
                    h = F(j,1000)
                    # Independent trapezoid integration split at the crossing.
                    a = base-w
                    cut = max(a,min(base,h*base/rise))
                    overlap = (rise/base)*(cut*cut-a*a)/2+h*(base-cut)
                    error = base*rise/2+w*h-2*overlap
                    self.assertLessEqual(r.error_area_mm2,error)

    def test_per_line_spill_is_not_confused_with_logical_spill(self):
        base,rise = F('1.134'),F('.2')
        r = solve(base,rise,**POLICY)
        a,w,h = base-r.width_mm,r.width_mm/2,r.height_mm
        self.assertEqual(spill_area(base,rise,a,a+w,h)/(w*h),F(1,4))
        self.assertEqual(spill_area(base,rise,a+w,base,h),0)

    def test_invalid_or_infeasible_dimensions(self):
        for base in (0,F(0),F(-1)):
            with self.assertRaises(ValueError):
                solve(base,F('.2'),**POLICY)
        self.assertIsNone(solve(F('.24'),F('.2'),**POLICY))
        self.assertIsNone(solve(F(1),F('.04'),**POLICY))

    def test_multiple_rectangles_beat_single_and_can_repeat_dimensions(self):
        policy = dict(minimum_width_mm=F('.25'),maximum_width_mm=F('.25'),
                      minimum_height_mm=F('.05'),maximum_height_mm=F('.18'))
        p = pack(F(1),F('.2'),grid_divisions=80,**policy)
        r = solve(F(1),F('.2'),**policy)
        self.assertGreater(len(p.rectangles),1)
        self.assertLess(p.error_area_mm2,r.error_area_mm2)
        self.assertTrue(all(r.right_mm-r.left_mm==F('.25') for r in p.rectangles))
        # Height saturation allows identical rectangles, with no uniqueness gate.
        saturated = pack(F(1),F('.2'),grid_divisions=80,
            **dict(policy,minimum_height_mm=F('.1'),maximum_height_mm=F('.1')))
        self.assertGreater(len(saturated.rectangles),1)
        self.assertEqual(len({(r.right_mm-r.left_mm,r.height_mm) for r in saturated.rectangles}),1)

    def test_packing_matches_exhaustive_small_lattice_with_gaps(self):
        policy = dict(minimum_width_mm=F('.2'),maximum_width_mm=F('.4'),
                      minimum_height_mm=F('.05'),maximum_height_mm=F('.18'))
        p = pack(F(1),F('.2'),grid_divisions=10,**policy)
        # Independent exhaustive enumeration of every disjoint interval set.
        def enumerate_gain(start):
            best = F(0)
            for a in range(start,10):
                for cells in range(2,5):
                    b = a+cells
                    if b>10:
                        continue
                    height = min(F('.18'),max(F('.05'),F(a+b,100)))
                    lo,hi = F(a,10),F(b,10)
                    cut = max(lo,min(hi,height/F('.2')))
                    overlap = F('.1')*(cut*cut-lo*lo)+height*(hi-cut)
                    area = (hi-lo)*height
                    if 2*overlap>=area:
                        best = max(best,2*overlap-area+enumerate_gain(b))
            return best
        self.assertEqual(p.error_area_mm2,F('.1')-enumerate_gain(0))
        refined = pack(F(1),F('.2'),grid_divisions=20,**policy)
        self.assertLessEqual(refined.error_area_mm2,p.error_area_mm2)

    def test_actual_adjacent_layer_triangles_preserve_every_original_segment(self):
        folder = ROOT/'artifacts/cuboid-tilt10-review'
        if not (folder/'original-slice/plate_1.gcode').is_file():
            self.skipTest('local actual fixture not distributed')
        source = (folder/'original-slice/plate_1.gcode').read_bytes()
        project = (folder/'original-slice/sliced.3mf').read_bytes()
        pinned = json.loads((folder/'current-review.json').read_text())
        hashes = dict(expected_source_sha256=pinned['source_slice_sha256'],
                      expected_project_sha256=pinned['placed_project_sha256'])
        content,manifest = build(source,project,**hashes)
        self.assertEqual(manifest['rectangle_constraints_exact_mm'],
            dict(minimum_width='1/4',maximum_width='9/20',minimum_height='2/25',
                 analysis_minimum_height='2/25',maximum_height='9/50'))
        self.assertGreater(manifest['candidate_count'],20)
        self.assertEqual(len(manifest['section_diagnostics']),10)
        for step in manifest['section_diagnostics']:
            self.assertEqual(step['status'],'UNVERIFIED_VIEW_ONLY')
            self.assertEqual(F(step['triangle_height_exact_mm']),F('.2'))
            self.assertTrue(step['lattice_optimum_proven'])
            self.assertFalse(step['continuous_position_optimum_proven'])
            self.assertLessEqual(F(step['error_area_exact_mm2']),F(step['coarse_error_area_exact_mm2']))
            for a,b,lower,top in step['rectangles_exact_mm']:
                self.assertTrue(F('.25')<=F(b)-F(a)<=F('.45'))
                self.assertTrue(F('.08')<=F(top)-F(lower)<=F('.18'))
            self.assertTrue(all(F(v)<=F(1,2) for v in step['individual_spill_fractions_exact']))
        before = source_segments(source,expected_sha256=hashes['expected_source_sha256'])
        after = source_segments(content.encode(),expected_sha256=hashlib.sha256(content.encode()).hexdigest())
        self.assertEqual(len(after),len(before)+manifest['candidate_count'])
        self.assertFalse(Counter(r[:6] for r in before)-Counter(r[:6] for r in after))
        self.assertFalse(manifest['printable_authorized'])
        self.assertFalse(manifest['continuous_contact_verified'])
        self.assertFalse(manifest['original_target_mesh_alignment_certified'])
        for candidate in manifest['candidate_segments']:
            self.assertTrue(candidate['bottom_matches_layer_top'])
            self.assertEqual(candidate['bottom_z_exact_mm'],candidate['layer_top_z_exact_mm'])
            self.assertEqual(candidate['z_adjustment_exact_mm'],'0')
        shifted_content,shifted = build(source,project,overlap_percent=F(30),**hashes)
        self.assertIn('Contact overlap percent: 30',shifted_content)
        self.assertGreater(shifted['candidate_count'],0)
        for candidate in shifted['candidate_segments']:
            h = F(candidate['top_z_exact_mm'])-F(candidate['bottom_z_exact_mm'])
            floor = F(candidate['layer_top_z_exact_mm'])
            self.assertGreaterEqual(h,F(4,35))
            self.assertEqual(F(candidate['bottom_z_exact_mm']),floor-h*F('.3'))
            self.assertGreaterEqual(F(candidate['remaining_height_above_layer_exact_mm']),F('.08'))
            self.assertEqual(F(candidate['top_z_exact_mm'])-floor,h*F('.7'))
            self.assertFalse(candidate['continuous_contact_verified'])
        for step in shifted['section_diagnostics']:
            self.assertFalse(step['posed_lattice_optimum_proven'])
            self.assertTrue(all(F(f)<=F(1,2) for f in step['posed_individual_spill_fractions_exact']))
        _,custom = build(source,project,minimum_width_mm=F('.30'),maximum_width_mm=F('.40'),
            minimum_height_mm=F('.10'),**hashes)
        self.assertGreater(custom['candidate_count'],0)
        for step in custom['section_diagnostics']:
            for a,b,lower,top in step['rectangles_exact_mm']:
                self.assertTrue(F('.30')<=F(b)-F(a)<=F('.40'))
                self.assertTrue(F('.10')<=F(top)-F(lower)<=F('.18'))
        with self.assertRaisesRegex(ValueError,'pinned'):
            build(source+b'x',project,**hashes)


if __name__ == '__main__':
    unittest.main()
