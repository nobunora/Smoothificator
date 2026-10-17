"""Research anchor validation does not grant matcher or canonical authority."""
import dataclasses
import math
import unittest

from adaptive_subedge.application.serialization import semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.insertion_anchor_v2 import InsertionAnchorV2
from adaptive_subedge.domain.plan import InsertionAnchor


class StringSubclass(str):
    pass


class FloatSubclass(float):
    pass


class IntSubclass(int):
    pass


class InsertionAnchorV2Tests(unittest.TestCase):
    def fields(self):
        return dict(anchor_id="anchor-1", structural_loop_ids=("loop-b", "loop-a"),
                    layer_index=1, boundary_signature="opaque boundary token",
                    target_structural_interval_id="interval-1",
                    boundary_signature_schema_version="opaque_boundary_signature_v1",
                    matching_tolerance_mm=0.001, matching_profile_id="research-profile")

    def test_frozen_order_preserving_without_proof_flags(self):
        anchor = InsertionAnchorV2(**self.fields())
        self.assertEqual(anchor.structural_loop_ids, ("loop-b", "loop-a"))
        for name in ("validated", "injectable", "__dict__"):
            self.assertFalse(hasattr(anchor, name))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            anchor.anchor_id = "changed"

    def test_all_eight_fields_required_and_extra_rejected(self):
        fields = self.fields()
        self.assertEqual(len(dataclasses.fields(InsertionAnchorV2)), 8)
        for missing in fields:
            with self.subTest(missing=missing), self.assertRaises(TypeError):
                InsertionAnchorV2(**{k: v for k, v in fields.items() if k != missing})
        with self.assertRaises(TypeError):
            InsertionAnchorV2(**fields, validated=True)

    def test_strings_are_exact_nonblank(self):
        for name in ("anchor_id", "boundary_signature", "target_structural_interval_id",
                     "boundary_signature_schema_version", "matching_profile_id"):
            for invalid in ("", " \t\n", None, False, 1, [], StringSubclass("token")):
                with self.subTest(field=name, value=invalid), self.assertRaises(ContractError):
                    InsertionAnchorV2(**(self.fields() | {name: invalid}))

    def test_loop_ids_are_nonempty_distinct_exact_immutable_strings(self):
        for invalid in ((), [], ["loop"], "loop", ("loop", "loop"), ("",),
                        (" \n",), (None,), ([],), (StringSubclass("loop"),)):
            with self.subTest(value=invalid), self.assertRaises(ContractError):
                InsertionAnchorV2(**(self.fields() | {"structural_loop_ids": invalid}))

    def test_layer_rejects_boolean_subclass_and_nonpositive(self):
        for invalid in (0, -1, True, 1.0, "1", None, IntSubclass(1)):
            with self.subTest(value=invalid), self.assertRaises(ContractError):
                InsertionAnchorV2(**(self.fields() | {"layer_index": invalid}))

    def test_tolerance_finite_positive_binary64(self):
        for invalid in (0, -0.0, -1, True, None, "0.1", math.nan, math.inf,
                        -math.inf, 10**400, FloatSubclass(0.1), IntSubclass(1)):
            with self.subTest(type=type(invalid)), self.assertRaises(ContractError):
                InsertionAnchorV2(**(self.fields() | {"matching_tolerance_mm": invalid}))
        for valid in (1, 0.1, math.ulp(0.0)):
            self.assertEqual(InsertionAnchorV2(**(self.fields() | {
                "matching_tolerance_mm": valid})).matching_tolerance_mm, valid)

    def test_unknown_schema_is_typed_rejection(self):
        with self.assertRaises(ContractError) as raised:
            InsertionAnchorV2(**(self.fields() | {
                "boundary_signature_schema_version": "opaque_boundary_signature_v2"}))
        self.assertEqual(raised.exception.reason, ReasonCode.UNKNOWN_IDENTITY_SCHEMA)

    def test_no_projection_and_v1_anchor_unchanged(self):
        with self.assertRaises(ContractError):
            semantic_tree(InsertionAnchorV2(**self.fields()))
        self.assertEqual(semantic_tree(InsertionAnchor("a", ("l",), 1, "s")), {
            "anchor_id": "a", "structural_loop_ids": ["l"],
            "layer_index": 1, "boundary_signature": "s"})


if __name__ == "__main__":
    unittest.main()
