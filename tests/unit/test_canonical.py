"""Independent SHA-256/struct vectors and failure cases for ADR-0062/0064."""
import hashlib
import math
import struct
import unittest
from dataclasses import FrozenInstanceError

from adaptive_subedge.application.serialization import (
    canonical_bytes, canonical_array_token, validate_array_token, identity_root, semantic_tree,
)
from adaptive_subedge.application.hashing import (
    domain_digest, typed_identity, create_plan, verify_plan, fingerprint_plugin_settings,
    fingerprint_resolved_execution,
)
from adaptive_subedge.domain.plan import PlanSemanticContent, SubEdgePlan
from adaptive_subedge.domain.metrics import ErrorMetrics
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.settings import PluginSettings, CandidateSegmentRegularityPolicy


def settings(tolerance=0.05):
    return PluginSettings("1", tolerance, 0.08, 0.01,
        CandidateSegmentRegularityPolicy("research-1", None, 0.02, 0.001, 1.0, 0.01, 0.01))


def plan_content(tolerance=0.05):
    return PlanSemanticContent(
        "0.5", "research-only",
        typed_identity("source-geometry", {"faces": (1, 2, 3)}),
        fingerprint_resolved_execution({"nozzle_mm": 0.4, "relative_e": True}),
        fingerprint_plugin_settings(settings(tolerance)),
        ("loop-1",), (), (), ErrorMetrics(0.04, 0.02, 0.03, -0.001),
        0.0, 0.0, 0.0, False, "analysis-only",
    )


class CanonicalTests(unittest.TestCase):
    def test_exact_scalar_and_mapping_bytes(self):
        self.assertEqual(canonical_bytes({"b": 0.0, "a": 2}), b"m2{s1:ai2;s1:bf0x0.0p+0;}")
        self.assertEqual(canonical_bytes({"a": 2, "b": -0.0}), canonical_bytes({"b": 0.0, "a": 2}))
        self.assertEqual(canonical_bytes(True), b"b1")
        self.assertEqual(canonical_bytes("日本"), b"s6:" + "日本".encode("utf-8"))
        self.assertNotEqual(canonical_bytes(1), canonical_bytes("1"))

    def test_rejects_invalid_values(self):
        for v in (math.nan, math.inf, -math.inf, {2, 1}, object()):
            with self.subTest(value=repr(v)), self.assertRaises(ContractError):
                canonical_bytes(v)
        with self.assertRaises(ContractError):
            semantic_tree(object())
        with self.assertRaises(ContractError):
            identity_root("new-unknown-domain", {})

    def test_independent_domain_sha256(self):
        root = identity_root("source-geometry", {"mesh": [1, 2]})
        encoded = canonical_bytes(root)
        expected = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0source-geometry\0" + encoded).hexdigest()
        self.assertEqual(domain_digest("source-geometry", encoded), expected)
        self.assertEqual(typed_identity("source-geometry", {"mesh": [1, 2]}).digest_hex, expected)
        self.assertNotEqual(expected, domain_digest("array", encoded))

    def test_array_big_endian_golden_and_zero(self):
        token = canonical_array_token("f64", (2,), (-0.0, 1.5))
        payload = b"ASE_ARRAY_V1\0f64" + struct.pack(">I", 1) + struct.pack(">Q", 2) + struct.pack(">dd", 0.0, 1.5)
        expected = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0array\0" + payload).hexdigest()
        self.assertEqual(token["digest_hex"], expected)
        self.assertEqual(token, canonical_array_token("f64", (2,), (0.0, 1.5)))
        self.assertEqual(canonical_array_token("i64", (2,), (-2**63, 2**63 - 1))["dtype"], "i64")
        validate_array_token(token)
        with self.assertRaises(ContractError):
            canonical_array_token("f64", (2,), (1.0,))
        with self.assertRaises(ContractError):
            canonical_array_token("i64", (1,), (2**63,))
        with self.assertRaises(ContractError):
            validate_array_token({**token, "digest_hex": "0" * 63})

    def test_fingerprints_no_map_order_and_settings_change(self):
        a = fingerprint_resolved_execution({"z": 1, "a": 0.5})
        b = fingerprint_resolved_execution({"a": 0.5, "z": 1})
        self.assertEqual(a, b)
        self.assertNotEqual(fingerprint_plugin_settings(settings(.05)), fingerprint_plugin_settings(settings(.06)))
        self.assertNotEqual(a.identity_type, fingerprint_plugin_settings(settings()).identity_type)

    def test_plan_identity_not_self_referential(self):
        plan = create_plan(plan_content())
        self.assertEqual(plan.plan_id, plan.plan_hash)
        self.assertEqual(len(plan.plan_hash), 64)
        verify_plan(plan)
        self.assertNotIn("plan_hash", semantic_tree(plan.content))
        with self.assertRaises(FrozenInstanceError):
            plan.plan_hash = "0" * 64
        wrong = SubEdgePlan(plan.content, "0" * 64, "0" * 64)
        with self.assertRaises(ContractError):
            verify_plan(wrong)
        self.assertNotEqual(plan.plan_hash, create_plan(plan_content(0.06)).plan_hash)


if __name__ == "__main__":
    unittest.main()
