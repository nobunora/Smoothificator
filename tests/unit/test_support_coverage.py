"""Actual-bead adaptive fixtures; these values are not printer recommendations."""
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F
import math
import unittest
from unittest.mock import patch

from adaptive_subedge.application.serialization import semantic_tree, identity_root
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint2, PrintPoint3
from adaptive_subedge.domain.settings import CandidateBeadBounds, SupportCoverageThresholds, SupportRefinementPolicy
from adaptive_subedge.domain.settings_v2 import SupportQueryNumericPolicy
from adaptive_subedge.domain.support_cell import NominalSupportSegment, SupportCellQueryPolicy
from adaptive_subedge.domain.support_coverage import AdaptiveSupportResult, SupportCoverageSnapshot, SupportFootprint
from adaptive_subedge.engine import support_coverage as engine


def source(name="base", start=(-1, 0, 1), end=(3, 0, 1), width=2, height=0.5):
    return NominalSupportSegment(name, PrintPoint3(*start), PrintPoint3(*end), width, height, "structural", 0)


class AdaptiveSupportTests(unittest.TestCase):
    def setUp(self):
        self.footprint = SupportFootprint(PrintPoint2(0, 0), PrintPoint2(2, 0), 1, 1.5, 10)
        self.refinement = SupportRefinementPolicy(2, 2, 0, 0, 5, 1/32)
        self.options = dict(bead_bounds=CandidateBeadBounds(0.25, 0.75, 0.125, 8),
                            thresholds=SupportCoverageThresholds(1, 1), refinement_policy=self.refinement,
                            numeric_policy=SupportQueryNumericPolicy("support_query_length_v1", 1e-12),
                            query_policy=SupportCellQueryPolicy("nominal_bead_cell_bounds_v1", 48, 16),
                            max_cells=2000, cancelled=lambda: False)

    def run_query(self, sources=None, footprint=None, **changes):
        return engine.evaluate_support_coverage(footprint or self.footprint,
            (source(),) if sources is None else sources, **(self.options | changes))

    def seams(self):
        return (source("left", (0, 0, 1), (1, 0, 1)), source("right", (1, 0, 1), (2, 0, 1)))

    def test_full_support_needs_two_passes_and_preserves_proof(self):
        result = self.run_query(max_cells=1)
        self.assertEqual((result.state, result.reason, result.levels_completed, result.cells_evaluated),
                         ("numerically-supported", "converged", 2, 1))
        self.assertEqual(result.metrics, SupportCoverageSnapshot(F(1), F(1), F(1, 2), F(1, 2), F(0), 1))
        one = self.run_query(refinement_policy=replace(self.refinement, max_support_refinement_levels=1))
        self.assertEqual((one.state, one.reason, one.levels_completed), ("incomplete", "max-levels", 1))

    def test_seam_refines_then_converges_at_final_allowed_pass(self):
        policy = replace(self.refinement, max_support_refinement_levels=3)
        result = self.run_query(self.seams(), refinement_policy=policy)
        self.assertEqual((result.state, result.levels_completed, result.cells_evaluated),
                         ("numerically-supported", 3, 3))
        self.assertEqual(result.metrics.supported_area_fraction_lower_bound, 1)
        self.assertEqual(result, self.run_query(tuple(reversed(self.seams())), refinement_policy=policy))

    def test_narrow_slit_never_becomes_full_support(self):
        sources = (source("left", (0, 0, 1), (31/32, 0, 1)), source("right", (33/32, 0, 1), (2, 0, 1)))
        result = self.run_query(sources)
        self.assertEqual(result.state, "incomplete")
        self.assertLessEqual(result.metrics.supported_area_fraction_lower_bound, F(31, 32))
        self.assertEqual(result.metrics.minimum_contiguous_support_width_lower_bound_mm, 0)
        self.assertGreater(result.metrics.unresolved_area_fraction, 0)
        relaxed = self.run_query(sources, thresholds=SupportCoverageThresholds(0, 0))
        self.assertEqual(relaxed.state, "incomplete")

    def test_equal_area_disconnected_support_has_smaller_width(self):
        policy = replace(self.refinement, initial_support_cell_size_mm=0.25, max_support_refinement_levels=1)
        continuous = (source(width=0.5, height=0.125),)
        disconnected = (source("a", (-1, -0.375, 1), (3, -0.375, 1), 0.25, 0.125),
                        source("b", (-1, 0.375, 1), (3, 0.375, 1), 0.25, 0.125))
        a = self.run_query(continuous, refinement_policy=policy).metrics
        b = self.run_query(disconnected, refinement_policy=policy).metrics
        self.assertEqual((a.supported_area_fraction_lower_bound, b.supported_area_fraction_lower_bound), (F(1, 2), F(1, 2)))
        self.assertEqual((a.minimum_contiguous_support_width_lower_bound_mm, b.minimum_contiguous_support_width_lower_bound_mm), (F(1, 2), F(1, 4)))

    def test_rotated_frame_and_reversal(self):
        footprint = replace(self.footprint, end=PrintPoint2(1, 1), width_mm=0.5)
        sources = (source(start=(-4, -4, 1), end=(5, 5, 1), width=8, height=1),)
        kwargs = dict(thresholds=SupportCoverageThresholds(1, 0.5))
        result = self.run_query(sources, footprint, **kwargs)
        self.assertEqual(result.state, "numerically-supported")
        self.assertEqual((result.metrics.supported_area_fraction_lower_bound,
                          result.metrics.minimum_contiguous_support_width_lower_bound_mm), (1, F(1, 2)))
        reversed_source = replace(sources[0], start=sources[0].end, end=sources[0].start)
        self.assertEqual(result, self.run_query((reversed_source,), replace(footprint, start=footprint.end, end=footprint.start), **kwargs))

    def test_high_partial_obstruction_prevents_success(self):
        sources = (source(), source("high", (0.75, 0, 11/8), (1.25, 0, 11/8), 1, 0.25))
        result = self.run_query(sources)
        self.assertNotEqual(result.state, "numerically-supported")
        self.assertLess(result.metrics.supported_area_fraction_lower_bound, 1)

    def test_empty_coverage_cannot_pass_zero_thresholds(self):
        result = self.run_query((), thresholds=SupportCoverageThresholds(0, 0))
        self.assertEqual((result.state, result.reason), ("numerically-rejected", "thresholds-failed"))
        self.assertIsNone(result.metrics.minimum_effective_height_lower_bound_mm)
        self.assertEqual(result.metrics.supported_area_fraction_lower_bound, 0)

    def test_cumulative_budget_preserves_last_complete_snapshot(self):
        initial = self.run_query(max_cells=31, refinement_policy=replace(self.refinement, initial_support_cell_size_mm=0.25))
        self.assertEqual((initial.reason, initial.cells_evaluated, initial.levels_completed), ("resource-limit", 0, 0))
        self.assertIsNone(initial.metrics)
        partial = self.run_query(self.seams(), max_cells=2)
        self.assertEqual((partial.reason, partial.cells_evaluated, partial.levels_completed), ("resource-limit", 1, 1))
        self.assertEqual(partial.metrics.unresolved_area_fraction, 1)

    def test_noninteger_factor_and_minimum_blocked_cells(self):
        policy = replace(self.refinement, support_refinement_factor=1.5)
        self.assertEqual(self.run_query(self.seams(), refinement_policy=policy).state, "numerically-supported")
        blocked = replace(self.refinement, minimum_support_cell_size_mm=2, max_support_refinement_levels=4)
        result = self.run_query(self.seams(), refinement_policy=blocked)
        self.assertEqual((result.reason, result.levels_completed, result.cells_evaluated), ("max-levels", 4, 4))
        self.assertEqual(result.metrics.unresolved_area_fraction, 1)

    def test_large_factor_and_tiny_increment_stay_bounded(self):
        huge = replace(self.refinement, support_refinement_factor=1e308, max_support_refinement_levels=10**9)
        result = self.run_query(self.seams(), refinement_policy=huge, max_cells=4)
        self.assertEqual((result.reason, result.cells_evaluated), ("resource-limit", 4))
        tiny = replace(self.refinement, support_refinement_factor=math.nextafter(1, 2), max_support_refinement_levels=10**9)
        result = self.run_query(self.seams(), refinement_policy=tiny, max_cells=1)
        self.assertEqual(result.reason, "resource-limit")

    def test_directed_binary64_rounding(self):
        for value in (F(1, 3), F(-1, 3), F(1, 2**1200), F(-1, 2**1200), F(1, 2)):
            self.assertLessEqual(F(engine._outward(value, False)), value)
            self.assertGreaterEqual(F(engine._outward(value, True)), value)

    def test_nonrepresentable_world_cell_reports_incomplete(self):
        footprint = SupportFootprint(PrintPoint2(1.7e308, 0), PrintPoint2(1.7e308, 1), 1e308, 1.5, 10)
        result = self.run_query(footprint=footprint,
            bead_bounds=CandidateBeadBounds(0.25, 0.75, 0.125, 1.5e308),
            refinement_policy=replace(self.refinement, initial_support_cell_size_mm=1e308))
        self.assertEqual((result.reason, result.levels_completed, result.cells_evaluated), ("coordinate-range", 0, 0))

    def test_cancellation_midpass_discards_partial_metrics(self):
        self.assertEqual(self.run_query(cancelled=lambda: True).reason, "cancelled")
        original = engine.query_nominal_support_cell
        calls = 0
        def query(*args, **kwargs):
            nonlocal calls
            outcome = original(*args, **kwargs)
            calls += 1
            return outcome
        with patch.object(engine, "query_nominal_support_cell", query):
            result = self.run_query(self.seams(), cancelled=lambda: calls >= 2)
        self.assertEqual((result.reason, result.levels_completed, result.cells_evaluated), ("cancelled", 1, 2))
        self.assertEqual(result.metrics.unresolved_area_fraction, 1)
        self.assertEqual(result.metrics.supported_area_fraction_lower_bound, 0)

    def test_cancel_callback_type_and_exception(self):
        with self.assertRaises(ContractError) as error:
            self.run_query(cancelled=lambda: 1)
        self.assertIs(error.exception.reason, ReasonCode.INVALID_SETTING)
        def fail():
            raise RuntimeError("caller cancellation failure")
        with self.assertRaisesRegex(RuntimeError, "caller cancellation failure"):
            self.run_query(cancelled=fail)

    def test_source_limit_and_chronology_remain_cell_owned(self):
        result = self.run_query((None, None), query_policy=replace(self.options["query_policy"], max_source_segments=1))
        self.assertEqual((result.reason, result.cells_evaluated), ("resource-limit", 1))
        with self.assertRaises(ContractError):
            self.run_query((replace(source(), execution_order=10),))
        with self.assertRaises(ContractError):
            self.run_query((None,))

    def test_types_required_fields_immutability_and_identity_exclusion(self):
        result = self.run_query()
        for value in (self.footprint, result.metrics, result):
            for omitted in fields(value):
                arguments = {f.name: getattr(value, f.name) for f in fields(value) if f != omitted}
                with self.assertRaises(TypeError):
                    type(value)(**arguments)
            with self.assertRaises(FrozenInstanceError):
                setattr(value, fields(value)[0].name, None)
            with self.assertRaises(ContractError):
                semantic_tree(value)
            with self.assertRaises(ContractError):
                identity_root("subedge-plan", value, schema_version="2")
        for change in ({"max_cells": True}, {"cancelled": None}, {"bead_bounds": {}}, {"numeric_policy": {}}):
            with self.assertRaises(ContractError) as error:
                self.run_query(**change)
            self.assertIs(error.exception.reason, ReasonCode.INVALID_SETTING)
        for change in ({"width_mm": True}, {"command_z_mm": math.inf}, {"execution_order": True}, {"end": self.footprint.start}):
            with self.assertRaises(ContractError):
                replace(self.footprint, **change)

    def test_snapshot_and_result_reject_invalid_shapes(self):
        good = self.run_query()
        for change in ({"unresolved_area_fraction": F(1)}, {"supported_area_fraction_lower_bound": 1.0},
                       {"leaf_count": True}, {"maximum_effective_height_upper_bound_mm": None}):
            with self.assertRaises(ContractError):
                replace(good.metrics, **change)
        for change in ({"state": "validated"}, {"levels_completed": 1}, {"metrics": None}, {"reason": "cancelled"}):
            with self.assertRaises(ContractError):
                replace(good, **change)


if __name__ == "__main__":
    unittest.main()
