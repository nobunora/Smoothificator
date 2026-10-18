"""Causal support identities and existing numeric/one-path execution owners."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from orca_plugin.gcode.linear_trace import trace_linear_execution
from tests.unit.test_supplemental_z_hop import anchor_fixture, policy_fixture
from tools.audit_continuous_path_contact import ContactPolicy
from tools.conditional_nominal_body import fingerprint
from tools.prepare_two_tier_intents import (
    SupportedPathIntent, TwoTierGraphPolicy, freeze_supported_graph, compose_supported_cycle,
)


def graph_policy():
    return TwoTierGraphPolicy(20,4096,1000,ContactPolicy(F('.001'),F('.000001'),12,1000,100,100,100,4096,128,'exact-span'))


def intent(name, *, parent=None, height=F('.1'), remaining=None, support=F(3), width=F('.4')):
    remaining = height if remaining is None else remaining
    return SupportedPathIntent(name,'0'*64,F(3),F('3.2'),support,width,height,remaining,
        ((F(10),F(11),support+remaining),(F(20),F(11),support+remaining)),parent)


def freeze(intents, **changes):
    return freeze_supported_graph(intents,**dict(dict(source_context_identity='0'*64,policy=policy_fixture(),
        graph_policy=graph_policy(),cancelled=lambda:False),**changes))


class TwoTierIntentTests(unittest.TestCase):
    def test_thinner_child_executes_later_with_original_floor_and_actual_parent(self):
        lower = intent('lower')
        upper = intent('upper',parent='lower',height=F('.08'),support=F('3.1'),width=F('.3'))
        plan = freeze((upper,lower))
        self.assertEqual(plan.execution_order,('lower','upper'))
        by_id = {p.intent.path_id:p for p in plan.paths}
        self.assertEqual(by_id['upper'].intent.original_source_floor_z_mm,F(3))
        self.assertEqual(by_id['upper'].local_support_numeric_adapter.path.floor_z_mm,F('3.1'))
        self.assertEqual(by_id['upper'].parent_frozen_identity,fingerprint(by_id['lower']))
        self.assertTrue(plan.immediate_support_slabs[0].centerline_contact.nominal_centerline_contact_proven)
        self.assertEqual(plan.immediate_support_slabs[0].depth_mm,0)
        block = compose_supported_cycle(anchor_fixture(),plan,policy_fixture(),cancelled=lambda:False)
        self.assertLess(block.index(b'PATH lower'),block.index(b'PATH upper'))
        replay = trace_linear_execution(block,initial_state=anchor_fixture())
        self.assertIsNone(replay.failure)
        self.assertEqual(replay.final_state,anchor_fixture())
        for event in replay.records:
            if event.before.xyz_mm[:2] != event.after.xyz_mm[:2] and not event.extruded_filament_mm:
                self.assertEqual(event.before.xyz_mm[2],F('3.6'))
                self.assertGreater(event.before.retraction_debt_mm,0)
        self.assertFalse(plan.physical_authority)

    def test_exact_thirty_overlap_compensation_and_strict_original_top(self):
        lower = intent('lower',height=F('.12'),remaining=F('.084'))
        upper = intent('upper',parent='lower',support=F('3.084'),height=F('.12'),remaining=F('.084'),width=F('.3'))
        plan = freeze((lower,upper))
        self.assertEqual(plan.immediate_support_slabs[0].child_height_fraction,F('.3'))
        for changed in (replace(upper,remaining_height_mm=F('.083'),points_mm=tuple((x,y,F('3.167')) for x,y,_ in upper.points_mm)),
            intent('upper',parent='lower',support=F('3.084'),height=F('.1'),remaining=F('.079')),
            intent('upper',parent='lower',support=F('3.084'),height=F('.116'),remaining=F('.116')),
            replace(upper,width_mm=F('.249')),replace(upper,physical_height_mm=F('.181'))):
            with self.assertRaises(ValueError):
                freeze((lower,changed))

    def test_malformed_missing_cyclic_depth_foreign_and_unsupported_span_reject(self):
        lower = intent('lower')
        upper = intent('upper',parent='lower',height=F('.08'),support=F('3.1'),width=F('.3'))
        cases = ((upper,), (replace(lower,parent_path_id='upper'),upper),
            (lower,upper,intent('third',parent='upper',support=F('3.18'),height=F('.08'))),
            (lower,replace(upper,source_context_identity='1'*64)),
            (lower,replace(upper,support_plane_z_mm=F('3.09'))),
            (lower,replace(upper,points_mm=((F(9),F(11),F('3.18')),(F(20),F(11),F('3.18'))))),
            (lower,replace(upper,points_mm=((F(10),F('11.2'),F('3.18')),(F(20),F('11.2'),F('3.18'))))))
        for paths in cases:
            with self.assertRaises(ValueError):
                freeze(paths)
        with self.assertRaises(ValueError):
            freeze((lower,upper),cancelled=lambda:True)
        with self.assertRaises(ValueError):
            freeze((lower,upper),graph_policy=replace(graph_policy(),max_paths=1))

    def test_forged_parent_numeric_identity_and_zero_query_budget_reject(self):
        paths = (intent('lower'),intent('upper',parent='lower',height=F('.08'),support=F('3.1'),width=F('.3')))
        plan = freeze(paths)
        child = next(p for p in plan.paths if p.intent.parent_path_id)
        forged = replace(plan,paths=tuple(replace(p,parent_frozen_identity='f'*64) if p is child else p for p in plan.paths))
        with self.assertRaisesRegex(ValueError,'forged'):
            compose_supported_cycle(anchor_fixture(),forged,policy_fixture(),cancelled=lambda:False)
        with self.assertRaises(ValueError):
            freeze(paths,graph_policy=replace(graph_policy(),max_coordinate_bits=1))


if __name__ == '__main__':
    unittest.main()
