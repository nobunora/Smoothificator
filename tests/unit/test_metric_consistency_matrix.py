"""Four exhaustive finite-domain ErrorMetrics contract checks, not estimator policy."""
from dataclasses import FrozenInstanceError, replace
from itertools import product
import math
import unittest

from adaptive_subedge.domain.metrics import ErrorMetrics
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.application.hashing import create_plan
from tests.unit.test_canonical import plan_content


class MetricConsistencyMatrix(unittest.TestCase):
    def test_dense_small_finite_grid_accepts_only_maximum_bounded_statistics(self):
        values = (0.0, 0.01, 0.02, 0.04)
        for maximum, rms, p95 in product(values, repeat=3):
            metrics = (maximum, rms, p95, 0.0)
            if rms <= maximum and p95 <= maximum:
                self.assertEqual(ErrorMetrics(*metrics).e_max_mm, maximum)
            else:
                with self.assertRaises(ContractError):
                    ErrorMetrics(*metrics)

    def test_signed_bias_positive_and_negative_boundary_grid(self):
        maxima = (0.0, 0.01, 0.02, 1.0)
        for maximum in maxima:
            for mean in (-maximum - 0.001, -maximum, 0., maximum, maximum + 0.001):
                with self.subTest(maximum=maximum, mean=mean):
                    if abs(mean) <= maximum:
                        self.assertEqual(ErrorMetrics(maximum, 0., 0., mean).signed_mean_mm, mean)
                    else:
                        with self.assertRaises(ContractError) as ctx:
                            ErrorMetrics(maximum, 0., 0., mean)
                        self.assertEqual(ctx.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_nonfinite_negative_and_nonbinary64_inputs_fail_all_four_fields(self):
        valid = ErrorMetrics(.04, .03, .02, -.001)
        for field in ("e_max_mm", "e_rms_mm", "e_p95_mm", "signed_mean_mm"):
            for invalid in (math.nan, math.inf, -math.inf, True, 10**400, []):
                with self.subTest(field=field, bad=type(invalid).__name__):
                    with self.assertRaises(ContractError):
                        replace(valid, **{field: invalid})
        for field in ("e_max_mm", "e_rms_mm", "e_p95_mm"):
            with self.assertRaises(ContractError):
                replace(valid, **{field: -.01})

    def test_frozen_metric_and_approved_signed_bias_plan_hash_sensitivity(self):
        baseline = plan_content()
        original = create_plan(baseline)
        for bias in (-.01, -.002, 0., .001):
            with self.subTest(bias=bias):
                changed = replace(baseline, error_metrics=replace(baseline.error_metrics,
                                                                  signed_mean_mm=bias))
                new_plan = create_plan(changed)
                self.assertEqual(new_plan.plan_id, new_plan.plan_hash)
                if bias != baseline.error_metrics.signed_mean_mm:
                    self.assertNotEqual(original.plan_hash, new_plan.plan_hash)
        with self.assertRaises(FrozenInstanceError):
            baseline.error_metrics.signed_mean_mm = .001


if __name__ == "__main__":
    unittest.main()
