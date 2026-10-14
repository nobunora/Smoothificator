"""Accepted ADR-0058: immutable conservative bounds are data, NOT acceptance proof."""
from dataclasses import FrozenInstanceError, fields, replace
import math
import unittest

from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.application.serialization import _FIELDS, semantic_tree, canonical_bytes
from adaptive_subedge.domain.metrics import ConservativeSupportBounds
from adaptive_subedge.domain.errors import ContractError, ReasonCode


def evidence():
    return ConservativeSupportBounds(.8, .15, .08, .2)


class ConservativeSupportBoundsADR58(unittest.TestCase):
    def test_exact_four_accepted_lower_and_upper_bound_field_names(self):
        v=evidence()
        self.assertEqual(tuple(f.name for f in fields(v)),_FIELDS[ConservativeSupportBounds])
        self.assertEqual(set(semantic_tree(v)),set(_FIELDS[ConservativeSupportBounds]))
        with self.assertRaises(FrozenInstanceError):
            v.supported_area_fraction_lower_bound=.2

    def test_fraction_extremes_and_zero_width_height_are_representable(self):
        for fraction in (0.,1.):
            v=ConservativeSupportBounds(fraction,0.,0.,0.)
            self.assertEqual(v.supported_area_fraction_lower_bound,fraction)
        self.assertEqual(evidence().maximum_effective_height_upper_bound_mm,.2)

    def test_all_fields_reject_nonfinite_boolean_and_mutable_invalid_input(self):
        for field in _FIELDS[ConservativeSupportBounds]:
            for bad in (None,False,[],{},math.nan,math.inf,-math.inf,10**400):
                with self.subTest(field=field,bad=type(bad).__name__),self.assertRaises(ContractError) as err:
                    replace(evidence(),**{field:bad})
                self.assertEqual(err.exception.reason,ReasonCode.INVALID_GEOMETRY)

    def test_negative_or_inverted_bounds_are_rejected_without_hardware_assumptions(self):
        v=evidence()
        for field,bad in (("supported_area_fraction_lower_bound",1.01),
                          ("supported_area_fraction_lower_bound",-.01),
                          ("minimum_contiguous_support_width_lower_bound_mm",-.001),
                          ("minimum_effective_height_lower_bound_mm",-.001),
                          ("maximum_effective_height_upper_bound_mm",-.001),
                          ("minimum_effective_height_lower_bound_mm",.21),
                          ("maximum_effective_height_upper_bound_mm",.07)):
            with self.subTest(field=field),self.assertRaises(ContractError):
                replace(v,**{field:bad})

    def test_canonical_value_sensitive_but_cannot_impersonate_settings(self):
        v=evidence()
        token=canonical_bytes(semantic_tree(v))
        self.assertEqual(token,canonical_bytes(semantic_tree(evidence())))
        for field,val in (("supported_area_fraction_lower_bound",.7),
                          ("minimum_contiguous_support_width_lower_bound_mm",.1),
                          ("minimum_effective_height_lower_bound_mm",.07),
                          ("maximum_effective_height_upper_bound_mm",.25)):
            with self.subTest(field=field):
                self.assertNotEqual(token,canonical_bytes(semantic_tree(replace(v,**{field:val}))))
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(v)


if __name__=="__main__":
    unittest.main()
