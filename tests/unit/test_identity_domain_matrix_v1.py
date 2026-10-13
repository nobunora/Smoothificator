"""Four ADR-0062/0064 v1 typed/hash domain invariants on synthetic DTOs."""
import hashlib
from dataclasses import replace
import unittest

from adaptive_subedge.application.hashing import (
    create_plan, domain_digest, domain_digest_chunks, typed_identity,
    typed_identities_equal, verify_plan,
)
from adaptive_subedge.application.serialization import canonical_bytes, identity_root
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.plan import IdentityReference, SubEdgePlan
from tests.unit.test_canonical import plan_content


class IdentityDomainMatrixV1(unittest.TestCase):
    def test_distinct_semantic_domains_do_not_reuse_identical_hash_payload(self):
        payload = {"name": "synthetic", "number": 5}
        identities = [typed_identity(domain, payload) for domain in
                      ("source-geometry", "plugin-settings", "execution-config", "subedge-plan")]
        self.assertEqual(len({i.digest_hex for i in identities}), 4)
        for domain, tag in (("source-geometry", "source-geometry"),
                            ("plugin-settings", "plugin-settings"),
                            ("execution-config", "execution-config"),
                            ("subedge-plan", "plan")):
            root = identity_root(domain, payload)
            independent = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0" + tag.encode("ascii") +
                                         b"\0" + canonical_bytes(root)).hexdigest()
            self.assertEqual(typed_identity(domain, payload).digest_hex, independent)

    def test_typed_identity_comparisons_reject_versions_and_cross_domain_refs(self):
        source = typed_identity("source-geometry", {"p": (1, 2)})
        unchanged = typed_identity("source-geometry", {"p": [1, 2]})
        different = typed_identity("source-geometry", {"p": (2, 1)})
        self.assertTrue(typed_identities_equal("source-geometry", source, unchanged))
        self.assertFalse(typed_identities_equal("source-geometry", source, different))
        for bad in (replace(source, schema_version="2"),
                    replace(source, canonical_encoding_version="2"),
                    typed_identity("plugin-settings", {"p": (1, 2)}),
                    source.digest_hex):
            with self.subTest(bad_type=type(bad).__name__), self.assertRaises(ContractError):
                typed_identities_equal("source-geometry", source, bad)

    def test_ordered_digest_chunks_match_independent_sha_for_all_boundaries(self):
        for chunks in ((b"",), (b"hello", b"", b"world"),
                       tuple(bytes([i]) for i in range(64)), ()):
            with self.subTest(chunks=len(chunks)):
                expected = hashlib.sha256(b"AdaptiveSubEdgeCanonicalV1\0array\0" +
                                          b"".join(chunks)).hexdigest()
                self.assertEqual(domain_digest_chunks("array", iter(chunks)), expected)
                self.assertEqual(domain_digest("array", b"".join(chunks)), expected)
        for malformed in ({}, set(), b"", "abc", None, 1, (b"ok", 1)):
            with self.subTest(bad_type=type(malformed).__name__), self.assertRaises(ContractError):
                domain_digest_chunks("array", malformed)

    def test_plan_hash_is_derived_not_circular_and_supplied_hash_mismatch_fails(self):
        content = plan_content()
        plan = create_plan(content)
        self.assertEqual(plan.plan_hash, plan.plan_id)
        self.assertEqual(plan.plan_hash, typed_identity("subedge-plan", content).digest_hex)
        verify_plan(plan)
        for malformed in ("0" * 64, "f" * 64):
            if malformed == plan.plan_hash:
                continue
            supplied = SubEdgePlan(content, malformed, malformed)
            with self.assertRaises(ContractError) as caught:
                verify_plan(supplied)
            self.assertEqual(caught.exception.reason, ReasonCode.INVALID_CANONICAL_VALUE)


if __name__ == "__main__":
    unittest.main()
