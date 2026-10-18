"""Recipe construction keeps intent separate from frozen reproduction evidence."""
from fractions import Fraction as F
import unittest

from tests.unit.test_source_contour_intents import contour
from tests.unit.test_supplemental_z_hop import policy_fixture
from tools.compile_nominal_recipe import (
    CircleRecipe, ContourRecipe, ExplicitPatchRecipe, GridVertexDisplacement, compile_nominal_recipe,
)
from tools.prepare_source_contour_intents import ContourConstructionPolicy


def compile_recipe(construction_recipe, **changes):
    arguments = dict(proposal_id='research.id', emitted_path_id='emitted_id', source_sha256='1'*64,
        project_sha256='2'*64, floor_z_mm=F(3), upper_z_mm=F('3.2'), width_mm=F('.3'),
        height_mm=F('.08'), remaining_height_mm=F('.08'), recipe=construction_recipe, emission_policy=policy_fixture(),
        construction_policy=ContourConstructionPolicy(9, 1000, 4096, 100000), cancelled=lambda: False)
    arguments.update(changes)
    return compile_nominal_recipe(**arguments)


class CompileNominalRecipeTests(unittest.TestCase):
    def test_circle_uses_owner_and_shared_freeze_with_explicit_legal_id(self):
        recipe = CircleRecipe((F(10), F(10)), F(1), 192, F('.002'))
        result = compile_recipe(recipe)
        self.assertEqual(len(result.frozen_emission.relative_e_mm), 192)
        self.assertEqual(result.proposal_id, 'research.id')
        self.assertEqual(result.frozen_emission.path.path_id, 'emitted_id')
        self.assertEqual(result.frozen_emission.path.points_mm[0], result.frozen_emission.path.points_mm[-1])
        with self.assertRaises(ValueError):
            compile_recipe(recipe, emitted_path_id='bad.id')

    def test_explicit_arc_cut_never_reconnects_and_displacement_is_pre_freeze_provenance(self):
        recipe = ContourRecipe(contour(), F(0), F(0), retained_edge_indices=(1, 2),
            vertex_displacements=(GridVertexDisplacement(0, (F(0), F('-.001')), 'declared finite patch separation'),))
        result = compile_recipe(recipe)
        self.assertEqual(len(result.frozen_emission.relative_e_mm), 2)
        self.assertEqual(result.removed_reference_edge_indices, (0, 3))
        self.assertNotEqual(result.frozen_emission.path.points_mm[0], result.frozen_emission.path.points_mm[-1])
        self.assertEqual(result.construction_reference.frozen_emission.path.points_mm[0][:2], (F(0), F(0)))
        changed = compile_recipe(ContourRecipe(contour(), F(0), F(0), retained_edge_indices=(1, 2)))
        self.assertNotEqual(result.recipe_identity, changed.recipe_identity)
        for retained in ((0, 2), (1, 1), (0, 1, 2, 3), (9,), ()):
            with self.assertRaises(ValueError):
                compile_recipe(ContourRecipe(contour(), F(0), F(0), retained_edge_indices=retained))

    def test_patch_exact_top_and_explicit_support_recipe_required(self):
        patch = ExplicitPatchRecipe(((F(0), F(0), F('3.08')), (F(1), F(0), F('3.08'))),
            ('actual-source-line',), 'declared finite patch')
        result = compile_recipe(patch)
        self.assertEqual(len(result.frozen_emission.relative_e_mm), 1)
        self.assertFalse(result.geometry_matches_reference)
        with self.assertRaises(ValueError):
            compile_recipe(patch, remaining_height_mm=F('.09'))
        with self.assertRaises(ValueError):
            compile_recipe(ExplicitPatchRecipe(patch.points_xyz_mm, (), patch.reason))

    def test_unknown_recipe_resources_and_cancel_reject(self):
        recipe = CircleRecipe((F(10), F(10)), F(1), 192, F('.002'))
        for changes in (dict(recipe={}), dict(cancelled=lambda: True), dict(cancelled=lambda: 1),
                       dict(construction_policy=ContourConstructionPolicy(9, 10, 4096, 10000))):
            with self.assertRaises(ValueError):
                compile_recipe(recipe, **changes)

    def test_final_quantized_graph_adjacent_overlap_area_orientation_and_interval_reject(self):
        def patch(xy):
            return ExplicitPatchRecipe(tuple((F(x), F(y), F('3.08')) for x, y in xy), ('actual-source',), 'explicit test patch')
        for recipe in (patch(((0, 0), (1, 0), (0, 0))),
                       patch(((0, 0), (1, '.0004'), ('.5', 1), ('.5', '.0003'))),
                       ContourRecipe(contour(((0, 0), (1, 0), (0, 1))), F(0), F(0),
                           vertex_displacements=(GridVertexDisplacement(2, (F('.5'), F(-1)), 'regression backtrack'),)),
                       ContourRecipe(contour(((0, 0), (1, 0), (0, 1))), F(0), F(0),
                           vertex_displacements=(GridVertexDisplacement(2, (F(0), F(-2)), 'regression reversed area'),))):
            with self.subTest(recipe=recipe), self.assertRaises(ValueError):
                compile_recipe(recipe)
        for recipe in (patch(((0, 0), (1, 0))), CircleRecipe((F(10), F(10)), F(1), 192, F('.002'))):
            with self.assertRaisesRegex(ValueError, 'ordered source interval'):
                compile_recipe(recipe, upper_z_mm=F('3.01'))
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            compile_recipe(CircleRecipe((F(10**400), F(10)), F(1), 192, F('.002')))


if __name__ == '__main__':
    unittest.main()
