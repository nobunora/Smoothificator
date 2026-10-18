"""Independent exact-area and fail-closed two-section fixtures."""
from fractions import Fraction as F
from itertools import combinations
import unittest
from unittest.mock import patch

from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.engine.section_difference import derive_convex_section_difference
from adaptive_subedge.engine import section_difference as engine
from tests.unit.test_mesh_topology import cube, tetrahedron


def frustum(lower_side=4, upper_side=2):
    low = (4-lower_side)/2
    high = (4-upper_side)/2
    vertices = tuple(PrintPoint3(*point) for point in (
        (low, low, 0), (4-low, low, 0), (4-low, 4-low, 0), (low, 4-low, 0),
        (high, high, 1), (4-high, high, 1), (4-high, 4-high, 1), (high, 4-high, 1)))
    triangles = ((0,2,1), (0,3,2), (4,5,6), (4,6,7), (0,1,5), (0,5,4),
                 (1,2,6), (1,6,5), (2,3,7), (2,7,6), (3,0,4), (3,4,7))
    return IndexedTriangleMesh(vertices, triangles)


def ringed_square():
    rings = ((0, 2), (0.25, 2), (0.5, 4), (0.75, 2), (1, 2))
    vertices = []
    for z, side in rings:
        low, high = 2-side/2, 2+side/2
        vertices.extend(PrintPoint3(*point) for point in
                        ((low,low,z), (high,low,z), (high,high,z), (low,high,z)))
    faces = [(0,2,1), (0,3,2), (16,17,18), (16,18,19)]
    for ring in range(4):
        for edge in range(4):
            a, b = 4*ring+edge, 4*ring+(edge+1) % 4
            c, d = 4*(ring+1)+(edge+1) % 4, 4*(ring+1)+edge
            faces.extend(((a,b,c), (a,c,d)))
    return IndexedTriangleMesh(tuple(vertices), tuple(faces))


def corner_frustum():
    base = frustum()
    top = ((0,0,1), (2,0,1), (2,2,1), (0,2,1))
    vertices = base.vertices[:4]+tuple(PrintPoint3(*point) for point in top)
    return IndexedTriangleMesh(vertices, base.triangles)


def skewed_triangle_frustum():
    vertices = tuple(PrintPoint3(*point) for point in
                     ((0,0,0), (4,0,0), (0,4,0),
                      (1,1,1), (2.5,1,1), (1,1.5,1)))
    triangles = ((0,2,1), (3,4,5), (0,1,4), (0,4,3),
                 (1,2,4), (2,5,4), (2,0,3), (2,3,5))
    return IndexedTriangleMesh(vertices, triangles)


class SectionDifferenceTests(unittest.TestCase):
    def derive(self, mesh=None, **changes):
        lower_z = changes.pop("lower_z_mm", 0.25)
        upper_z = changes.pop("upper_z_mm", 0.75)
        args = dict(algorithm_version="convex_section_difference_v1",
                    max_vertices=100, max_triangles=100, max_mesh_pair_checks=1000,
                    max_section_segments=100, max_section_pair_checks=1000,
                    max_clip_vertex_tests=1000, cancelled=lambda: False)
        return derive_convex_section_difference(frustum() if mesh is None else mesh,
                                                lower_z, upper_z, **(args | changes))

    def test_square_frustum_exact_difference(self):
        result = self.derive()
        self.assertEqual((result.state, result.reason, result.area_mm2),
                         ("complete", "difference-derived", F(6)))
        self.assertEqual(len(result.cells_xy_mm), 4)
        self.assertEqual(sum((polygon_area(cell) for cell in result.cells_xy_mm), F(0)), F(6))
        self.assertTrue(all(interiors_disjoint(a, b)
                            for a, b in combinations(result.cells_xy_mm, 2)))
        self.assertEqual(result.lower_section.command_z_mm, F(1, 4))
        self.assertEqual(result.upper_section.command_z_mm, F(3, 4))
        # Every cell centroid lies in the lower section and outside the upper one.
        for cell in result.cells_xy_mm:
            centroid = tuple(sum(point[i] for point in cell)/len(cell) for i in (0, 1))
            self.assertTrue(F(1, 4) <= centroid[0] <= F(15, 4))
            self.assertFalse(F(3, 4) < centroid[0] < F(13, 4)
                             and F(3, 4) < centroid[1] < F(13, 4))

    def test_tetrahedral_difference_and_same_section(self):
        triangle = self.derive(tetrahedron())
        self.assertEqual((triangle.state, triangle.area_mm2), ("complete", F(1, 4)))
        equal = self.derive(cube())
        self.assertEqual((equal.state, equal.reason, equal.cells_xy_mm, equal.area_mm2),
                         ("complete", "empty-difference", (), F(0)))

    def test_triangle_order_and_midheight_bulge_limit(self):
        mesh = frustum()
        reordered = IndexedTriangleMesh(mesh.vertices, tuple(reversed(mesh.triangles)))
        self.assertEqual(self.derive(mesh).cells_xy_mm, self.derive(reordered).cells_xy_mm)
        bulged = self.derive(ringed_square(), lower_z_mm=0.125, upper_z_mm=0.875)
        self.assertEqual((bulged.state, bulged.reason, bulged.area_mm2),
                         ("complete", "empty-difference", F(0)))
        # Both endpoint sections match, although the section at z=0.5 expands.
        self.assertNotEqual(self.derive(ringed_square(), lower_z_mm=0.125,
                                        upper_z_mm=0.5).state, "complete")

    def test_shared_boundary_omits_zero_area_pieces(self):
        result = self.derive(corner_frustum())
        self.assertEqual((result.state, result.area_mm2), ("complete", F(6)))
        self.assertEqual(len(result.cells_xy_mm), 2)
        self.assertTrue(all(polygon_area(cell) > 0 for cell in result.cells_xy_mm))

    def test_skewed_triangle_retains_exact_nonbinary_intersections(self):
        result = self.derive(skewed_triangle_frustum())
        self.assertEqual(result.state, "complete")
        self.assertEqual(result.area_mm2, F(61, 16))
        denominators = {v.denominator for cell in result.cells_xy_mm
                        for point in cell for v in point}
        self.assertTrue(any(d & (d-1) for d in denominators))

    def test_lower_failure_stops_before_upper_and_upper_cancel_discards_all(self):
        with patch.object(engine, "_section", wraps=engine._section) as section:
            result = self.derive(cube(), lower_z_mm=-1)
        self.assertEqual((result.state, result.reason), ("rejected", "empty-section"))
        self.assertEqual(section.call_count, 1)

        calls = 0
        active_cancel = False
        original = engine._section

        def section_after_lower(*args, **kwargs):
            nonlocal calls, active_cancel
            calls += 1
            if calls == 2:
                active_cancel = True
            return original(*args, **kwargs)

        with patch.object(engine, "_section", side_effect=section_after_lower):
            cancelled = self.derive(cancelled=lambda: active_cancel)
        self.assertEqual((cancelled.state, cancelled.reason, cancelled.lower_section,
                          cancelled.upper_section, cancelled.cells_xy_mm),
                         ("incomplete", "cancelled", None, None, ()))

    def test_cancellation_at_failure_and_final_publication(self):
        fail_cancel = False

        def failed_section(*_args, **_kwargs):
            nonlocal fail_cancel
            fail_cancel = True
            raise engine._SectionStop("incomplete", "resource-limit")

        with patch.object(engine, "_section", side_effect=failed_section):
            result = self.derive(cancelled=lambda: fail_cancel)
        self.assertEqual((result.state, result.reason, result.cells_xy_mm),
                         ("incomplete", "cancelled", ()))

        calls = 0

        def count_checks():
            nonlocal calls
            calls += 1
            return False

        self.assertEqual(self.derive(cancelled=count_checks).state, "complete")
        checked = 0

        def cancel_last_check():
            nonlocal checked
            checked += 1
            return checked == calls

        result = self.derive(cancelled=cancel_last_check)
        self.assertEqual((result.state, result.reason, result.cells_xy_mm),
                         ("incomplete", "cancelled", ()))

        cancelled_after_construction = False
        constructor = engine.ConvexSectionDifference

        def cancel_after_constructor(*args):
            nonlocal cancelled_after_construction
            value = constructor(*args)
            if value.state == "complete":
                cancelled_after_construction = True
            return value

        with patch.object(engine, "ConvexSectionDifference",
                          side_effect=cancel_after_constructor):
            result = self.derive(cancelled=lambda: cancelled_after_construction)
        self.assertEqual((result.state, result.reason, result.cells_xy_mm),
                         ("incomplete", "cancelled", ()))

    def test_cancellation_in_containment_and_split(self):
        for trigger in (1, 17):
            calls = 0
            should_cancel = False
            original = engine._plane

            def stop_after_plane(*args):
                nonlocal calls, should_cancel
                calls += 1
                if calls == trigger:
                    should_cancel = True
                return original(*args)

            with patch.object(engine, "_plane", side_effect=stop_after_plane):
                result = self.derive(cancelled=lambda: should_cancel)
            self.assertEqual((result.state, result.reason, result.cells_xy_mm),
                             ("incomplete", "cancelled", ()))

    def test_outward_expansion_and_empty_section_fail_closed(self):
        expanding = self.derive(frustum(2, 4))
        self.assertEqual((expanding.state, expanding.reason),
                         ("rejected", "non-nested-sections"))
        self.assertEqual((expanding.lower_section, expanding.cells_xy_mm,
                          expanding.area_mm2), (None, (), None))
        empty = derive_convex_section_difference(cube(), -1, 0.75,
            algorithm_version="convex_section_difference_v1", max_vertices=100,
            max_triangles=100, max_mesh_pair_checks=1000, max_section_segments=100,
            max_section_pair_checks=1000, max_clip_vertex_tests=1000,
            cancelled=lambda: False)
        self.assertEqual((empty.state, empty.reason), ("rejected", "empty-section"))

    def test_exact_budget_boundary_and_invalid_inputs(self):
        self.assertEqual(self.derive(max_clip_vertex_tests=48).state, "complete")
        limited = self.derive(max_clip_vertex_tests=47)
        self.assertEqual((limited.state, limited.reason, limited.cells_xy_mm),
                         ("incomplete", "resource-limit", ()))
        for changes in (dict(max_clip_vertex_tests=True),
                        dict(algorithm_version="future"), dict(cancelled=None)):
            with self.assertRaises(ContractError):
                self.derive(**changes)
        with self.assertRaises(ContractError):
            self.derive(upper_z_mm=0.25)
        self.assertEqual(self.derive(cancelled=lambda: True).reason, "cancelled")


def polygon_area(points):
    return abs(sum((a[0]*b[1]-a[1]*b[0]
                    for a, b in zip(points, points[1:]+points[:1])), F(0)))/2


def interiors_disjoint(first, second):
    for source, other in ((first, second), (second, first)):
        for a, b in zip(source, source[1:]+source[:1]):
            if max((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
                   for p in other) <= 0:
                return True
    return False
