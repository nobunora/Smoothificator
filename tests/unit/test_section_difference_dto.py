"""Constructor boundaries, not engine correctness or geometry certification."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import unittest

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.mesh_section import MeshSectionLoop, MeshSectionVertex
from adaptive_subedge.domain.section_difference import ConvexSectionDifference


def polygon(points):
    return tuple((F(x), F(y)) for x, y in points)


SQUARE = polygon(((0, 0), (1, 0), (1, 1), (0, 1)))


def section(z):
    return MeshSectionLoop(F(z), tuple(MeshSectionVertex((i,), None, x, y)
                                      for i, (x, y) in enumerate(SQUARE)))


def result():
    return ConvexSectionDifference("complete", "difference-derived", F(0), F(1),
                                   section(0), section(1), (SQUARE,), F(1))


class SectionDifferenceDtoTests(unittest.TestCase):
    def invalid(self, **changes):
        with self.assertRaises(ContractError) as caught:
            replace(result(), **changes)
        self.assertIs(caught.exception.reason, ReasonCode.INVALID_GEOMETRY)

    def test_exact_value_and_immutable(self):
        value = result()
        self.assertEqual(value.area_mm2, F(1))
        with self.assertRaises(FrozenInstanceError):
            value.area_mm2 = F(2)
        self.assertFalse(hasattr(value, "__dict__"))
        triangle = polygon(((0, 0), (F(1, 3), 0), (0, F(2, 7))))
        self.assertEqual(replace(value, cells_xy_mm=(triangle,), area_mm2=F(1, 21)).area_mm2, F(1, 21))

    def test_empty_and_failure_matrix(self):
        empty = replace(result(), reason="empty-difference", cells_xy_mm=(), area_mm2=F(0))
        self.assertEqual(empty.cells_xy_mm, ())
        for state, reason in (("incomplete", "cancelled"), ("incomplete", "resource-limit"),
                              ("rejected", "non-nested-sections"), ("rejected", "empty-mesh")):
            value = ConvexSectionDifference(state, reason, F(0), F(1), None, None, (), None)
            self.assertIsNone(value.area_mm2)
        for changes in (dict(reason="empty-difference"), dict(cells_xy_mm=()),
                        dict(state="rejected", reason="non-nested-sections"),
                        dict(state="incomplete", reason="predicate-uncertain"), dict(state=True)):
            self.invalid(**changes)

    def test_exact_metadata_and_height_association(self):
        for changes in (dict(lower_z_mm=0), dict(upper_z_mm=F(0)), dict(area_mm2=1),
                        dict(lower_section=section(1)), dict(upper_section=None),
                        dict(cells_xy_mm=[SQUARE]), dict(area_mm2=F(2))):
            self.invalid(**changes)

    def test_polygon_canonical_shape(self):
        invalid = (SQUARE[1:]+SQUARE[:1], SQUARE[::-1], SQUARE+(SQUARE[0],),
                   polygon(((0, 0), (1, 0), (1, 1), (1, 0), (0, 1))),
                   polygon(((0, 0), (F(1, 2), 0), (1, 0), (1, 1), (0, 1))),
                   polygon(((0, 0), (1, 0), (F(1, 2), F(1, 2)), (1, 1), (0, 1))))
        for cell in invalid:
            with self.subTest(cell=cell):
                self.invalid(cells_xy_mm=(cell,))
        self.invalid(cells_xy_mm=(((0, F(0)), *SQUARE[1:]),))

    def test_positive_turn_star_is_rejected(self):
        # Convex pentagon walked in star order; positive local turns are insufficient.
        ring = polygon(((0, 0), (4, 0), (5, 3), (2, 5), (-1, 3)))
        star = tuple(ring[i] for i in (4, 1, 3, 0, 2))
        area = sum(star[i][0]*star[(i+1) % 5][1]-star[i][1]*star[(i+1) % 5][0]
                   for i in range(5))/2
        self.assertGreater(area, 0)
        self.invalid(cells_xy_mm=(star,), area_mm2=area)

    def test_constructor_does_not_assert_cross_cell_or_mesh_proof(self):
        # Same cell twice is intentionally engine-owned overlap validation.
        value = replace(result(), cells_xy_mm=(SQUARE, SQUARE), area_mm2=F(2))
        self.assertEqual(value.area_mm2, F(2))
