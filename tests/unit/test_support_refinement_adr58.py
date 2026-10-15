"""Accepted ADR-0058 explicit conservative support refinement settings values."""
from dataclasses import FrozenInstanceError, fields, replace
import math
import unittest

from adaptive_subedge.application.hashing import fingerprint_plugin_settings
from adaptive_subedge.application.serialization import _FIELDS, semantic_tree, canonical_bytes
from adaptive_subedge.domain.settings import SupportRefinementPolicy
from adaptive_subedge.domain.errors import ContractError, ReasonCode


def research():
    return SupportRefinementPolicy(.2, 2., .01, .005, 6, .0125)


class SupportRefinementADR58(unittest.TestCase):
    def test_six_accepted_fields_are_immutable_and_exactly_registered(self):
        v=research()
        self.assertEqual(tuple(f.name for f in fields(v)),_FIELDS[SupportRefinementPolicy])
        with self.assertRaises(FrozenInstanceError):
            v.initial_support_cell_size_mm=1.
        self.assertEqual(v.max_support_refinement_levels,6)

    def test_positive_initial_minimum_cell_and_refinement_factor_constraints(self):
        for field,bad in (("initial_support_cell_size_mm",0),
                          ("minimum_support_cell_size_mm",-1),
                          ("support_refinement_factor",1.),
                          ("support_refinement_factor",math.inf),
                          ("minimum_support_cell_size_mm",.3)):
            with self.subTest(field=field), self.assertRaises(ContractError) as err:
                replace(research(),**{field:bad})
            self.assertEqual(err.exception.reason,ReasonCode.INVALID_SETTING)

    def test_fraction_width_and_integer_budget_boundaries(self):
        v=research()
        for fraction in (0.,1.):
            self.assertEqual(replace(v,support_metric_convergence_fraction=fraction)
                             .support_metric_convergence_fraction,fraction)
        for bad in (-.01,1.01,True,math.nan):
            with self.assertRaises(ContractError):
                replace(v,support_metric_convergence_fraction=bad)
        for bad in (-.001,True,math.nan,math.inf):
            with self.assertRaises(ContractError):
                replace(v,support_width_convergence_mm=bad)
        for bad in (-1,0,True,1.3,[],None):
            with self.assertRaises(ContractError):
                replace(v,max_support_refinement_levels=bad)

    def test_exact_canonical_bytes_change_for_each_declared_semantic_field(self):
        v=research()
        baseline=canonical_bytes(semantic_tree(v))
        replacements={
          "initial_support_cell_size_mm":.3,
          "support_refinement_factor":3.,
          "support_metric_convergence_fraction":.02,
          "support_width_convergence_mm":.01,
          "max_support_refinement_levels":7,
          "minimum_support_cell_size_mm":.01,
        }
        self.assertEqual(baseline,canonical_bytes(semantic_tree(research())))
        for key,val in replacements.items():
            with self.subTest(key=key):
                self.assertNotEqual(baseline,canonical_bytes(semantic_tree(replace(v,**{key:val}))))

    def test_research_fragment_not_a_full_v1_settings_fingerprint(self):
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(research())
        with self.assertRaises(TypeError):
            SupportRefinementPolicy()


if __name__=="__main__":
    unittest.main()
