"""Exact empirical correction and real plugin settings persistence contracts."""
from dataclasses import replace
from fractions import Fraction as F
from tempfile import TemporaryDirectory
import unittest
from adaptive_subedge.engine.empirical_material import resolve_policy, factor_for_angle, factor_for_section
from adaptive_subedge.application.empirical_material_settings import encode_policy, decode_policy, policy_identity
from smoothificator_preview.material_settings import load_policy, save_policy


class EmpiricalMaterialTests(unittest.TestCase):
    def test_endpoints_actual_section_and_exact_factor(self):
        policy = resolve_policy()
        self.assertEqual(policy.maximum_angle_degrees, F('33.95770549'))
        self.assertEqual(factor_for_angle(F(0), policy).factor, 1)
        self.assertEqual(factor_for_angle(policy.maximum_angle_degrees, policy).factor, F(1,4))
        self.assertEqual(factor_for_angle(F(45), policy).factor, F(1,4))
        actual = factor_for_section(F('.4'), F('.2'), policy)
        self.assertEqual(actual.angle_degrees, F('26.56505118'))
        self.assertEqual(actual.factor, 1-3*actual.angle_degrees/(4*policy.maximum_angle_degrees))

    def test_strict_roundtrip_and_forged_endpoint(self):
        policy = resolve_policy()
        self.assertEqual(decode_policy(encode_policy(policy)), policy)
        self.assertEqual(len(policy_identity(policy)),64)
        for content in (b'{}',b'['*1500+b']'*1500,b'{"schema":1,"schema":2}',encode_policy(policy).replace(b'33.95770549',b'34')):
            with self.assertRaises(ValueError): decode_policy(content)
        for end in (F(0),F(101),.5,True):
            with self.assertRaises(ValueError): resolve_policy(end_percent=end)
        with self.assertRaises(ValueError): resolve_policy(start_percent=F(40),end_percent=F(50))

    def test_atomic_save_reload_and_corruption_preserved(self):
        with TemporaryDirectory() as root:
            initial,path=load_policy(root)
            self.assertFalse(path.exists())
            changed=resolve_policy(start_percent=F(95),end_percent=F(55),retract_mm=F(2))
            self.assertEqual(save_policy(root,changed)[0],changed)
            self.assertEqual(load_policy(root)[0],changed)
            self.assertNotEqual(policy_identity(initial),policy_identity(changed))
            path.write_bytes(b'broken')
            with self.assertRaises(ValueError): load_policy(root)
            self.assertEqual(path.read_bytes(),b'broken')

    def test_real_entrypoint_save_reopen_and_stale_window(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from tests.unit.test_readonly_preview import PreviewLifecycleTests
        module, windows = PreviewLifecycleTests().load_entrypoint()
        with TemporaryDirectory() as root:
            module.orca.host.plugin = SimpleNamespace(storage=lambda: root)
            capability = module.CandidatePreview()
            with patch.dict("sys.modules", {"numpy": SimpleNamespace(__version__="2.2.6")}):
                capability.execute()
                epoch = capability.window_epoch
                request = {"command":"save_material_policy", "start_percent":"95", "end_percent":"55",
                    "retract_mm":"1.6", "wipe_mm":"1", "admission_layer_height_mm":"0.2",
                    "admission_minimum_width_mm":"0.21", "minimum_modeled_thickness_mm":"0.08"}
                capability.on_message(request, epoch)
                saved = windows[-1].posted[-1]["material_settings"]
                self.assertEqual(saved["settings"]["end_percent"],"55")
                capability.execute()
                self.assertEqual(load_policy(root)[0].end_percent,F(55))
                capability.on_message(request | {"end_percent":"60"}, epoch)
                self.assertEqual(load_policy(root)[0].end_percent,F(55))
                html = module.page(module.copy_model(module.orca.host.model()))
                self.assertIn("補完試験出力用設定", html)
                self.assertIn("未保存の変更", html)
                self.assertIn("以前のJSON設定を使用", html)

    def test_v1_preserves_explicit_endpoint_and_no_filter(self):
        legacy = resolve_policy(end_percent=F(50), minimum_modeled_thickness_mm=None)
        content = encode_policy(legacy)
        self.assertIn(b'material-v1', content)
        self.assertNotIn(b'minimum_modeled_thickness_mm', content)
        restored = decode_policy(content)
        self.assertEqual(restored.end_percent,F(50))
        self.assertIsNone(restored.minimum_modeled_thickness_mm)
        self.assertEqual(encode_policy(restored),content)
        current=resolve_policy()
        self.assertEqual(current.end_percent,F(25))
        self.assertEqual(current.minimum_modeled_thickness_mm,F('.08'))
        self.assertIn(b'material-v2',encode_policy(current))
        self.assertNotEqual(policy_identity(current),policy_identity(legacy))

    def test_modeled_area_gate_exact_boundaries_and_units(self):
        from adaptive_subedge.engine.empirical_material import compare_modeled_minimum_thickness as compare, PI_LOWER, PI_UPPER
        common=dict(filament_diameter_mm=F(2),length_mm=F(10),flow_multiplier=F(1),nominal_width_mm=F('.08'),minimum_height_mm=F('.08'))
        # w=h makes required area pi*h²/4, so exact equality has rational E.
        equality=F('.08')**2*10/4
        self.assertTrue(compare(corrected_e_mm=equality,**common).accepted)
        self.assertFalse(compare(corrected_e_mm=equality-F(1,10**9),**common).accepted)
        self.assertTrue(compare(corrected_e_mm=equality+F(1,10**9),**common).accepted)
        self.assertTrue(compare(corrected_e_mm=2*equality,**(common|{'flow_multiplier':F(2)})).accepted)
        self.assertTrue(compare(corrected_e_mm=4*equality,**(common|{'filament_diameter_mm':F(1)})).accepted)
        self.assertFalse(compare(corrected_e_mm=equality,**(common|{'nominal_width_mm':F('.21')})).accepted)
        self.assertLess(PI_UPPER-PI_LOWER,F(1,10**50))
        near_pi=F('3.141592653589793238462643383279502884197169399375105820974944')
        h=F('.08');w=F('.21');boundary_e=10*(h*h/4+(w*h-h*h)/near_pi)
        unresolved=compare(corrected_e_mm=boundary_e,**(common|{'nominal_width_mm':w}))
        self.assertEqual(unresolved.state,'unresolved-pi-enclosure')
        self.assertFalse(unresolved.accepted)
        for bad in (0,True,float('nan'),F(0),F(-1)):
            with self.assertRaises(ValueError):compare(corrected_e_mm=bad,**common)

if __name__=='__main__': unittest.main()
