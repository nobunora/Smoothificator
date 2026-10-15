"""Accepted ADR-0047: directional error data remains independent of Plan v1."""
from dataclasses import FrozenInstanceError, fields, replace
import math
import unittest

from adaptive_subedge.application.hashing import create_plan
from adaptive_subedge.application.serialization import _FIELDS, canonical_bytes, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.metrics import BidirectionalSurfaceErrorMetrics
from tests.unit.test_canonical import plan_content


def sample():
    return BidirectionalSurfaceErrorMetrics(.12, .15, .1, .13, .08, .11)


class BidirectionalSurfaceErrorMetricsADR47(unittest.TestCase):
    def test_six_exact_fields_and_immutability(self):
        value = sample()
        self.assertEqual(tuple(f.name for f in fields(value)),
                         _FIELDS[BidirectionalSurfaceErrorMetrics])
        with self.assertRaises(FrozenInstanceError):
            value.e_max_pred_to_src_mm = .2

    def test_zero_and_directional_equality_are_valid(self):
        self.assertEqual(BidirectionalSurfaceErrorMetrics(0, 0, 0, 0, 0, 0)
                         .e_max_src_to_pred_mm, 0)
        self.assertEqual(BidirectionalSurfaceErrorMetrics(.2, .3, .2, .3, .2, .3)
                         .e_p95_src_to_pred_mm, .3)

    def test_nonfinite_bad_types_and_negative_reject_typed(self):
        for name in _FIELDS[BidirectionalSurfaceErrorMetrics]:
            for bad in (None, True, False, "0.1", [], {}, math.nan,
                        math.inf, -math.inf, -0.001, 10 ** 400):
                with self.subTest(field=name, bad=str(type(bad))), self.assertRaises(ContractError) as cm:
                    replace(sample(), **{name: bad})
                self.assertEqual(cm.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_directional_p95_and_rms_cannot_exceed_own_max(self):
        baseline = sample()
        for name, value in (
            ("e_p95_pred_to_src_mm", .121),
            ("e_p95_src_to_pred_mm", .151),
            ("e_rms_pred_to_src_mm", .121),
            ("e_rms_src_to_pred_mm", .151),
        ):
            with self.subTest(field=name), self.assertRaises(ContractError) as cm:
                replace(baseline, **{name: value})
            self.assertEqual(cm.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_canonical_projection_field_sensitivity(self):
        original = sample()
        projection = canonical_bytes(semantic_tree(original))
        self.assertEqual(projection, canonical_bytes(semantic_tree(sample())))
        for field_name, changed in (
            ("e_max_pred_to_src_mm", .13),
            ("e_max_src_to_pred_mm", .16),
            ("e_p95_pred_to_src_mm", .09),
            ("e_p95_src_to_pred_mm", .12),
            ("e_rms_pred_to_src_mm", .07),
            ("e_rms_src_to_pred_mm", .1),
        ):
            with self.subTest(field=field_name):
                self.assertNotEqual(
                    projection, canonical_bytes(
                        semantic_tree(replace(original, **{field_name: changed}))))

    def test_plan_v1_hash_and_schema_do_not_change(self):
        v1 = plan_content()
        h1 = create_plan(v1).plan_hash
        _ = canonical_bytes(semantic_tree(sample()))
        self.assertEqual(create_plan(v1).plan_hash, h1)
        self.assertNotIn("bidirectional_error_metrics", semantic_tree(v1))


if __name__ == "__main__":
    unittest.main()
