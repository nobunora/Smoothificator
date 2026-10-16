"""Independent exact rectangle-union fixtures for the internal metric sweep."""
from fractions import Fraction as F
from itertools import permutations
import random
import unittest

from adaptive_subedge.engine.support_width import _minimum_supported_width


def rect(t0, t1, v0, v1):
    return tuple(F(x) for x in (t0, t1, v0, v1))


def oracle(rectangles):
    """Small-fixture exact arrangement, independent of the segment-tree algorithm."""
    breaks = sorted({F(0), F(1)} | {x for r in rectangles for x in r[:2]})
    minimum = None
    for left, right in zip(breaks, breaks[1:]):
        active = sorted((v0, v1) for t0, t1, v0, v1 in rectangles if t0 <= left and t1 >= right)
        longest = F(0)
        if active:
            start, end = active[0]
            for lower, upper in active[1:]:
                if lower <= end:
                    end = max(end, upper)
                else:
                    longest = max(longest, end - start)
                    start, end = lower, upper
            longest = max(longest, end - start)
        minimum = longest if minimum is None else min(minimum, longest)
    return minimum


class SupportWidthTests(unittest.TestCase):
    def width(self, rectangles):
        return _minimum_supported_width(tuple(rectangles), lambda: None)

    def test_empty_full_and_exact_rational_width(self):
        self.assertEqual(self.width(()), 0)
        self.assertEqual(self.width((rect(0, 1, -1, 1),)), 2)
        self.assertEqual(self.width((rect(0, 1, F(-1, 3), F(1, 7)),)), F(10, 21))

    def test_disconnected_equal_area_different_contiguous_width(self):
        central = (rect(0, 1, F(-1, 4), F(1, 4)),)
        split = (rect(0, 1, F(-1, 2), F(-1, 4)), rect(0, 1, F(1, 4), F(1, 2)))
        self.assertEqual(sum((r[1]-r[0]) * (r[3]-r[2]) for r in central), F(1, 2))
        self.assertEqual(sum((r[1]-r[0]) * (r[3]-r[2]) for r in split), F(1, 2))
        self.assertEqual(self.width(central), F(1, 2))
        self.assertEqual(self.width(split), F(1, 4))

    def test_touching_lateral_intervals_merge_without_double_counting_overlap(self):
        self.assertEqual(self.width((rect(0, 1, -1, 0), rect(0, 1, 0, 1))), 2)
        self.assertEqual(self.width((rect(0, 1, -1, F(1, 2)), rect(0, 1, 0, 1))), 2)
        self.assertEqual(self.width((rect(0, 1, -1, 1), rect(0, 1, -1, 1))), 2)

    def test_nested_coverage_count_survives_removal_of_one_cover(self):
        rectangles = (rect(0, 1, 0, 2), rect(0, F(1, 3), 0, 2),
                      rect(F(1, 3), F(2, 3), F(1, 2), F(3, 2)))
        self.assertEqual(self.width(rectangles), 2)

    def test_coincident_longitudinal_events_do_not_create_fake_gap(self):
        rectangles = (rect(0, F(1, 2), -1, 0), rect(0, F(1, 2), 0, 1),
                      rect(F(1, 2), 1, -1, 1))
        for order in permutations(rectangles):
            self.assertEqual(self.width(order), 2)

    def test_longitudinal_leading_trailing_and_interior_gaps_are_zero(self):
        for rectangles in ((rect(F(1, 8), 1, -1, 1),),
                           (rect(0, F(7, 8), -1, 1),),
                           (rect(0, F(7, 16), -1, 1), rect(F(9, 16), 1, -1, 1))):
            self.assertEqual(self.width(rectangles), 0)

    def test_arbitrarily_thin_strip_controls_minimum_not_average(self):
        epsilon = F(1, 10**100)
        rectangles = (rect(0, F(1, 2), -1, 1), rect(F(1, 2), F(1, 2)+epsilon, 0, F(1, 10)),
                      rect(F(1, 2)+epsilon, 1, -1, 1))
        self.assertEqual(self.width(rectangles), F(1, 10))

    def test_reversal_mirroring_translation_and_permutation_invariance(self):
        rectangles = (rect(0, 1, -1, F(-1, 2)), rect(0, F(1, 2), F(-1, 2), 1),
                      rect(F(1, 2), 1, F(-1, 2), 0))
        expected = F(1)
        self.assertEqual(self.width(rectangles), expected)
        reversed_t = tuple((1-b, 1-a, c, d) for a, b, c, d in rectangles)
        mirrored_v = tuple((a, b, -d, -c) for a, b, c, d in rectangles)
        translated = tuple((a, b, c+F(17, 3), d+F(17, 3)) for a, b, c, d in rectangles)
        for variant in (reversed_t, mirrored_v, translated, tuple(reversed(rectangles))):
            self.assertEqual(self.width(variant), expected)

    def test_batched_events_call_cancellation_once_each_including_domain_ends(self):
        rectangles = (rect(0, F(1, 2), 0, 1), rect(F(1, 2), 1, 0, 1), rect(0, 1, 1, 2))
        calls = []
        self.assertEqual(_minimum_supported_width(rectangles, lambda: calls.append(True)), 2)
        self.assertEqual(len(calls), 3)
        calls.clear()
        self.assertEqual(_minimum_supported_width((), lambda: calls.append(True)), 0)
        self.assertEqual(len(calls), 2)

    def test_cancellation_exception_propagates_before_first_or_middle_event(self):
        class Cancelled(Exception):
            pass
        for stop in (1, 2, 3):
            calls = 0
            def check():
                nonlocal calls
                calls += 1
                if calls == stop:
                    raise Cancelled("cancel")
            rectangles = (rect(0, F(1, 2), 0, 1), rect(F(1, 2), 1, 0, 1))
            with self.assertRaises(Cancelled):
                _minimum_supported_width(rectangles, check)
            self.assertEqual(calls, stop)

    def test_deterministic_small_arrangements_match_independent_oracle(self):
        rng = random.Random(581)
        for _ in range(80):
            rectangles = []
            for _ in range(rng.randrange(1, 18)):
                t0, t1 = sorted(rng.sample(range(9), 2))
                v0, v1 = sorted(rng.sample(range(-8, 9), 2))
                rectangles.append(rect(F(t0, 8), F(t1, 8), F(v0, 8), F(v1, 8)))
            rectangles = tuple(rectangles)
            self.assertEqual(self.width(rectangles), oracle(rectangles))


if __name__ == "__main__":
    unittest.main()
