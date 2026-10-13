"""Independent SHA-256/struct vectors and failure cases for ADR-0062/0064."""
import hashlib
import math
import struct
import unittest
from dataclasses import FrozenInstanceError, replace

from adaptive_subedge.application.serialization import (
    canonical_bytes, canonical_array_token, validate_array_token, identity_root, semantic_tree,
)
from adaptive_subedge.application.hashing import (
    domain_digest, typed_identity, create_plan, verify_plan, fingerprint_plugin_settings,
    fingerprint_resolved_execution, typed_identities_equal, domain_digest_chunks,
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
        from adaptive_subedge.domain.geometry import PrintPoint2
        self.assertEqual(canonical_bytes(semantic_tree(PrintPoint2(1, 2))),
                         canonical_bytes(semantic_tree(PrintPoint2(1.0, 2.0))))

    def test_rejects_invalid_values(self):
        for v in (math.nan, math.inf, -math.inf, {2, 1}, object()):
            with self.subTest(value=repr(v)), self.assertRaises(ContractError):
                canonical_bytes(v)
        with self.assertRaises(ContractError):
            semantic_tree(object())
        with self.assertRaises(ContractError):
            identity_root("new-unknown-domain", {})

    def test_cyclic_inputs_fail_with_stable_contract_reason(self):
        cyclic_list = []
        cyclic_list.append(cyclic_list)
        cyclic_map = {}
        cyclic_map["self"] = cyclic_map
        for bad in (cyclic_list, cyclic_map):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaises(ContractError):
                    semantic_tree(bad)
                with self.assertRaises(ContractError):
                    canonical_bytes(bad)
                with self.assertRaises(ContractError):
                    typed_identity("source-geometry", {"graph": bad})
        self.assertEqual(canonical_bytes({"a": [1, 2]}), b"m1{s1:al2[i1;i2;]}")

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
            canonical_array_token("f64", (1,), (10**400,))
        with self.assertRaises(ContractError):
            validate_array_token({**token, "digest_hex": "0" * 63})

    def test_2d_array_exact_bytes_and_c_logical_order(self):
        shape = (2, 3)
        values = (1, 2, 3, 4, 5, 6)
        header = b"ASE_ARRAY_V1\0i64" + struct.pack(">IQQ", 2, 2, 3)
        raw = header + struct.pack(">6q", *values)
        expected = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0array\0" + raw).hexdigest()
        self.assertEqual(canonical_array_token("i64", shape, values)["digest_hex"], expected)
        # Conceptual Fortran-order storage of the same matrix; an owning
        # adapter must restore C-logical values before calling the encoder.
        fortran_memory = (1, 4, 2, 5, 3, 6)
        c_logical = tuple(fortran_memory[row + 2 * col] for row in range(2) for col in range(3))
        self.assertEqual(c_logical, values)
        self.assertEqual(canonical_array_token("i64", shape, c_logical)["digest_hex"], expected)
        self.assertNotEqual(canonical_array_token("i64", (3, 2), values)["digest_hex"], expected)

    def test_streamed_digest_matches_reference_and_rejects_nonbytes(self):
        data = tuple(range(2048))
        header = b"ASE_ARRAY_V1\0i64" + struct.pack(">IQQ", 2, 64, 32)
        expected = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0array\0" +
                                  header + struct.pack(">2048q", *data)).hexdigest()
        self.assertEqual(canonical_array_token("i64", (64, 32), data)["digest_hex"], expected)
        self.assertEqual(domain_digest_chunks("array", (b"abc", b"def")),
                         domain_digest("array", b"abcdef"))
        with self.assertRaises(ContractError):
            domain_digest_chunks("array", (b"ok", bytearray(b"mutable")))

    def test_subnormal_float_array_and_unknown_token_schema(self):
        subnormal = float.fromhex("0x0.0000000000001p-1022")
        header = b"ASE_ARRAY_V1\0f64" + struct.pack(">IQ", 1, 1)
        expected = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0array\0" +
                                  header + struct.pack(">d", subnormal)).hexdigest()
        token = canonical_array_token("f64", (1,), (subnormal,))
        self.assertEqual(token["digest_hex"], expected)
        with self.assertRaises(ContractError):
            validate_array_token({**token, "array_schema_version": "ASE_ARRAY_V2"})

    def test_typed_identity_comparison_rejects_wrong_schema(self):
        a = typed_identity("source-geometry", {"mesh": 1})
        equal = typed_identity("source-geometry", {"mesh": 1})
        changed = typed_identity("source-geometry", {"mesh": 2})
        self.assertTrue(typed_identities_equal("source-geometry", a, equal))
        self.assertFalse(typed_identities_equal("source-geometry", a, changed))
        with self.assertRaises(ContractError):
            typed_identities_equal("source-geometry", a, typed_identity("execution-config", {"mesh": 1}))
        with self.assertRaises(ContractError):
            typed_identities_equal("source-geometry", a, replace(equal, schema_version="2"))
        with self.assertRaises(ContractError):
            typed_identities_equal("source-geometry", a.digest_hex, equal)

    def test_large_canonical_integers_are_environment_independent(self):
        positive = 10 ** 5000
        expected = b"i1" + b"0" * 5000 + b";"
        self.assertEqual(canonical_bytes(positive), expected)
        self.assertEqual(canonical_bytes(-positive), b"i-1" + b"0" * 5000 + b";")
        self.assertEqual(canonical_bytes(0), b"i0;")

    def test_identity_api_rejects_unhashable_type_labels(self):
        from adaptive_subedge.application.serialization import validate_root
        sample = typed_identity("source-geometry", {"mesh": 1})
        for bad in ([], {"type": "source-geometry"}, 1):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                typed_identity(bad, {})
            with self.subTest(comparison=bad), self.assertRaises(ContractError):
                typed_identities_equal(bad, sample, sample)
            with self.subTest(root=bad), self.assertRaises(ContractError):
                validate_root(identity_root("source-geometry", {}), bad)

    def test_anchor_semantic_identity_changes_plan_hash(self):
        from adaptive_subedge.domain.plan import InsertionAnchor
        original = plan_content()
        changed = replace(original, anchors=(InsertionAnchor("insert-1", ("loop-1",), 2, "known"),))
        self.assertNotEqual(create_plan(original).plan_hash, create_plan(changed).plan_hash)
        changed_again = replace(changed, anchors=(InsertionAnchor("insert-2", ("loop-1",), 2, "known"),))
        self.assertNotEqual(create_plan(changed).plan_hash, create_plan(changed_again).plan_hash)

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
