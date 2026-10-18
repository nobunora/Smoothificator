from fractions import Fraction as F
from tempfile import TemporaryDirectory
import unittest
from adaptive_subedge.engine.smooth_dimensions import resolve_policy,target_dimensions_for_angle,target_dimensions_for_section
from adaptive_subedge.application.smooth_dimension_settings import encode_policy,decode_policy,policy_identity
from smoothificator_preview import dimension_settings

class SmoothDimensionTests(unittest.TestCase):
    def test_plateau_midpoint_endpoint_and_monotonic(self):
        p=resolve_policy();w=F('.4');h=F('.18')
        for angle in (F(0),F(10)):
            t=target_dimensions_for_angle(angle,w,h,p)
            self.assertEqual((t.retention,t.target_width_mm,t.target_height_mm),(1,w,h))
        end=target_dimensions_for_angle(p.maximum_angle_degrees,w,h,p)
        self.assertEqual((end.retention,end.target_width_mm,end.target_height_mm),(0,F('.21'),F('.08')))
        # Endpoint has odd 1e-8 tick count; choose an exactly representable symmetric policy.
        from dataclasses import replace
        p=resolve_policy(plateau_end_degrees=F('10.00000001'))
        middle=(p.maximum_angle_degrees+p.plateau_end_degrees)/2
        t=target_dimensions_for_angle(middle,w,h,p)
        self.assertEqual(t.retention,F(1,2))
        prior=w
        for angle in range(90):
            t=target_dimensions_for_angle(F(angle),w,h,p)
            self.assertLessEqual(t.target_width_mm,prior);prior=t.target_width_mm
            self.assertTrue(F('.08')<=t.target_height_mm<=h)
        actual=target_dimensions_for_section(F('.4'),F('.2'),w,h,p)
        self.assertEqual(actual.angle_degrees,F('26.56505118'))

    def test_closed_codec_invalid_bounds_and_distinct_identity(self):
        p=resolve_policy();content=encode_policy(p)
        self.assertEqual(decode_policy(content),p)
        self.assertEqual(len(policy_identity(p)),64)
        for content in (b'{}',b'['*1500+b']'*1500,content.replace(b'33.95770549',b'34')):
            with self.assertRaises(ValueError):decode_policy(content)
        for kwargs in ({'plateau_end_degrees':F(40)},{'minimum_height_mm':F('.2')},{'minimum_width_mm':F('.2')},{'dimension_grid_mm':F('.003')},{'maximum_width_ticks':True},{'maximum_extra_width_ticks':2},{'maximum_extra_width_ticks':True},{'dimension_grid_mm':F('.01')}):
            with self.assertRaises(ValueError):resolve_policy(**kwargs)
        with self.assertRaises(ValueError):target_dimensions_for_angle(F(20),F('.2'),F('.1'),p)
        self.assertNotEqual(policy_identity(p),policy_identity(resolve_policy(plateau_end_degrees=F(11))))

    def test_v1_roundtrip_preserves_zero_extra_and_identity(self):
        legacy=resolve_policy(maximum_extra_width_ticks=0,schema_version=1)
        content=encode_policy(legacy)
        self.assertIn(b'taper-v1',content)
        self.assertNotIn(b'maximum_extra_width_ticks',content)
        restored=decode_policy(content)
        self.assertEqual(restored.maximum_extra_width_ticks,0)
        self.assertEqual(encode_policy(restored),content)
        self.assertEqual(policy_identity(restored),policy_identity(legacy))
        self.assertEqual(resolve_policy(maximum_extra_width_ticks=0,dimension_grid_mm=F('.01')).dimension_grid_mm,F('.01'))
        current=resolve_policy()
        self.assertIn(b'taper-v2',encode_policy(current))
        self.assertEqual(current.maximum_extra_width_ticks,1)
        self.assertNotEqual(policy_identity(current),policy_identity(legacy))

    def test_separate_file_persistence_and_real_entrypoint(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from tests.unit.test_readonly_preview import PreviewLifecycleTests
        from smoothificator_preview.material_settings import save_policy as save_empirical
        from adaptive_subedge.engine.empirical_material import resolve_policy as empirical
        module,windows=PreviewLifecycleTests().load_entrypoint()
        with TemporaryDirectory() as root:
            _,old=save_empirical(root,empirical());oldbytes=old.read_bytes()
            module.orca.host.plugin=SimpleNamespace(storage=lambda:root)
            capability=module.CandidatePreview()
            with patch.dict('sys.modules',{'numpy':SimpleNamespace(__version__='2.2.6')}):
                capability.execute();epoch=capability.window_epoch
                request={'command':'save_dimension_policy','admission_layer_height_mm':'0.2','admission_minimum_width_mm':'0.21','plateau_end_degrees':'11','minimum_height_mm':'0.08','minimum_width_mm':'0.21','dimension_grid_mm':'0.001','retention_expression':'1-t','reference_minimum_width_mm':'0.21','width_tail_start_degrees':'30','width_tail_expression':'1-t'}
                capability.on_message(request,epoch)
                self.assertEqual(windows[-1].posted[-1]['dimension_settings']['settings']['plateau_end_degrees'],'11')
                capability.execute()
                self.assertEqual(dimension_settings.load_policy(root)[0].plateau_end_degrees,F(11))
                self.assertEqual(dimension_settings.load_policy(root)[0].retention_expression,'1-t')
                self.assertEqual(dimension_settings.load_policy(root)[0].schema_version,5)
                self.assertEqual(dimension_settings.load_policy(root)[0].width_tail_expression,'1-t')
                capability.on_message(request|{'plateau_end_degrees':'12'},epoch)
                self.assertEqual(dimension_settings.load_policy(root)[0].plateau_end_degrees,F(11))
                self.assertEqual(dimension_settings.load_policy(root)[0].retention_expression,'1-t')
                self.assertEqual(dimension_settings.load_policy(root)[0].schema_version,5)
                self.assertEqual(dimension_settings.load_policy(root)[0].width_tail_expression,'1-t')
                self.assertEqual(old.read_bytes(),oldbytes)
                html=module.page(module.copy_model(module.orca.host.model()))
                self.assertIn('経験吐出補正25%と併用しません',html)
                self.assertIn('save_dimension_policy',html)

if __name__=='__main__':unittest.main()
