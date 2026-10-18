"""Real exact-kernel regression tests for continuous parameter coverage."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from tools.audit_continuous_path_contact import (
    ChronologicalSource, ContactPath, ContactPolicy, audit_continuous_path_contact,
)


def source(name='base', order=1, start=('-1', '0'), end=('2', '0'), z='2.2', width='.4'):
    segment = ExactNominalTopSegment(name, (*map(F, start), F(z)), (*map(F, end), F(z)),
                                     F(width), F('.2'), 'structural')
    return ChronologicalSource(segment, order)


def path(points=(('0', '0'), ('1', '0')), bottom='2.2', order=10):
    return ContactPath('candidate', order, tuple(tuple(map(F, p)) for p in points), F(bottom))


def policy(**changes):
    return replace(ContactPolicy(F('.001'), F('.001'), 12, 1023, 100, 100, 100, 4096, 128), **changes)


def audit(candidate=None, sources=None, settings=None, cancelled=lambda: False):
    return audit_continuous_path_contact(candidate or path(), (source(),) if sources is None else sources,
                                         policy=policy() if settings is None else settings, cancelled=cancelled)


class ContinuousPathTests(unittest.TestCase):
    def assert_partition(self, report, segment_count):
        for index in range(segment_count):
            leaves = [piece for piece in report.intervals if piece.segment_index == index]
            self.assertEqual(leaves[0].parameter_start, 0)
            self.assertEqual(leaves[-1].parameter_end, 1)
            for left, right in zip(leaves, leaves[1:]):
                self.assertEqual(left.parameter_end, right.parameter_start)

    def test_flat_axis_aligned_path_exact_bottom_touch_and_closed_interval_cover(self):
        report = audit()
        self.assertEqual(report.state, 'nominal-centerline-contact-proven')
        self.assertTrue(report.nominal_centerline_contact_proven)
        self.assertEqual(report.cells_queried, 1)
        self.assertFalse(report.physical_print_authorized)
        self.assertFalse(report.printable_authorized)
        self.assert_partition(report, 1)
        with self.assertRaises(FrozenInstanceError):
            report.printable_authorized = True

    def test_oblique_line_subdivision_never_uses_off_line_box_gap(self):
        report = audit(path((('0', '0'), ('1', '1'))),
                       (source(start=('-1', '-1'), end=('2', '2'), width='.6'),))
        self.assertEqual(report.state, 'nominal-centerline-contact-proven')
        self.assertGreater(report.cells_queried, 1)
        self.assertEqual(report.gap_intervals, 0)
        self.assert_partition(report, 1)

    def test_polyline_both_original_segments_covered(self):
        report = audit(path((('0', '0'), ('.5', '0'), ('1', '0'))))
        self.assertTrue(report.nominal_centerline_contact_proven)
        self.assert_partition(report, 2)

    def test_supported_endpoints_do_not_hide_midsegment_gap(self):
        supports = (source('left', 1, end=('.4', '0')), source('right', 2, start=('.6', '0')))
        report = audit(sources=supports)
        self.assertEqual(report.state, 'gap-proven')
        self.assertGreater(report.supported_intervals, 0)
        self.assertGreater(report.gap_intervals, 0)
        self.assertGreater(report.unresolved_intervals, 0)
        self.assertFalse(report.nominal_centerline_contact_proven)
        self.assertTrue(any(w.parameter_start > 0 and w.parameter_end < 1 and w.state == 'gap' for w in report.intervals))
        self.assert_partition(report, 1)

    def test_future_and_same_order_sources_excluded_without_z_substitution(self):
        for order in (10, 11):
            report = audit(sources=(source(order=order),))
            self.assertEqual(report.state, 'gap-proven')
            self.assertEqual(report.earlier_source_count, 0)
            self.assertEqual(report.excluded_source_count, 1)
        low = audit(sources=(source(z='2.0'),))
        self.assertEqual(low.state, 'gap-proven')
        self.assertEqual(low.earlier_source_count, 1)
        self.assertEqual(low.intervals[0].top_upper_mm, F('2.0'))

    def test_exact_support_side_boundary_is_unresolved_instead_of_false_gap(self):
        report = audit(path((('0', '.1'), ('1', '.1'))), settings=policy(max_depth=3))
        self.assertEqual(report.state, 'incomplete')
        self.assertEqual(report.gap_intervals, 0)
        self.assertFalse(report.nominal_centerline_contact_proven)

    def test_explicit_query_depth_input_and_kernel_limits_are_incomplete(self):
        diagonal = path((('0', '0'), ('1', '1')))
        supports = (source(start=('-1', '-1'), end=('2', '2'), width='.6'),)
        for settings in (policy(max_depth=0), policy(max_queries=1), policy(max_coordinate_bits=2)):
            report = audit(diagonal, supports, settings)
            self.assertEqual(report.state, 'incomplete')
            self.assertFalse(report.nominal_centerline_contact_proven)
            self.assert_partition(report, 1)
        report = audit(sources=(source('a', 1), source('b', 2)), settings=policy(kernel_max_sources=1))
        self.assertEqual(report.state, 'incomplete')
        self.assertEqual(report.intervals[0].reason, 'kernel-resource-limit')
        report = audit(sources=(source('a', 1), source('b', 2)), settings=policy(max_input_sources=1))
        self.assertEqual(report.cells_queried, 0)
        self.assertEqual(report.state, 'incomplete')
        report = audit(path((('0', '0'), ('.5', '0'), ('1', '0'))), settings=policy(max_path_segments=1))
        self.assertEqual(report.cells_queried, 0)
        self.assert_partition(report, 2)

    def test_cancellation_before_and_during_real_kernel_stays_incomplete(self):
        report = audit(cancelled=lambda: True)
        self.assertEqual(report.state, 'incomplete')
        self.assertEqual(report.cells_queried, 0)
        self.assertTrue(report.cancelled)
        calls = 0
        def cancelled():
            nonlocal calls
            calls += 1
            return calls == 4
        report = audit(cancelled=cancelled)
        self.assertEqual(report.state, 'incomplete')
        self.assertTrue(report.cancelled)
        self.assertFalse(report.nominal_centerline_contact_proven)
        with self.assertRaisesRegex(ValueError, 'exact bool'):
            audit(cancelled=lambda: 1)

    def test_proven_gap_is_retained_with_unresolved_budget_remainder(self):
        report = audit(path((('0', '0'), ('1', '0'), ('2', '0'))), sources=(), settings=policy(max_queries=1))
        self.assertEqual(report.state, 'gap-proven')
        self.assertEqual(report.gap_intervals, 1)
        self.assertEqual(report.unresolved_intervals, 1)
        self.assert_partition(report, 2)

    def test_input_id_order_type_grid_and_policy_validation(self):
        for sources in ([source()], (source('same', 1), source('same', 2)),
                        (source('a', 1), source('b', 1)), (source('candidate', 1),)):
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                audit(sources=sources)
        for changes in ({'padding_mm': F(0)}, {'max_depth': True}, {'max_queries': 0},
                        {'sqrt_fraction_bits': 4097}, {'xy_resolution_mm': .001}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                policy(**changes)
        with self.assertRaises(ValueError):
            path((('0', '0'), ('0', '0')))
        with self.assertRaises(ValueError):
            replace(path(), execution_order=True)
        with self.assertRaises(ValueError):
            ChronologicalSource(source().segment, True)
        with self.assertRaisesRegex(ValueError, 'quantized grid'):
            audit(path((('0', '0'), ('1/3', '0'))))
