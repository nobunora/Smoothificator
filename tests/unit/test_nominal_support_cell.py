"""Analytic stadium-sweep fixtures independent of the provider's interval arithmetic."""
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F
import math
import unittest

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.domain.support_cell import NominalSupportSegment, SupportCellQueryPolicy, SupportCellQueryResult, SupportCellXY
from adaptive_subedge.engine.support_cell import _sqrt_bounds, query_nominal_support_cell


def segment(name="base", start=(0, 0, 1), end=(4, 0, 1), width=2, height=1, kind="structural", order=0):
    return NominalSupportSegment(name, PrintPoint3(*start), PrintPoint3(*end), width, height, kind, order)


class NominalSupportCellTests(unittest.TestCase):
    def setUp(self):
        self.cell = SupportCellXY(1, 2, -0.25, 0.25)
        self.policy = SupportCellQueryPolicy("nominal_bead_cell_bounds_v1", 32, 16)
        self.bounds = CandidateBeadBounds(0.25, 0.75, 0.125, 4)

    def query(self, sources, cell=None, **changes):
        kwargs = dict(command_z_mm=1.5, execution_order=10, height_bounds=self.bounds, policy=self.policy)
        return query_nominal_support_cell(cell or self.cell, sources, **(kwargs | changes))

    def reject(self, call, reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure:
            call()
        self.assertIs(failure.exception.reason, reason)

    def test_flat_center_exact_even_low_precision(self):
        result = self.query((segment(),), policy=replace(self.policy, sqrt_fraction_bits=1))
        self.assertEqual(result, SupportCellQueryResult("proven-supported", F(1), F(1), F(1, 2), F(1, 2), "height-within-bounds"))
        # Radius is not representable on the selected coarse square-root grid.
        result = self.query((segment(height=0.6),), policy=replace(self.policy, sqrt_fraction_bits=1))
        self.assertEqual((result.top_z_lower_mm, result.top_z_upper_mm), (F(1), F(1)))

    def test_rotated_segment_exact_affine_coverage(self):
        rotated = segment(end=(3, 4, 1))
        cell = SupportCellXY(11/8, 13/8, 15/8, 17/8)
        result = self.query((rotated,), cell)
        self.assertEqual(result.state, "proven-supported")
        self.assertEqual((result.top_z_lower_mm, result.top_z_upper_mm), (F(1), F(1)))
        self.assertEqual(result, self.query((replace(rotated, start=rotated.end, end=rotated.start),), cell))

    def test_flat_caps_disjoint_crossing_and_closed_endpoint(self):
        empty = self.query((segment(),), SupportCellXY(-0.25, -0.125, -0.125, 0.125))
        self.assertEqual((empty.state, empty.reason), ("proven-unsupported", "disjoint"))
        partial = self.query((segment(),), SupportCellXY(-0.125, 0.125, -0.125, 0.125))
        self.assertEqual((partial.state, partial.reason), ("unresolved", "coverage-unresolved"))
        self.assertIsNone(partial.top_z_lower_mm)
        touching = self.query((segment(),), SupportCellXY(-0.125, 0, -0.125, 0.125))
        self.assertEqual(touching.reason, "coverage-unresolved")
        self.assertEqual(self.query((segment(),), SupportCellXY(0, 0.125, -0.125, 0.125)).state, "proven-supported")

    def test_curved_side_bounds_enclose_independent_radicals(self):
        result = self.query((segment(),), SupportCellXY(1, 2, 0.75, 0.875),
            command_z_mm=1.25, height_bounds=CandidateBeadBounds(0.25, 0.5, 0.125, 4))
        self.assertEqual(result.state, "proven-supported")
        # True min/max tops are 1/2+sqrt(7/64), 1/2+sqrt(3/16).
        lower_offset, upper_offset = result.top_z_lower_mm - F(1, 2), result.top_z_upper_mm - F(1, 2)
        self.assertGreaterEqual(lower_offset, 0)
        self.assertLessEqual(lower_offset**2, F(7, 64))
        self.assertGreaterEqual(upper_offset**2, F(3, 16))
        self.assertLessEqual(result.top_z_upper_mm, 1)
        self.assertEqual(result.effective_height_lower_mm, F(5, 4) - result.top_z_upper_mm)
        self.assertEqual(result.effective_height_upper_mm, F(5, 4) - result.top_z_lower_mm)

    def test_circle_side_boundary_and_mixed_height(self):
        circle = segment(width=1, height=1)
        cell = SupportCellXY(1, 2, 3/8, 1/2)
        result = self.query((circle,), cell, command_z_mm=1.25,
            height_bounds=CandidateBeadBounds(0.25, 1, 0.125, 4))
        self.assertEqual(result.state, "proven-supported")
        self.assertEqual(result.top_z_lower_mm, F(1, 2))
        self.assertGreaterEqual((result.top_z_upper_mm - F(1, 2))**2, F(7, 64))
        mixed = self.query((circle,), cell, command_z_mm=1.25,
            height_bounds=CandidateBeadBounds(0.25, 0.5, 0.125, 4))
        self.assertEqual((mixed.state, mixed.reason), ("unresolved", "height-unresolved"))

    def test_sloped_locus_inclusive_heights_and_reversal(self):
        source = segment(start=(0, 0, 0.5), end=(4, 0, 1.5))
        settings = dict(command_z_mm=2, height_bounds=CandidateBeadBounds(1, 1.25, 0.125, 4))
        result = self.query((source,), **settings)
        self.assertEqual((result.top_z_lower_mm, result.top_z_upper_mm), (F(3, 4), F(1)))
        self.assertEqual((result.effective_height_lower_mm, result.effective_height_upper_mm), (F(1), F(5, 4)))
        self.assertEqual(result.state, "proven-supported")
        self.assertEqual(result, self.query((replace(source, start=source.end, end=source.start),), **settings))

    def test_partial_high_overlap_not_ignored(self):
        high = segment("high", (1.5, 0, 11/8), (3, 0, 11/8), 1, 0.25)
        result = self.query((segment(), high))
        self.assertEqual((result.state, result.reason), ("unresolved", "height-unresolved"))
        self.assertEqual((result.top_z_lower_mm, result.top_z_upper_mm), (F(1), F(11, 8)))
        self.assertEqual(result.effective_height_lower_mm, F(1, 8))
        self.assertEqual(result, self.query((high, segment())))
        full = replace(high, start=PrintPoint3(0, 0, 11/8), end=PrintPoint3(4, 0, 11/8))
        self.assertEqual(self.query((segment(), full)).state, "proven-unsupported")

    def test_full_coverage_suffices_despite_lower_partial_source(self):
        low = segment("low", (1.5, 0, 0.75), (3, 0, 0.75), 1, 0.25)
        self.assertEqual(self.query((segment(), low)), self.query((segment(),)))

    def test_seam_only_union_stays_unresolved_until_partitioned(self):
        sources = (segment("left", end=(1, 0, 1)), segment("right", start=(1, 0, 1), end=(2, 0, 1)))
        cell = SupportCellXY(0.5, 1.5, -0.25, 0.25)
        result = self.query(sources, cell)
        self.assertEqual(result.reason, "coverage-unresolved")
        self.assertIsNone(result.effective_height_upper_mm)
        for part in (replace(cell, x_max_mm=1), replace(cell, x_min_mm=1)):
            self.assertEqual(self.query(sources, part).state, "proven-supported")

    def test_empty_too_low_and_signed_obstructing_heights(self):
        self.assertEqual(self.query(()).reason, "disjoint")
        self.assertEqual(self.query((segment(),), command_z_mm=3).reason, "height-outside-bounds")
        high = segment(start=(0, 0, 2), end=(4, 0, 2))
        result = self.query((high,))  # Earlier structural material is never discarded for high Z.
        self.assertEqual(result.state, "proven-unsupported")
        self.assertEqual(result.effective_height_lower_mm, F(-1, 2))

    def test_sqrt_exact_rational_enclosures_and_precision_tightening(self):
        fixtures = ((F(2), F(362, 256), F(363, 256)), (F(7, 64), F(84, 256), F(85, 256)),
                    (F(3, 16), F(110, 256), F(111, 256)), (F(9, 16), F(3, 4), F(3, 4)), (F(0), F(0), F(0)))
        for value, lower, upper in fixtures:
            self.assertEqual(_sqrt_bounds(value, 8), (lower, upper))
            finer = _sqrt_bounds(value, 16)
            self.assertTrue(lower <= finer[0] <= finer[1] <= upper)
            self.assertTrue(finer[0]**2 <= value <= finer[1]**2)
        cell = SupportCellXY(1, 2, 0.75, 0.875)
        results = [self.query((segment(),), cell, policy=replace(self.policy, sqrt_fraction_bits=b)) for b in (4, 8, 16, 32)]
        for coarse, fine in zip(results, results[1:]):
            self.assertLessEqual(coarse.top_z_lower_mm, fine.top_z_lower_mm)
            self.assertGreaterEqual(coarse.top_z_upper_mm, fine.top_z_upper_mm)

    def test_extreme_and_subnormal_geometry_uses_exact_predicates(self):
        huge = segment(start=(-1e308, 0, 1), end=(1e308, 0, 1))
        self.assertEqual(self.query((huge,)).state, "proven-supported")
        tiny = math.ulp(0.0)
        source = segment(start=(0, 0, 1), end=(4*tiny, 0, 1), width=4*tiny, height=tiny)
        result = self.query((source,), SupportCellXY(tiny, 2*tiny, 0, tiny))
        self.assertEqual(result.state, "proven-supported")
        self.assertEqual(result.top_z_lower_mm, F(1))

    def test_chronology_unique_ids_and_candidate_constant_z(self):
        for sources in ((segment(order=10),), (segment(order=11),), (segment(), segment())):
            self.reject(lambda: self.query(sources))
        self.reject(lambda: self.query((segment(kind="candidate", start=(0, 0, 1.5), end=(4, 0, 1.5)),)))
        self.assertEqual(self.query((segment(kind="candidate"),)).state, "proven-supported")
        self.reject(lambda: segment(kind="candidate", end=(4, 0, 1.25)))

    def test_resource_precedence_never_produces_success(self):
        policy = replace(self.policy, max_source_segments=1)
        # Count checked before deliberately malformed elements, IDs or chronology.
        result = self.query((None, None), policy=policy)
        self.assertEqual(result, SupportCellQueryResult("unresolved", None, None, None, None, "resource-limit"))
        self.reject(lambda: self.query((None,), policy=policy))
        self.reject(lambda: self.query((None, None), policy=policy, execution_order=True))
        self.reject(lambda: self.query((None, None), policy=policy, command_z_mm=math.inf))
        self.reject(lambda: self.query((None, None), policy=policy, height_bounds={}), ReasonCode.INVALID_SETTING)

    def test_invalid_domain_inputs_and_exact_query_types(self):
        for value in (True, math.inf, math.nan, 10**400, "1"):
            self.reject(lambda: SupportCellXY(value, 2, 0, 1))
            self.reject(lambda: segment(width=value))
        for cell in ((0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 1, 1)):
            self.reject(lambda: SupportCellXY(*cell))
        self.reject(lambda: segment(end=(0, 0, 2)))
        self.reject(lambda: segment(width=0.5, height=1))
        self.reject(lambda: self.query([segment()]))
        for change in ({"sqrt_fraction_bits": 0}, {"sqrt_fraction_bits": 4097}, {"sqrt_fraction_bits": True},
                       {"max_source_segments": 0}, {"max_source_segments": True}, {"version": "other"}):
            self.reject(lambda: replace(self.policy, **change), ReasonCode.INVALID_SETTING)
        class CellSubclass(SupportCellXY):
            pass
        self.reject(lambda: self.query((segment(),), CellSubclass(1, 2, -0.25, 0.25)))

    def test_dtos_required_frozen_and_excluded_from_identity(self):
        values = (self.cell, segment(), self.policy, self.query((segment(),)))
        for value in values:
            self.assertFalse(hasattr(value, "__dict__"))
            for omitted in fields(value):
                arguments = {f.name: getattr(value, f.name) for f in fields(value) if f != omitted}
                with self.assertRaises(TypeError):
                    type(value)(**arguments)
            with self.assertRaises(FrozenInstanceError):
                setattr(value, fields(value)[0].name, None)
            with self.assertRaises(ContractError):
                semantic_tree(value)
            for domain in ("subedge-plan", "plugin-settings"):
                with self.assertRaises(ContractError):
                    identity_root(domain, value, schema_version="2")

    def test_result_shape_rejects_invented_or_inconsistent_bounds(self):
        good = self.query((segment(),))
        for change in ({"state": "validated"}, {"reason": "resource-limit"}, {"top_z_lower_mm": 1.0},
                       {"top_z_lower_mm": None}, {"top_z_upper_mm": None}, {"top_z_lower_mm": F(2)},
                       {"effective_height_lower_mm": F(2)}, {"reason": "coverage-unresolved"}):
            self.reject(lambda: replace(good, **change))


if __name__ == "__main__":
    unittest.main()
