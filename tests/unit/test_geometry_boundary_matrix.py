"""Five approved immutable geometric value boundaries; no mesh/optimizer algorithms."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import (
    PrintPoint2, PrintPoint3, StructuralLoopReference, StructuralPathSegment,
)
from adaptive_subedge.domain.plan import SubEdgeSegment, SubEdgePath
from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree


class GeometryBoundaryMatrix(unittest.TestCase):
    def test_point2_binary64_contract_and_canonical_int_float_parity(self):
        point = PrintPoint2(1, 2)
        self.assertEqual(canonical_bytes(semantic_tree(point)),
                         canonical_bytes(semantic_tree(PrintPoint2(1.0, 2.0))))
        with self.assertRaises(FrozenInstanceError):
            point.x_mm = 4
        for invalid in (True, None, [1], "1", math.nan, math.inf, -math.inf, 10 ** 400):
            with self.subTest(value=type(invalid).__name__), self.assertRaises(ContractError):
                PrintPoint2(invalid, 0)

    def test_point3_all_axes_reject_nonnumeric_and_nonfinite(self):
        valid = PrintPoint3(-1, 2, 3)
        self.assertEqual(valid.z_mm, 3)
        for field in ("x_mm", "y_mm", "z_mm"):
            for bad in (False, math.inf, float("nan"), 10 ** 400):
                with self.subTest(field=field, bad=type(bad).__name__):
                    data = dict(x_mm=1., y_mm=2., z_mm=3.)
                    data[field] = bad
                    with self.assertRaises(ContractError) as e:
                        PrintPoint3(**data)
                    self.assertEqual(e.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_structural_segment_endpoints_and_positive_bead_dimensions(self):
        start, end = PrintPoint3(0, 0, 0), PrintPoint3(1, 0, 0)
        valid = StructuralPathSegment(start, end, .4, .2, .03, 1., 0, "outer")
        self.assertIs(valid.start, start)
        for field, bad in (("width_mm", 0), ("local_height_mm", -1),
                           ("local_geometric_mm3_per_mm", float("inf")),
                           ("command_flow_modifier", False),
                           ("layer_index", True), ("role", []), ("end", [1, 0, 0])):
            with self.subTest(field=field), self.assertRaises(ContractError):
                replace(valid, **{field: bad})

    def test_structural_loop_immutable_reference_and_malformed_members(self):
        points = (PrintPoint3(0, 0, 0), PrintPoint3(1, 0, 0), PrintPoint3(0, 1, 0))
        valid = StructuralLoopReference("loop-a", points, .02, "synthetic-shape")
        self.assertEqual(valid.points, points)
        for changes in (
            {"points": list(points)}, {"points": points[:2]},
            {"points": (points[0], "mutable", points[2])},
            {"loop_id": ""}, {"canonical_shape_hash": ""},
            {"seam_gap_allowance_mm": -.001},
            {"seam_gap_allowance_mm": 10 ** 400},
        ):
            with self.subTest(fields=tuple(changes)), self.assertRaises(ContractError):
                replace(valid, **changes)

    def test_open_candidate_segment_and_path_continuity_fail_closed(self):
        a, b, c = PrintPoint2(0, 0), PrintPoint2(1, 0), PrintPoint2(2, 0)
        first = SubEdgeSegment(a, b, .2, .1, .1, .4, .03, .03, 25.)
        second = replace(first, start_xy=b, end_xy=c)
        valid = SubEdgePath("path-a", "interval-a", .2, .01, 0, (first, second))
        self.assertEqual(len(valid.segments), 2)
        for bad in (
            {"segments": (first, replace(second, start_xy=a))},
            {"segments": (first, replace(second, command_z_mm=.3))},
            {"support_dependency_path_ids": ("support-a", "support-a")},
            {"execution_order": True}, {"planned_seam_gap_mm": -.01},
        ):
            with self.subTest(fields=tuple(bad)), self.assertRaises(ContractError):
                replace(valid, **bad)
        for field, bad in (
            ("end_xy", a), ("width_mm", .05), ("requested_speed_mm_s", 0),
            ("commanded_mm3_per_mm", math.nan),
        ):
            with self.subTest(segment=field), self.assertRaises(ContractError):
                replace(first, **{field: bad})


if __name__ == "__main__":
    unittest.main()
