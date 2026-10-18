"""Specimen mapping, coherent geometry and independent native policy binding."""
from dataclasses import replace
from fractions import Fraction as F
import json
import unittest
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha256

from tests.unit.test_native_user_dimensions import user_recipe
from tests.unit.test_two_tier_intents import graph_policy
from tools.coupon_spatial_calibration import (CouponCalibrationPolicy,CouponCalibrationSourcePath,NativeCouponCalibration,
    encode_coupon_policy,decode_coupon_policy,policy_identity,surface_arc_at_y,profile_angle_at_arc,window_factor,
    smoothstep,stadium_area,coupon_emission_hop,resolve_coupon_path,calibration_targets)
from tools.prepare_two_tier_intents import freeze_supported_graph
from tools.gui_native_trial_copy import rebuild_native_trial_copy
from tools.conditional_nominal_body import fingerprint
from tools.coupon_profile_association import verify_coupon_profile
from tools.gui_native_trial_trace import native_profile_caps


def geometry_fixture(original,profile):
    vertices=[p for y,z in profile for p in ((0,y,0),(30,y,0),(0,y,z),(30,y,z))]
    faces=[]
    for i in range(len(profile)-1):
        a,b=4*i,4*(i+1)
        faces.extend(((a,b,b+1),(a,b+1,a+1),(a+2,a+3,b+3),(a+2,b+3,b+2),
            (a,b+2,b),(a,a+2,b+2),(a+1,b+1,b+3),(a+1,b+3,a+3)))
    a=4*(len(profile)-1);faces.extend(((0,1,3),(0,3,2),(a,a+2,a+3),(a,a+3,a+1)))
    vertex_xml=''.join(f'<vertex x="{x}" y="{float(y)}" z="{float(z)}"/>' for x,y,z in vertices)
    face_xml=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in faces)
    ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    root=f'<model xmlns="{ns}" xmlns:p="urn:test"><resources><object id="2"><components><component objectid="1" p:path="/3D/Objects/coupon.model" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object></resources><build><item objectid="2" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></build></model>'
    part=f'<model xmlns="{ns}"><resources><object id="1"><mesh><vertices>{vertex_xml}</vertices><triangles>{face_xml}</triangles></mesh></object></resources></model>'
    output=BytesIO()
    with ZipFile(BytesIO(original)) as source,ZipFile(output,'w',ZIP_DEFLATED) as target:
        for entry in source.infolist():target.writestr(entry,root.encode() if entry.filename=='3D/3dmodel.model' else source.read(entry.filename))
        target.writestr('3D/Objects/coupon.model',part.encode())
    return output.getvalue()


def calibrated_recipe(*,origin=F(0),policy=None):
    old=user_recipe();insertion=old.insertions[0];reference=insertion.plan.paths[0].intent
    reference_taper=replace(old.dimension_taper,policy=replace(old.dimension_taper.policy,
        schema_version=5,width_tail_start_degrees=old.dimension_taper.policy.maximum_angle_degrees-F('.01')))
    profile=((origin,F(2)),(origin+30,F(17)))
    geometry=geometry_fixture(old.geometry_project_bytes,profile)
    material=native_profile_caps(old.source_bytes,old.project_bytes,geometry,old.limits)[0]
    context=replace(old.context,geometry_project_sha256=sha256(geometry).hexdigest(),effective_profile_identity=material.projection_identity)
    identity=fingerprint(context)
    reference=replace(reference,source_context_identity=identity)
    reference_taper=replace(reference_taper,paths=tuple(replace(p,original_intent=replace(p.original_intent,source_context_identity=identity)) for p in reference_taper.paths))
    old=replace(old,context=context,geometry_project_bytes=geometry)
    source=CouponCalibrationSourcePath(reference,insertion.policy)
    calibration=NativeCouponCalibration(policy or CouponCalibrationPolicy(),profile,old.context.geometry_project_sha256,'b'*64,
        reference_taper,reference.path_id,(source,))
    intent,decision=resolve_coupon_path(source,calibration);hop=coupon_emission_hop(insertion.policy,calibration.policy)
    plan=freeze_supported_graph((intent,),source_context_identity=reference.source_context_identity,policy=hop,
        graph_policy=graph_policy(),cancelled=lambda:False)
    return replace(old,dimension_taper=None,coupon_calibration=calibration,
        insertions=(replace(insertion,policy=hop,plan=plan),)),decision


class CouponCalibrationTests(unittest.TestCase):
    def test_closed_exact_policy_roundtrip_identity(self):
        p=CouponCalibrationPolicy();encoded=encode_coupon_policy(p)
        self.assertEqual(decode_coupon_policy(encoded),p)
        self.assertEqual(policy_identity(p),policy_identity(decode_coupon_policy(encoded)))
        for mutate in (lambda r:r.update(extra='1'),lambda r:r.update(shoulder_mm=.5),
                       lambda r:r.update(windows=[[True,'8','.2']]),lambda r:r.update(schema_version=True)):
            raw=json.loads(encoded);mutate(raw)
            with self.assertRaises(ValueError):decode_coupon_policy(json.dumps(raw).encode())
        with self.assertRaises(ValueError):decode_coupon_policy(b'{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(ValueError,'nesting'):decode_coupon_policy(b'['*4000+b']'*4000)

    def test_legacy_arc_codec_bytes_and_new_coordinate_are_version_bound(self):
        old=CouponCalibrationPolicy(schema_version=1,coordinate='surface_arc')
        self.assertEqual(policy_identity(old),'58c8538d98825607f884d1df2a70cbfd1571bfada9d933945b9c02222e4c8f3a')
        self.assertNotIn(b'coordinate',encode_coupon_policy(old))
        self.assertEqual(decode_coupon_policy(encode_coupon_policy(old)),old)
        new=CouponCalibrationPolicy();self.assertEqual(new.coordinate,'projected')
        self.assertNotEqual(policy_identity(new),policy_identity(old))
        document=json.loads(encode_coupon_policy(new));document.pop('coordinate')
        with self.assertRaises(ValueError):decode_coupon_policy(json.dumps(document).encode())
        with self.assertRaises(ValueError):replace(old,coordinate='projected')

    def test_projected_and_arc_distances_are_explicit_separate_diagnostics(self):
        r,decision=calibrated_recipe()
        self.assertEqual(decision['calibration_distance_mm'],11)
        self.assertEqual(decision['projected_distance_mm'],11)
        self.assertGreater(decision['ruler_surface_arc_mm'],11)
        self.assertEqual(decision['ruler_coordinate'],'projected')
        arc=replace(r.coupon_calibration,policy=replace(r.coupon_calibration.policy,coordinate='surface_arc'))
        distance,_,_=calibration_targets(arc.paths[0],arc)
        self.assertEqual(distance,decision['ruler_surface_arc_mm'])

    def test_projected_new_residual_before16_uses_endpoint_not_admission_seed(self):
        r,_=calibrated_recipe(origin=F(-4));cal=r.coupon_calibration
        reference=replace(cal.reference_taper,policy=replace(cal.reference_taper.policy,minimum_width_mm=F('.02')))
        source=cal.paths[0];old=source.reference_intent
        intent=replace(old,width_mm=F('.141'),physical_height_mm=F('.01'),remaining_height_mm=F('.01'),
            points_mm=tuple((x,y,F('3.01')) for x,y,z in old.points_mm))
        hop=replace(source.admission_hop,bounds=replace(source.admission_hop.bounds,min_candidate_width_mm=.14))
        residual=replace(source,reference_intent=intent,admission_hop=hop,mode='residual',section_base_mm=F('.2'),section_rise_mm=F('.2'))
        cal=replace(cal,reference_taper=reference,paths=(residual,))
        distance,area,height=calibration_targets(residual,cal)
        self.assertEqual(distance,15);self.assertEqual(height,F('.01'))
        self.assertEqual(area,F('.9')*stadium_area(F('.02'),F('.01')))
        self.assertLess(area,stadium_area(F('.141'),F('.01'))/5)
        # At projected16 the profile slope exceeds the old maximum; explicit clamp gives the same endpoint.
        cal=replace(cal,placed_profile=((F(-5),F(2)),(F(25),F(32))))
        distance,area,height=calibration_targets(residual,cal)
        self.assertEqual((distance,area,height),(F(16),F('.9')*stadium_area(F('.02'),F('.01')),F('.01')))

    def test_window_plateaus_shoulders_and_overlap_fail(self):
        p=CouponCalibrationPolicy()
        for s,expected in ((F(6),1),(F('6.5'),F('1.2')),(F('8.5'),F('1.2')),(F(9),1),
                           (F('10.5'),F('1.2')),(F('12.5'),F('1.2')),(F(14),F('.9')),(F(16),F('.9'))):
            self.assertEqual(window_factor(s,p),expected)
        self.assertEqual(window_factor(F('6.25'),p),F('1.1'))
        bad=replace(p,windows=((F(1),F(2),F('-.9')),(F(1),F(2),F('-.9'))))
        with self.assertRaisesRegex(ValueError,'window-factor-nonpositive'):window_factor(F('1.5'),bad)

    def test_source_profile_arc_and_local_slope(self):
        profile=((F(10),F(2)),(F(13),F(6)),(F(16),F(10)))
        self.assertEqual(surface_arc_at_y(profile,F(13)),5)
        self.assertEqual(surface_arc_at_y(profile,F('14.5')),F('7.5'))
        self.assertGreater(profile_angle_at_arc(profile,F(5)),50)
        with self.assertRaises(ValueError):surface_arc_at_y(profile,F(9))
        with self.assertRaises(ValueError):surface_arc_at_y(tuple(reversed(profile)),F(13))

    def test_two_minimum_bounds_adapter_only(self):
        r,_=calibrated_recipe();source=r.coupon_calibration.paths[0];new=r.insertions[0].policy
        self.assertEqual(replace(new,bounds=source.admission_hop.bounds),source.admission_hop)
        self.assertEqual(replace(new.bounds,min_candidate_height_mm=source.admission_hop.bounds.min_candidate_height_mm,
            min_candidate_width_mm=source.admission_hop.bounds.min_candidate_width_mm),source.admission_hop.bounds)

    def test_native_full_e_source_recovery_and_exact_coverage(self):
        r,_=calibrated_recipe();copy=rebuild_native_trial_copy(r,cancelled=lambda:False)
        span=copy.insertion_spans[0]
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],r.source_bytes)
        expected=sum(r.insertions[0].plan.paths[0].local_support_numeric_adapter.relative_e_mm,F(0))
        self.assertEqual(copy.total_added_relative_e_mm,expected)

    def test_stale_intent_or_bounds_or_geometry_fails_native(self):
        r,_=calibrated_recipe();cal=r.coupon_calibration
        changed=replace(cal,policy=replace(cal.policy,windows=((F(0),F(20),F('.4')),)))
        with self.assertRaisesRegex(ValueError,'authoritative geometry'):rebuild_native_trial_copy(replace(r,coupon_calibration=changed),cancelled=lambda:False)
        bad_hop=replace(r.insertions[0].policy,xy_speed_mm_s=r.insertions[0].policy.xy_speed_mm_s/2)
        with self.assertRaises(ValueError):rebuild_native_trial_copy(replace(r,insertions=(replace(r.insertions[0],policy=bad_hop),)),cancelled=lambda:False)
        with self.assertRaisesRegex(ValueError,'geometry identity'):rebuild_native_trial_copy(replace(r,coupon_calibration=replace(cal,geometry_sha256='c'*64)),cancelled=lambda:False)

    def test_cannot_combine_taper_or_empirical_modes(self):
        r,_=calibrated_recipe()
        with self.assertRaisesRegex(ValueError,'distinct immutable specimen'):rebuild_native_trial_copy(replace(r,dimension_taper=r.coupon_calibration.reference_taper),cancelled=lambda:False)

    def test_reference_mapping_cannot_be_forged(self):
        r,_=calibrated_recipe();cal=r.coupon_calibration;source=cal.paths[0]
        with self.assertRaisesRegex(ValueError,'authoritative V5'):replace(cal,paths=(replace(source,reference_intent=replace(source.reference_intent,width_mm=F('.2'))),))
        with self.assertRaisesRegex(ValueError,'requires V5'):replace(cal,reference_taper=user_recipe().dimension_taper)

    def test_actual_mesh_association_rejects_same_digest_false_profile(self):
        r,_=calibrated_recipe();cal=r.coupon_calibration
        self.assertEqual(verify_coupon_profile(r.geometry_project_bytes,cal.placed_profile),(F(0),F(30)))
        changed=replace(cal,placed_profile=tuple((y,z+1) for y,z in cal.placed_profile))
        with self.assertRaisesRegex(ValueError,'profile differs'):rebuild_native_trial_copy(replace(r,coupon_calibration=changed),cancelled=lambda:False)

    def test_mesh_XML_external_declarations_and_zip_bounds_fail_closed(self):
        r,_=calibrated_recipe();cal=r.coupon_calibration
        with self.assertRaisesRegex(ValueError,'byte bound'):verify_coupon_profile(b'x'*20000001,cal.placed_profile)
        output=BytesIO()
        with ZipFile(output,'w') as z:z.writestr('3D/3dmodel.model',b'<!DOCTYPE model [<!ENTITY x "bad">]><model/>')
        with self.assertRaisesRegex(ValueError,'declarations'):verify_coupon_profile(output.getvalue(),cal.placed_profile)

    def test_mesh_unit_and_namespace_are_not_silently_reinterpreted(self):
        r,_=calibrated_recipe();profile=r.coupon_calibration.placed_profile
        for member in ('3D/3dmodel.model','3D/Objects/coupon.model'):
            output=BytesIO()
            with ZipFile(BytesIO(r.geometry_project_bytes)) as source,ZipFile(output,'w') as target:
                for entry in source.infolist():
                    content=source.read(entry.filename)
                    if entry.filename==member:content=content.replace(b'<model ',b'<model unit="inch" ',1)
                    target.writestr(entry,content)
            with self.assertRaisesRegex(ValueError,'millimeter'):verify_coupon_profile(output.getvalue(),profile)
        output=BytesIO()
        with ZipFile(BytesIO(r.geometry_project_bytes)) as source,ZipFile(output,'w') as target:
            for entry in source.infolist():
                content=source.read(entry.filename).replace(b'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',b'urn:wrong')
                target.writestr(entry,content)
        with self.assertRaisesRegex(ValueError,'namespace'):verify_coupon_profile(output.getvalue(),profile)
        output=BytesIO()
        with ZipFile(BytesIO(r.geometry_project_bytes)) as source,ZipFile(output,'w') as target:
            for entry in source.infolist():
                content=source.read(entry.filename)
                if entry.filename=='3D/Objects/coupon.model':content=content.replace(b'<mesh>',b'<mesh xmlns="urn:foreign">')
                target.writestr(entry,content)
        with self.assertRaisesRegex(ValueError,'target differs'):verify_coupon_profile(output.getvalue(),profile)

    def test_tail_is_coherent_nonincreasing_and_representation_bounded(self):
        # Move the profile origin so the same valid native path lies past17mm arc.
        r,decision=calibrated_recipe(origin=F(-7));cal=r.coupon_calibration
        self.assertEqual(decision['target_height_mm'],F('.012'))
        self.assertEqual(decision['target_area_mm2'],stadium_area(F('.015'),F('.012')))
        self.assertGreaterEqual(decision['resolved_intent']['width_mm'],F('.012'))
        self.assertEqual(r.insertions[0].plan.paths[0].intent.support_plane_z_mm,3)
        self.assertLessEqual(decision['resolved_area_mm2'],stadium_area(F('.1'),F('.01')))
        rebuild_native_trial_copy(r,cancelled=lambda:False)

    def test_explicit_residual_admission_requires_saved_rise_and_short_base(self):
        r,_=calibrated_recipe();cal=r.coupon_calibration;source=cal.paths[0]
        hop=replace(source.admission_hop,bounds=replace(source.admission_hop.bounds,min_candidate_width_mm=.14))
        for base,rise in ((F('.1'),F('.1')),(F('.19'),F('.2'))):
            with self.assertRaisesRegex(ValueError,'residual source admission'):
                replace(cal,paths=(replace(source,mode='residual',admission_hop=hop,section_base_mm=base,section_rise_mm=rise),))

    def test_legacy_fingerprint_unchanged_when_mode_inactive(self):
        r=user_recipe();a=rebuild_native_trial_copy(r,cancelled=lambda:False)
        b=rebuild_native_trial_copy(replace(r,coupon_calibration=None),cancelled=lambda:False)
        self.assertEqual(a,b)


if __name__=='__main__':unittest.main()
