"""Analytic continuous-interval certificates, not repeated-sampling expectations."""
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F
import math
import unittest

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.settings import MeshSectionPolicy
from adaptive_subedge.domain.section_stability import SectionStabilityResult
from adaptive_subedge.engine.mesh_section import section_mesh_plane
from adaptive_subedge.engine.section_stability import certify_section_stability
from tests.unit.test_mesh_topology import cube, tetrahedron, subdivide
from tests.unit.test_mesh_section import bipyramid


class SectionStabilityTests(unittest.TestCase):
    def setUp(self):
        self.policy=MeshSectionPolicy("indexed_plane_section_v1",2**-20,2**-22,2**-20,0.25,"exact_event_partition_v1")

    def certify(self,mesh=None,z=0.5,halfwidth=0.125,**changes):
        kwargs=dict(policy=self.policy,max_vertices=1000,max_triangles=2000,max_mesh_pair_checks=100000,
                    max_section_segments=1000,max_section_pair_checks=100000,max_section_queries=100,cancelled=lambda:False)
        return certify_section_stability(cube() if mesh is None else mesh,z,halfwidth,**(kwargs|changes))

    def invalid(self,call,reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure: call()
        self.assertIs(failure.exception.reason,reason)

    def test_cube_exact_moving_diagonal_bound_and_inclusive_tolerance(self):
        expected=SectionStabilityResult("complete","stable",F(3,8),F(5,8),F(1,4))
        self.assertEqual(self.certify(),expected)
        smaller=replace(self.policy,section_quantization_geometry_tolerance_mm=math.nextafter(0.25,0))
        self.assertEqual(self.certify(policy=smaller),replace(expected,state="incomplete",reason="displacement-unproven"))
        # Actual cube boundary XY is stationary; rejection is only an unproven conservative bound.
        self.assertEqual(self.certify().maximum_boundary_displacement_upper_bound_mm,F(1,4))

    def test_refined_cube_crosses_ordinary_vertex_events_without_exclusion(self):
        mesh=subdivide(cube())
        result=self.certify(mesh)
        self.assertEqual((result.state,result.reason),("complete","stable"))
        self.assertEqual(result.maximum_boundary_displacement_upper_bound_mm,F(1,4))

    def test_sloping_tetra_hand_computed_piecewise_bound(self):
        mesh=replace(tetrahedron(),vertices=tuple(PrintPoint3(*p) for p in ((0,0,0),(1,0,1),(0,1,2),(0,0,3))))
        policy=replace(self.policy,section_quantization_geometry_tolerance_mm=1.5)
        result=self.certify(mesh,1,0.5,policy=policy)
        # Lower slab speed factor2 gives1; upper factor3 gives1.5.
        self.assertEqual(result,SectionStabilityResult("complete","stable",F(1,2),F(3,2),F(3,2)))

    def test_orphan_tangent_vertex_event_cannot_hide_behind_simple_sections(self):
        mesh=bipyramid(((1,0,0),(0,1,0),(-1,0,0),(0,-1,0)),(0,0,1),(0,0,0.5))
        result=self.certify(mesh,0.625,0.125,policy=replace(self.policy,section_quantization_geometry_tolerance_mm=10))
        self.assertEqual(result,SectionStabilityResult("incomplete","topology-event-unproven",F(1,2),F(3,4),None))

    def test_same_side_on_edge_rejects_even_when_on_vertices_are_in_loop(self):
        mesh=cube()
        roof=tuple(PrintPoint3(p.x_mm,p.y_mm,0.5 if i in (4,6) else p.z_mm)
                   for i,p in enumerate(mesh.vertices))
        mesh=replace(mesh,vertices=roof)
        public_policy=replace(self.policy,section_stability_sampling_convergence_version="unavailable_v1")
        section=section_mesh_plane(mesh,0.5,policy=public_policy,max_vertices=100,max_triangles=100,
            max_section_segments=100,max_pair_checks=1000,cancelled=lambda:False)
        self.assertEqual(section.state,"complete")
        self.assertTrue({(4,),(6,)}.issubset({p.source_vertex_ids for p in section.loop.vertices}))
        # Roof edge(4,6) is tangent: incident roof thirds5,7 both have Z=1.
        # Its endpoints are represented, so only the edge guard detects this event.
        result=self.certify(mesh,0.4375,0.0625)
        self.assertEqual(result,SectionStabilityResult("incomplete","topology-event-unproven",F(3,8),F(1,2),None))

    def test_coplanar_empty_and_multi_loop_fail_without_bound(self):
        self.assertEqual(self.certify(z=0.125).reason,"coplanar-facet")
        outside=self.certify(z=2)
        self.assertEqual((outside.state,outside.reason,outside.maximum_boundary_displacement_upper_bound_mm),
                         ("rejected","non-simple-section",None))
        mesh=bipyramid(((1,0,0),(0,1,0),(-1,0,0),(0,-1,0)),(0,0,1),(0,0,0.5))
        self.assertEqual(self.certify(mesh,0.25,0.0625).reason,"multiple-loops")

    def test_symbolic_route_does_not_change_public_near_on_behavior(self):
        z=2**-21
        public_policy=replace(self.policy,section_stability_sampling_convergence_version="unavailable_v1")
        public=section_mesh_plane(cube(),z,policy=public_policy,max_vertices=100,max_triangles=100,
            max_section_segments=100,max_pair_checks=1000,cancelled=lambda:False)
        self.assertEqual((public.state,public.reason),("incomplete","predicate-uncertain"))
        symbolic=self.certify(z=z,halfwidth=2**-24)
        self.assertEqual(symbolic.state,"complete")
        self.assertEqual(symbolic.maximum_boundary_displacement_upper_bound_mm,F(1,2**23))

    def test_nonrepresentable_knots_and_midpoints_remain_distinct_rationals(self):
        half=2**-55
        result=self.certify(halfwidth=half)
        self.assertEqual(result.state,"complete")
        self.assertEqual(result.z_lower_mm,F(1,2)-F(half))
        self.assertEqual(result.z_upper_mm,F(1,2)+F(half))
        self.assertEqual(result.maximum_boundary_displacement_upper_bound_mm,2*F(half))
        self.assertEqual(float(result.z_lower_mm),float(result.z_upper_mm))

    def test_interval_arithmetic_can_exceed_binary64_range(self):
        result=self.certify(z=1e308,halfwidth=1e308)
        self.assertEqual(result.z_lower_mm,0)
        self.assertEqual(result.z_upper_mm,2*F(1e308))
        self.assertEqual((result.state,result.reason),("rejected","coplanar-facet"))

    def test_mirror_global_reversal_and_z_translation_preserve_bound(self):
        mesh=cube()
        variants=(replace(mesh,triangles=tuple((a,c,b) for a,b,c in mesh.triangles)),
                  replace(mesh,vertices=tuple(PrintPoint3(-p.x_mm,p.y_mm,p.z_mm) for p in mesh.vertices)))
        expected=self.certify(mesh)
        for candidate in variants: self.assertEqual(self.certify(candidate),expected)
        translated=replace(mesh,vertices=tuple(PrintPoint3(p.x_mm+13,p.y_mm-7,p.z_mm+4) for p in mesh.vertices))
        result=self.certify(translated,4.5)
        self.assertEqual(result.maximum_boundary_displacement_upper_bound_mm,expected.maximum_boundary_displacement_upper_bound_mm)
        self.assertEqual(result.z_lower_mm,expected.z_lower_mm+4)
        self.assertEqual(result.z_upper_mm,expected.z_upper_mm+4)

    def test_mesh_section_and_total_query_budgets(self):
        # Three knots (lower/center/upper) require five queries before any work.
        for change in ({"max_mesh_pair_checks":65},{"max_section_segments":7},
                       {"max_section_pair_checks":55},{"max_section_queries":4},{"max_vertices":7}):
            result=self.certify(**change)
            self.assertEqual((result.state,result.reason),("incomplete","resource-limit"))
            self.assertIsNone(result.maximum_boundary_displacement_upper_bound_mm)
        self.assertEqual(self.certify(max_mesh_pair_checks=66,max_section_segments=8,
            max_section_pair_checks=56,max_section_queries=5).state,"complete")

    def test_malformed_policy_limits_query_and_callback(self):
        for field in ("version","section_stability_sampling_convergence_version"):
            self.invalid(lambda:self.certify(policy=replace(self.policy,**{field:"other"})),ReasonCode.INVALID_SETTING)
        for field in ("max_vertices","max_triangles","max_mesh_pair_checks","max_section_segments","max_section_pair_checks","max_section_queries"):
            for bad in (0,-1,True,1.5):
                self.invalid(lambda:self.certify(**{field:bad}),ReasonCode.INVALID_SETTING)
        for bad in (0,-1,True,math.inf,math.nan,10**400):
            self.invalid(lambda:self.certify(halfwidth=bad))
        for bad in (True,math.inf,math.nan,"0.5"):
            self.invalid(lambda:self.certify(z=bad))
        self.invalid(lambda:self.certify(mesh={}))
        self.invalid(lambda:self.certify(policy={}),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.certify(cancelled=None),ReasonCode.INVALID_SETTING)
        for bad in (0,1,None,"false"):
            self.invalid(lambda:self.certify(cancelled=lambda:bad),ReasonCode.INVALID_SETTING)
        def explode(): raise LookupError("caller")
        with self.assertRaises(LookupError): self.certify(cancelled=explode)

    def test_cancellation_every_checkpoint_discards_partial_bound(self):
        count=0
        def count_calls():
            nonlocal count
            count+=1
            return False
        self.assertEqual(self.certify(tetrahedron(),cancelled=count_calls).state,"complete")
        for target in range(1,count+1):
            seen=0
            def cancel():
                nonlocal seen
                seen+=1
                return seen==target
            result=self.certify(tetrahedron(),cancelled=cancel)
            self.assertEqual((result.state,result.reason),("incomplete","cancelled"))
            self.assertIsNone(result.maximum_boundary_displacement_upper_bound_mm)
            self.assertEqual(seen,target)

    def test_result_shape_immutability_and_no_canonical_authority(self):
        result=self.certify()
        self.assertFalse(hasattr(result,"__dict__"))
        for omitted in fields(result):
            kwargs={f.name:getattr(result,f.name) for f in fields(result) if f!=omitted}
            with self.assertRaises(TypeError): SectionStabilityResult(**kwargs)
        with self.assertRaises(FrozenInstanceError): result.state="rejected"
        with self.assertRaises(ContractError): semantic_tree(result)
        with self.assertRaises(ContractError): identity_root("subedge-plan",result,schema_version="2")
        for change in ({"z_lower_mm":0.0},{"z_upper_mm":result.z_lower_mm},
                       {"maximum_boundary_displacement_upper_bound_mm":None},
                       {"maximum_boundary_displacement_upper_bound_mm":F(-1)},
                       {"state":"incomplete","reason":"cancelled"},{"reason":"predicate-uncertain"}):
            self.invalid(lambda:replace(result,**change))


if __name__=="__main__":
    unittest.main()
