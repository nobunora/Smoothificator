"""Five independent ADR-0062/0064 array framing and rejection vectors (no NumPy)."""
import hashlib
import math
import struct
import unittest

from adaptive_subedge.application.serialization import canonical_array_token, validate_array_token
from adaptive_subedge.domain.errors import ContractError, ReasonCode

PREFIX = b"AdaptiveSubEdgeCanonicalV1\0array\0"


class CanonicalArrayMatrix(unittest.TestCase):
    def test_multidimensional_i64_boundary_endianness_golden(self):
        ints = (-2 ** 63, -1, 0, 2 ** 63 - 1)
        payload = b"ASE_ARRAY_V1\0i64" + struct.pack(">IQQQ", 3, 1, 2, 2)
        payload += b"".join(struct.pack(">q", x) for x in ints)
        expected = hashlib.sha256(PREFIX + payload).hexdigest()
        token = canonical_array_token("i64", (1, 2, 2), ints)
        self.assertEqual(token["digest_hex"], expected)
        self.assertEqual(token["shape"], [1, 2, 2])
        validate_array_token(token)

    def test_f64_negative_zero_and_subnormal_fixed_big_endian(self):
        smallest = float.fromhex("0x0.0000000000001p-1022")
        values = (-0.0, +0.0, smallest, -smallest)
        payload = b"ASE_ARRAY_V1\0f64" + struct.pack(">IQQ", 2, 2, 2)
        payload += b"".join(struct.pack(">d", 0.0 if x == 0 else x) for x in values)
        digest = hashlib.sha256(PREFIX + payload).hexdigest()
        token = canonical_array_token("f64", (2, 2), values)
        self.assertEqual(token["digest_hex"], digest)
        self.assertEqual(token, canonical_array_token("f64", (2, 2), (0.0, 0.0, smallest, -smallest)))
        validate_array_token(token)

    def test_identical_logical_C_matrix_from_conceptual_F_storage(self):
        rows, cols = 3, 2
        row_major = (1, 2, 3, 4, 5, 6)
        column_major_storage = (1, 3, 5, 2, 4, 6)
        recovered = tuple(column_major_storage[i + rows * j]
                          for i in range(rows) for j in range(cols))
        self.assertEqual(recovered, row_major)
        self.assertEqual(canonical_array_token("i64", (rows, cols), recovered),
                         canonical_array_token("i64", (rows, cols), row_major))
        self.assertNotEqual(canonical_array_token("i64", (rows, cols), column_major_storage),
                            canonical_array_token("i64", (rows, cols), row_major))

    def test_invalid_shapes_and_values_fail_with_typed_reason(self):
        invalids = (
            ("i64", (True,), (1,)),
            ("i64", (-1,), ()),
            ("i64", (2,), (1,)),
            ("i64", (1,), (True,)),
            ("i64", (1,), (2 ** 63,)),
            ("f64", (1,), (math.nan,)),
            ("f64", (1,), (math.inf,)),
            ("f64", (1,), (10 ** 400,)),
            ("u32", (1,), (1,)),
            ("i64", [1], (1,)),
        )
        for dtype, shape, vals in invalids:
            with self.subTest(dtype=dtype, shape=shape), self.assertRaises(ContractError) as err:
                canonical_array_token(dtype, shape, vals)
            self.assertEqual(err.exception.reason, ReasonCode.INVALID_CANONICAL_VALUE)

    def test_token_rejects_missing_extra_or_wrong_schema_fields(self):
        token = canonical_array_token("f64", (0, 3), ())
        malformed = (
            {k: v for k, v in token.items() if k != "shape"},
            {**token, "unexpected": 5},
            {**token, "array_schema_version": "ASE_ARRAY_V2"},
            {**token, "shape": [0, -1]},
            {**token, "digest_hex": token["digest_hex"].upper()},
            {**token, "dtype": "i32"},
            {**token, "shape": (0, 3)},
        )
        for item in malformed:
            with self.subTest(keys=tuple(item)), self.assertRaises(ContractError):
                validate_array_token(item)
        validate_array_token(token)


if __name__ == "__main__":
    unittest.main()
