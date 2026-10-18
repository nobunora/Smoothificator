import unittest
from fractions import Fraction as F
from dataclasses import replace
from io import BytesIO
from zipfile import ZipFile
from tools.flat_matrix_fixture import *

class Tests(unittest.TestCase):
 def test_complete_geometry_and_numbered_line_layout(self):
  vertices,faces=flat_matrix_mesh();self.assertEqual(len(matrix_cells()),25);self.assertEqual(len({c['id'] for c in matrix_cells()}),25)
  self.assertEqual(tuple((min(v[k] for v in vertices),max(v[k] for v in vertices)) for k in range(3)),((0,64),(0,64),(0,1)))
  edges={}
  for tri in faces:
   for a,b in zip(tri,tri[1:]+tri[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
  self.assertTrue(all(len(e)==2 and e[0]==e[1][::-1] for e in edges.values()))
  for c in matrix_cells():self.assertEqual(c['end_xy_mm'][0]-c['start_xy_mm'][0],10);self.assertEqual(c['label_origin_xy_mm'][1]-c['start_xy_mm'][1],3)
 def test_every_label_has_printable_strokes_and_its_own_cell(self):
  rectangles=label_rectangles();self.assertEqual({r[4] for r in rectangles},{f'{i:02d}' for i in range(1,26)})
  self.assertTrue(all(min(b-a,d-c)>=F('.6') for a,b,c,d,_ in rectangles))
 def test_version_and_placement_are_closed(self):
  for bad in (True,None,[],2):
   with self.assertRaises(ValueError):FlatMatrixFixture(schema_version=bad)
  with self.assertRaises(ValueError):FlatMatrixFixture(translation_mm=(F(0),F(0),F(0)))
 def test_full_mesh_association_rejects_stale_vertex(self):
  def archive(fixture,stale=False):
   vertices,faces,translation=serialized_matrix_mesh(fixture);local=[tuple(p[i]-translation[i] for i in range(3)) for p in vertices]
   if stale:local[0]=(local[0][0]+F('.001'),*local[0][1:])
   ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';prod='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
   main=f'<model unit="millimeter" xmlns="{ns}" xmlns:p="{prod}"><resources><object id="1"><components><component objectid="2" p:path="/3D/part.model" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object></resources><build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 '+ ' '.join(str(float(v)) for v in translation)+'"/></build></model>'
   part=f'<model unit="millimeter" xmlns="{ns}"><resources><object id="2"><mesh><vertices>'+''.join('<vertex '+ ' '.join(f'{k}="{float(v):.9g}"' for k,v in zip('xyz',p))+'/>' for p in local)+'</vertices><triangles>'+''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in faces)+'</triangles></mesh></object></resources></model>'
   buffer=BytesIO()
   with ZipFile(buffer,'w') as z:z.writestr('3D/3dmodel.model',main);z.writestr('3D/part.model',part)
   return buffer.getvalue()
  for mode in ('input-v1','orca-f32-v1'):
   fixture=FlatMatrixFixture(serialization_mode=mode);self.assertEqual(verify_flat_matrix(archive(fixture),fixture),matrix_cells())
   with self.assertRaises(ValueError):verify_flat_matrix(archive(fixture,True),fixture)
 def test_orca_serialization_is_stable(self):
  a=serialized_matrix_mesh(FlatMatrixFixture());b=serialized_matrix_mesh(FlatMatrixFixture());self.assertEqual(a,b);self.assertEqual(a[2],(F(90),F(90),F('.5')))
if __name__=='__main__':unittest.main()
