"""ADR-0059 topology-aware mesh section policy: frozen contract, not geometry execution."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.settings import MeshSectionPolicy
from adaptive_subedge.application.serialization import semantic_tree, canonical_bytes


def mesh_section_policy():
    return MeshSectionPolicy(
        version="research-section-v1",
        section_predicate_epsilon_mm=0.0001,
        coplanar_section_epsilon_mm=0.0001,
        mesh_section_join_tolerance_mm=0.001,
        section_quantization_geometry_tolerance_mm=0.005,
        section_stability_sampling_convergence_version="stability-research-v1",
    )


class MeshSectionPolicyTests(unittest.TestCase):
    def test_immutable_canonical_policy(self):
        p = mesh_section_policy()
        with self.assertRaises(FrozenInstanceError):
            p.mesh_section_join_tolerance_mm = 5
        encoded = canonical_bytes(semantic_tree(p))
        self.assertEqual(encoded, canonical_bytes(semantic_tree(mesh_section_policy())))
        self.assertIn(b"section_predicate_epsilon_mm", encoded)
        self.assertNotEqual(encoded, canonical_bytes(semantic_tree(replace(p, section_predicate_epsilon_mm=0.0002))))

    def test_tolerances_must_be_finite_positive(self):
        p = mesh_section_policy()
        for key in ("section_predicate_epsilon_mm", "coplanar_section_epsilon_mm",
                    "mesh_section_join_tolerance_mm", "section_quantization_geometry_tolerance_mm"):
            for wrong in (0, -1, math.nan, math.inf, True, 10**400):
                with self.subTest(key=key, wrong=str(type(wrong))), self.assertRaises(ContractError):
                    replace(p, **{key: wrong})

    def test_versions_require_immutable_string(self):
        p = mesh_section_policy()
        for key in ("version", "section_stability_sampling_convergence_version"):
            for wrong in ("  ", 42, ["mutable"]):
                with self.subTest(key=key, wrong=str(type(wrong))), self.assertRaises(ContractError):
                    replace(p, **{key: wrong})


if __name__ == "__main__":
    unittest.main()
