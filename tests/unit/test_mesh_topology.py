"""Independent combinatorial fixtures; prepared topology is not embeddedness proof."""
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F
import math
import unittest

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint3
from adaptive_subedge.domain.mesh_topology import IndexedTriangleMesh, OrientedMeshTopology, MeshTopologyResult
from adaptive_subedge.engine.mesh_topology import prepare_mesh_topology


def tetrahedron():
    return IndexedTriangleMesh(tuple(PrintPoint3(*p) for p in ((0,0,0), (1,0,0), (0,1,0), (0,0,1))),
        ((0,2,1), (0,1,3), (0,3,2), (1,2,3)))


def cube():
    vertices = ((0,0,0), (1,0,0), (1,1,0), (0,1,0), (0,0,1), (1,0,1), (1,1,1), (0,1,1))
    triangles = ((0,2,1), (0,3,2), (4,5,6), (4,6,7), (0,1,5), (0,5,4),
                 (1,2,6), (1,6,5), (2,3,7), (2,7,6), (3,0,4), (3,4,7))
    return IndexedTriangleMesh(tuple(PrintPoint3(*p) for p in vertices), triangles)


def subdivide(mesh):
    vertices = list(mesh.vertices)
    midpoints = {}
    def midpoint(a, b):
        edge = tuple(sorted((a, b)))
        if edge not in midpoints:
            pa, pb = vertices[a], vertices[b]
            midpoints[edge] = len(vertices)
            vertices.append(PrintPoint3((pa.x_mm+pb.x_mm)/2, (pa.y_mm+pb.y_mm)/2, (pa.z_mm+pb.z_mm)/2))
        return midpoints[edge]
    faces = []
    for a, b, c in mesh.triangles:
        ab, bc, ca = midpoint(a,b), midpoint(b,c), midpoint(c,a)
        faces.extend(((a,ab,ca), (ab,b,bc), (ca,bc,c), (ab,bc,ca)))
    return IndexedTriangleMesh(tuple(vertices), tuple(faces))


def signed_six_volume(vertices, triangles):
    """Independent determinant expansion at the global origin."""
    total = F(0)
    for triangle in triangles:
        a,b,c = (tuple(F(float(x)) for x in (vertices[i].x_mm,vertices[i].y_mm,vertices[i].z_mm)) for i in triangle)
        total += a[0]*b[1]*c[2] + a[1]*b[2]*c[0] + a[2]*b[0]*c[1] - a[2]*b[1]*c[0] - a[1]*b[0]*c[2] - a[0]*b[2]*c[1]
    return total


class MeshTopologyTests(unittest.TestCase):
    def prepare(self, mesh, **changes):
        return prepare_mesh_topology(mesh, **(dict(max_vertices=10000, max_triangles=20000, cancelled=lambda:False) | changes))

    def rejected(self, mesh, reason):
        self.assertEqual(self.prepare(mesh), MeshTopologyResult("rejected", reason, None))

    def invalid(self, call, reason=ReasonCode.INVALID_GEOMETRY):
        with self.assertRaises(ContractError) as failure:
            call()
        self.assertIs(failure.exception.reason, reason)

    def test_tetra_exact_edges_adjacency_and_original_identity(self):
        mesh = tetrahedron()
        result = self.prepare(mesh)
        self.assertEqual((result.state, result.reason), ("complete", "prepared"))
        topology = result.topology
        self.assertIs(topology.mesh, mesh)
        self.assertEqual(topology.oriented_triangles, mesh.triangles)
        self.assertEqual(topology.edges, ((0,1,0,1), (0,2,0,2), (0,3,1,2), (1,2,0,3), (1,3,1,3), (2,3,2,3)))
        self.assertEqual(topology.vertex_faces, ((0,1,2), (0,1,3), (0,2,3), (1,2,3)))
        self.assertEqual(topology.input_signed_volume_six_mm3, F(1))
        self.assertFalse(topology.globally_flipped)

    def test_cube_exact_volume_and_connectivity(self):
        mesh = cube()
        topology = self.prepare(mesh).topology
        self.assertEqual(topology.input_signed_volume_six_mm3, F(6))
        self.assertEqual(len(topology.edges), 18)
        self.assertEqual(sum(map(len, topology.vertex_faces)), 36)
        for low, high, face0, face1 in topology.edges:
            self.assertLess(low, high)
            self.assertLess(face0, face1)
            for face in (face0, face1):
                self.assertTrue({low, high}.issubset(mesh.triangles[face]))
        self.assertEqual(self.prepare(mesh), self.prepare(mesh))

    def test_global_reversal_mirror_and_translation_preserve_input(self):
        mesh = tetrahedron()
        reversed_mesh = replace(mesh, triangles=tuple((a,c,b) for a,b,c in mesh.triangles))
        mirror = replace(mesh, vertices=tuple(PrintPoint3(-p.x_mm,p.y_mm,p.z_mm) for p in mesh.vertices))
        translated = replace(mesh, vertices=tuple(PrintPoint3(p.x_mm+17,p.y_mm-31,p.z_mm+9) for p in mesh.vertices))
        for candidate, sign in ((reversed_mesh,-1), (mirror,-1), (translated,1)):
            original_triangles = candidate.triangles
            topology = self.prepare(candidate).topology
            self.assertEqual(topology.input_signed_volume_six_mm3, sign)
            self.assertEqual(topology.globally_flipped, sign<0)
            self.assertEqual(signed_six_volume(candidate.vertices, topology.oriented_triangles), 1)
            self.assertEqual(candidate.triangles, original_triangles)
            self.assertEqual(tuple(t[0] for t in topology.oriented_triangles), tuple(t[0] for t in original_triangles))

    def test_empty_unused_and_bounds_precedence(self):
        self.rejected(IndexedTriangleMesh((),()), "empty-mesh")
        mesh = tetrahedron()
        self.rejected(replace(mesh, vertices=mesh.vertices+(PrintPoint3(4,4,4),)), "unused-vertex")
        planar = replace(mesh, vertices=tuple(PrintPoint3(p.x_mm,p.y_mm,0) for p in mesh.vertices))
        self.rejected(planar, "degenerate-bounds")

    def test_degenerate_duplicate_and_reversed_duplicate_faces(self):
        mesh = tetrahedron()
        self.rejected(replace(mesh, triangles=((0,0,1),)+mesh.triangles), "degenerate-triangle")
        # All extents stay positive, and the new point is used only by a collinear face.
        collinear = replace(mesh, vertices=mesh.vertices+(PrintPoint3(2,0,0),), triangles=mesh.triangles+((0,1,4),))
        self.rejected(collinear, "degenerate-triangle")
        for duplicate in (mesh.triangles[0], tuple(reversed(mesh.triangles[0]))):
            self.rejected(replace(mesh, triangles=mesh.triangles+(duplicate,)), "duplicate-triangle")

    def test_open_edge_nonmanifold_edge_and_local_winding(self):
        mesh = tetrahedron()
        self.rejected(replace(mesh, triangles=mesh.triangles[1:]), "nonmanifold-edge")
        extra = replace(mesh, vertices=mesh.vertices+(PrintPoint3(0,-1,1),), triangles=mesh.triangles+((0,1,4),))
        self.rejected(extra, "nonmanifold-edge")
        a,b,c=mesh.triangles[0]
        self.rejected(replace(mesh, triangles=((a,c,b),)+mesh.triangles[1:]), "inconsistent-winding")

    def test_disconnected_closed_shells(self):
        mesh=tetrahedron()
        other=tuple(PrintPoint3(p.x_mm+3,p.y_mm,p.z_mm) for p in mesh.vertices)
        disconnected=IndexedTriangleMesh(mesh.vertices+other, mesh.triangles+tuple(tuple(i+4 for i in f) for f in mesh.triangles))
        self.rejected(disconnected,"disconnected-shell")

    def test_connected_edge_manifold_with_pinched_vertex_link(self):
        mesh=subdivide(cube())
        # Opposite original cube corners have disjoint neighbors after edge subdivision.
        # Identifying them preserves the connected face graph and two-face edges,
        # but joins two disjoint vertex-link cycles into a pinched vertex.
        def remap(index):
            index = 0 if index == 6 else index
            return index-1 if index>6 else index
        pinched=IndexedTriangleMesh(mesh.vertices[:6]+mesh.vertices[7:], tuple(tuple(remap(i) for i in f) for f in mesh.triangles))
        self.rejected(pinched,"nonmanifold-vertex")

    def test_zero_volume_and_nonembedded_manifold_are_distinct(self):
        ring=((1,0,0),(0,1,0),(-1,0,0),(0,-1,0))
        faces=tuple(f for i in range(4) for f in ((4,i,(i+1)%4),(5,(i+1)%4,i)))
        zero=IndexedTriangleMesh(tuple(PrintPoint3(*p) for p in ring+((0,0,1),(0,0,1))),faces)
        self.rejected(zero,"zero-signed-volume")
        folded=replace(zero,vertices=zero.vertices[:5]+(PrintPoint3(0,0,0.5),))
        result=self.prepare(folded)
        self.assertEqual(result.state,"complete")
        self.assertFalse(hasattr(result,"injectable"))
        self.assertFalse(hasattr(result.topology,"material_side_validated"))

    def test_exact_subnormal_and_huge_signed_volume(self):
        mesh=tetrahedron()
        for scale in (math.ulp(0.0),1e308):
            candidate=replace(mesh,vertices=tuple(PrintPoint3(p.x_mm*scale,p.y_mm*scale,p.z_mm*scale) for p in mesh.vertices))
            topology=self.prepare(candidate).topology
            self.assertEqual(topology.input_signed_volume_six_mm3,F(scale)**3)

    def test_outer_tuple_only_and_malformed_elements_checked_within_budget(self):
        for vertices,triangles in (([],()),((),[])):
            self.invalid(lambda:IndexedTriangleMesh(vertices,triangles))
        mesh=tetrahedron()
        for bad in (None,{},(0,0,0)):
            malformed=replace(mesh,vertices=(bad,)+mesh.vertices[1:])
            self.invalid(lambda:self.prepare(malformed))
        for face in ((True,1,2),(-1,1,2),(0,1,4),(0,1),[0,1,2],(0,1,2.0)):
            malformed=replace(mesh,triangles=(face,)+mesh.triangles[1:])
            self.invalid(lambda:self.prepare(malformed))
        class IntSubclass(int): pass
        self.invalid(lambda:self.prepare(replace(mesh,triangles=((IntSubclass(0),2,1),)+mesh.triangles[1:])))

    def test_limits_resource_precedence_and_exact_threshold(self):
        mesh=tetrahedron()
        self.assertEqual(self.prepare(mesh,max_vertices=4,max_triangles=4).state,"complete")
        for changes in ({"max_vertices":3},{"max_triangles":3}):
            self.assertEqual(self.prepare(mesh,**changes),MeshTopologyResult("incomplete","resource-limit",None))
        malformed=IndexedTriangleMesh((None,)*5,((False,),)*5)
        self.assertEqual(self.prepare(malformed,max_vertices=4),MeshTopologyResult("incomplete","resource-limit",None))
        for name in ("max_vertices","max_triangles"):
            for value in (0,-1,True,1.5,None):
                self.invalid(lambda:self.prepare(mesh,**{name:value}),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.prepare(mesh,cancelled=None),ReasonCode.INVALID_SETTING)

    def test_cancellation_every_observed_checkpoint_and_no_partial_view(self):
        mesh=tetrahedron()
        count=0
        def count_calls():
            nonlocal count
            count+=1
            return False
        self.assertEqual(self.prepare(mesh,cancelled=count_calls).state,"complete")
        self.assertGreater(count,4+4+6+4+4)
        for target in range(1,count+1):
            calls=0
            def cancel():
                nonlocal calls
                calls+=1
                return calls==target
            result=self.prepare(mesh,cancelled=cancel)
            self.assertEqual(result,MeshTopologyResult("incomplete","cancelled",None))
            self.assertEqual(calls,target)
        oversized=IndexedTriangleMesh((None,)*5,())
        self.assertEqual(self.prepare(oversized,max_vertices=1,cancelled=lambda:True).reason,"cancelled")

    def test_bad_callback_values_and_exceptions_propagate(self):
        for value in (0,1,None,"false"):
            self.invalid(lambda:self.prepare(tetrahedron(),cancelled=lambda:value),ReasonCode.INVALID_SETTING)
        def fails(): raise LookupError("caller failure")
        with self.assertRaises(LookupError): self.prepare(tetrahedron(),cancelled=fails)

    def test_large_graph_iterative_traversal(self):
        mesh=tetrahedron()
        for _ in range(4): mesh=subdivide(mesh)
        self.assertEqual(len(mesh.triangles),1024)
        result=self.prepare(mesh)
        self.assertEqual(result.state,"complete")
        self.assertEqual(result.topology.input_signed_volume_six_mm3,1)
        self.assertEqual(len(result.topology.edges),1536)

    def test_immutable_required_types_and_projection_exclusion(self):
        mesh=tetrahedron()
        result=self.prepare(mesh)
        for value in (mesh,result.topology,result):
            self.assertFalse(hasattr(value,"__dict__"))
            for omitted in fields(value):
                kwargs={f.name:getattr(value,f.name) for f in fields(value) if f!=omitted}
                with self.assertRaises(TypeError): type(value)(**kwargs)
            with self.assertRaises(FrozenInstanceError): setattr(value,fields(value)[0].name,None)
            with self.assertRaises(ContractError): semantic_tree(value)
            with self.assertRaises(ContractError): identity_root("subedge-plan",value,schema_version="2")
        for state,reason,topology in (("complete","prepared",None),("rejected","empty-mesh",result.topology),
                                      ("incomplete","cancelled",result.topology),("validated","prepared",result.topology)):
            self.invalid(lambda:MeshTopologyResult(state,reason,topology))

    def test_topology_constructor_shape_does_not_grant_proof(self):
        topology=self.prepare(tetrahedron()).topology
        for change in ({"mesh":{}},{"oriented_triangles":[]},{"edges":tuple(reversed(topology.edges))},
                       {"vertex_faces":topology.vertex_faces[:-1]},{"input_signed_volume_six_mm3":0},
                       {"input_signed_volume_six_mm3":F(0)},{"globally_flipped":True},{"globally_flipped":1}):
            self.invalid(lambda:replace(topology,**change))


if __name__ == "__main__":
    unittest.main()
