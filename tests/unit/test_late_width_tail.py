"""Late width tail preserves printed V4 band and historical policy identities."""
from fractions import Fraction as F
from dataclasses import replace
import json
import unittest
from adaptive_subedge.engine.smooth_dimensions import resolve_user_policy,target_dimensions_for_angle
from adaptive_subedge.application.smooth_dimension_settings import encode_policy,decode_policy,policy_identity

class LateWidthTailTests(unittest.TestCase):
    def test_v5_defaults_band_preservation_and_endpoint(self):
        old=resolve_user_policy(schema_version=4);new=resolve_user_policy()
        self.assertEqual((new.schema_version,new.minimum_height_mm,new.minimum_width_mm,new.reference_minimum_width_mm,new.width_tail_start_degrees),(5,F('.01'),F('.02'),F('.1'),F(30)))
        for w,h in ((F('.21'),F('.13')),(F('.4'),F('.18')),(F('.3'),F('.01'))):
            for angle in (F(0),F(10),F(25),F('27.56349123'),F(30)):
                self.assertEqual(target_dimensions_for_angle(angle,w,h,new),target_dimensions_for_angle(angle,w,h,old))
            end=target_dimensions_for_angle(new.maximum_angle_degrees,w,h,new)
            self.assertEqual((end.target_width_mm,end.target_height_mm),(F('.02'),F('.01')))
            for angle in (F('30.00000001'),F(31),F(32),F(33),new.maximum_angle_degrees):
                a=target_dimensions_for_angle(angle,w,h,new);b=target_dimensions_for_angle(angle,w,h,old)
                self.assertEqual(a.target_height_mm,b.target_height_mm)
                self.assertLessEqual(a.target_width_mm,b.target_width_mm)
                self.assertGreaterEqual(a.target_width_mm,new.minimum_width_mm)

    def test_v4_actual_saved_document_identity_and_v5_closed_schema(self):
        old=resolve_user_policy(schema_version=4)
        self.assertEqual(policy_identity(old),'f482321fc9c6f70168cf1b99a818a2bb08d394b978360d1ee922dd9ddfc357f4')
        self.assertNotIn(b'width_tail',encode_policy(old))
        self.assertEqual(encode_policy(decode_policy(encode_policy(old))),encode_policy(old))
        new=resolve_user_policy();self.assertEqual(decode_policy(encode_policy(new)),new)
        self.assertNotEqual(policy_identity(new),policy_identity(replace(new,width_tail_expression='1-t')))
        doc=json.loads(encode_policy(new));del doc['settings']['reference_minimum_width_mm']
        with self.assertRaises(ValueError):decode_policy(json.dumps(doc).encode())
        doc=json.loads(encode_policy(new));doc['schema']='smoothificator-geometric-dimension-taper-v4'
        with self.assertRaises(ValueError):decode_policy(json.dumps(doc).encode())

    def test_invalid_bounds_formula_and_height_width_fail_closed(self):
        for kwargs in ({'width_tail_start_degrees':F(10)},{'width_tail_start_degrees':F(40)},
                       {'reference_minimum_width_mm':F('.019')},{'reference_minimum_width_mm':F('.1001')},
                       {'width_tail_expression':'1/(1+t)'},{'minimum_width_mm':F('.009')}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):resolve_user_policy(**kwargs)
        p=resolve_user_policy()
        with self.assertRaisesRegex(ValueError,'below-reference'):target_dimensions_for_angle(F(25),F('.05'),F('.01'),p)
        custom=resolve_user_policy(retention_expression='1-t+10*t*(1-t)')
        with self.assertRaisesRegex(ValueError,'height-exceeds-width'):target_dimensions_for_angle(F(33),F('.21'),F('.18'),custom)
        smaller=resolve_user_policy(minimum_width_mm=F('.002'),minimum_height_mm=F('.001'))
        self.assertEqual(smaller.minimum_width_mm,F('.002'))

if __name__=='__main__':unittest.main()
