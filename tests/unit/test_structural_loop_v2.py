"""Exact predicate checks at magnitudes that defeat float area comparisons."""
import dataclasses
import math
import unittest

from adaptive_subedge.application.serialization import semantic_tree
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.geometry import PrintPoint3, StructuralLoopReference
from adaptive_subedge.domain.structural_loop_v2 import StructuralLoopReferenceV2


class StructuralLoopV2Tests(unittest.TestCase):
    def fields(self, points=None):
        points = points or (PrintPoint3(0, 0, 0), PrintPoint3(2, 0, 0), PrintPoint3(0, 2, 0))
        coordinates = tuple((p.x_mm, p.y_mm, p.z_mm) for p in points)
        return dict(loop_id="loop", points=points, seam_gap_allowance_mm=0,
                    loop_length_mm=7.0,
                    bounds_print_space_mm=tuple(v for i in range(3)
                        for v in (min(p[i] for p in coordinates), max(p[i] for p in coordinates))),
                    coordinate_frame="centered_printobject_mm_v1", winding_orientation="unknown",
                    winding_policy_version="declared_xy_winding_v1",
                    material_side_policy_version="unverified-research-policy",
                    matching_anchor_points_print_space_mm=points,
                    anchor_predicate_version="exact_binary64_cross_product_v1",
                    shape_canonicalization_version="unverified-research-shape", canonical_shape_hash="a" * 64)

    def reject(self, **changes):
        with self.assertRaises(ContractError):
            StructuralLoopReferenceV2(**(self.fields() | changes))

    def test_immutable_required_fields_and_order(self):
        fields = self.fields()
        loop = StructuralLoopReferenceV2(**fields)
        self.assertEqual(loop.points, fields["points"])
        self.assertEqual(len(dataclasses.fields(loop)), 13)
        for name in fields:
            with self.subTest(name=name), self.assertRaises(TypeError):
                StructuralLoopReferenceV2(**{k: v for k, v in fields.items() if k != name})
        with self.assertRaises(dataclasses.FrozenInstanceError):
            loop.loop_id = "other"
        self.assertFalse(hasattr(loop, "validated"))

    def test_duplicate_points_and_explicit_closure_reject(self):
        points = self.fields()["points"]
        for bad in ((), [], list(points), points + (points[0],), (points[0],) * 3,
                    (None, points[1], points[2])):
            self.reject(points=bad)
            self.reject(matching_anchor_points_print_space_mm=bad)

    def test_bounds_exact_ordered_and_anchors_inside(self):
        for bad in ((), [0, 2, 0, 2, 0, 0], (0, 3, 0, 2, 0, 0),
                    (2, 0, 0, 2, 0, 0), (0, math.inf, 0, 2, 0, 0),
                    (False, 2, 0, 2, 0, 0)):
            self.reject(bounds_print_space_mm=bad)
        self.reject(matching_anchor_points_print_space_mm=(
            PrintPoint3(0, 0, 0), PrintPoint3(2, 0, 0), PrintPoint3(0, 3, 0)))

    def test_exact_collinearity_and_later_noncollinear_anchor(self):
        collinear = (PrintPoint3(0, 0, 0), PrintPoint3(1, 0, 0), PrintPoint3(2, 0, 0))
        self.reject(matching_anchor_points_print_space_mm=collinear)
        StructuralLoopReferenceV2(**(self.fields() | {
            "matching_anchor_points_print_space_mm": collinear + (PrintPoint3(0, 1, 0),)}))

    def test_exact_predicate_handles_subnormal_extreme_and_3d(self):
        tiny = math.ulp(0.0)
        for points in ((PrintPoint3(0, 0, 0), PrintPoint3(tiny, 0, 0), PrintPoint3(0, tiny, 0)),
                       (PrintPoint3(-1e308, 0, 0), PrintPoint3(1e308, 0, 0), PrintPoint3(0, 1e308, 0)),
                       (PrintPoint3(0, 0, 0), PrintPoint3(0, 0, 1), PrintPoint3(0, 1, 0))):
            with self.subTest(points=points):
                StructuralLoopReferenceV2(**self.fields(points))

    def test_duplicate_after_binary64_conversion_reject(self):
        points = (PrintPoint3(2**54, 0, 0), PrintPoint3(2**54 + 1, 0, 0), PrintPoint3(0, 1, 0))
        with self.assertRaises(ContractError):
            StructuralLoopReferenceV2(**self.fields(points))

    def test_metadata_versions_digest_and_numbers(self):
        fields = self.fields()
        for key, value in fields.items():
            if type(value) is str:
                for bad in (None, "", " \t", 3):
                    self.reject(**{key: bad})
        for key in ("coordinate_frame", "winding_policy_version", "anchor_predicate_version", "winding_orientation"):
            self.reject(**{key: "not-supported"})
        for bad in ("a" * 63, "A" * 64, "z" * 64):
            self.reject(canonical_shape_hash=bad)
        for bad in (True, -1, math.inf, math.nan, 10**400):
            self.reject(loop_length_mm=bad)
            self.reject(seam_gap_allowance_mm=bad)
        self.reject(loop_length_mm=0)

    def test_standalone_not_canonical_and_v1_projection_unchanged(self):
        with self.assertRaises(ContractError):
            semantic_tree(StructuralLoopReferenceV2(**self.fields()))
        old = StructuralLoopReference("loop", self.fields()["points"], 0, "legacy")
        self.assertEqual(set(semantic_tree(old)), {"loop_id", "points", "seam_gap_allowance_mm", "canonical_shape_hash"})


if __name__ == "__main__":
    unittest.main()
