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

    def test_signed_mean_larger_than_maximum_in_both_directions_rejected(self):
        for mean in (-0.051, 0.051):
            with self.subTest(mean=mean), self.assertRaises(ContractError) as ctx:
                ErrorMetrics(0.05, 0.03, 0.04, mean)
            self.assertEqual(ctx.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_signed_mean_on_maximum_boundary_is_allowed(self):
        for mean in (-0.05, 0.05):
            with self.subTest(mean=mean):
                outcome = ErrorMetrics(0.05, 0.05, 0.05, mean)
                self.assertEqual(outcome.signed_mean_mm, mean)
        self.assertEqual(ErrorMetrics(0.0, 0.0, 0.0, 0.0).signed_mean_mm, 0.0)

    def test_signed_mean_changes_authoritative_plan_hash_without_other_field_changes(self):
        baseline = plan_content()
        altered = replace(baseline, error_metrics=replace(
            baseline.error_metrics, signed_mean_mm=0.001))
        self.assertNotEqual(create_plan(baseline).plan_hash,
                            create_plan(altered).plan_hash)

    def test_valid_metric_change_affects_plan_hash_and_bytes(self):
        original = plan_content()
        changed = replace(original, error_metrics=replace(original.error_metrics, e_rms_mm=0.025))
        self.assertNotEqual(canonical_bytes(semantic_tree(original.error_metrics)),
                            canonical_bytes(semantic_tree(changed.error_metrics)))
        self.assertNotEqual(create_plan(original).plan_hash, create_plan(changed).plan_hash)


if __name__ == "__main__":
    unittest.main()
