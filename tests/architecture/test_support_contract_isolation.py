"""Phase 0.5 support Settings/outcome DTO ownership and strict v1 identity gate."""
from dataclasses import fields, replace, FrozenInstanceError
import unittest

from adaptive_subedge.application.hashing import fingerprint_plugin_settings, typed_identity
from adaptive_subedge.application.serialization import _FIELDS, semantic_tree, canonical_bytes
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.metrics import ConservativeSupportBounds, SupportCoverageMetrics
from adaptive_subedge.domain.settings import (
    SupportCoverageThresholds, SupportRefinementPolicy, CandidateBeadBounds, PluginSettings,
)
from tests.unit.test_v1_settings_fingerprint_golden import v1_settings


class SupportContractIsolation(unittest.TestCase):
    def test_accepted_dto_families_have_full_exact_field_registration(self):
        for dto in (SupportCoverageThresholds, SupportRefinementPolicy,
                    ConservativeSupportBounds, CandidateBeadBounds):
            with self.subTest(dto=dto.__name__):
                self.assertEqual(tuple(f.name for f in fields(dto)),_FIELDS[dto])
                self.assertTrue(dto.__dataclass_params__.frozen)
                self.assertEqual(len(_FIELDS[dto]),len(set(_FIELDS[dto])))

    def test_conservative_result_and_legacy_coverage_diagnostic_are_not_interchangeable(self):
        proof = ConservativeSupportBounds(.7, .12, .04, .2)
        legacy = SupportCoverageMetrics("research-v1", .7, .7)
        self.assertNotEqual(semantic_tree(proof),semantic_tree(legacy))
        self.assertIn("supported_area_fraction_lower_bound",semantic_tree(proof))
        self.assertNotIn("supported_area_fraction_lower_bound",semantic_tree(legacy))
        self.assertNotIn(SupportCoverageMetrics, (SupportCoverageThresholds, SupportRefinementPolicy))
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(proof)
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(legacy)

    def test_v1_seven_fields_remain_closed_and_fingerprint_bytes_stable(self):
        settings=v1_settings()
        base=fingerprint_plugin_settings(settings)
        self.assertEqual(tuple(f.name for f in fields(PluginSettings)),
            ("schema_version","surface_error_tolerance_mm",
             "minimum_effective_bead_height_mm","candidate_seam_gap_mm",
             "regularity_policy","tool_clearance_profile","physical_injection_requested"))
        self.assertEqual(_FIELDS[PluginSettings],tuple(f.name for f in fields(PluginSettings)))
        # Instantiating standalone research values has no effect on the v1 identity.
        SupportCoverageThresholds(.7,.1)
        SupportRefinementPolicy(.2,2.,.01,.005,5,.0125)
        ConservativeSupportBounds(.7,.1,.05,.2)
        self.assertEqual(fingerprint_plugin_settings(settings),base)
        with self.assertRaises(ContractError):
            replace(settings,schema_version="2")

    def test_support_values_are_data_not_a_physical_authorization(self):
        support=SupportCoverageThresholds(1.,1.)
        refinement=SupportRefinementPolicy(.1,2.,0.,0.,5,.01)
        proof=ConservativeSupportBounds(1.,1.,.1,.2)
        self.assertTrue(all(canonical_bytes(semantic_tree(v)) for v in (support,refinement,proof)))
        settings=v1_settings()
        with self.assertRaises(ContractError) as err:
            settings.require_physical_injection()
        self.assertEqual(err.exception.reason,ReasonCode.PHYSICAL_INJECTION_NOT_AUTHORIZED)
        with self.assertRaises(ContractError):
            replace(settings,physical_injection_requested=True)


if __name__=="__main__":
    unittest.main()
