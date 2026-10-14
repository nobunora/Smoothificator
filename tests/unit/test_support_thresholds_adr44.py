"""Accepted ADR-0044 declared support threshold values, not support geometry."""
from dataclasses import FrozenInstanceError, fields, replace
import math
import unittest

from adaptive_subedge.application.serialization import _FIELDS, canonical_bytes, semantic_tree
from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import SupportCoverageThresholds


class SupportThresholdsADR44(unittest.TestCase):
    def test_valid_fraction_extrema_and_nonnegative_contact_width(self):
        for fraction in (0, .25, 1):
            for contact_width in (0., .05, 10.):
                with self.subTest(fraction=fraction,width=contact_width):
                    value=SupportCoverageThresholds(fraction,contact_width)
                    self.assertEqual(value.min_support_area_fraction,fraction)
        with self.assertRaises(FrozenInstanceError):
            value.min_support_contact_width_mm=2.

    def test_reject_invalid_area_fraction_with_stable_settings_reason(self):
        for bad in (-.01, 1.01, True, [], "1.0", None, float("nan"), float("inf"), 10**400):
            with self.subTest(type=type(bad).__name__), self.assertRaises(ContractError) as error:
                SupportCoverageThresholds(bad, .2)
            self.assertEqual(error.exception.reason,ReasonCode.INVALID_SETTING)

    def test_reject_invalid_contact_width_with_stable_settings_reason(self):
        for bad in (-.01, True, {}, "1", None, float("nan"), float("-inf"), 10**400):
            with self.subTest(type=type(bad).__name__), self.assertRaises(ContractError) as error:
                SupportCoverageThresholds(.5,bad)
            self.assertEqual(error.exception.reason,ReasonCode.INVALID_SETTING)

    def test_declared_canonical_projection_exact_and_semantically_sensitive(self):
        baseline=SupportCoverageThresholds(.75,.2)
        self.assertEqual(tuple(f.name for f in fields(baseline)),_FIELDS[SupportCoverageThresholds])
        self.assertEqual(set(semantic_tree(baseline)),set(_FIELDS[SupportCoverageThresholds]))
        self.assertEqual(canonical_bytes(semantic_tree(baseline)),
                         canonical_bytes(semantic_tree(SupportCoverageThresholds(.75,.2))))
        for changed in (replace(baseline,min_support_area_fraction=.8),
                        replace(baseline,min_support_contact_width_mm=.3)):
            self.assertNotEqual(canonical_bytes(semantic_tree(changed)),
                                canonical_bytes(semantic_tree(baseline)))

    def test_standalone_thresholds_are_not_plugin_settings_v1(self):
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(SupportCoverageThresholds(.6,.1))
        with self.assertRaises(TypeError):
            SupportCoverageThresholds()


if __name__=="__main__":
    unittest.main()
