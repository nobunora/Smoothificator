"""Exact finite area against independent polygon clipping and real ring25."""
from fractions import Fraction as F
import json
import unittest

from tools.build_triangle_rectangle_review import ROOT, posed_intersection_area
from tools.solve_triangle_rectangle import (
    PackedRectangle, finite_triangle_rectangle_intersection_area, spill_area,
)


def clipped_polygon_area(base, rise, left, right, bottom, top):
    """Independent Sutherland-Hodgman clipping of the triangle, then shoelace."""
    polygon = [(F(0), F(0)), (base, F(0)), (base, rise)]
    for axis, boundary, direction in ((0, left, 1), (0, right, -1), (1, bottom, 1), (1, top, -1)):
        clipped = []
        for start, end in zip(polygon, polygon[1:]+polygon[:1]):
            start_inside = direction*(start[axis]-boundary) >= 0
            end_inside = direction*(end[axis]-boundary) >= 0
            if start_inside != end_inside:
                t = (boundary-start[axis])/(end[axis]-start[axis])
                clipped.append(tuple(a+t*(b-a) for a, b in zip(start, end)))
            if end_inside:
                clipped.append(end)
        polygon = clipped
    if len(polygon) < 3:
        return F(0)
    return abs(sum(a[0]*b[1]-a[1]*b[0] for a, b in zip(polygon, polygon[1:]+polygon[:1])))/2


def legacy_area(base, rise, left, right, bottom, top):
    def below(height):
        return F(0) if height <= 0 else (right-left)*height-spill_area(base, rise, left, right, height)
    return below(top)-below(bottom)


class FiniteTriangleIntersectionTests(unittest.TestCase):
    def test_each_external_side_is_clipped_to_finite_triangle(self):
        for rectangle, expected in (
                ((-1, 1, 0, 1), F(1, 2)), ((1, 3, 0, 1), F(1)),
                ((0, 2, -1, 1), F(3, 2)), ((0, 2, 1, 3), F(1, 2)),
                ((-1, 3, -1, 3), F(2))):
            with self.subTest(rectangle=rectangle):
                self.assertEqual(finite_triangle_rectangle_intersection_area(F(2), F(2), *map(F, rectangle)), expected)

    def test_disjoint_and_boundary_only_contact_are_exact_zero(self):
        for rectangle in ((-2, -1, 0, 1), (2, 3, 0, 1), (0, 1, -1, 0),
                          (0, 2, 2, 3), (0, 1, 1, 2)):
            with self.subTest(rectangle=rectangle):
                self.assertEqual(finite_triangle_rectangle_intersection_area(F(2), F(2), *map(F, rectangle)), 0)

    def test_legacy_equivalence_when_horizontally_contained(self):
        base, rise = F('1.134'), F('.2')
        for left, right in ((F(0), base), (base/4, 3*base/4), (base/2, base)):
            for bottom, top in ((F(0), F('.1')), (F('-.054'), F('.126')),
                                (F('.05'), F('.4')), (F('-.3'), F('-.1'))):
                self.assertEqual(finite_triangle_rectangle_intersection_area(base, rise, left, right, bottom, top),
                                 legacy_area(base, rise, left, right, bottom, top))

    def test_independent_exact_polygon_clipping_on_external_rational_rectangles(self):
        base, rise = F(7, 5), F(3, 7)
        for left in (F(-1, 3), F(0), F(1, 4), F(6, 5), F(3, 2)):
            for width in (F(1, 5), F(1), F(7, 3)):
                for bottom in (F(-1, 7), F(0), F(1, 7), F(1)):
                    for height in (F(1, 10), F(1, 2)):
                        rectangle = (left, left+width, bottom, bottom+height)
                        actual = finite_triangle_rectangle_intersection_area(base, rise, *rectangle)
                        self.assertEqual(actual, clipped_polygon_area(base, rise, *rectangle))
                        self.assertLessEqual(actual, width*height)
                        self.assertLessEqual(actual, base*rise/2)

    def test_real_ring25_outward_example_old_and_finite_spill(self):
        manifest = json.loads((ROOT/'artifacts/revolved-exponential-review/current-review.json').read_bytes())
        ring = next(r for r in manifest['rings'] if r['id'] == 'ring-25')
        row = next(r for r in manifest['section_diagnostics'] if r['floor_z_exact_mm'] == ring['floor_z_exact_mm'])
        base, rise = F(row['triangle_base_exact_mm']), F(row['triangle_height_exact_mm'])
        width, height, remaining = F(ring['width_exact_mm']), F('.18'), F('.126')
        center = F(ring['radius_exact_mm'])+F('.04')-F(row['left_radius_exact_mm'])
        left, right, bottom = center-width/2, center+width/2, remaining-height
        area = finite_triangle_rectangle_intersection_area(base, rise, left, right, bottom, remaining)
        self.assertEqual(area, clipped_polygon_area(base, rise, left, right, bottom, remaining))
        old_spill = 1-legacy_area(base, rise, left, right, bottom, remaining)/(width*height)
        finite_spill = 1-area/(width*height)
        self.assertEqual(old_spill, F(45253668587, 150685429950))
        self.assertEqual(finite_spill, F(61993776587, 150685429950))
        self.assertLess(finite_spill, F(1, 2))
        self.assertGreater(right, base)
        rectangle = PackedRectangle(left, right, height, F(0))
        self.assertEqual(posed_intersection_area(base, rise, rectangle, bottom), area)

    def test_malformed_or_nonexact_inputs_reject(self):
        valid = (F(2), F(2), F(0), F(1), F(0), F(1))
        for index in range(len(valid)):
            for bad in (0.5, 1, True, '1'):
                args = list(valid)
                args[index] = bad
                with self.subTest(index=index, bad=bad), self.assertRaises(ValueError):
                    finite_triangle_rectangle_intersection_area(*args)
        for args in ((F(0), *valid[1:]), (valid[0], F(-1), *valid[2:]),
                     (*valid[:2], F(1), F(0), *valid[4:]),
                     (*valid[:2], F(1), F(1), *valid[4:]), (*valid[:4], F(1), F(1))):
            with self.assertRaises(ValueError):
                finite_triangle_rectangle_intersection_area(*args)
