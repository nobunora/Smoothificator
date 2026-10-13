"""ADR-0049: canonical integer bytes independent of Python's decimal digit cap."""
import sys
import unittest

from adaptive_subedge.application.serialization import canonical_bytes
from adaptive_subedge.application.hashing import typed_identity
from adaptive_subedge.domain.errors import ContractError


class CanonicalIntegerLimitTests(unittest.TestCase):
    def test_large_nonzero_decimal_chunks_under_minimum_supported_limit(self):
        original = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(640)
            huge = 10 ** 1500 + (10 ** 999 - 1)
            expected = b"i1" + b"0" * 500 + b"9" * 999 + b";"
            self.assertEqual(canonical_bytes(huge), expected)
            self.assertEqual(canonical_bytes(-huge), b"i-1" + expected[1:])
        finally:
            sys.set_int_max_str_digits(original)

    def test_small_and_boundary_integers_unaffected_by_runtime_cap(self):
        original = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(640)
            for v, token in ((0, b"i0;"), (1, b"i1;"), (-1, b"i-1;"),
                             (10 ** 639, b"i1" + b"0" * 639 + b";")):
                with self.subTest(value_bits=v.bit_length()):
                    self.assertEqual(canonical_bytes(v), token)
        finally:
            sys.set_int_max_str_digits(original)

    def test_typed_identity_semantics_match_with_and_without_digit_cap(self):
        huge = 10 ** 1400 + 1234567
        original = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(0)
            unrestricted = typed_identity("source-geometry", {"counter": huge})
            sys.set_int_max_str_digits(640)
            restricted = typed_identity("source-geometry", {"counter": huge})
            self.assertEqual(restricted, unrestricted)
        finally:
            sys.set_int_max_str_digits(original)


if __name__ == "__main__":
    unittest.main()
