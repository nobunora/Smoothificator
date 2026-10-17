"""Exact planned-path regularity boundaries, independent of rounded norms."""
from dataclasses import FrozenInstanceError, replace
import math
import unittest

from adaptive_subedge.application.serialization import identity_root, semantic_tree
from adaptive_subedge.domain.errors import ContractError, ReasonCode
from adaptive_subedge.domain.geometry import PrintPoint2
from adaptive_subedge.domain.plan import SubEdgePath, SubEdgeSegment
from adaptive_subedge.domain.settings import CandidateSegmentRegularityPolicy
from adaptive_subedge.domain.path_regularity import PathRegularityResult
from adaptive_subedge.engine.path_regularity import evaluate_path_regularity


def segment(start=(0,0),end=(1,0),**changes):
    base=SubEdgeSegment(PrintPoint2(*start),PrintPoint2(*end),1,0,0.25,0.5,0.125,0.125,1)
    return replace(base,**changes)


def path(*segments):
    return SubEdgePath("research-path","interval",1,0,0,segments)


class PathRegularityTests(unittest.TestCase):
    def policy(self,**changes):
        base=CandidateSegmentRegularityPolicy("planned_segment_regularity_v1",None,0.125,0.125,1,1,1)
        return replace(base,**changes)

    def evaluate(self,candidate,policy=None,**changes):
        return evaluate_path_regularity(candidate,policy=self.policy() if policy is None else policy,
                                        **(dict(max_segments=10,cancelled=lambda:False)|changes))

    def rejected(self,candidate,reason,indices,policy=None):
        self.assertEqual(self.evaluate(candidate,policy),PathRegularityResult("rejected",reason,indices))

    def invalid(self,call,reason):
        with self.assertRaises(ContractError) as caught: call()
        self.assertIs(caught.exception.reason,reason)

    def test_regular_single_segment_needs_no_physical_evidence(self):
        self.assertEqual(self.evaluate(path(segment())),PathRegularityResult("complete","regular",()))

    def test_strict_length_and_sqrt_rounding_neighbor(self):
        policy=self.policy(min_candidate_segment_length_mm=1)
        self.rejected(path(segment()),"segment-length",(0,),policy)
        self.assertEqual(self.evaluate(path(segment(end=(1,2**-27))),policy).state,"complete")
        self.rejected(path(segment(end=(math.nextafter(1,0),0))),"segment-length",(0,),policy)
        self.assertEqual(self.evaluate(path(segment(end=(math.nextafter(1,math.inf),0))),policy).state,"complete")

    def test_inclusive_time_and_next_float(self):
        candidate=path(segment(requested_speed_mm_s=2))
        policy=self.policy(min_candidate_segment_time_s=0.5)
        self.assertEqual(self.evaluate(candidate,policy).state,"complete")
        self.rejected(candidate,"segment-time",(0,),replace(policy,min_candidate_segment_time_s=math.nextafter(0.5,math.inf)))

    def test_commanded_rate_exact_product_not_rounded_or_geometric(self):
        first=segment(commanded_mm3_per_mm=1,requested_speed_mm_s=1)
        second=segment((1,0),(2,0),commanded_mm3_per_mm=math.nextafter(1,math.inf),requested_speed_mm_s=math.nextafter(1,0))
        policy=self.policy(max_adjacent_commanded_volumetric_rate_step_mm3_s=0)
        self.rejected(path(first,second),"adjacent-rate-step",(0,1),policy)
        first=replace(first,commanded_mm3_per_mm=0.5,requested_speed_mm_s=2,geometric_mm3_per_mm=8)
        second=replace(second,commanded_mm3_per_mm=0.25,requested_speed_mm_s=4,geometric_mm3_per_mm=0.001)
        self.assertEqual(self.evaluate(path(first,second),policy).state,"complete")

    def test_rate_inclusive_step_and_one_ulp_over(self):
        first=segment(commanded_mm3_per_mm=0.5,requested_speed_mm_s=2)
        second=segment((1,0),(2,0),commanded_mm3_per_mm=0.75,requested_speed_mm_s=2)
        policy=self.policy(max_adjacent_commanded_volumetric_rate_step_mm3_s=0.5)
        self.assertEqual(self.evaluate(path(first,second),policy).state,"complete")
        self.rejected(path(first,replace(second,commanded_mm3_per_mm=math.nextafter(0.75,math.inf))),"adjacent-rate-step",(0,1),policy)

    def test_width_and_height_inclusive_boundaries(self):
        for field,setting,reason,initial in (("width_mm","max_adjacent_width_step_mm","adjacent-width-step",0.5),("effective_bead_height_mm","max_adjacent_effective_height_step_mm","adjacent-height-step",0.25)):
            first=segment(**{field:initial})
            second=segment((1,0),(2,0),**{field:initial+0.125})
            policy=self.policy(**{setting:0.125})
            self.assertEqual(self.evaluate(path(first,second),policy).state,"complete")
            self.rejected(path(first,replace(second,**{field:math.nextafter(initial+0.125,math.inf)})),reason,(0,1),policy)

    def test_all_individual_checks_precede_any_adjacent_check(self):
        first=segment()
        second=segment((1,0),(2,0),commanded_mm3_per_mm=4)
        third=segment((2,0),(2.0625,0))
        self.rejected(path(first,second,third),"segment-length",(2,))
        # Within the individual phase, the earliest segment wins, not a later length failure.
        self.rejected(path(replace(first,requested_speed_mm_s=16),second,third),"segment-time",(0,))
        self.rejected(path(segment(end=(0.125,0),requested_speed_mm_s=16)),"segment-length",(0,))

    def test_adjacent_pair_order_and_rate_width_height_precedence(self):
        first=segment()
        second=segment((1,0),(2,0),commanded_mm3_per_mm=4,width_mm=2,effective_bead_height_mm=1.5)
        self.rejected(path(first,second),"adjacent-rate-step",(0,1))
        second=replace(second,commanded_mm3_per_mm=first.commanded_mm3_per_mm)
        self.rejected(path(first,second),"adjacent-width-step",(0,1))
        self.rejected(path(first,second),"adjacent-height-step",(0,1),self.policy(max_adjacent_width_step_mm=2))
        a=segment(width_mm=0.5)
        b=segment((1,0),(2,0),width_mm=2)
        c=segment((2,0),(3,0),commanded_mm3_per_mm=4,width_mm=2)
        self.rejected(path(a,b,c),"adjacent-width-step",(0,1))

    def test_no_implicit_end_to_start_comparison(self):
        segments=(segment((0,0),(1,0),width_mm=0.5),segment((1,0),(1,1),width_mm=0.75),segment((1,1),(0,0),width_mm=1))
        self.assertEqual(self.evaluate(path(*segments),self.policy(max_adjacent_width_step_mm=0.25)).state,"complete")

    def test_huge_differences_products_and_subnormal_squares(self):
        huge=path(segment((-1e308,0),(1e308,0),requested_speed_mm_s=1e308))
        self.assertEqual(self.evaluate(huge,self.policy(min_candidate_segment_length_mm=1e308,min_candidate_segment_time_s=2)).state,"complete")
        tiny=math.ulp(0.0)
        small=path(segment(end=(2*tiny,0)))
        self.assertEqual(self.evaluate(small,self.policy(min_candidate_segment_length_mm=tiny,min_candidate_segment_time_s=tiny)).state,"complete")
        first=segment(commanded_mm3_per_mm=1e308,requested_speed_mm_s=2)
        second=segment((1,0),(2,0),commanded_mm3_per_mm=1e308,requested_speed_mm_s=3)
        self.rejected(path(first,second),"adjacent-rate-step",(0,1))

    def test_budget_and_invalid_setting_types(self):
        candidate=path(segment(),segment((1,0),(2,0)))
        self.assertEqual(self.evaluate(candidate,max_segments=1),PathRegularityResult("incomplete","resource-limit",()))
        for value in (0,True,1.0):
            self.invalid(lambda:self.evaluate(candidate,max_segments=value),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.evaluate(candidate,self.policy(version="legacy")),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.evaluate(candidate,cancelled=None),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.evaluate(candidate,cancelled=lambda:1),ReasonCode.INVALID_SETTING)
        self.invalid(lambda:self.evaluate(object()),ReasonCode.INVALID_GEOMETRY)

    def test_cancellation_all_checkpoints_including_failure_returns(self):
        cases=((path(segment()),{},self.policy()),
               (path(segment()),{},self.policy(min_candidate_segment_length_mm=1)),
               (path(segment(),segment((1,0),(2,0),width_mm=2)),{},self.policy()),
               (path(segment(),segment((1,0),(2,0))),dict(max_segments=1),self.policy()))
        for candidate,changes,policy in cases:
            total=0
            def count():
                nonlocal total
                total+=1
                return False
            self.evaluate(candidate,policy,cancelled=count,**changes)
            self.assertGreaterEqual(total,2)
            for target in range(1,total+1):
                seen=0
                def cancel():
                    nonlocal seen
                    seen+=1
                    return seen==target
                self.assertEqual(self.evaluate(candidate,policy,cancelled=cancel,**changes),PathRegularityResult("incomplete","cancelled",()))
        def explode(): raise LookupError("caller")
        with self.assertRaisesRegex(LookupError,"caller"):
            self.evaluate(path(segment()),cancelled=explode)

    def test_result_is_frozen_closed_and_not_serialization_authority(self):
        result=PathRegularityResult("complete","regular",())
        with self.assertRaises(FrozenInstanceError): result.reason="changed"
        self.assertFalse(hasattr(result,"__dict__"))
        with self.assertRaises(ContractError): semantic_tree(result)
        with self.assertRaises(ContractError): identity_root("subedge-plan",result,schema_version="2")
        for state,reason,indices in (("complete","regular",(0,)),("incomplete","cancelled",(0,)),("rejected","segment-length",()),("rejected","segment-time",(0,1)),("rejected","adjacent-rate-step",(0,2)),("rejected","adjacent-width-step",(True,2)),("rejected","adjacent-height-step",(-1,0)),("complete","feasible",())):
            self.invalid(lambda:PathRegularityResult(state,reason,indices),ReasonCode.INVALID_GEOMETRY)


if __name__=="__main__":
    unittest.main()
