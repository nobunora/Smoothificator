"""Bounded ADR-0044 support ratio value-model regressions (not physical support)."""
from dataclasses import FrozenInstanceError
from dataclasses import replace
import math
import unittest

from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.metrics import SupportCoverageMetrics


class CoverageValueBoundaryTests(unittest.TestCase):
    def test_closed_fraction_endpoints_and_frozen_instance(self):
        for ratio in (0.0, 1.0):
            with self.subTest(ratio=ratio):
                point = SupportCoverageMetrics("coverage-v1", ratio, ratio)
                self.assertEqual((point.required_coverage_ratio, point.measured_coverage_ratio),
                                 (ratio, ratio))
                with self.assertRaises(FrozenInstanceError):
                    point.measured_coverage_ratio = 0.5

    def test_out_of_range_nonfinite_and_nonnumeric_ratios_reject_typed(self):
        for wrong in (-0.00001, 1.00001, float("nan"), float("inf"), float("-inf"),
                      10 ** 400, True, "0.5", [0.5], None):
            with self.subTest(wrong=repr(wrong)):
                for field in ("required_coverage_ratio", "measured_coverage_ratio"):
                    args = {"version": "coverage-v1", "required_coverage_ratio": 0.4,
                            "measured_coverage_ratio": 0.8}
                    args[field] = wrong
                    with self.assertRaises(ContractError) as caught:
                        SupportCoverageMetrics(**args)
                    self.assertEqual(caught.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_version_type_and_semantic_normalization(self):
        class StringSubclass(str):
            pass
        for wrong in (StringSubclass("coverage-v1"), [], {"version": 1}, 0):
            with self.subTest(version=repr(wrong)), self.assertRaises(ContractError):
                SupportCoverageMetrics(wrong, 0.5, 0.75)
        literal_float = SupportCoverageMetrics("coverage-v1", 0.0, 1.0)
        literal_int = SupportCoverageMetrics("coverage-v1", 0, 1)
        self.assertEqual(canonical_bytes(semantic_tree(literal_float)),
                         canonical_bytes(semantic_tree(literal_int)))
        self.assertNotEqual(canonical_bytes(semantic_tree(literal_float)),
                            canonical_bytes(semantic_tree(replace(literal_float,
                                                                  measured_coverage_ratio=0.9))))


if __name__ == "__main__":
    unittest.main()
