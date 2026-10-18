"""Whole-range common-rectangle certificates, never endpoint-only acceptance."""
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
import unittest

from tools.audit_radial_rectangle_spill import bound_radial_rectangle_spill
from tools.solve_triangle_rectangle import finite_triangle_rectangle_intersection_area


def arguments(**changes):
    params = dict(triangle_base_mm=F(1), triangle_rise_mm=F(1), triangle_left_radius_mm=F(0),
        center_radius_lower_mm=F(1, 2), center_radius_upper_mm=F(1, 2),
        width_lower_mm=F(1), width_upper_mm=F(1), bottom_mm=F(0), top_mm=F(1),
        center_bins=8, width_bins=8, max_cells=1000, max_coordinate_bits=4096, cancelled=lambda: False)
    params.update(changes)
    return params


class RadialRectangleSpillTests(unittest.TestCase):
    def test_analytic_partial_full_absent_and_finite_lateral_clip(self):
        half = bound_radial_rectangle_spill(**arguments())
        self.assertEqual(half.spill_upper_bound, F(1, 2))
        self.assertEqual(half.effective_bins, (1, 1))
        full = bound_radial_rectangle_spill(**arguments(center_radius_lower_mm=F(3, 4),
            center_radius_upper_mm=F(3, 4), width_lower_mm=F(1, 2), width_upper_mm=F(1, 2), top_mm=F(1, 4)))
        self.assertEqual(full.spill_upper_bound, F(0))
        absent = bound_radial_rectangle_spill(**arguments(center_radius_lower_mm=F(2), center_radius_upper_mm=F(2)))
        self.assertEqual(absent.spill_upper_bound, F(1))
        clipped = bound_radial_rectangle_spill(**arguments(center_radius_lower_mm=F(1),
            center_radius_upper_mm=F(1), bottom_mm=F(-1), top_mm=F(2)))
        # Integral x dx over [.5,1] is3/8; rectangle area3.
        self.assertEqual(clipped.spill_upper_bound, F(7, 8))
        with self.assertRaises(FrozenInstanceError):
            half.status = 'accepted'

    def test_entire_parameter_cells_dominate_exact_interior_rectangles(self):
        params = arguments(triangle_left_radius_mm=F(2), center_radius_lower_mm=F(9, 4),
            center_radius_upper_mm=F(11, 4), width_lower_mm=F(1, 4), width_upper_mm=F(3, 4),
            bottom_mm=F(-1, 10), top_mm=F(3, 5), center_bins=4, width_bins=4)
        certificate = bound_radial_rectangle_spill(**params)
        self.assertEqual(len(certificate.cells), 16)
        for cell in certificate.cells:
            for t in (F(0), F(1, 3), F(1, 2), F(1)):
                c = cell.center_interval_mm[0]*(1-t)+cell.center_interval_mm[1]*t
                for u in (F(0), F(2, 5), F(1)):
                    w = cell.width_interval_mm[0]*(1-u)+cell.width_interval_mm[1]*u
                    area = finite_triangle_rectangle_intersection_area(F(1), F(1), c-w/2-2,
                        c+w/2-2, params['bottom_mm'], params['top_mm'])
                    spill = 1-area/(w*(params['top_mm']-params['bottom_mm']))
                    self.assertLessEqual(spill, cell.spill_upper_bound)
                    self.assertLessEqual(spill, certificate.spill_upper_bound)
        coarse = bound_radial_rectangle_spill(**dict(params, center_bins=1, width_bins=1))
        fine = bound_radial_rectangle_spill(**dict(params, center_bins=8, width_bins=8))
        self.assertLessEqual(certificate.spill_upper_bound, coarse.spill_upper_bound)
        self.assertLessEqual(fine.spill_upper_bound, certificate.spill_upper_bound)

    def test_empty_common_rectangle_and_resource_incompleteness(self):
        params = arguments(center_radius_lower_mm=F(0), center_radius_upper_mm=F(1),
            width_lower_mm=F(1, 10), width_upper_mm=F(1, 10), center_bins=1)
        self.assertEqual(bound_radial_rectangle_spill(**params).spill_upper_bound, F(1))
        for changes, reason in ((dict(center_bins=4, max_cells=2), 'cell-limit'),
                                (dict(max_coordinate_bits=1), 'coordinate-bit-limit'),
                                (dict(cancelled=lambda: True), 'cancelled')):
            report = bound_radial_rectangle_spill(**dict(params, **changes))
            self.assertEqual(report.status, 'incomplete')
            self.assertEqual(report.reason, reason)
            self.assertIsNone(report.spill_upper_bound)
        calls = []
        def cancel_later():
            calls.append(1)
            return len(calls) == 3
        report = bound_radial_rectangle_spill(**dict(params, center_bins=4, cancelled=cancel_later))
        self.assertEqual(len(report.cells), 1)
        self.assertIsNone(report.spill_upper_bound)

    def test_invalid_exact_inputs_limits_and_cancellation(self):
        for changes in (dict(triangle_base_mm=1), dict(triangle_rise_mm=F(0)),
                dict(triangle_left_radius_mm=F(-1)), dict(center_radius_lower_mm=F(-1)),
                dict(width_lower_mm=F(0)), dict(width_lower_mm=F(2)), dict(top_mm=F(0)),
                dict(center_bins=True), dict(width_bins=0), dict(max_cells=F(1)),
                dict(max_coordinate_bits=0), dict(cancelled=None), dict(cancelled=lambda: 0)):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                bound_radial_rectangle_spill(**arguments(**changes))


if __name__ == '__main__':
    unittest.main()
