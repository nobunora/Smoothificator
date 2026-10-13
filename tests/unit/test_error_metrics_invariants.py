"""SPECIFICATION §16 / ADR-0050: summary error bounds, not an estimator."""
from dataclasses import FrozenInstanceError, replace
import unittest

from adaptive_subedge.application.hashing import create_plan
from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.metrics import ErrorMetrics
from tests.unit.test_canonical import plan_content


class ErrorMetricsInvariantTests(unittest.TestCase):
    def test_directional_summary_bounds_are_valid_at_equality_and_zero(self):
        for maximum, rms, percentile in (
            (0.0, 0.0, 0.0), (0.02, 0.02, 0.02),
            (0.05, 0.02, 0.04), (0.04, 0.0, 0.04)):
            with self.subTest(maximum=maximum, rms=rms, percentile=percentile):
                item = ErrorMetrics(maximum, rms, percentile, 0.0)
                self.assertEqual(item.e_max_mm, maximum)
                with self.assertRaises(FrozenInstanceError):
                    item.e_max_mm = 0.5

    def test_rms_above_directional_maximum_rejects_typed(self):
        with self.assertRaises(ContractError) as caught:
            ErrorMetrics(0.02, 0.021, 0.01, 0.0)
        self.assertEqual(caught.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_percentile_above_directional_maximum_rejects_typed(self):
        with self.assertRaises(ContractError) as caught:
            ErrorMetrics(0.02, 0.01, 0.021, 0.0)
        self.assertEqual(caught.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_valid_metric_change_affects_plan_hash_and_bytes(self):
        original = plan_content()
        changed = replace(original, error_metrics=replace(original.error_metrics, e_rms_mm=0.025))
        self.assertNotEqual(canonical_bytes(semantic_tree(original.error_metrics)),
                            canonical_bytes(semantic_tree(changed.error_metrics)))
        self.assertNotEqual(create_plan(original).plan_hash, create_plan(changed).plan_hash)


if __name__ == "__main__":
    unittest.main()
