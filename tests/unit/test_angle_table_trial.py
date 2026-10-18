from dataclasses import replace
from fractions import Fraction as F
import unittest
from tools.angle_table_trial import (AngleTablePolicy,SectionMember,Rect,Block,floor_union_error,
    physical_spill_legal,select_epsilon,build_angle_table,lookup_angle_table)


class AngleTableTests(unittest.TestCase):
    def test_exact_policy_and_overlap_grid(self):
        p=AngleTablePolicy(overlap_percent=F(30))
        assert max(p.heights)==F('.19') and min(p.heights)==F('.12')
        assert all(h<F('.2') and (h*F('.7')/p.grid_mm).denominator==1 for h in p.heights)
        for bad in (.2,True,float('nan')):
            with self.assertRaises(ValueError):replace(p,layer_height_mm=bad)
        assert replace(p,epsilon_fraction=F('.01')).identity!=p.identity
        with self.assertRaises(ValueError):replace(p,overlap_percent=F(31))
        with self.assertRaises(ValueError):replace(p,grid_mm=F(1,10**25),maximum_events=1)
        with self.assertRaises(ValueError):replace(p,epsilon_fraction=.02)
        with self.assertRaises(ValueError):replace(p,minimum_improvement_fraction=True)
        with self.assertRaises(ValueError):replace(p,physical_height_step_mm=F(1,10**25))

    def test_zero_overlap_has_no_physical_downshift_and_strict_cap_endpoint(self):
        p=AngleTablePolicy(slope_step=F('.1'),maximum_slope=F('.3'),width_samples_mm=(F('.251'),F('.401')))
        assert p.overlap_percent==0
        assert p.heights==tuple(F(i,100) for i in range(8,20))+(F('.199'),)
        assert p.identity!=replace(p,overlap_percent=F(30)).identity
        assert p.identity!=replace(p,physical_height_step_mm=F('.005')).identity
        table=build_angle_table(p)
        for row in table.bins:
            for member in ((row.member,) if row.member else ())+row.alternatives:
                for block in member.blocks:
                    assert block.lower.bottom_mm==0
                    if block.upper is not None:assert block.upper.bottom_mm==block.lower.top_mm

    def test_actual_short_base_cannot_enter_through_lower_eligible_bin(self):
        p=AngleTablePolicy(slope_step=F('.01'),maximum_slope=F('.68'),width_samples_mm=(F('.211'),))
        table=build_angle_table(p)
        for slope in (F('.674'),F('.675'),F('.68')):
            assert lookup_angle_table(table,F('.2')/slope,F('.2'))==(None,'strict-short-base')
        for slope in (F('.67'),F('.673')):
            member,reason=lookup_angle_table(table,F('.2')/slope,F('.2'))
            assert reason!='strict-short-base'
            assert member is not None


    def test_floor_union_does_not_penalize_buried_overlap_but_spill_does(self):
        a=Block(Rect(F(0),F(1),F('-.2'),F('.1')),None)
        b=Block(Rect(F(0),F(1),F(0),F('.1')),None)
        assert floor_union_error(F(1),F(1),(a,))==floor_union_error(F(1),F(1),(b,))
        assert not physical_spill_legal(F(1),F(1),a.lower)
        assert physical_spill_legal(F(1),F(1),b.lower)


    def test_upper_intersection_counted_once(self):
        root=Rect(F(0),F(1),F('-.03'),F('.07'))
        upper=Rect(F(0),F(1),F('.04'),F('.14'))
        combined=Block(Rect(F(0),F(1),F('-.03'),F('.14')),None)
        assert floor_union_error(F(1),F(1),(Block(root,upper),))==floor_union_error(F(1),F(1),(combined,))


    def test_epsilon_prefers_fewer_paths_then_upper_count(self):
        p=AngleTablePolicy();r=Rect(F(0),F('.3'),F(0),F('.1'))
        simpler=SectionMember((Block(r,None),),F('.11'))
        best=SectionMember((Block(r,r),),F('.1'))
        assert select_epsilon((best,simpler),F(1),p)==simpler
        assert select_epsilon((best,simpler),F(1),replace(p,epsilon_fraction=F(0)))==best
        assert select_epsilon((simpler,),F('.111'),p) is None


    def test_reusable_bins_and_conservative_lookup(self):
        p=AngleTablePolicy(slope_step=F('.1'),maximum_slope=F('.5'),width_samples_mm=(F('.301'),))
        table=build_angle_table(p)
        assert table.bins[0].reason=='flat' and table.boundary_brackets
        assert lookup_angle_table(table,F(100),F('.2'))[0] is None
        member,reason=lookup_angle_table(table,F('.4'),F('.2'))
        assert reason in ('validated-finite-bin-member','precomputed-bin-no-member-meets-improvement')
        if member:assert member.error_mm2<F('.04')
        with self.assertRaises(ValueError):build_angle_table(p,cancelled=lambda:True)
        with self.assertRaises(ValueError):build_angle_table(p,cancelled=lambda:1)

    def test_stale_table_and_forged_height_are_rejected(self):
        from tools.angle_table_trial import AngleBin,_table_identity
        p=AngleTablePolicy(slope_step=F('.5'),maximum_slope=F('.5'),width_samples_mm=(F('.301'),))
        table=build_angle_table(p)
        bad=SectionMember((Block(Rect(F('.19'),F('.4'),F('-.075'),F('.175')),None),),F('.01'))
        bins=(table.bins[0],AngleBin(F('.5'),'selected',bad,F('.04'),'forged'))
        with self.assertRaises(ValueError):lookup_angle_table(replace(table,bins=bins),F('.4'),F('.2'))
        bound=replace(table,bins=bins,content_identity=_table_identity(p,bins))
        assert lookup_angle_table(bound,F('.4'),F('.2'))==(None,'bin-height-grid-revalidation')
        flat_bins=(AngleBin(F(0),'selected',bad,F(0),'forged'),table.bins[1])
        with self.assertRaises(ValueError):
            lookup_angle_table(replace(table,bins=flat_bins,content_identity=_table_identity(p,flat_bins)),F(100),F('.2'))

    def test_every_precomputed_upper_is_meaningfully_smaller_and_no_taller(self):
        p=AngleTablePolicy(slope_step=F('.1'),maximum_slope=F('.3'),width_samples_mm=(F('.251'),F('.401')))
        table=build_angle_table(p);uppers=0
        for row in table.bins:
            for member in ((row.member,) if row.member else ())+row.alternatives:
                for block in member.blocks:
                    if block.upper is None:continue
                    uppers+=1;a,b=block.lower,block.upper
                    assert a.left_mm<b.left_mm<b.right_mm<a.right_mm
                    assert b.right_mm-b.left_mm<a.right_mm-a.left_mm
                    assert b.top_mm-b.bottom_mm<=a.top_mm-a.bottom_mm
                    assert b.left_mm-a.left_mm==a.right_mm-b.right_mm
        assert uppers>0
        assert replace(p,stack_topology_version=2).identity==p.identity
        with self.assertRaises(ValueError):replace(p,stack_topology_version=1)
