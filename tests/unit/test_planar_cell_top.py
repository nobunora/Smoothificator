"""Exact planar-cell top proof and fail-closed boundaries."""
from fractions import Fraction as F
import unittest
from unittest.mock import patch

from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.planar_cell_top import PlanarCellTopCoverage
from adaptive_subedge.engine import planar_cell_top as engine
from tests.unit.test_mesh_topology import cube, tetrahedron
from tests.unit.test_section_difference import frustum


SQUARE = ((F(1), F(1)), (F(3), F(1)), (F(3), F(3)), (F(1), F(3)))
UNIT = ((F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1)))


def ringed_solid(outside_top, inside_top):
    outer = ((0, 0), (4, 0), (4, 4), (0, 4))
    inner = ((1, 1), (3, 1), (3, 3), (1, 3))
    vertices = tuple(PrintPoint3(x, y, z) for ring, z in
                     ((outer, 0), (outer, outside_top),
                      (inner, outside_top), (inner, inside_top)) for x, y in ring)
    faces = [(0, 2, 1), (0, 3, 2), (12, 13, 14), (12, 14, 15)]
    for i in range(4):
        j = (i+1) % 4
        faces.extend(((i, j, 4+j), (i, 4+j, 4+i),
                      (4+i, 4+j, 8+j), (4+i, 8+j, 8+i),
                      (8+i, 8+j, 12+j), (8+i, 12+j, 12+i)))
    return IndexedTriangleMesh(vertices, tuple(faces))


class PlanarCellTopTests(unittest.TestCase):
    def certify(self, mesh=None, cell=SQUARE, **changes):
        settings = dict(algorithm_version="planar_cell_top_v1", max_vertices=100,
                        max_triangles=100, max_mesh_pair_checks=1000,
                        max_cell_vertices=20, max_centroid_tests=100,
                        max_facet_clip_tests=1000, cancelled=lambda: False)
        return engine.certify_planar_cell_top(frustum() if mesh is None else mesh,
                                              cell, **(settings | changes))

    def test_coplanar_top_facets_and_permutation(self):
        mesh = frustum()
        first = self.certify(mesh)
        second = self.certify(IndexedTriangleMesh(mesh.vertices, tuple(reversed(mesh.triangles))))
        self.assertEqual(first, second)
        self.assertEqual((first.state, first.reason, first.plane_a, first.plane_b,
                          first.plane_c_mm, first.area_mm2),
                         ("complete", "planar-top-covered", F(0), F(0), F(1), F(4)))

    def test_sloped_tetrahedral_top(self):
        cell = ((F(1, 4), F(1, 4)), (F(1, 2), F(1, 4)), (F(1, 4), F(1, 2)))
        top = self.certify(tetrahedron(), cell)
        self.assertEqual((top.state, top.plane_a, top.plane_b,
                          top.plane_c_mm, top.area_mm2),
                         ("complete", F(-1), F(-1), F(1), F(1, 32)))

    def test_centroid_and_clip_budget_boundary(self):
        self.assertEqual(self.certify(max_centroid_tests=36,
                                      max_facet_clip_tests=12*4*7).state, "complete")
        for changes in (dict(max_centroid_tests=35), dict(max_facet_clip_tests=335)):
            result = self.certify(**changes)
            self.assertEqual((result.state, result.reason, result.cell_xy_mm,
                              result.area_mm2), ("incomplete", "resource-limit", None, None))

    def test_uncovered_and_no_top_facet(self):
        uncovered = self.certify(frustum(),
                                 ((F(0), F(0)), (F(4), F(0)), (F(4), F(4)), (F(0), F(4))))
        self.assertEqual((uncovered.state, uncovered.reason), ("rejected", "uncovered-top"))
        outside = self.certify(frustum(),
                               ((F(5), F(5)), (F(6), F(5)), (F(6), F(6)), (F(5), F(6))))
        self.assertEqual((outside.state, outside.reason), ("rejected", "no-top-facing-facet"))

    def test_closed_recess_spanning_plateau_and_pocket(self):
        cell = ((F(1, 2), F(1, 4)), (F(7, 2), F(1, 4)),
                (F(7, 2), F(5, 4)), (F(1, 2), F(5, 4)))
        result = self.certify(ringed_solid(2, 1), cell)
        self.assertEqual((result.state, result.reason, result.cell_xy_mm),
                         ("rejected", "uncovered-top", None))

    def test_closed_raised_feature_touching_cell_edge(self):
        cell = ((F(1, 2), F(3, 2)), (F(1), F(3, 2)),
                (F(1), F(5, 2)), (F(1, 2), F(5, 2)))
        result = self.certify(ringed_solid(1, 2), cell)
        self.assertEqual((result.state, result.reason, result.cell_xy_mm),
                         ("rejected", "above-top-plane", None))

    def test_boundary_only_higher_contact(self):
        # A projected vertical facet touching only a cell boundary must not
        # disappear from the exact prism clip as a zero-area contact.
        vertical = ((F(-1), F(0), F(0)), (F(0), F(0), F(2)),
                    (F(0), F(0), F(0)))
        self.assertIn((F(0), F(0), F(2)), engine._clip(vertical, UNIT, lambda: None))
        mesh = frustum()
        cell = ((F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1)))
        result = self.certify(mesh, cell)
        self.assertEqual(result.state, "rejected")

    def test_clip_vertex_bound_with_vertical_projection_and_corner_contacts(self):
        cell = ((F(0), F(0)), (F(2), F(0)), (F(2), F(2)), (F(0), F(2)))
        vertical = ((F(-1), F(0), F(0)), (F(3), F(0), F(1)),
                    (F(0), F(0), F(2)))
        clipped = engine._clip(vertical, cell, lambda: None)
        self.assertEqual(len(clipped), 4)
        self.assertEqual(clipped[0][:2], clipped[-1][:2])
        corner_crossing = ((F(4), F(4), F(-1)), (F(-1), F(1), F(-3)),
                           (F(4), F(-1), F(-1)))
        self.assertEqual(len(engine._clip(corner_crossing, cell, lambda: None)), 6)
        self.assertLessEqual(6, len(cell)+3)

    def test_invalid_cells_and_settings(self):
        invalid = (
            ((F(0), F(0)), (F(1), F(0)), (F(2), F(0))),
            ((F(0), F(0)), (F(2), F(0)), (F(1), F(1)), (F(2), F(2)), (F(0), F(2))),
            ((F(0), F(0)), (F(1), F(1)), (F(0), F(1)), (F(1), F(0))),
            ((F(0), F(0)), (F(1), F(0)), (F(0), 1.0)),
        )
        for cell in invalid:
            with self.subTest(cell=cell), self.assertRaises(ContractError) as raised:
                self.certify(cell=cell)
            self.assertEqual(raised.exception.reason, ReasonCode.INVALID_GEOMETRY)
        with self.assertRaises(ContractError):
            self.certify(max_cell_vertices=True)
        with self.assertRaises(ContractError):
            self.certify(cancelled=lambda: 0)

    def test_cancel_at_clip_and_before_failure_return(self):
        def stop_at_clip():
            stop_at_clip.calls += 1
            return stop_at_clip.calls > 230
        stop_at_clip.calls = 0
        self.assertEqual(self.certify(cancelled=stop_at_clip).state, "incomplete")
        cancelled = [False]
        def failed_embedding(*_args):
            cancelled[0] = True
            raise engine._Stopped("rejected", "empty-mesh")
        with patch.object(engine, "_embedding", side_effect=failed_embedding):
            result = self.certify(cancelled=lambda: cancelled[0])
        self.assertEqual((result.state, result.reason), ("incomplete", "cancelled"))

    def test_dto_rejects_partial_geometry(self):
        with self.assertRaises(ContractError):
            PlanarCellTopCoverage("rejected", "uncovered-top", UNIT, None, None, None, None)
        with self.assertRaises(ContractError):
            PlanarCellTopCoverage("complete", "planar-top-covered", UNIT,
                                  F(0), F(0), F(1), F(2))


if __name__ == "__main__":
    unittest.main()
