"""ADR-0045/0050 research-only estimator and local surface correspondence DTOs."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.settings import SurfaceCorrespondencePolicy, ErrorEstimatorConfig
from adaptive_subedge.application.serialization import canonical_bytes, semantic_tree


def correspondence():
    return SurfaceCorrespondencePolicy(
        version="research-v1", max_surface_correspondence_distance_mm=0.5,
        min_surface_normal_dot=0.75,
        interaction_neighborhood_expansion_mm=0.01,
        interaction_neighborhood_tolerance_mm=0.005,
        normal_ray_numeric_tolerance_mm=0.0001,
        normal_ray_numeric_policy_version="ray-research-v1",
        closest_point_fallback_policy_version="local-only-v1",
    )


def estimator():
    return ErrorEstimatorConfig(
        version="research-v1", initial_error_sample_spacing_mm=0.1,
        error_refinement_factor=2.0, error_metric_convergence_mm=0.001,
        max_error_refinement_levels=4,
        closest_point_sign_numeric_tolerance_version="sign-v1",
        surface_correspondence_policy=correspondence(),
    )


class EstimatorContracts(unittest.TestCase):
    def test_correspondence_frozen_and_canonical_deterministic(self):
        p = correspondence()
        with self.assertRaises(FrozenInstanceError):
            p.max_surface_correspondence_distance_mm = 2
        self.assertEqual(canonical_bytes(semantic_tree(p)), canonical_bytes(semantic_tree(correspondence())))
        self.assertNotEqual(canonical_bytes(semantic_tree(p)),
                            canonical_bytes(semantic_tree(replace(p, min_surface_normal_dot=0.5))))

    def test_reject_correspondence_invalid_numeric_limits_and_metadata(self):
        p = correspondence()
        cases = (
            ("max_surface_correspondence_distance_mm", 0),
            ("max_surface_correspondence_distance_mm", float("inf")),
            ("min_surface_normal_dot", -1.01),
            ("min_surface_normal_dot", True),
            ("interaction_neighborhood_expansion_mm", -0.01),
            ("interaction_neighborhood_tolerance_mm", 0),
            ("normal_ray_numeric_tolerance_mm", math.nan),
            ("closest_point_fallback_policy_version", ["mutable"]),
            ("normal_ray_numeric_policy_version", ""),
        )
        for key, bad in cases:
            with self.subTest(key=key, bad=bad), self.assertRaises(ContractError):
                replace(p, **{key: bad})

    def test_estimator_frozen_and_canonical_changes(self):
        e = estimator()
        with self.assertRaises(FrozenInstanceError):
            e.max_error_refinement_levels = 99
        self.assertEqual(canonical_bytes(semantic_tree(e)), canonical_bytes(semantic_tree(estimator())))
        self.assertNotEqual(canonical_bytes(semantic_tree(e)), canonical_bytes(semantic_tree(replace(e, max_error_refinement_levels=5))))
        self.assertNotEqual(canonical_bytes(semantic_tree(e)),
                            canonical_bytes(semantic_tree(replace(e, surface_correspondence_policy=replace(correspondence(), min_surface_normal_dot=0.0)))))

    def test_estimator_invalid_refinement_and_types_rejected(self):
        e = estimator()
        cases = (
            ("version", {"mutable": "v"}),
            ("initial_error_sample_spacing_mm", 0),
            ("error_refinement_factor", 1),
            ("error_refinement_factor", float("nan")),
            ("error_metric_convergence_mm", -1),
            ("max_error_refinement_levels", False),
            ("max_error_refinement_levels", 0),
            ("closest_point_sign_numeric_tolerance_version", []),
            ("surface_correspondence_policy", {"mutable": "policy"}),
        )
        for field, value in cases:
            with self.subTest(field=field), self.assertRaises(ContractError):
                replace(e, **{field: value})


if __name__ == "__main__":
    unittest.main()
