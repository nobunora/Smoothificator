"""Accepted ADR-0043 research-only candidate bead bounds; no physical printer defaults."""
from dataclasses import FrozenInstanceError, fields, replace
import math
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.application.serialization import _FIELDS, canonical_bytes, semantic_tree
from adaptive_subedge.application.hashing import fingerprint_plugin_settings


class CandidateBeadBoundsTests(unittest.TestCase):
    def test_declared_ordered_positive_envelope_is_immutable(self):
        limits = CandidateBeadBounds(.08, .3, .2, .6)
        self.assertEqual(tuple(f.name for f in fields(limits)), _FIELDS[CandidateBeadBounds])
        with self.assertRaises(FrozenInstanceError):
            limits.max_candidate_width_mm = 0.7
        self.assertEqual(limits.min_candidate_height_mm, .08)

    def test_all_numerical_bounds_reject_invalid_values(self):
        limits = CandidateBeadBounds(.08, .3, .2, .6)
        for field in _FIELDS[CandidateBeadBounds]:
            for bad in (0, -0.001, True, None, [], "0.1", math.nan, math.inf, -math.inf, 10**400):
                with self.subTest(field=field, bad_type=type(bad).__name__), self.assertRaises(ContractError) as err:
                    replace(limits, **{field: bad})
                self.assertEqual(err.exception.reason, ReasonCode.INVALID_SETTING)

    def test_inverted_extrema_fail_but_equal_min_max_is_valid(self):
        limits = CandidateBeadBounds(.08, .3, .2, .6)
        for changes in ({"max_candidate_height_mm": .07},
                        {"min_candidate_width_mm": .7}):
            with self.subTest(field=tuple(changes)), self.assertRaises(ContractError):
                replace(limits, **changes)
        fixed = CandidateBeadBounds(.1, .1, .5, .5)
        self.assertEqual(fixed.min_candidate_height_mm, fixed.max_candidate_height_mm)
        self.assertEqual(fixed.min_candidate_width_mm, fixed.max_candidate_width_mm)

    def test_no_unapproved_cross_axis_constraint_or_default_applied(self):
        # ADR-0043 requires width >= effective height per SEGMENT, not min_width >= max_height.
        valid_envelope = CandidateBeadBounds(.08, .8, .2, .9)
        self.assertLess(valid_envelope.min_candidate_width_mm, valid_envelope.max_candidate_height_mm)
        self.assertEqual(len(_FIELDS[CandidateBeadBounds]), 4)
        with self.assertRaises(TypeError):
            CandidateBeadBounds()

    def test_canonical_fields_are_deterministic_but_not_part_of_settings_v1(self):
        envelope = CandidateBeadBounds(.08, .3, .2, .6)
        self.assertEqual(canonical_bytes(semantic_tree(envelope)),
                         canonical_bytes(semantic_tree(CandidateBeadBounds(.08, .3, .2, .6))))
        self.assertNotEqual(canonical_bytes(semantic_tree(envelope)),
                            canonical_bytes(semantic_tree(replace(envelope, max_candidate_height_mm=.31))))
        with self.assertRaises(ContractError):
            fingerprint_plugin_settings(envelope)


if __name__ == "__main__":
    unittest.main()
