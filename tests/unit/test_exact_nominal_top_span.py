"""Whole-span exact bounds, not acceptance from separate endpoint samples."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.engine.support_cell import query_exact_nominal_top_span
from tests.unit.test_continuous_path_contact import audit, path, policy, source


def query(start=(F(0), F(0)), end=(F(1), F(0)), sources=None, **options):
    settings = dict(max_sources=100, max_coordinate_bits=4096, sqrt_fraction_bits=128, cancelled=lambda: False)
    settings.update(options)
    return query_exact_nominal_top_span(start, end, (source().segment,) if sources is None else sources, **settings)


class ExactNominalTopSpanTests(unittest.TestCase):
    def test_covered_oblique_span_gets_whole_span_reason(self):
        support = source(start=('-1', '-1'), end=('2', '2')).segment
        result = query((F(0), F(0)), (F(1), F(1)), (support,))
        self.assertEqual(result.state, 'full-bounded')
        self.assertEqual(result.reason, 'one-segment-covers-span')
        self.assertEqual(result.top_z_lower_mm, F('2.2'))

    def test_different_endpoint_supports_cannot_certify_gap_between_them(self):
        supports = (source('left', 1, end=('.4', '0')).segment,
                    source('right', 2, start=('.6', '0')).segment)
        result = query(sources=supports)
        self.assertEqual(result.state, 'unresolved-partial')
        self.assertIsNone(result.top_z_lower_mm)
        self.assertEqual(result.top_z_upper_mm, F('2.2'))

    def test_partial_span_varying_z_and_rounded_lateral_profile(self):
        partial = query((F(-2), F(0)), (F(0), F(0)))
        self.assertEqual(partial.state, 'unresolved-partial')
        varying = replace(source(start=('0', '0'), end=('1', '0'), z='2').segment,
                          end_xyz_mm=(F(1), F(0), F('2.4')))
        result = query((F('.25'), F(0)), (F('.75'), F(0)), (varying,))
        self.assertEqual((result.top_z_lower_mm, result.top_z_upper_mm), (F('2.1'), F('2.3')))
        rounded = query((F(0), F('.15')), (F(1), F('.15')))
        self.assertEqual(rounded.state, 'full-bounded')
        self.assertLessEqual((rounded.top_z_lower_mm-F('2.1'))**2, F(3, 400))
        self.assertGreaterEqual((rounded.top_z_upper_mm-F('2.1'))**2, F(3, 400))

    def test_degenerate_nonexact_duplicate_resources_and_cancellation(self):
        for start, end in (((F(0), F(0)), (F(0), F(0))),
                           ((0, F(0)), (F(1), F(0))), ([F(0), F(0)], (F(1), F(0))),
                           ((F(0),), (F(1), F(0)))):
            with self.subTest(start=start, end=end), self.assertRaises(ContractError):
                query(start, end)
        with self.assertRaises(ContractError):
            query(sources=(source().segment, source().segment))
        for settings in ({'max_coordinate_bits': 1}, {'max_sources': 1}, {'cancelled': lambda: True}):
            supports = (source('a').segment, source('b').segment) if 'max_sources' in settings else None
            self.assertEqual(query(sources=supports, **settings).state, 'incomplete')
        with self.assertRaises(ContractError):
            query(cancelled=lambda: 1)

    def test_tool_span_mode_oblique_query_provenance_and_old_default_unchanged(self):
        candidate = path((('0', '0'), ('1', '1')))
        supports = (source(start=('-1', '-1'), end=('2', '2')),)
        old = audit(candidate, supports)
        exact = audit(candidate, supports, policy(query_geometry_mode='exact-span'))
        self.assertTrue(old.nominal_centerline_contact_proven)
        self.assertTrue(exact.nominal_centerline_contact_proven)
        self.assertGreater(old.cells_queried, 1)
        self.assertEqual(exact.cells_queried, 0)
        self.assertEqual(exact.spans_queried, 1)
        self.assertEqual(exact.query_count, 1)
        self.assertEqual(exact.queried_spans[0].endpoints_xy_mm, candidate.points_xy_mm)
        self.assertIsNone(exact.intervals[0].enclosing_cell)
        self.assertEqual(exact.intervals[0].queried_span_xy_mm, candidate.points_xy_mm)

    def test_tool_span_partition_gap_future_and_query_budget_remain_explicit(self):
        supports = (source('left', 1, end=('.4', '0')), source('right', 2, start=('.6', '0')))
        report = audit(sources=supports, settings=policy(query_geometry_mode='exact-span'))
        self.assertEqual(report.state, 'gap-proven')
        self.assertGreater(report.gap_intervals, 0)
        self.assertTrue(all(piece.enclosing_cell is None for piece in report.intervals))
        self.assertEqual(report.intervals[0].parameter_start, 0)
        self.assertEqual(report.intervals[-1].parameter_end, 1)
        for a, b in zip(report.intervals, report.intervals[1:]):
            self.assertEqual(a.parameter_end, b.parameter_start)
        limited = audit(sources=supports, settings=policy(query_geometry_mode='exact-span', max_queries=1))
        self.assertEqual(limited.state, 'incomplete')
        self.assertEqual(limited.query_count, 1)
        self.assertEqual(len(limited.queried_spans), 1)
        self.assertEqual(limited.queried_spans[0].parameter_start, 0)
        self.assertEqual(limited.queried_spans[0].parameter_end, 1)
        self.assertTrue(all(piece.queried_span_xy_mm is None for piece in limited.intervals))
        future = audit(sources=(source(order=11),), settings=policy(query_geometry_mode='exact-span'))
        self.assertEqual(future.state, 'gap-proven')
        self.assertEqual(future.excluded_source_count, 1)
        cancelled = audit(settings=policy(query_geometry_mode='exact-span'), cancelled=lambda: True)
        self.assertEqual(cancelled.state, 'incomplete')
        self.assertEqual(cancelled.spans_queried, 0)
