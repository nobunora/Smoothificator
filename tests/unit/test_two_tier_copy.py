"""Source-bound supported composition preserves originals and original settings."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest

from adaptive_subedge.domain.settings import CandidateBeadBounds
from tests.unit.test_conditional_nominal_copy import BODY, conditional_fixture, insertion_fixture
from tests.unit.test_conditional_preview_annotations import PRIOR, ANNOTATIONS, TAGS
from tests.unit.test_two_tier_intents import graph_policy, intent
from tools.conditional_nominal_body import interpret_nominal_body
from tools.conditional_nominal_copy import ConditionalPathInput, _context_identity, associate_derived_path
from tools.compose_two_tier_copy import (
    TwoTierCopyPolicy, SupportedConditionalInsertion, compose_two_tier_copy, write_two_tier_copy,
)
from tools.prepare_two_tier_intents import freeze_supported_graph


COPY_POLICY=TwoTierCopyPolicy(1000000,10000,10,20,2000000)


def fixture(*, excessive_height=False, extra_comments=b''):
    future=(b'M624 AQAAAAAAAAA=\nG1 X1 Y2 Z3.2 F6000\nG1 E.8 F1800\n'
            b'G1 X2 Y2 E.1 F6000\nG1 E-.8 F1800\nM625\n')
    inputs=conditional_fixture(PRIOR+extra_comments+BODY+future)
    old=insertion_fixture(inputs)
    trace=interpret_nominal_body(*inputs)
    context=_context_identity(trace)
    policy=old.policy
    if excessive_height:
        policy=replace(policy,bounds=CandidateBeadBounds(.08,.3,.25,.45))
        paths=(intent('lower',height=F('.19'),remaining=F('.14')),)
    else:
        paths=(intent('lower'),intent('upper',parent='lower',support=F('3.1'),height=F('.08'),width=F('.3')))
    paths=tuple(replace(p,source_context_identity=context) for p in paths)
    plan=freeze_supported_graph(paths,source_context_identity=context,policy=policy,graph_policy=graph_policy(),cancelled=lambda:False)
    lower=next(p.local_support_numeric_adapter for p in plan.paths if p.intent.path_id=='lower')
    template=old.paths[0]
    association=associate_derived_path(trace,inputs[3],lower,original_recipe=template.original_recipe,
        original_inputs=template.original_inputs,geometry_evidence=template.geometry_evidence,
        matched_source_lines=template.association.matched_source_lines)
    root=ConditionalPathInput(lower,association,template.original_recipe,template.original_inputs,template.geometry_evidence)
    insertion=SupportedConditionalInsertion(old.anchor,plan,policy,(root,))
    return inputs,insertion


def compose(inputs,insertion,**changes):
    return compose_two_tier_copy(inputs,(insertion,),**dict(dict(copy_policy=COPY_POLICY,cancelled=lambda:False),**changes))


class TwoTierCopyTests(unittest.TestCase):
    def test_actual_lower_association_child_parent_identity_and_comment_only_annotations(self):
        inputs,insertion=fixture()
        plain=compose(inputs,insertion)
        preview=compose(inputs,insertion,annotation_policy=ANNOTATIONS)
        span=preview.insertion_spans[0]
        block=preview.output_bytes[span.output_start:span.output_end]
        self.assertEqual(preview.output_bytes[:span.output_start]+preview.output_bytes[span.output_end:],inputs[0])
        old=plain.insertion_spans[0]
        self.assertEqual(b''.join(l for l in block.splitlines(keepends=True) if not l.startswith(TAGS)),
            plain.output_bytes[old.output_start:old.output_end])
        self.assertLess(block.index(b'PATH lower'),block.index(b'PATH upper'))
        self.assertIn(b'; LAYER_HEIGHT: 0.08',block)
        self.assertEqual(span.child_support_identities[0][0],'upper')
        self.assertEqual(len(span.root_association_identities),1)
        self.assertFalse(preview.whole_original_job_interactions_complete)
        self.assertFalse(preview.printable_authorized)

    def test_saved_layer_90percent_rejects_permissive_caller_bounds(self):
        inputs,insertion=fixture(excessive_height=True)
        self.assertEqual(insertion.plan.paths[0].intent.physical_height_mm,F('.19'))
        with self.assertRaises(ValueError):
            compose(inputs,insertion)

    def test_current_original_next_layer_parent_context_and_budgets_revalidated(self):
        inputs,insertion=fixture()
        foreign=replace(insertion.plan,source_context_identity='f'*64)
        with self.assertRaisesRegex(ValueError,'context'):
            compose(inputs,replace(insertion,plan=foreign))
        intents=tuple(replace(p.intent,original_next_layer_z_mm=F('3.3')) for p in insertion.plan.paths)
        plan=freeze_supported_graph(intents,source_context_identity=insertion.plan.source_context_identity,
            policy=insertion.emission_policy,graph_policy=graph_policy(),cancelled=lambda:False)
        with self.assertRaisesRegex(ValueError,'first actual future'):
            compose(inputs,replace(insertion,plan=plan))
        with self.assertRaises(ValueError):
            compose(inputs,replace(insertion,original_floor_roots=()))
        for changes in (dict(cancelled=lambda:True),dict(copy_policy=replace(COPY_POLICY,max_output_bytes=1))):
            with self.assertRaises(ValueError):
                compose(inputs,insertion,**changes)

    def test_writer_fresh_rebuild_nooverwrite_alias_and_forged_receipt_reject(self):
        inputs,insertion=fixture()
        copy=compose(inputs,insertion,annotation_policy=ANNOTATIONS)
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            source,project=folder/'source.gcode',folder/'project.3mf'
            source.write_bytes(inputs[0]);project.write_bytes(inputs[1])
            kwargs=dict(source_path=source,project_path=project,producer=inputs[2],descriptor=inputs[3],entry=inputs[4],
                motion=inputs[5],insertions=(insertion,),cancelled=lambda:False,annotation_policy=ANNOTATIONS)
            target=folder/'new.UNVERIFIED_VIEW_ONLY.gcode'
            with self.assertRaises(ValueError):
                write_two_tier_copy(replace(copy,output_sha256='0'*64),target,**kwargs)
            write_two_tier_copy(copy,target,**kwargs)
            self.assertEqual(target.read_bytes(),copy.output_bytes)
            with self.assertRaises(ValueError):
                write_two_tier_copy(copy,target,**kwargs)
            with self.assertRaises(ValueError):
                write_two_tier_copy(copy,source,**kwargs)

    def test_cr_only_physical_lines_obey_same_preparse_event_budget_as_body_interpreter(self):
        from unittest.mock import patch
        inputs,insertion=fixture(extra_comments=b'; CR-only bounded comment\r'*1000)
        lf_count=inputs[0].count(b'\n')
        self.assertGreater(len(interpret_nominal_body(*inputs).events),lf_count)
        with patch('tools.compose_two_tier_copy.interpret_nominal_body') as interpret:
            with self.assertRaisesRegex(ValueError,'event budget'):
                compose(inputs,insertion,copy_policy=replace(COPY_POLICY,max_source_events=lf_count))
            interpret.assert_not_called()
        permitted=replace(COPY_POLICY,max_source_events=len(inputs[0].splitlines()))
        copy=compose(inputs,insertion,copy_policy=permitted)
        span=copy.insertion_spans[0]
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:],inputs[0])


if __name__=='__main__':
    unittest.main()
