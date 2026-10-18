"""User-calibrated formula mode and strict historical policy compatibility."""
from fractions import Fraction as F
import json
import unittest
from adaptive_subedge.engine.retention_polynomial import retention_coefficients,retention_for_t
from adaptive_subedge.engine.smooth_dimensions import resolve_user_policy,resolve_policy,target_dimensions_for_angle
from adaptive_subedge.application.smooth_dimension_settings import encode_policy,decode_policy,policy_identity

class UserDimensionFormulaTests(unittest.TestCase):
    def test_default_and_custom_formula_targets(self):
        p=resolve_user_policy(schema_version=4)
        self.assertEqual((p.schema_version,p.minimum_height_mm,p.minimum_width_mm),(4,F('.01'),F('.1')))
        self.assertFalse(p.research_endpoint_envelope)
        lower=resolve_user_policy(schema_version=4,minimum_height_mm=F('.001'),minimum_width_mm=F('.002'))
        self.assertEqual((lower.minimum_height_mm,lower.minimum_width_mm),(F('.001'),F('.002')))
        with self.assertRaises(ValueError):resolve_user_policy(schema_version=4,minimum_height_mm=F('.0001'))
        endpoint=target_dimensions_for_angle(p.maximum_angle_degrees,F('.4'),F('.18'),p)
        self.assertEqual((endpoint.target_width_mm,endpoint.target_height_mm),(F('.1'),F('.01')))
        linear=resolve_user_policy(schema_version=4,retention_expression='1-t')
        self.assertEqual(retention_for_t('1-t',F(1,2)),F(1,2))
        self.assertNotEqual(policy_identity(p),policy_identity(linear))
        self.assertEqual(retention_coefficients('1-t/2-t/2'),(F(1),F(-1)))
        # Deliberately nonmonotonic/overshooting formulas are bounded at evaluation.
        self.assertEqual(retention_for_t('1-t+10*t*(1-t)',F(1,2)),1)
        self.assertEqual(retention_for_t('1-t-10*t*(1-t)',F(1,2)),0)

    def test_reject_unsafe_singular_and_excessive_expressions(self):
        bad=['__import__("os")','t.real','t[0]','1/(1+t)','1/(t-t)','1/(2-2)','1-t**-1','1-t**13','1-t**True','1-t**1.5','1-(t**8*t**8)','1-t+'+'9'*100,'1-t+'+'-'*30+'0','1-t+'+'0+'*100+'0','1','t','1-t;print(1)','1-t/0','1-t%2','1-t**(1+1)','1-t+1e100','1-t+'+'0'*513]
        for expression in bad:
            with self.subTest(expression=expression),self.assertRaises(ValueError):resolve_user_policy(schema_version=4,retention_expression=expression)

    def test_v1_v2_v3_canonical_documents_unchanged(self):
        policies=[resolve_policy(schema_version=1,maximum_extra_width_ticks=0),resolve_policy(),resolve_policy(schema_version=3,research_endpoint_envelope=True,minimum_height_mm=F('.01'),minimum_width_mm=F('.1'))]
        for p in policies:
            doc=json.loads(encode_policy(p))
            self.assertNotIn('retention_expression',doc['settings'])
            expected=json.dumps(doc,sort_keys=True,separators=(',',':')).encode()+b'\n'
            self.assertEqual(encode_policy(decode_policy(expected)),expected)
        self.assertEqual(policy_identity(policies[0]),'9a975ddbfc72cbd62ce2b56f23a288a48eef6a59aaac1e3414cde1472d3484bb')
        self.assertEqual(policy_identity(policies[1]),'ef495b4dcea8fdbb3d92488c93996e9f5a251bbea2b51315256c884698234ab2')
        current=resolve_user_policy(schema_version=4);content=encode_policy(current)
        self.assertEqual(decode_policy(content),current)
        doc=json.loads(content);doc['settings']['retention_expression']='1/(1+t)'
        with self.assertRaises(ValueError):decode_policy(json.dumps(doc).encode())
        doc=json.loads(content);doc['settings']['research_endpoint_envelope']=False
        with self.assertRaises(ValueError):decode_policy(json.dumps(doc).encode())

    def test_actual_page_script_loads_historical_v3_without_missing_controls(self):
        import re,subprocess,shutil
        from smoothificator_preview.ui import page
        from tests.unit.test_band_preview_application import snapshot_fixture
        node=shutil.which('node')
        if not node:self.skipTest('node runtime unavailable')
        p=resolve_policy(schema_version=3,research_endpoint_envelope=True,minimum_height_mm=F('.01'),minimum_width_mm=F('.1'))
        record={'settings':json.loads(encode_policy(p))['settings'],'saved':True,'path':'legacy.json','identity':policy_identity(p)}
        html=page(snapshot_fixture(),None,record)
        ids=re.findall(r'id="([^"]+)"',html)
        script=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
        harness='const elements=Object.fromEntries('+json.dumps(ids)+'.map(id=>[id,{value:"",textContent:"",addEventListener(){},replaceChildren(){}}]));const document={getElementById(id){return elements[id]??null;}};let receive;const window={orca:{postMessage(){},onMessage(fn){receive=fn;}}};'
        check='receive({dimension_settings:'+json.dumps(record)+'});if(elements.dimension_retention_expression.value!=="1-(6*t**5-15*t**4+10*t**3)")throw Error("legacy formula missing");'
        current=resolve_user_policy();current_record={'settings':json.loads(encode_policy(current))['settings'],'saved':True,'path':'v5.json','identity':policy_identity(current)}
        check+='receive({dimension_settings:'+json.dumps(current_record)+'});if(elements.dimension_minimum_width_mm.value!=="0.02"||elements.dimension_reference_minimum_width_mm.value!=="0.1")throw Error("V5 controls not loaded");'
        run=subprocess.run([node,'-e',harness+script+check],capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)

if __name__=='__main__':unittest.main()
