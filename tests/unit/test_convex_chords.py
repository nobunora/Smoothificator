"""Independent analytic checks for unscored rectangular chord proposals."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import math
import unittest
from unittest.mock import patch

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.convex_chords import ChordProposal, ConvexChordProposalSet
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh
from adaptive_subedge.engine.convex_chords import propose_convex_chords
from adaptive_subedge.engine import convex_chords
from adaptive_subedge.engine.material_side import _Stopped
from tests.unit.test_mesh_topology import cube, tetrahedron


def prism(ring, cap_triangles):
    n=len(ring)
    vertices=tuple(PrintPoint3(x,y,z) for z in (0,1) for x,y in ring)
    faces=[(a,c,b) for a,b,c in cap_triangles]
    faces.extend((a+n,b+n,c+n) for a,b,c in cap_triangles)
    for i in range(n):
        j=(i+1)%n
        faces.extend(((i,j,j+n),(i,j+n,i+n)))
    return IndexedTriangleMesh(vertices,tuple(faces))


def triangle_prism(height=1):
    return prism(((0,0),(1,0),(0,height)),((0,1,2),))


class ConvexChordTests(unittest.TestCase):
    def propose(self,mesh=None,z=0.5,**changes):
        kwargs=dict(axis="X",width_mm=0.25,end_trim_mm=0.125,
                    chord_positions_mm=(0.25,),algorithm_version="convex_axis_chords_v1",
                    max_positions=10,max_vertices=100,max_triangles=100,
                    max_mesh_pair_checks=1000,max_section_segments=100,
                    max_section_pair_checks=1000,max_ray_directions=8,cancelled=lambda:False)
        return propose_convex_chords(cube() if mesh is None else mesh,z,**(kwargs|changes))

    def invalid(self,call,reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure: call()
        self.assertIs(failure.exception.reason,reason)

    def test_cube_sorted_positions_and_axis_parity(self):
        for axis in ("X","Y"):
            result=self.propose(axis=axis,chord_positions_mm=(0.75,0.25,0.5))
            self.assertEqual((result.state,result.reason),("complete","proposals-evaluated"))
            self.assertEqual(tuple(row.position_mm for row in result.proposals),(F(1,4),F(1,2),F(3,4)))
            for row in result.proposals:
                start,end=(F(1,8),row.position_mm),(F(7,8),row.position_mm)
                if axis=="Y": start,end=start[::-1],end[::-1]
                self.assertEqual(row,ChordProposal(row.position_mm,"proposed","unscored",start,end))

    def test_sloped_halfplane_exact_analytic_triangle(self):
        result=self.propose(triangle_prism())
        self.assertEqual(result.proposals,(ChordProposal(F(1,4),"proposed","unscored",(F(1,8),F(1,4)),(F(1,2),F(1,4))),))
        row=self.propose(triangle_prism(),axis="Y").proposals[0]
        self.assertEqual((row.start_xy_mm,row.end_xy_mm),((F(1,4),F(1,8)),(F(1,4),F(1,2))))

    def test_nonbinary_rational_endpoint_is_preserved(self):
        row=self.propose(triangle_prism(3),chord_positions_mm=(0.5,)).proposals[0]
        self.assertEqual(row.end_xy_mm,(F(2,3),F(1,2)))
        self.assertNotEqual(F(float(row.end_xy_mm[0])),row.end_xy_mm[0])

    def test_transverse_width_and_boundary_equality(self):
        rows=self.propose(chord_positions_mm=(0.0625,0.125,0.875,0.9375)).proposals
        self.assertEqual(tuple(row.reason for row in rows),("empty-footprint","unscored","unscored","empty-footprint"))
        self.assertEqual(self.propose(width_mm=1,chord_positions_mm=(0.5,)).proposals[0].state,"proposed")
        self.assertEqual(self.propose(width_mm=2).proposals[0].reason,"empty-footprint")

    def test_singleton_and_trimmed_zero_are_insufficient_span(self):
        for changes in (dict(chord_positions_mm=(0.875,)),dict(chord_positions_mm=(0.625,))):
            row=self.propose(triangle_prism(),**changes).proposals[0]
            self.assertEqual((row.state,row.reason,row.start_xy_mm,row.end_xy_mm),("rejected","insufficient-span",None,None))
        self.assertEqual(self.propose(end_trim_mm=0.5).proposals[0].reason,"insufficient-span")

    def test_winding_mirror_and_translation(self):
        mesh=cube()
        reversed_mesh=replace(mesh,triangles=tuple((a,c,b) for a,b,c in mesh.triangles))
        self.assertEqual(self.propose(mesh),self.propose(reversed_mesh))
        mirrored=replace(mesh,vertices=tuple(PrintPoint3(-p.x_mm,p.y_mm,p.z_mm) for p in mesh.vertices))
        row=self.propose(mirrored).proposals[0]
        self.assertEqual((row.start_xy_mm,row.end_xy_mm),((F(-7,8),F(1,4)),(F(-1,8),F(1,4))))
        shifted=replace(mesh,vertices=tuple(PrintPoint3(p.x_mm+8,p.y_mm-4,p.z_mm+2) for p in mesh.vertices))
        row=self.propose(shifted,2.5,chord_positions_mm=(-3.75,)).proposals[0]
        self.assertEqual((row.start_xy_mm,row.end_xy_mm),((F(65,8),F(-15,4)),(F(71,8),F(-15,4))))

    def test_concavity_rejected_without_hull_repair(self):
        mesh=prism(((0,0),(2,0),(2,1),(1,1),(1,2),(0,2)),((0,1,3),(1,2,3),(0,3,5),(3,4,5)))
        result=self.propose(mesh)
        self.assertEqual((result.state,result.reason,result.proposals),("rejected","nonconvex-section",()))

    def test_fresh_geometry_rejections_and_empty_section(self):
        mesh=tetrahedron()
        for candidate,z,reason in ((replace(mesh,triangles=mesh.triangles[1:]),0.5,"nonmanifold-edge"),(cube(),2,"empty-section"),(cube(),0,"coplanar-facet")):
            result=self.propose(candidate,z)
            self.assertEqual((result.state,result.reason,result.proposals),("rejected",reason,()))

    def test_positions_budget_before_elements_and_mesh_scan(self):
        malformed=IndexedTriangleMesh((object(),),(object(),))
        result=self.propose(malformed,chord_positions_mm=(object(),object()),max_positions=1)
        self.assertEqual((result.state,result.reason,result.proposals),("incomplete","resource-limit",()))
        for positions in ((),(0.0,-0.0),(1,1.0),(math.nan,),[0.25],(object(),)):
            self.invalid(lambda:self.propose(chord_positions_mm=positions))

    def test_scalar_version_limit_and_callback_validation(self):
        for changes in (dict(width_mm=0),dict(width_mm=-1),dict(width_mm=math.inf),dict(end_trim_mm=0),dict(end_trim_mm=True),dict(axis="x")):
            self.invalid(lambda:self.propose(**changes))
        for changes in (dict(algorithm_version="unknown"),dict(max_positions=True),dict(max_ray_directions=0),dict(cancelled=None),dict(cancelled=lambda:1)):
            self.invalid(lambda:self.propose(**changes),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.propose(z=math.nan))
        with self.assertRaisesRegex(RuntimeError,"callback"):
            self.propose(cancelled=lambda:(_ for _ in ()).throw(RuntimeError("callback")))

    def test_each_resource_cap_discards_rows(self):
        for name,value in (("max_vertices",7),("max_triangles",11),("max_mesh_pair_checks",65),("max_section_segments",1),("max_section_pair_checks",1)):
            with self.subTest(name=name):
                result=self.propose(**{name:value})
                self.assertEqual((result.state,result.reason,result.proposals),("incomplete","resource-limit",()))

    def test_fresh_embedding_and_section_once_per_call(self):
        with patch.object(convex_chords,"_embedding",wraps=convex_chords._embedding) as embedding, patch.object(convex_chords,"_section",wraps=convex_chords._section) as section:
            for _ in range(2):
                self.assertEqual(self.propose(chord_positions_mm=(0.25,0.5,0.75)).state,"complete")
            self.assertEqual(embedding.call_count,2)
            self.assertEqual(section.call_count,2)

    def test_material_helper_rows_and_global_discard(self):
        for side,reason in (("boundary-contact","centerline-contact"),("strictly-outside","centerline-outside")):
            with patch.object(convex_chords,"_classify_segment",return_value=side):
                row=self.propose().proposals[0]
                self.assertEqual((row.state,row.reason,row.start_xy_mm,row.end_xy_mm),("rejected",reason,None,None))
        for reason in ("ray-directions-exhausted","classification-inconsistent"):
            with patch.object(convex_chords,"_classify_segment",side_effect=["strictly-inside",_Stopped("incomplete",reason)]):
                result=self.propose(chord_positions_mm=(0.25,0.75))
                self.assertEqual((result.state,result.reason,result.proposals),("incomplete",reason,()))

    def test_cancellation_at_every_observed_checkpoint(self):
        observed=0
        def count():
            nonlocal observed
            observed+=1
            return False
        result=self.propose(tetrahedron(),cancelled=count,chord_positions_mm=(0.125,0.25),width_mm=0.125,end_trim_mm=0.03125)
        self.assertEqual(result.state,"complete")
        self.assertGreater(observed,10)
        for stop in range(1,observed+1):
            calls=0
            def cancel():
                nonlocal calls
                calls+=1
                return calls==stop
            result=self.propose(tetrahedron(),cancelled=cancel,chord_positions_mm=(0.125,0.25),width_mm=0.125,end_trim_mm=0.03125)
            self.assertEqual((result.state,result.reason,result.proposals),("incomplete","cancelled",()),stop)

    def test_dtos_immutable_and_not_identity_authority(self):
        result=self.propose()
        with self.assertRaises(FrozenInstanceError): result.reason="changed"
        self.assertFalse(hasattr(result,"__dict__"))
        self.assertFalse(hasattr(result.proposals[0],"__dict__"))
        for value in (result,result.proposals[0]):
            with self.assertRaises(ContractError): semantic_tree(value)
            with self.assertRaises(ContractError): identity_root("subedge-plan",value,schema_version="2")
        row=result.proposals[0]
        invalid_rows=(lambda:replace(row,position_mm=0.25),lambda:replace(row,state="rejected"),lambda:replace(row,start_xy_mm=(0,F(1,4))),lambda:replace(row,reason="scored"),lambda:replace(row,end_xy_mm=row.start_xy_mm))
        for factory in invalid_rows: self.invalid(factory)
        for changes in (dict(proposals=(row,row)),dict(width_mm=F(0)),dict(state="incomplete",reason="cancelled"),dict(axis="Y")):
            self.invalid(lambda:replace(result,**changes))


if __name__=="__main__":
    unittest.main()
