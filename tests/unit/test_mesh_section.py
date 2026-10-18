"""Exact analytic mesh-plane fixtures; CCW is not material-side certification."""
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F
import math
import unittest

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.domain.mesh_section import MeshSectionVertex, MeshSectionLoop, MeshSectionResult
from adaptive_subedge.domain.settings import MeshSectionPolicy
from adaptive_subedge.engine.mesh_section import _segments_intersect, section_mesh_plane
from tests.unit.test_mesh_topology import cube, tetrahedron


def bipyramid(ring, top, bottom):
    n=len(ring)
    faces=tuple(face for i in range(n) for face in ((n,i,(i+1)%n),(n+1,(i+1)%n,i)))
    return IndexedTriangleMesh(tuple(PrintPoint3(*p) for p in tuple(ring)+(top,bottom)),faces)


def twice_area(loop):
    points=loop.vertices
    return sum((a.x_mm*b.y_mm-a.y_mm*b.x_mm for a,b in zip(points,points[1:]+points[:1])),F(0))


class MeshSectionTests(unittest.TestCase):
    def setUp(self):
        self.policy=MeshSectionPolicy("indexed_plane_section_v1",2**-20,2**-22,2**-20,2**-20,"unavailable_v1")

    def section(self,mesh,z,**changes):
        kwargs=dict(policy=self.policy,max_vertices=10000,max_triangles=20000,
                    max_section_segments=10000,max_pair_checks=100000,cancelled=lambda:False)
        return section_mesh_plane(mesh,z,**(kwargs|changes))

    def outcome(self,mesh,z,state,reason,**changes):
        self.assertEqual(self.section(mesh,z,**changes),MeshSectionResult(state,reason,None))

    def invalid(self,call,reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure: call()
        self.assertIs(failure.exception.reason,reason)

    def test_tetra_ordinary_exact_points_parameters_and_ccw(self):
        result=self.section(tetrahedron(),0.5)
        self.assertEqual((result.state,result.reason),("complete","section-loop"))
        loop=result.loop
        self.assertEqual(loop.command_z_mm,F(1,2))
        self.assertEqual({(p.x_mm,p.y_mm) for p in loop.vertices},{(F(0),F(0)),(F(1,2),F(0)),(F(0),F(1,2))})
        self.assertEqual({p.source_vertex_ids for p in loop.vertices},{(0,3),(1,3),(2,3)})
        self.assertTrue(all(p.edge_parameter==F(1,2) for p in loop.vertices))
        self.assertEqual(twice_area(loop),F(1,4))
        self.assertEqual(loop.vertices[0].source_vertex_ids,(0,3))
        self.assertNotEqual(loop.vertices[0],loop.vertices[-1])

    def test_cube_keeps_topological_diagonal_intersections(self):
        loop=self.section(cube(),0.5).loop
        self.assertEqual(len(loop.vertices),8)
        self.assertEqual(twice_area(loop),2)
        self.assertEqual({(p.x_mm,p.y_mm) for p in loop.vertices},
            {(F(0),F(0)),(F(1,2),F(0)),(F(1),F(0)),(F(1),F(1,2)),
             (F(1),F(1)),(F(1,2),F(1)),(F(0),F(1)),(F(0),F(1,2))})
        self.assertEqual(loop.vertices[0].source_vertex_ids,min(p.source_vertex_ids for p in loop.vertices))
        self.assertEqual(self.section(cube(),0.5).loop,loop)

    def test_sloping_tetra_exact_vertex_event(self):
        mesh=replace(tetrahedron(),vertices=tuple(PrintPoint3(*p) for p in ((0,0,0),(1,0,1),(0,1,2),(0,0,3))))
        loop=self.section(mesh,1).loop
        self.assertEqual({(p.x_mm,p.y_mm) for p in loop.vertices},{(F(1),F(0)),(F(0),F(1,2)),(F(0),F(0))})
        vertex=next(p for p in loop.vertices if p.source_vertex_ids==(1,))
        self.assertIsNone(vertex.edge_parameter)
        self.assertEqual({p.source_vertex_ids for p in loop.vertices},{(1,),(0,2),(0,3)})
        edge=next(p for p in loop.vertices if p.source_vertex_ids==(0,3))
        self.assertEqual(edge.edge_parameter,F(1,3))

    def test_shared_on_edge_opposite_material_included_once(self):
        mesh=replace(tetrahedron(),vertices=tuple(PrintPoint3(*p) for p in ((0,0,0),(1,0,0),(0,1,-1),(0,0,1))))
        loop=self.section(mesh,0).loop
        self.assertEqual(len(loop.vertices),3)
        self.assertEqual({p.source_vertex_ids for p in loop.vertices},{(0,),(1,),(2,3)})
        self.assertEqual(twice_area(loop),F(1,2))

    def test_tangent_vertex_tangent_edge_and_outside_are_empty(self):
        self.outcome(tetrahedron(),1,"empty","no-crossing")
        self.outcome(tetrahedron(),2,"empty","no-crossing")
        mesh=replace(tetrahedron(),vertices=tuple(PrintPoint3(*p) for p in ((0,0,0),(1,0,0),(0,1,1),(0,0,2))))
        self.outcome(mesh,0,"empty","no-crossing")

    def test_coplanar_precedence_and_numeric_near_on_uncertainty(self):
        self.outcome(cube(),0,"rejected","coplanar-facet")
        self.outcome(cube(),1,"rejected","coplanar-facet")
        self.outcome(cube(),2**-23,"rejected","coplanar-facet")
        self.outcome(cube(),2**-21,"incomplete","predicate-uncertain")
        # Small positive tolerances are not broad arbitrary exclusion bands.
        self.assertEqual(self.section(cube(),2**-18).state,"complete")
        self.outcome(tetrahedron(),1-2**-21,"incomplete","predicate-uncertain")

    def test_input_winding_reversal_mirror_and_unchanged_selected_z(self):
        mesh=tetrahedron()
        original=self.section(mesh,0.5).loop
        reversed_mesh=replace(mesh,triangles=tuple((a,c,b) for a,b,c in mesh.triangles))
        self.assertEqual(self.section(reversed_mesh,0.5).loop,original)
        mirror=replace(mesh,vertices=tuple(PrintPoint3(-p.x_mm,p.y_mm,p.z_mm) for p in mesh.vertices))
        mirrored=self.section(mirror,0.5).loop
        self.assertEqual(twice_area(mirrored),F(1,4))
        self.assertEqual({(p.x_mm,p.y_mm) for p in mirrored.vertices},{(-p.x_mm,p.y_mm) for p in original.vertices})
        self.assertEqual(mirrored.command_z_mm,F(1,2))
        self.assertFalse(hasattr(mirrored,"quantization_stable"))

    def test_distinct_near_nodes_are_rejected_not_welded(self):
        policy=replace(self.policy,section_predicate_epsilon_mm=2**-30,
            coplanar_section_epsilon_mm=2**-32,mesh_section_join_tolerance_mm=2**-8)
        self.outcome(tetrahedron(),1-2**-10,"rejected","ambiguous-join",policy=policy)

    def test_multiple_nested_loops_in_connected_nonembedded_source(self):
        mesh=bipyramid(((1,0,0),(0,1,0),(-1,0,0),(0,-1,0)),(0,0,1),(0,0,0.5))
        self.outcome(mesh,0.25,"rejected","multiple-loops")

    def test_saddle_vertex_actual_graph_branch(self):
        ring=((2,0,1),(1,2,-1),(-1,2,1),(-2,0,-1),(-1,-2,1),(1,-2,-1))
        mesh=bipyramid(ring,(0,0,3),(0,0,0))
        self.outcome(mesh,0,"rejected","non-simple-graph")

    def test_self_crossing_ring_with_nonzero_mesh_volume(self):
        mesh=bipyramid(((0,0,0),(3,2,0),(0,2,0),(2,0,0)),(0.5,0.5,1),(0.5,0.5,-1))
        self.outcome(mesh,0,"rejected","self-intersection")

    def test_actual_adjacent_backtrack_and_nonadjacent_touch_reject(self):
        rings=(((0,0,0),(2,0,0),(1,0,0),(2,2,0),(0,2,0)),
               ((0,0,0),(2,0,0),(2,2,0),(1,0,0),(0,2,0)))
        for ring in rings:
            mesh=bipyramid(ring,(0.5,0.5,1),(0.5,0.5,-1))
            self.outcome(mesh,0,"rejected","self-intersection")

    def test_closed_segment_predicate_exact_overlap_touch_and_disjoint(self):
        def point(x,y): return F(x),F(y)
        a,b=point(0,0),point(2,0)
        for c,d in ((point(1,0),point(3,0)),(point(2,0),point(3,0)),
                     (point(1,-1),point(1,1)),(point(1,0),point(1,1))):
            self.assertTrue(_segments_intersect(a,b,c,d))
        for c,d in ((point(3,0),point(4,0)),(point(0,F(1,10**100)),point(2,F(1,10**100)))):
            self.assertFalse(_segments_intersect(a,b,c,d))

    def test_topology_failure_and_resource_propagation(self):
        mesh=tetrahedron()
        self.outcome(replace(mesh,triangles=mesh.triangles[1:]),0.5,"rejected","nonmanifold-edge")
        self.outcome(mesh,0.5,"incomplete","resource-limit",max_vertices=3)
        self.outcome(mesh,0.5,"incomplete","resource-limit",max_section_segments=2)
        # Three nodes and three edges require 3+3=6 pair slots.
        self.outcome(mesh,0.5,"incomplete","resource-limit",max_pair_checks=5)
        self.assertEqual(self.section(mesh,0.5,max_section_segments=3,max_pair_checks=6).state,"complete")
        # Cube contributes eight nodes and eight edges: 28+28 checks.
        self.outcome(cube(),0.5,"incomplete","resource-limit",max_pair_checks=55)
        self.assertEqual(self.section(cube(),0.5,max_pair_checks=56).state,"complete")

    def test_exact_policy_types_versions_and_numeric_query_contract(self):
        for field in ("version","section_stability_sampling_convergence_version"):
            self.invalid(lambda:self.section(tetrahedron(),0.5,policy=replace(self.policy,**{field:"unknown"})),ReasonCode.INVALID_SETTING)
        for field in ("max_vertices","max_triangles","max_section_segments","max_pair_checks"):
            for bad in (0,-1,True,1.5):
                self.invalid(lambda:self.section(tetrahedron(),0.5,**{field:bad}),ReasonCode.INVALID_SETTING)
        for bad in (True,math.inf,math.nan,10**400,"0.5"):
            self.invalid(lambda:self.section(tetrahedron(),bad))
        self.invalid(lambda:self.section({},0.5))
        self.invalid(lambda:self.section(tetrahedron(),0.5,policy={}),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.section(tetrahedron(),0.5,cancelled=None),ReasonCode.INVALID_SETTING)

    def test_cancellation_every_checkpoint_never_publishes_partial_loop(self):
        calls=0
        def count():
            nonlocal calls
            calls+=1
            return False
        self.assertEqual(self.section(tetrahedron(),0.5,cancelled=count).state,"complete")
        for target in range(1,calls+1):
            seen=0
            def cancel():
                nonlocal seen
                seen+=1
                return seen==target
            self.outcome(tetrahedron(),0.5,"incomplete","cancelled",cancelled=cancel)
            self.assertEqual(seen,target)
        for bad in (1,0,None,"false"):
            self.invalid(lambda:self.section(tetrahedron(),0.5,cancelled=lambda:bad),ReasonCode.INVALID_SETTING)
        def explode(): raise LookupError("callback")
        with self.assertRaises(LookupError): self.section(tetrahedron(),0.5,cancelled=explode)

    def test_exact_scaling_avoids_float_area_overflow(self):
        scale=1e200
        mesh=replace(tetrahedron(),vertices=tuple(PrintPoint3(p.x_mm*scale,p.y_mm*scale,p.z_mm*scale) for p in tetrahedron().vertices))
        z=scale/2
        loop=self.section(mesh,z).loop
        self.assertEqual(loop.command_z_mm,F(z))
        self.assertEqual(twice_area(loop),F(scale)**2/4)

    def test_shape_validation_required_immutability_and_identity_exclusion(self):
        result=self.section(tetrahedron(),0.5)
        vertex=result.loop.vertices[0]
        for value in (vertex,result.loop,result):
            self.assertFalse(hasattr(value,"__dict__"))
            for omitted in fields(value):
                kwargs={f.name:getattr(value,f.name) for f in fields(value) if f!=omitted}
                with self.assertRaises(TypeError): type(value)(**kwargs)
            with self.assertRaises(FrozenInstanceError): setattr(value,fields(value)[0].name,None)
            with self.assertRaises(ContractError): semantic_tree(value)
            with self.assertRaises(ContractError): identity_root("subedge-plan",value,schema_version="2")
        for change in ({"source_vertex_ids":[]},{"source_vertex_ids":(1,0)},
                       {"source_vertex_ids":(True,)},{"edge_parameter":F(0)},
                       {"edge_parameter":F(1)},{"edge_parameter":None},{"x_mm":0.0}):
            self.invalid(lambda:replace(vertex,**change))
        for change in ({"command_z_mm":0.5},{"vertices":list(result.loop.vertices)},
                       {"vertices":result.loop.vertices[:2]},
                       {"vertices":(vertex,vertex,vertex)}):
            self.invalid(lambda:replace(result.loop,**change))
        for state,reason,loop in (("complete","section-loop",None),("empty","no-crossing",result.loop),
                                  ("incomplete","predicate-uncertain",result.loop),("validated","section-loop",result.loop)):
            self.invalid(lambda:MeshSectionResult(state,reason,loop))


if __name__ == "__main__":
    unittest.main()
