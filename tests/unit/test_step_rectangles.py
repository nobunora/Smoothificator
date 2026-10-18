"""Constraint and optimality witnesses for the exact 2D research solver."""
from fractions import Fraction as F
import unittest
from tools.solve_step_rectangles import (
    Section, Rectangle, largest_rectangle, fill_section,
    split_line_intervals, largest_tiled_rectangle, fill_tiled_section,
)


class StepRectangleTests(unittest.TestCase):
    def test_wide_rectangle_is_tiled_with_adjusted_equal_widths(self):
        intervals = split_line_intervals(Rectangle(F(2),F(3),F(0),F('.1')),
            minimum_width=F('.25'),maximum_width=F('.45'))
        self.assertEqual(len(intervals),3)
        self.assertEqual(intervals[0][0],2)
        self.assertEqual(intervals[-1][1],3)
        self.assertEqual(sum((b-a for a,b in intervals),F(0)),1)
        self.assertTrue(all(b-a==F(1,3) for a,b in intervals))
        self.assertTrue(all(a[1]==b[0] for a,b in zip(intervals,intervals[1:])))

    def test_tiling_boundaries_and_untileable_gap(self):
        for span,count in (('.45',1),('.50',2),('.90',2)):
            intervals = split_line_intervals(Rectangle(F(0),F(span),F(0),F('.05')),
                minimum_width=F('.25'),maximum_width=F('.45'))
            self.assertEqual(len(intervals),count)
            self.assertTrue(all(F('.25')<=b-a<=F('.45') for a,b in intervals))
        self.assertEqual(split_line_intervals(Rectangle(F(0),F('.46'),F(0),F('.05')),
            minimum_width=F('.25'),maximum_width=F('.45')),())

    def test_rectangle_optimizer_avoids_untileable_total_width(self):
        rectangle = largest_tiled_rectangle(Section(F(0),F('.95'),F(0),F(1),F(0)),
            minimum_line_width=F('.25'),maximum_line_width=F('.45'),
            minimum_height=F('.05'),maximum_height=F(1))
        self.assertEqual(rectangle.right-rectangle.left,F('.5'))
        self.assertEqual(rectangle.area,F('.225'))

    def test_line_width_limit_does_not_cap_logical_rectangle(self):
        rectangles,_ = fill_tiled_section(Section(F(0),F(2),F(0),F('.1'),F(0)),
            minimum_line_width=F('.25'),maximum_line_width=F('.45'),
            minimum_height=F('.05'),maximum_height=F('.18'))
        self.assertEqual(rectangles[0].right-rectangles[0].left,1)
        for r in rectangles:
            intervals = split_line_intervals(r,minimum_width=F('.25'),maximum_width=F('.45'))
            self.assertTrue(intervals)
            self.assertEqual(intervals[0][0],r.left)
            self.assertEqual(intervals[-1][1],r.right)

    def test_triangle_has_analytic_maximum_at_half_width(self):
        section = Section(F(0),F(4),F(0),F(1),F(0))
        r = largest_rectangle(section,minimum_width=F('.1'),minimum_height=F('.1'),maximum_height=F(10))
        self.assertEqual((r.left,r.right,r.top,r.area),(F(2),F(4),F(2),F(4)))

    def test_height_cap_and_minimum_width_change_optimum(self):
        section = Section(F(0),F(4),F(0),F(1),F(0))
        r = largest_rectangle(section,minimum_width=F('.1'),minimum_height=F('.1'),maximum_height=F(1))
        self.assertEqual((r.left,r.right,r.top),(F(1),F(4),F(1)))
        r = largest_rectangle(section,minimum_width=F(3),minimum_height=F('.1'),maximum_height=F(10))
        self.assertEqual((r.left,r.right,r.top),(F(1),F(4),F(1)))

    def test_thin_terrace_has_no_solution_despite_positive_residual(self):
        # 0.1-mm highest residual at slope 0.18: 0.34*0.18+0.08 > 0.1.
        self.assertIsNone(largest_rectangle(Section(F(0),F('5/9'),F(0),F('.18'),F(0)),
            minimum_width=F('.34'),minimum_height=F('.08'),maximum_height=F('.32')))

    def test_maximum_width_is_part_of_optimization(self):
        r = largest_rectangle(Section(F(0),F(4),F(0),F(1),F(0)),
            minimum_width=F('.25'),maximum_width=F('.45'),
            minimum_height=F('.05'),maximum_height=F(10))
        self.assertEqual((r.left,r.right,r.top),(F('3.55'),F(4),F('3.55')))
        with self.assertRaises(ValueError):
            largest_rectangle(Section(F(0),F(4),F(0),F(1),F(0)),
                minimum_width=F('.25'),maximum_width=F('.24'),
                minimum_height=F('.05'),maximum_height=F('.18'))

    def test_new_dimensions_make_previously_infeasible_step_feasible(self):
        r = largest_rectangle(Section(F(0),F('5/9'),F(0),F('.18'),F(0)),
            minimum_width=F('.25'),maximum_width=F('.45'),
            minimum_height=F('.05'),maximum_height=F('.18'))
        self.assertIsNotNone(r)
        self.assertTrue(F('.25') <= r.right-r.left <= F('.45'))
        self.assertTrue(F('.05') <= r.top-r.bottom <= F('.18'))
        self.assertLessEqual(r.top,F('.18')*r.left)

    def test_every_insertion_respects_maximum_width(self):
        rectangles,_ = fill_section(Section(F(0),F(4),F(0),F(1),F(0)),
            minimum_width=F('.25'),maximum_width=F('.45'),
            minimum_height=F('.05'),maximum_height=F('.18'))
        self.assertGreater(len(rectangles),1)
        self.assertTrue(all(F('.25') <= r.right-r.left <= F('.45') and
            F('.05') <= r.top-r.bottom <= F('.18') for r in rectangles))

    def test_closed_boundary_minimum_dimensions_are_accepted(self):
        r = largest_rectangle(Section(F(0),F(1),F(0),F(1),F(0)),
            minimum_width=F('.34'),minimum_height=F('.66'),maximum_height=F('.66'))
        self.assertEqual((r.right-r.left,r.top-r.bottom),(F('.34'),F('.66')))

    def test_multiple_insertions_rest_on_updated_floor_without_exceeding_plane(self):
        section = Section(F(0),F(4),F(0),F(1),F(0))
        rectangles,residual = fill_section(section,minimum_width=F('.25'),
            minimum_height=F('.25'),maximum_height=F('.5'))
        self.assertGreater(len(rectangles),1)
        for i,r in enumerate(rectangles):
            self.assertLessEqual(r.top,section.slope*r.left+section.intercept)
            self.assertGreaterEqual(r.right-r.left,F('.25'))
            self.assertTrue(F('.25') <= r.top-r.bottom <= F('.5'))
            support = [p for p in rectangles[:i] if p.top==r.bottom and p.left<=r.left and p.right>=r.right]
            self.assertTrue(r.bottom==section.bottom or support)
        self.assertTrue(all(largest_rectangle(s,minimum_width=F('.25'),
            minimum_height=F('.25'),maximum_height=F('.5')) is None for s in residual))

    def test_invalid_constraints_are_rejected(self):
        with self.assertRaises(ValueError):
            largest_rectangle(Section(F(0),F(1),F(0),F(0),F(1)),
                minimum_width=F('.3'),minimum_height=F('.2'),maximum_height=F('.1'))


if __name__ == '__main__':
    unittest.main()
