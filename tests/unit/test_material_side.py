"""Independent exact embedding and parity fixtures; no printer authority implied."""
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F
import math
import unittest

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.material_side import MeshEmbeddingResult, MeshPointClassification
from adaptive_subedge.engine.material_side import evaluate_mesh_embedding, classify_mesh_point
from adaptive_subedge.engine.mesh_topology import prepare_mesh_topology
from adaptive_subedge.engine.triangle_intersection import _intersection_vertices, _point_on_triangle, _ray_hit
from tests.unit.test_mesh_topology import cube, tetrahedron
from tests.unit.test_mesh_section import bipyramid


def point(*coordinates):
    return tuple(F(x) for x in coordinates)


class MaterialSideTests(unittest.TestCase):
    def kwargs(self,changes):
        return dict(max_vertices=1000,max_triangles=2000,max_pair_checks=100000,cancelled=lambda:False)|changes

    def embed(self,mesh,**changes):
        return evaluate_mesh_embedding(mesh,**self.kwargs(changes))

    def classify(self,mesh,p,**changes):
        return classify_mesh_point(mesh,p,**(self.kwargs({})|{"max_ray_directions":8}|changes))

    def invalid(self,call,reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure: call()
        self.assertIs(failure.exception.reason,reason)

    def test_tetrahedron_and_coplanar_triangulated_cube_are_embedded(self):
        for mesh in (tetrahedron(),cube()):
            self.assertEqual(self.embed(mesh),MeshEmbeddingResult("complete","embedded"))
            self.assertEqual(self.embed(mesh),self.embed(mesh))

    def test_tetra_inside_outside_and_all_boundary_dimensions(self):
        mesh=tetrahedron()
        fixtures=(((0.125,0.125,0.125),"inside"),((1,1,1),"outside"),
                  ((0.25,0.25,0.5),"boundary"),((0.5,0.5,0),"boundary"),((0,0,0),"boundary"))
        for coordinates,expected in fixtures:
            self.assertEqual(self.classify(mesh,PrintPoint3(*coordinates)),MeshPointClassification("complete","classified",expected))

    def test_cube_classifications_and_boundary_precedes_ray_ambiguity(self):
        mesh=cube()
        fixtures=(((0.5,0.5,0.5),"inside"),((2,0.5,0.5),"outside"),
                  ((0.5,0.5,0),"boundary"),((1,0.5,1),"boundary"),((1,1,1),"boundary"))
        for coordinates,expected in fixtures:
            self.assertEqual(self.classify(mesh,PrintPoint3(*coordinates)).classification,expected)
        self.assertEqual(self.classify(mesh,PrintPoint3(1,1,1),max_ray_directions=1).classification,"boundary")

    def test_deterministic_ray_edge_then_vertex_retry_and_exhaustion(self):
        # k=0 hits the side-face diagonal; k=1 hits (1,1,1); k=2 hits a face interior.
        mesh=cube()
        center=PrintPoint3(0.5,0.5,0.5)
        for count in (1,2):
            self.assertEqual(self.classify(mesh,center,max_ray_directions=count),
                MeshPointClassification("incomplete","ray-directions-exhausted",None))
        self.assertEqual(self.classify(mesh,center,max_ray_directions=3).classification,"inside")

    def test_mirror_reversal_translation_preserve_material_classification(self):
        mesh=tetrahedron()
        variants=((replace(mesh,triangles=tuple((a,c,b) for a,b,c in mesh.triangles)),PrintPoint3(0.125,0.125,0.125)),
                  (replace(mesh,vertices=tuple(PrintPoint3(-p.x_mm,p.y_mm,p.z_mm) for p in mesh.vertices)),PrintPoint3(-0.125,0.125,0.125)),
                  (replace(mesh,vertices=tuple(PrintPoint3(p.x_mm+17,p.y_mm-31,p.z_mm+9) for p in mesh.vertices)),PrintPoint3(17.125,-30.875,9.125)))
        for variant,p in variants:
            self.assertEqual(self.embed(variant).state,"complete")
            self.assertEqual(self.classify(variant,p).classification,"inside")

    def test_bowtie_mesh_passes_topology_but_embedding_rejects(self):
        mesh=bipyramid(((0,0,0),(3,2,0),(0,2,0),(2,0,0)),(0.5,0.5,1),(0.5,0.5,-1))
        self.assertEqual(prepare_mesh_topology(mesh,max_vertices=100,max_triangles=100,cancelled=lambda:False).state,"complete")
        self.assertEqual(self.embed(mesh),MeshEmbeddingResult("rejected","self-intersection"))
        self.assertEqual(self.classify(mesh,PrintPoint3(0,0,0)),MeshPointClassification("rejected","self-intersection",None))

    def test_distinct_source_vertices_with_coincident_coordinates_reject(self):
        mesh=cube()
        touching=replace(mesh,vertices=mesh.vertices[:6]+(mesh.vertices[0],)+mesh.vertices[7:])
        self.assertEqual(prepare_mesh_topology(touching,max_vertices=100,max_triangles=100,cancelled=lambda:False).state,"complete")
        self.assertEqual(self.embed(touching),MeshEmbeddingResult("rejected","self-intersection"))

    def test_concave_nested_cones_are_not_mislabelled_self_intersection(self):
        mesh=bipyramid(((1,0,0),(0,1,0),(-1,0,0),(0,-1,0)),(0,0,1),(0,0,0.5))
        self.assertEqual(self.embed(mesh).state,"complete")
        self.assertEqual(self.classify(mesh,PrintPoint3(0,0,0.75)).classification,"inside")
        self.assertEqual(self.classify(mesh,PrintPoint3(0,0,0.25)).classification,"outside")

    def test_coplanar_intersection_area_edge_point_disjoint_and_winding(self):
        a=(point(0,0,0),point(2,0,0),point(0,2,0))
        cases=(((point(1,0,0),point(3,0,0),point(1,2,0)),{point(1,0,0),point(2,0,0),point(1,1,0)}),
               ((point(0,0,0),point(2,0,0),point(2,-2,0)),{point(0,0,0),point(2,0,0)}),
               ((point(2,0,0),point(3,0,0),point(2,-1,0)),{point(2,0,0)}),
               ((point(3,0,0),point(4,0,0),point(3,1,0)),set()))
        for b,expected in cases:
            self.assertEqual(set(_intersection_vertices(a,b)),expected)
            self.assertEqual(set(_intersection_vertices(b,a)),expected)
            self.assertEqual(set(_intersection_vertices(tuple(reversed(a)),b)),expected)

    def test_noncoplanar_interval_intersection_and_parallel_disjoint(self):
        a=(point(0,0,0),point(2,0,0),point(0,2,0))
        b=(point(F(1,2),-1,-1),point(F(1,2),3,-1),point(F(1,2),1,1))
        expected={point(F(1,2),0,0),point(F(1,2),F(3,2),0)}
        self.assertEqual(set(_intersection_vertices(a,b)),expected)
        self.assertEqual(set(_intersection_vertices(b,a)),expected)
        parallel=tuple((x,y,z+1) for x,y,z in a)
        self.assertEqual(tuple(_intersection_vertices(a,parallel)),())
        edge=(point(0,0,0),point(2,0,0),point(0,0,2))
        self.assertEqual(set(_intersection_vertices(a,edge)),{point(0,0,0),point(2,0,0)})

    def test_projection_axes_and_signed_normal_do_not_change_intersection(self):
        a=(point(0,0,0),point(2,0,0),point(0,2,0))
        b=(point(1,0,0),point(3,0,0),point(1,2,0))
        expected={point(1,0,0),point(2,0,0),point(1,1,0)}
        for indices in ((0,2,1),(2,0,1),(1,0,2)):
            def permute(p): return tuple(p[i] for i in indices)
            self.assertEqual(set(_intersection_vertices(tuple(map(permute,a)),tuple(map(permute,b)))),set(map(permute,expected)))

    def test_point_membership_and_ray_degeneracies(self):
        triangle=(point(0,0,0),point(2,0,0),point(0,2,0))
        for p in (point(0,0,0),point(1,0,0),point(F(1,2),F(1,2),0)):
            self.assertTrue(_point_on_triangle(p,triangle))
        self.assertFalse(_point_on_triangle(point(1,1,F(1,10**100)),triangle))
        self.assertFalse(_point_on_triangle(point(2,2,0),triangle))
        self.assertEqual(_ray_hit(point(F(1,2),F(1,2),1),point(0,0,-1),triangle),"hit")
        self.assertEqual(_ray_hit(point(0,0,1),point(0,0,-1),triangle),"ambiguous")
        self.assertEqual(_ray_hit(point(10,10,0),point(1,0,0),triangle),"ambiguous")
        self.assertEqual(_ray_hit(point(F(1,2),F(1,2),-1),point(0,0,-1),triangle),"miss")
        self.assertEqual(_ray_hit(point(F(1,2),F(1,2),1),point(1,0,0),triangle),"miss")

    def test_extreme_and_tiny_coordinates_remain_exact(self):
        base=tetrahedron()
        for scale in (math.ldexp(1.0,-1000),1e200):
            mesh=replace(base,vertices=tuple(PrintPoint3(p.x_mm*scale,p.y_mm*scale,p.z_mm*scale) for p in base.vertices))
            self.assertEqual(self.embed(mesh).state,"complete")
            self.assertEqual(self.classify(mesh,PrintPoint3(scale/8,scale/8,scale/8)).classification,"inside")
        tiny=math.ulp(0.0)
        mesh=replace(base,vertices=tuple(PrintPoint3(p.x_mm*tiny,p.y_mm*tiny,p.z_mm*tiny) for p in base.vertices))
        self.assertEqual(self.embed(mesh).state,"complete")

    def test_topology_failure_pair_budget_and_invalid_inputs(self):
        mesh=tetrahedron()
        self.assertEqual(self.embed(replace(mesh,triangles=mesh.triangles[1:])).reason,"nonmanifold-edge")
        self.assertEqual(self.embed(mesh,max_pair_checks=5),MeshEmbeddingResult("incomplete","resource-limit"))
        self.assertEqual(self.embed(mesh,max_pair_checks=6).state,"complete")
        self.assertEqual(self.embed(cube(),max_pair_checks=65).reason,"resource-limit")
        self.assertEqual(self.embed(cube(),max_pair_checks=66).state,"complete")
        for field in ("max_vertices","max_triangles","max_pair_checks"):
            for value in (0,-1,True,1.5):
                self.invalid(lambda:self.embed(mesh,**{field:value}),ReasonCode.INVALID_SETTING)
        for value in (0,-1,True,1.5):
            self.invalid(lambda:self.classify(mesh,PrintPoint3(0,0,0),max_ray_directions=value),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.embed({}))
        self.invalid(lambda:self.classify(mesh,(0,0,0)))
        self.invalid(lambda:self.embed(mesh,cancelled=None),ReasonCode.INVALID_SETTING)

    def test_cancellation_at_every_embedding_and_classification_checkpoint(self):
        mesh=tetrahedron()
        for operation in (lambda callback:self.embed(mesh,cancelled=callback),
                          lambda callback:self.classify(mesh,PrintPoint3(0.125,0.125,0.125),cancelled=callback),
                          lambda callback:self.classify(mesh,PrintPoint3(0,0,0),cancelled=callback)):
            count=0
            def count_calls():
                nonlocal count
                count+=1
                return False
            self.assertEqual(operation(count_calls).state,"complete")
            for target in range(1,count+1):
                seen=0
                def cancel():
                    nonlocal seen
                    seen+=1
                    return seen==target
                result=operation(cancel)
                self.assertEqual((result.state,result.reason),("incomplete","cancelled"))
                self.assertEqual(seen,target)
                if type(result) is MeshPointClassification: self.assertIsNone(result.classification)

    def test_callback_bad_bool_and_exception_propagation(self):
        for bad in (0,1,None,"false"):
            self.invalid(lambda:self.embed(tetrahedron(),cancelled=lambda:bad),ReasonCode.INVALID_SETTING)
        def explode(): raise LookupError("caller")
        with self.assertRaises(LookupError): self.classify(tetrahedron(),PrintPoint3(0,0,0),cancelled=explode)

    def test_result_shapes_frozen_and_not_canonical_proof_tokens(self):
        values=(MeshEmbeddingResult("complete","embedded"),MeshPointClassification("complete","classified","inside"))
        for value in values:
            self.assertFalse(hasattr(value,"__dict__"))
            for omitted in fields(value):
                kwargs={f.name:getattr(value,f.name) for f in fields(value) if f!=omitted}
                with self.assertRaises(TypeError): type(value)(**kwargs)
            with self.assertRaises(FrozenInstanceError): setattr(value,"state","rejected")
            with self.assertRaises(ContractError): semantic_tree(value)
            with self.assertRaises(ContractError): identity_root("subedge-plan",value,schema_version="2")
        for state,reason in (("validated","embedded"),("complete","self-intersection"),("incomplete","embedded")):
            self.invalid(lambda:MeshEmbeddingResult(state,reason))
        for state,reason,classification in (("complete","classified",None),("complete","classified","unknown"),
                                            ("incomplete","cancelled","inside"),("rejected","self-intersection","boundary")):
            self.invalid(lambda:MeshPointClassification(state,reason,classification))


if __name__=="__main__":
    unittest.main()
