"""Exact equal-band research geometry boundary checks."""
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.engine import convex_chords as engine
from adaptive_subedge.engine.material_side import _Stopped
from tests.unit.test_convex_chords import prism
from tests.unit.test_mesh_topology import cube


class ConvexBandTests(unittest.TestCase):
    def propose(self, mesh=None, **changes):
        args = dict(axis="X", span_min_mm=0, span_max_mm=1,
                    minimum_width_mm=0.25, maximum_width_mm=0.375,
                    display_height_mm=0.125, end_trim_mm=0.125,
                    algorithm_version="convex_equal_bands_v1", max_chords=64,
                    max_vertices=100, max_triangles=100, max_mesh_pair_checks=1000,
                    max_section_segments=100, max_section_pair_checks=1000,
                    max_ray_directions=8, cancelled=lambda: False)
        return engine.propose_convex_band_preview(cube() if mesh is None else mesh,
                                                  0.5, **(args | changes))

    def test_rational_partition_and_fresh_once_axis_parity(self):
        for axis in ("X", "Y"):
            with patch.object(engine, "_embedding", wraps=engine._embedding) as embedding:
                result = self.propose(axis=axis)
            self.assertEqual(embedding.call_count, 1)
            self.assertEqual(result.width_mm, F(1, 3))
            self.assertEqual(tuple(r.position_mm for r in result.proposals),
                             (F(1, 6), F(1, 2), F(5, 6)))
            self.assertEqual(result.common_running_interval, (F(1, 8), F(7, 8)))
            self.assertEqual(result.proposals[0].position_mm-result.width_mm/2, 0)
            self.assertEqual(result.proposals[-1].position_mm+result.width_mm/2, 1)

    def test_width_equality_single_band_and_height(self):
        result = self.propose(minimum_width_mm=1, maximum_width_mm=1, display_height_mm=1)
        self.assertEqual((result.width_mm, len(result.proposals)), (F(1), 1))
        self.assertEqual(self.propose(display_height_mm=0.375).reason, "width-span-infeasible")
        self.assertEqual(self.propose(minimum_width_mm=0.625,
                                     maximum_width_mm=0.75).reason, "width-span-infeasible")

    def test_budget_and_infeasibility_precede_mesh(self):
        with patch.object(engine, "_embedding", side_effect=AssertionError("mesh read")):
            self.assertEqual(self.propose(max_chords=2).reason, "resource-limit")
            self.assertEqual(self.propose(display_height_mm=1).reason, "width-span-infeasible")

    def test_rejected_band_discards_all(self):
        result = self.propose(span_max_mm=1.25)
        self.assertEqual((result.state, result.reason), ("rejected", "band-chord-rejected"))
        self.assertEqual((result.proposals, result.section, result.width_mm), ((), None, None))

    def test_no_common_interval_for_slanted_convex_strip(self):
        mesh = prism(((0, 0), (1, 0), (5, 1), (4, 1)), ((0, 1, 2), (0, 2, 3)))
        result = self.propose(mesh, minimum_width_mm=0.125, maximum_width_mm=0.125,
                              end_trim_mm=0.0625)
        self.assertEqual(result.reason, "no-common-running-span")
        self.assertIsNone(result.common_running_interval)

    def test_cancel_unknown_and_final_return_checkpoint(self):
        self.assertEqual(self.propose(cancelled=lambda: True).reason, "cancelled")
        with patch.object(engine, "_propose", side_effect=_Stopped("incomplete", "ray-directions-exhausted")):
            result = self.propose()
        self.assertEqual((result.reason, result.proposals), ("ray-directions-exhausted", ()))
        calls = 0
        def cancelled():
            nonlocal calls
            calls += 1
            return calls == 2
        self.assertEqual(self.propose(display_height_mm=1, cancelled=cancelled).reason, "cancelled")

    def test_closed_dto_and_invalid_inputs(self):
        result = self.propose()
        for changes in (dict(common_running_interval=(F(0), F(1))), dict(width_mm=F(1, 4)),
                        dict(command_z_mm=0.5), dict(proposals=()), dict(reason="feasible")):
            with self.assertRaises(ContractError):
                replace(result, **changes)
        for changes in (dict(minimum_width_mm=True), dict(span_max_mm=float("inf")),
                        dict(span_max_mm=0), dict(max_chords=True), dict(algorithm_version="future")):
            with self.assertRaises(ContractError):
                self.propose(**changes)
