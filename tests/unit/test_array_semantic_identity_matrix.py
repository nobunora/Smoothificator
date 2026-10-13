"""Four new array semantic-identity vectors (source adapter logical-order ownership)."""
import hashlib
import struct
from dataclasses import replace
import unittest

from adaptive_subedge.application.serialization import (
    canonical_array_token, validate_array_token, canonical_bytes
)
from adaptive_subedge.application.hashing import typed_identity
from adaptive_subedge.domain.errors import ContractError, ReasonCode

PREFIX = b"AdaptiveSubEdgeCanonicalV1\0array\0"


class ArraySemanticIdentityMatrix(unittest.TestCase):
    def test_different_rank_and_shape_never_collide_for_same_values(self):
        data = (1, 2, 3, 4)
        token1 = canonical_array_token("i64", (4,), data)
        token2 = canonical_array_token("i64", (2, 2), data)
        token3 = canonical_array_token("i64", (1, 4), data)
        token4 = canonical_array_token("i64", (2, 1, 2), data)
        self.assertEqual(len({t["digest_hex"] for t in (token1,token2,token3,token4)}),4)
        for t in (token1,token2,token3,token4):
            validate_array_token(t)

    def test_i64_vs_f64_same_integers_are_semantically_different(self):
        integer_token = canonical_array_token("i64", (3,), (0, 1, -1))
        float_token = canonical_array_token("f64", (3,), (0.0, 1.0, -1.0))
        self.assertNotEqual(integer_token["digest_hex"], float_token["digest_hex"])
        self.assertEqual(integer_token["shape"], float_token["shape"])
        self.assertNotEqual(typed_identity("source-geometry", {"a": integer_token}),
                            typed_identity("source-geometry", {"a": float_token}))

    def test_signed_big_endian_2d_independent_negative_integer_frame(self):
        values = (-1, -128, -32768, -(2**63))
        expected_frame = b"ASE_ARRAY_V1\0i64" + struct.pack(">IQQ", 2, 2, 2)
        expected_frame += b"".join(struct.pack(">q", v) for v in values)
        expected = hashlib.sha256(PREFIX + expected_frame).hexdigest()
        self.assertEqual(canonical_array_token("i64", (2, 2), values)["digest_hex"], expected)
        self.assertNotEqual(canonical_array_token("i64", (2, 2), tuple(reversed(values)))["digest_hex"], expected)

    def test_reject_invalid_array_token_keys_types_and_digest_without_truncation(self):
        token = canonical_array_token("f64", (2,), (0.0, -0.0))
        self.assertEqual(len(token["digest_hex"]),64)
        for altered in (
            {**token, "digest_hex": token["digest_hex"][:-1]},
            {**token, "digest_hex": token["digest_hex"].upper()},
            {**token, "shape": [2.0]},
            {**token, "shape": [True, 2]},
            {**token, "dtype": "unknown"},
            {**token, "array_schema_version": "ASE_ARRAY_V2"},
            {**token, "not_declared": 0},
        ):
            with self.subTest(case=str(list(altered))), self.assertRaises(ContractError):
                validate_array_token(altered)
        validate_array_token(token)


if __name__ == "__main__":
    unittest.main()
