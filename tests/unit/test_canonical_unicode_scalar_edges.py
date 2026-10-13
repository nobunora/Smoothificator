"""Four ADR-0049/0062 canonical scalar/order and root schema regression vectors."""
import hashlib
import unittest

from adaptive_subedge.application.serialization import (
    canonical_bytes, identity_root, validate_root, semantic_tree
)
from adaptive_subedge.application.hashing import typed_identity
from adaptive_subedge.domain.errors import ContractError, ReasonCode


class CanonicalUnicodeScalarEdges(unittest.TestCase):
    def test_string_length_uses_utf8_bytes_not_unicode_codepoint_count(self):
        for text in ("", "A", "é", "e\u0301", "日本語", "😀", "a\0b"):
            with self.subTest(text=text):
                encoded = text.encode("utf-8")
                self.assertEqual(canonical_bytes(text),
                                 b"s"+str(len(encoded)).encode("ascii")+b":"+encoded)

    def test_mapping_key_sort_is_unicode_codepoint_order_and_not_insertion_order(self):
        pairs = {"😀": 3, "é": 2, "e\u0301": 4, "a": 1}
        keys = sorted(pairs)
        independent = (b"m4{" +
            b"".join(b"s"+str(len(k.encode("utf-8"))).encode("ascii")+b":"+k.encode("utf-8")
                     +b"i"+str(pairs[k]).encode("ascii")+b";" for k in keys)+b"}")
        self.assertEqual(canonical_bytes(pairs), independent)
        self.assertEqual(canonical_bytes(dict(reversed(list(pairs.items())))), independent)

    def test_negative_zero_float_normalizes_while_int_and_bool_tags_stay_distinct(self):
        self.assertEqual(canonical_bytes(-0.0), canonical_bytes(0.0))
        self.assertNotEqual(canonical_bytes(False), canonical_bytes(0))
        self.assertNotEqual(canonical_bytes(0), canonical_bytes(0.0))
        self.assertEqual(canonical_bytes(-1), b"i-1;")
        self.assertEqual(canonical_bytes(-0), b"i0;")

    def test_root_field_whitelist_rejects_extra_missing_or_wrong_version(self):
        root = identity_root("source-geometry", {"mesh": ["A", 1]})
        validate_root(root, "source-geometry")
        corrupt = (
            {**root, "additional": 1},
            {k:v for k,v in root.items() if k != "payload"},
            {**root, "identity_type": "plugin-settings"},
            {**root, "schema_version": "2"},
            {**root, "canonical_encoding_version": "2"},
        )
        for item in corrupt:
            with self.subTest(keys=tuple(item)), self.assertRaises(ContractError) as caught:
                validate_root(item, "source-geometry")
            self.assertEqual(caught.exception.reason, ReasonCode.UNKNOWN_IDENTITY_SCHEMA)
        valid_id = typed_identity("source-geometry", {"mesh": ["A", 1]})
        expected = hashlib.sha256(
            b"AdaptiveSubEdgeCanonicalV1\0source-geometry\0"+canonical_bytes(root)).hexdigest()
        self.assertEqual(valid_id.digest_hex, expected)


if __name__ == "__main__":
    unittest.main()
