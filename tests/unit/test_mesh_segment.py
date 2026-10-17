"""Whole-segment material tests that endpoint-only classification cannot satisfy."""
from dataclasses import FrozenInstanceError, fields, replace
import math
import unittest
from unittest.mock import patch

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.material_side import MeshSegmentClassification
from adaptive_subedge.engine.material_side import classify_mesh_point, classify_mesh_segment
from adaptive_subedge.engine import material_side
from tests.unit.test_mesh_topology import cube, tetrahedron
from tests.unit.test_mesh_section import bipyramid


class MeshSegmentTests(unittest.TestCase):
    def kwargs(self,changes):
        return dict(max_vertices=1000,max_triangles=2000,max_pair_checks=100000,
                    max_ray_directions=8,cancelled=lambda:False)|changes

    def classify(self,mesh,start,end,**changes):
        return classify_mesh_segment(mesh,PrintPoint3(*start),PrintPoint3(*end),**self.kwargs(changes))

    def invalid(self,call,reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure: call()
        self.assertIs(failure.exception.reason,reason)

    def expect_both_directions(self,mesh,start,end,classification):
        expected=MeshSegmentClassification("complete","classified",classification)
        self.assertEqual(self.classify(mesh,start,end),expected)
        self.assertEqual(self.classify(mesh,end,start),expected)

    def test_simple_inside_and_outside_noncontact(self):
        self.expect_both_directions(tetrahedron(),(0.125,0.125,0.125),(0.25,0.125,0.125),"strictly-inside")
        self.expect_both_directions(cube(),(2,0.25,0.25),(3,0.75,0.75),"strictly-outside")

    def test_inside_endpoints_can_exit_concave_material(self):
        mesh=bipyramid(((1,0,0),(0,1,0),(-1,0,0),(0,-1,0)),(0,0,1),(0,0,0.5))
        start,end=(-0.625,0,0.25),(0.625,0,0.25)
        for endpoint in (start,end):
            self.assertEqual(classify_mesh_point(mesh,PrintPoint3(*endpoint),**self.kwargs({})).classification,"inside")
        self.assertEqual(classify_mesh_point(mesh,PrintPoint3(0,0,0.25),**self.kwargs({})).classification,"outside")
        self.expect_both_directions(mesh,start,end,"boundary-contact")
        # A shorter segment wholly in the cavity has no material contact.
        self.expect_both_directions(mesh,(-0.25,0,0.25),(0.25,0,0.25),"strictly-outside")

    def test_outside_endpoints_crossing_solid_are_contact(self):
        self.expect_both_directions(cube(),(-1,0.5,0.5),(2,0.5,0.5),"boundary-contact")

    def test_endpoint_face_edge_vertex_contact_has_precedence(self):
        for end in ((1,0.5,0.5),(1,1,0.5),(1,1,1)):
            self.expect_both_directions(cube(),(0.5,0.5,0.5),end,"boundary-contact")

    def test_coplanar_face_overlap_and_shared_edge_overlap(self):
        self.expect_both_directions(cube(),(-1,0.5,1),(2,0.5,1),"boundary-contact")
        self.expect_both_directions(cube(),(-1,0,1),(2,0,1),"boundary-contact")
        self.expect_both_directions(cube(),(0.125,0.125,1),(0.75,0.125,1),"boundary-contact")

    def test_single_vertex_tangent_from_outside(self):
        # x+y=0, z=1 meets the closed unit cube only at (0,0,1).
        self.expect_both_directions(cube(),(-1,1,1),(1,-1,1),"boundary-contact")

    def test_coplanar_but_disjoint_does_not_invent_contact(self):
        # At z=1 the first ray is coplanar; other deterministic directions resolve outside.
        self.expect_both_directions(cube(),(2,2,1),(3,2,1),"strictly-outside")

    def test_contact_precedes_endpoint_ray_exhaustion(self):
        result=self.classify(cube(),(0.5,0.5,0.5),(2,0.5,0.5),max_ray_directions=1)
        self.assertEqual(result.classification,"boundary-contact")
        result=self.classify(cube(),(0.5,0.5,0.5),(0.75,0.5,0.5),max_ray_directions=1)
        self.assertEqual((result.state,result.reason,result.classification),("incomplete","ray-directions-exhausted",None))

    def test_reversal_mirror_translation_and_global_winding(self):
        mesh=tetrahedron()
        variants=((replace(mesh,triangles=tuple((a,c,b) for a,b,c in mesh.triangles)),(0.125,0.125,0.125),(0.25,0.125,0.125)),
                  (replace(mesh,vertices=tuple(PrintPoint3(-p.x_mm,p.y_mm,p.z_mm) for p in mesh.vertices)),(-0.125,0.125,0.125),(-0.25,0.125,0.125)),
                  (replace(mesh,vertices=tuple(PrintPoint3(p.x_mm+17,p.y_mm-9,p.z_mm+2) for p in mesh.vertices)),(17.125,-8.875,2.125),(17.25,-8.875,2.125)))
        for candidate,start,end in variants: self.expect_both_directions(candidate,start,end,"strictly-inside")

    def test_tiny_huge_and_subnormal_nonzero_segments(self):
        base=tetrahedron()
        for scale in (math.ldexp(1.0,-1000),1e200):
            mesh=replace(base,vertices=tuple(PrintPoint3(p.x_mm*scale,p.y_mm*scale,p.z_mm*scale) for p in base.vertices))
            self.expect_both_directions(mesh,(scale/8,scale/8,scale/8),(scale/4,scale/8,scale/8),"strictly-inside")
        tiny=math.ulp(0.0)
        mesh=replace(base,vertices=tuple(PrintPoint3(p.x_mm*tiny,p.y_mm*tiny,p.z_mm*tiny) for p in base.vertices))
        self.expect_both_directions(mesh,(0,0,0),(tiny,0,0),"boundary-contact")

    def test_fresh_embedding_invalidity_precedes_contact_classification(self):
        mesh=bipyramid(((0,0,0),(3,2,0),(0,2,0),(2,0,0)),(0.5,0.5,1),(0.5,0.5,-1))
        result=self.classify(mesh,(0,0,0),(3,2,0))
        self.assertEqual(result,MeshSegmentClassification("rejected","self-intersection",None))
        open_mesh=replace(tetrahedron(),triangles=tetrahedron().triangles[1:])
        self.assertEqual(self.classify(open_mesh,(0,0,0),(1,0,0)).reason,"nonmanifold-edge")

    def test_pair_resource_limit_and_exact_budget(self):
        start,end=(0.125,0.125,0.125),(0.25,0.125,0.125)
        self.assertEqual(self.classify(tetrahedron(),start,end,max_pair_checks=5),MeshSegmentClassification("incomplete","resource-limit",None))
        self.assertEqual(self.classify(tetrahedron(),start,end,max_pair_checks=6).classification,"strictly-inside")

    def test_internal_endpoint_inconsistency_fails_closed(self):
        # Fault injection at a private helper is not a public proof-producing port.
        for outcomes in (("inside","outside"),("boundary","inside")):
            with patch("adaptive_subedge.engine.material_side._classify_point",side_effect=outcomes):
                result=self.classify(cube(),(0.25,0.25,0.25),(0.75,0.25,0.25))
            self.assertEqual(result,MeshSegmentClassification("incomplete","classification-inconsistent",None))

    def test_embedding_is_fresh_once_per_public_segment_call(self):
        with patch.object(material_side,"_embedding",wraps=material_side._embedding) as embedding:
            for _ in range(2):
                result=self.classify(tetrahedron(),(0.125,0.125,0.125),(0.25,0.125,0.125))
                self.assertEqual(result.classification,"strictly-inside")
            self.assertEqual(embedding.call_count,2)

    def test_bad_types_limits_and_normalized_zero_length_reject(self):
        kwargs=self.kwargs({})
        self.invalid(lambda:classify_mesh_segment(cube(),(0,0,0),PrintPoint3(1,0,0),**kwargs))
        self.invalid(lambda:self.classify(cube(),(0,0,0),(0,0,0)))
        # Distinct exact ints collapse to the same normalized binary64 coordinate.
        self.invalid(lambda:self.classify(cube(),(2**54,0,0),(2**54+1,0,0)))
        for field in ("max_vertices","max_triangles","max_pair_checks","max_ray_directions"):
            for bad in (0,-1,True,1.5):
                self.invalid(lambda:self.classify(cube(),(0,0,0),(1,0,0),**{field:bad}),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.classify(cube(),(0,0,0),(1,0,0),cancelled=None),ReasonCode.INVALID_SETTING)

    def test_cancellation_all_observed_phases_has_no_partial_classification(self):
        for start,end in (((0.125,0.125,0.125),(0.25,0.125,0.125)),((0,0,0),(1,0,0))):
            count=0
            def count_calls():
                nonlocal count
                count+=1
                return False
            self.assertEqual(self.classify(tetrahedron(),start,end,cancelled=count_calls).state,"complete")
            for target in range(1,count+1):
                seen=0
                def cancel():
                    nonlocal seen
                    seen+=1
                    return seen==target
                result=self.classify(tetrahedron(),start,end,cancelled=cancel)
                self.assertEqual(result,MeshSegmentClassification("incomplete","cancelled",None))
                self.assertEqual(seen,target)

    def test_callback_exception_and_bad_bool_propagate(self):
        for bad in (0,1,None,"false"):
            self.invalid(lambda:self.classify(cube(),(0,0,0),(1,0,0),cancelled=lambda:bad),ReasonCode.INVALID_SETTING)
        def explode(): raise LookupError("caller")
        with self.assertRaises(LookupError): self.classify(cube(),(0,0,0),(1,0,0),cancelled=explode)

    def test_immutable_closed_result_and_canonical_exclusion(self):
        result=MeshSegmentClassification("complete","classified","strictly-inside")
        self.assertFalse(hasattr(result,"__dict__"))
        for omitted in fields(result):
            kwargs={f.name:getattr(result,f.name) for f in fields(result) if f!=omitted}
            with self.assertRaises(TypeError): MeshSegmentClassification(**kwargs)
        with self.assertRaises(FrozenInstanceError): result.classification="strictly-outside"
        with self.assertRaises(ContractError): semantic_tree(result)
        with self.assertRaises(ContractError): identity_root("subedge-plan",result,schema_version="2")
        for state,reason,classification in (("complete","classified",None),("complete","classified","inside"),
                                            ("incomplete","classification-inconsistent","boundary-contact"),
                                            ("rejected","self-intersection","strictly-outside")):
            self.invalid(lambda:MeshSegmentClassification(state,reason,classification))


if __name__=="__main__":
    unittest.main()
