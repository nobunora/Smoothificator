"""Exact deterministic ruler association and version-bound angle coordinates."""
from dataclasses import replace
from fractions import Fraction as F
from io import BytesIO
from zipfile import ZipFile
from types import SimpleNamespace
import unittest
import json
from tests.unit.test_coupon_spatial_calibration import calibrated_recipe,geometry_fixture
from tools.stepped_coupon_fixture import SteppedCouponFixture,stepped_coupon_mesh,verify_stepped_coupon
from tools.coupon_spatial_calibration import CouponCalibrationPolicy,encode_coupon_policy,decode_coupon_policy,policy_identity,calibration_targets,stadium_area,window_factor


def fixture_archive():
 recipe,_=calibrated_recipe();fixture=SteppedCouponFixture((F(0),F(0),F(0)));v,f,_,_=stepped_coupon_mesh()
 original=recipe.geometry_project_bytes
 vertices=''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in v)
 faces=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in f)
 part=f'<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1"><mesh><vertices>{vertices}</vertices><triangles>{faces}</triangles></mesh></object></resources></model>'.encode()
 output=BytesIO()
 with ZipFile(BytesIO(original)) as source,ZipFile(output,'w') as target:
  for info in source.infolist():target.writestr(info,part if info.filename=='3D/Objects/coupon.model' else source.read(info.filename))
 return fixture,output.getvalue()


class SteppedCouponTests(unittest.TestCase):
 def test_closed_ruler_mesh_and_exact_association(self):
  with self.assertRaises(ValueError):SteppedCouponFixture((F(0),F(0),F(0)),schema_version=True)
  fixture,archive=fixture_archive();self.assertEqual(verify_stepped_coupon(archive,fixture.placed_angle_profile(),fixture),(F(0),F(30)))
  vertices,faces,profile,ticks=stepped_coupon_mesh();self.assertEqual(len(ticks),9);self.assertEqual(profile[0],(0.,1.8));self.assertEqual(max(v[2] for v in vertices),11)
  self.assertEqual(min(v[0] for v in vertices),-7);self.assertEqual(max(v[0] for v in vertices),30)
  for changed in (replace(fixture,translation_mm=(F(1),F(0),F(0))),):
   with self.assertRaisesRegex(ValueError,'association'):verify_stepped_coupon(archive,changed.placed_angle_profile(),changed)
  with self.assertRaisesRegex(ValueError,'association'):verify_stepped_coupon(archive,fixture.placed_angle_profile()[:-1],fixture)
 def test_foreign_units_faces_and_ruler_vertices_rejected(self):
  fixture,archive=fixture_archive()
  for before,after in ((b'<model xmlns=',b'<model unit="inch" xmlns='),(b'x="-7.000000000"',b'x="-6.999000000"'),(b'v1="0"',b'v1="1"')):
   output=BytesIO()
   with ZipFile(BytesIO(archive)) as source,ZipFile(output,'w') as target:
    for info in source.infolist():target.writestr(info,source.read(info.filename).replace(before,after))
   with self.assertRaises(ValueError):verify_stepped_coupon(output.getvalue(),fixture.placed_angle_profile(),fixture)
 def test_angle_mapping_codec_is_explicit_and_legacy_bytes_preserved(self):
  p=CouponCalibrationPolicy(schema_version=3,coordinate='reference_angle',reference_geometry_sha256='f'*64)
  self.assertEqual(decode_coupon_policy(encode_coupon_policy(p)),p)
  for bad in ('3',None,[],True):
   raw=json.loads(encode_coupon_policy(p));raw['schema_version']=bad
   with self.assertRaisesRegex(ValueError,'integer'):decode_coupon_policy(json.dumps(raw).encode())
  self.assertNotEqual(policy_identity(p),policy_identity(CouponCalibrationPolicy()))
  self.assertNotIn(b'reference_geometry',encode_coupon_policy(CouponCalibrationPolicy()))
  for changes in ({'coordinate':'projected'},{'reference_geometry_sha256':''},{'schema_version':2}):
   with self.assertRaises(ValueError):replace(p,**changes)
 def test_pinned_float32_roundtrip_matches_every_coordinate(self):
  from tools.stepped_coupon_fixture import _serialized_mesh
  fixture,archive=fixture_archive();exported=replace(fixture,serialization_mode='orca-f32-v1')
  placed,faces,_,transform=_serialized_mesh(exported)
  # The oracle serialization uses independent binary32 packing and nine-digit strings.
  import struct
  f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
  original,_,_,_=stepped_coupon_mesh();imported=[tuple(f32(x) for x in p) for p in original]
  center=tuple(f32((min(p[i] for p in imported)+max(p[i] for p in imported))/2) for i in range(3))
  self.assertEqual(transform,tuple(F(format(x,'.9g')) for x in center))
  self.assertEqual(placed,tuple(tuple(F(format(f32(p[i]-center[i]),'.9g'))+transform[i] for i in range(3)) for p in imported))
  self.assertGreater(len(exported.placed_angle_profile()),47)
 def test_reference_angle_uses_actual_section_and_tail_anchor(self):
  recipe,_=calibrated_recipe();old=recipe.coupon_calibration;source=old.paths[0]
  p=CouponCalibrationPolicy(schema_version=3,coordinate='reference_angle',reference_geometry_sha256='f'*64)
  # Exact atan(1)=45deg gives coordinate20, independent of specimen Y.
  context=SimpleNamespace(policy=p,placed_profile=old.placed_profile,reference_taper=old.reference_taper,anchor_reference_path_id=old.anchor_reference_path_id)
  actual=replace(source,section_base_mm=F(1),section_rise_mm=F(1),mode='residual')
  distance,area,height=calibration_targets(actual,context)
  self.assertEqual(distance,F(20));self.assertEqual(area,stadium_area(p.tail_width_mm,p.tail_height_mm));self.assertEqual(height,p.tail_height_mm)

if __name__=='__main__':unittest.main()
