"""Independent arithmetic fixtures, not recommended physical printer settings."""
import inspect
import math
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.settings import CandidateBeadBounds
from adaptive_subedge.engine.flow_model import (
    bead_width_from_geometric_flow, candidate_geometric_line_flow,
    commanded_external_line_flow, effective_candidate_height, zaa_local_bead,
)


class FlowModelTests(unittest.TestCase):
    def setUp(self):
        self.bounds = CandidateBeadBounds(0.125, 0.5, 0.25, 1.0)
        self.command = dict(print_flow_ratio=1.0, filament_flow_ratio=1.0,
                            set_other_flow_ratios=False, outer_wall_flow_ratio=1.0)

    def rejects(self, function, *args, reason=ReasonCode.INVALID_GEOMETRY, **kwargs):
        with self.assertRaises(ContractError) as failure:
            function(*args, **kwargs)
        self.assertIs(failure.exception.reason, reason)

    def test_independent_stadium_and_circle_examples(self):
        result = candidate_geometric_line_flow(0.2, 0.4, bounds=self.bounds)
        self.assertTrue(math.isclose(result, 0.04 + 0.01 * math.pi, rel_tol=1e-15))
        circle = candidate_geometric_line_flow(0.25, 0.25, bounds=self.bounds)
        self.assertTrue(math.isclose(circle, math.pi * 0.25**2 / 4, rel_tol=1e-15))
        self.assertIs(type(result), float)

    def test_forward_inverse_parity_interior_dimensions(self):
        for height, width in ((0.15, 0.35), (0.2, 0.4), (0.3, 0.6), (0.4, 0.9)):
            q = candidate_geometric_line_flow(height, width, bounds=self.bounds)
            derived = bead_width_from_geometric_flow(height, q)
            self.assertTrue(math.isclose(derived, width, rel_tol=1e-14, abs_tol=1e-15))
            self.assertTrue(math.isclose(candidate_geometric_line_flow(height, derived, bounds=self.bounds), q, rel_tol=1e-14, abs_tol=1e-15))

    def test_candidate_boundaries_are_inclusive_without_tolerance(self):
        for height, width in ((0.125, 0.25), (0.5, 1.0)):
            candidate_geometric_line_flow(height, width, bounds=self.bounds)
        for height, width in ((math.nextafter(0.125, 0), 0.25), (math.nextafter(0.5, math.inf), 1),
                              (0.125, math.nextafter(0.25, 0)), (0.5, math.nextafter(1, math.inf)), (0.5, 0.25)):
            self.rejects(candidate_geometric_line_flow, height, width, bounds=self.bounds)

    def test_exact_bounds_type_and_required_arguments(self):
        class DerivedBounds(CandidateBeadBounds):
            pass
        for bounds in (None, {}, DerivedBounds(0.125, 0.5, 0.25, 1)):
            self.rejects(candidate_geometric_line_flow, 0.2, 0.4, bounds=bounds, reason=ReasonCode.INVALID_SETTING)
            self.rejects(effective_candidate_height, 0.3, 0.1, bounds=bounds, reason=ReasonCode.INVALID_SETTING)
        for function in (candidate_geometric_line_flow, bead_width_from_geometric_flow, zaa_local_bead,
                         effective_candidate_height, commanded_external_line_flow):
            self.assertTrue(all(p.default is inspect.Parameter.empty for p in inspect.signature(function).parameters.values()))

    def test_scalar_types_nonfinite_and_large_integer_reject(self):
        class DerivedFloat(float):
            pass
        class DerivedInt(int):
            pass
        for bad in (True, False, "0.2", None, DerivedFloat(0.2), DerivedInt(1), math.nan, math.inf, -math.inf, 10**400):
            for args in ((bad, 0.4), (0.2, bad)):
                self.rejects(candidate_geometric_line_flow, *args, bounds=self.bounds)
                self.rejects(bead_width_from_geometric_flow, *args)
            self.rejects(zaa_local_bead, 0.2, 0.1, bad)
            self.rejects(effective_candidate_height, bad, 0, bounds=self.bounds)
            self.rejects(effective_candidate_height, 0.25, bad, bounds=self.bounds)
            for field in ("print_flow_ratio", "filament_flow_ratio", "outer_wall_flow_ratio"):
                self.rejects(commanded_external_line_flow, 0.1, **(self.command | {field: bad}))

    def test_nonpositive_and_impossible_cross_sections(self):
        for bad in (0, -0.0, -1):
            self.rejects(candidate_geometric_line_flow, bad, 0.4, bounds=self.bounds)
            self.rejects(candidate_geometric_line_flow, 0.2, bad, bounds=self.bounds)
            self.rejects(bead_width_from_geometric_flow, bad, 0.1)
            self.rejects(bead_width_from_geometric_flow, 0.2, bad)
            self.rejects(zaa_local_bead, bad, 0.1, 0)
            self.rejects(zaa_local_bead, 0.2, bad, 0)
        self.rejects(bead_width_from_geometric_flow, 1, 0.1)

    def test_area_and_inverse_overflow_and_underflow(self):
        tiny = math.ulp(0.0)
        huge_bounds = CandidateBeadBounds(tiny, 1e308, tiny, 1e308)
        self.rejects(candidate_geometric_line_flow, 1e308, 1e308, bounds=huge_bounds)
        self.rejects(candidate_geometric_line_flow, tiny, tiny, bounds=huge_bounds)
        self.rejects(bead_width_from_geometric_flow, tiny, 1e308)
        self.rejects(bead_width_from_geometric_flow, 1e308, tiny)

    def test_zaa_local_height_flow_and_derived_width(self):
        nominal_q = 0.04 + 0.01 * math.pi
        for offset in (-0.05, 0, 0.05):
            height, q, width = zaa_local_bead(0.2, nominal_q, offset)
            self.assertEqual(height, 0.2 + offset)
            self.assertEqual(q, nominal_q * ((0.2 + offset) / 0.2))
            self.assertTrue(math.isclose(height * width - height**2 * (1 - math.pi / 4), q, rel_tol=1e-14))
            self.assertTrue(all(type(x) is float for x in (height, q, width)))
        self.assertNotEqual(zaa_local_bead(0.2, nominal_q, 0.05)[2], 0.4)
        self.assertEqual(zaa_local_bead(0.2, nominal_q, 0)[:2], (0.2, nominal_q))
        # Structural arithmetic has no candidate bounds or calibration parameters.
        self.assertEqual(len(inspect.signature(zaa_local_bead).parameters), 3)
        self.assertGreater(zaa_local_bead(1, 2, 0)[2], self.bounds.max_candidate_width_mm)

    def test_zaa_rejects_nonpositive_height_and_each_invalid_intermediate(self):
        for offset in (-0.2, -0.3):
            self.rejects(zaa_local_bead, 0.2, 0.1, offset)
        self.rejects(zaa_local_bead, 1e308, 1, 1e308)  # height overflow
        self.rejects(zaa_local_bead, math.ulp(0.0), 1, 1)  # ratio overflow
        self.rejects(zaa_local_bead, 1, 1e308, 1)  # local flow overflow
        self.rejects(zaa_local_bead, 1, math.ulp(0.0), -0.75)  # local flow underflow

    def test_effective_height_uses_support_and_explicit_height_bounds(self):
        for command, support in ((0.25, 0), (2.25, 2), (-1.75, -2)):
            self.assertEqual(effective_candidate_height(command, support, bounds=self.bounds), 0.25)
        for height in (0.125, 0.5):
            self.assertEqual(effective_candidate_height(height, 0, bounds=self.bounds), height)
        for command, support in ((0.2, 0.2), (0.1, 0.2), (1e308, -1e308),
                                  (math.nextafter(0.125, 0), 0), (math.nextafter(0.5, math.inf), 0)):
            self.rejects(effective_candidate_height, command, support, bounds=self.bounds)

    def test_commanded_flow_role_toggle_and_geometry_separation(self):
        q = candidate_geometric_line_flow(0.2, 0.4, bounds=self.bounds)
        width = bead_width_from_geometric_flow(0.2, q)
        ratios = self.command | dict(print_flow_ratio=1.2, filament_flow_ratio=0.98, outer_wall_flow_ratio=1.1)
        self.assertEqual(commanded_external_line_flow(q, **ratios), (q * 1.2) * 0.98)
        self.assertEqual(commanded_external_line_flow(q, **(ratios | {"set_other_flow_ratios": True})), ((q * 1.2) * 0.98) * 1.1)
        self.assertEqual(candidate_geometric_line_flow(0.2, 0.4, bounds=self.bounds), q)
        self.assertEqual(bead_width_from_geometric_flow(0.2, q), width)

    def test_commanded_flow_validates_disabled_ratio_bool_and_products(self):
        for bad in (0, 1, None, "true"):
            self.rejects(commanded_external_line_flow, 1, **(self.command | {"set_other_flow_ratios": bad}), reason=ReasonCode.INVALID_SETTING)
        for field in ("print_flow_ratio", "filament_flow_ratio", "outer_wall_flow_ratio"):
            for bad in (0, -1):
                self.rejects(commanded_external_line_flow, 1, **(self.command | {field: bad}))
        for bad in (0, -1, True, math.inf, math.nan, 10**400):
            self.rejects(commanded_external_line_flow, bad, **self.command)
        for field in ("print_flow_ratio", "filament_flow_ratio", "outer_wall_flow_ratio"):
            enabled = self.command | {"set_other_flow_ratios": True}
            self.rejects(commanded_external_line_flow, 1e308, **(enabled | {field: 2}))
            self.rejects(commanded_external_line_flow, math.ulp(0.0), **(enabled | {field: 0.25}))
        # A later tiny multiplier cannot rescue an earlier overflowing product.
        self.rejects(commanded_external_line_flow, 1e308,
            **(self.command | {"print_flow_ratio": 2, "filament_flow_ratio": 1e-308}))

    def test_repeatability_and_builtin_float_outputs(self):
        cases = (lambda: candidate_geometric_line_flow(0.25, 1, bounds=self.bounds),
                 lambda: bead_width_from_geometric_flow(1, 1),
                 lambda: effective_candidate_height(0.25, 0, bounds=self.bounds),
                 lambda: commanded_external_line_flow(1, **self.command))
        for call in cases:
            first = call()
            self.assertIs(type(first), float)
            self.assertEqual(first, call())
        self.assertEqual(zaa_local_bead(1, 1, 0), zaa_local_bead(1, 1, 0))


if __name__ == "__main__":
    unittest.main()
