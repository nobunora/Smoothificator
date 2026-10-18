"""Public-kernel closed interval coverage and honest negative proofs."""
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch
from tests.unit.test_continuous_path_contact import source,path
from tools.native_certified_contact import NativeStripContactPolicy,audit_native_constant_z_contact

P=NativeStripContactPolicy(100,10,100,100,10000,4096,128,F(1,10**12))

def audit(sources=None, candidate=None, policy=P, cancelled=lambda:False):
    return audit_native_constant_z_contact(candidate or path(),(source(),) if sources is None else sources,policy=policy,cancelled=cancelled)

class NativeCertifiedContactTests(unittest.TestCase):
    def test_two_sources_closed_union_certifies_entire_span(self):
        report=audit((source('left',1,end=('.5','0')),source('right',2,start=('.5','0'))))
        self.assertTrue(report.nominal_centerline_contact_proven)
        self.assertEqual([(c.parameter_start,c.parameter_end) for c in report.certificates],[(F(0),F('.5')),(F('.5'),F(1))])
        self.assertEqual(report.query_count,2)
        self.assertFalse(report.physical_authority)

    def test_real_gap_requires_all_source_point_counterexample(self):
        report=audit((source('left',1,end=('.4','0')),source('right',2,start=('.6','0'))))
        self.assertEqual(report.state,'gap-proven')
        self.assertEqual(report.gap_witness.parameter,F('.5'))

    def test_inward_approximation_gap_is_not_geometric_gap(self):
        report=audit(candidate=path((('0','.05'),('1','.05'))),policy=replace(P,inner_inset_mm=F('.2')))
        self.assertEqual(report.state,'incomplete')
        self.assertIsNone(report.gap_witness)

    def test_chronology_and_sloped_source_do_not_invent_positive_coverage(self):
        self.assertEqual(audit((source(order=11),)).state,'gap-proven')
        original=source();sloped=replace(original,segment=replace(original.segment,end_xyz_mm=(F(2),F(0),F('2.3'))))
        self.assertEqual(audit((sloped,)).state,'incomplete')

    def test_duplicate_identity_order_and_candidate_alias_reject(self):
        for sources in ((source(),source('other')), (source(),source(order=2)),(source('candidate'),)):
            with self.assertRaises(ValueError):audit(sources)

    def test_budgets_and_exact_types(self):
        self.assertEqual(audit(candidate=path(bottom='2.21'),policy=replace(P,max_coordinate_bits=4,inner_inset_mm=F(0))).reason,'coordinate-bit-limit')
        self.assertEqual(audit(policy=replace(P,max_events=1)).reason,'event-limit')
        self.assertEqual(audit((source('left',1,end=('.5','0')),source('right',2,start=('.5','0'))),policy=replace(P,max_queries=1)).reason,'query-limit')
        with self.assertRaises(ValueError):audit(cancelled=lambda:1)
        with self.assertRaises(ValueError):NativeStripContactPolicy(100,10,100,100,10000,4096,128,0)

    def test_cancellation_latches_and_final_publication_cannot_pass(self):
        import tools.native_certified_contact as owner
        original=owner.NativeStripContactReport
        publishing=False
        def construct(*args,**kwargs):
            nonlocal publishing
            result=original(*args,**kwargs);publishing=True;return result
        with patch.object(owner,'NativeStripContactReport',side_effect=construct):
            report=audit(cancelled=lambda:publishing)
        self.assertTrue(report.cancelled)
        self.assertFalse(report.nominal_centerline_contact_proven)
        answers=iter((True,False,False))
        report=audit(cancelled=lambda:next(answers,False))
        self.assertTrue(report.cancelled)

if __name__=='__main__':unittest.main()

