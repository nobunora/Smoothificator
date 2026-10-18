"""Causal ownership/contact permissions never exempt entire paths or future beads."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from tests.unit.test_conditional_nominal_copy import BODY, conditional_fixture, insertion_fixture
from tools.audit_conditional_tool_chronology import NominalTipContactPolicy, ToolChronologyPolicy, audit_conditional_tool_chronology
from tools.audit_provisional_tip_sweep import PlanarTipSweepPolicy
from tools.compile_conditional_job import CompiledConditionalGroup, CompiledConditionalJob, ConditionalCompilationPolicy
from tools.compile_nominal_recipe import CompiledNominalRecipe
from tools.conditional_nominal_copy import compose_conditional_nominal_copy
from tools.conditional_nominal_model import ConditionalModelPolicy, NominalDepositionPremise, extract_conditional_nominal_model
from tools.prepare_source_contour_intents import ContourConstructionPolicy
from tools.provisional_tool_geometry import ProvisionalPlanarTip


def fixture(stationary=False):
    body = b'; LAYER_HEIGHT: 0.2\n; LINE_WIDTH: 0.4\n'+BODY
    if stationary:
        body = body.replace(b'G1 E.8 F1800', b'G1 E.80001 F1800')
    inputs = conditional_fixture(body)
    insertion = insertion_fixture(inputs)
    copy = compose_conditional_nominal_copy(*inputs, (insertion,))
    frozen = insertion.paths[0].frozen_emission
    compiled = CompiledNominalRecipe('synthetic', frozen.path.path_id, '0'*64, inputs[3].source_sha256,
        inputs[3].project_sha256, insertion.upper_z_mm, frozen, None, (), False, False, False)
    group = CompiledConditionalGroup(F(3), F('3.2'), F(0), F(1), F('.2'), 1, (compiled,), insertion)
    job = CompiledConditionalJob('0'*64, '1'*64, '2'*64, '3'*64, '4'*64,
        ConditionalCompilationPolicy(2, 10, 100, ContourConstructionPolicy(9, 100, 4096, 100000)), (group,), (), copy)
    model = extract_conditional_nominal_model(inputs, NominalDepositionPremise('Declared linearE/affineXYZ.'),
        policy=ConditionalModelPolicy(1000, 1000, 4096), cancelled=lambda: False)
    contact = NominalTipContactPolicy(((frozen.path.path_id, 1, 0),), ((frozen.path.path_id, 0), (frozen.path.path_id, 1)),
        ((insertion.anchor.byte_offset, model.spans[0].original_geometry.segment_id),), True)
    return dict(inputs=inputs, model=model, job=job, geometry=ProvisionalPlanarTip(), contact_policy=contact,
        policy=ToolChronologyPolicy(1000, 1000, 10000, 1000, 10000, 10000, PlanarTipSweepPolicy(128, 4096, 128)),
        cancelled=lambda: False)


class ConditionalToolChronologyTests(unittest.TestCase):
    def test_exact_causal_own_join_and_source_anchor_region_complete(self):
        report = audit_conditional_tool_chronology(**fixture())
        self.assertEqual(report.state, 'incomplete')
        self.assertTrue(report.moving_material_interactions_complete)
        self.assertTrue(report.body_moving_material_interactions_complete)
        self.assertFalse(report.whole_original_job_interactions_complete)
        self.assertIn('opaque-execution-outside-body', report.reason)
        self.assertEqual([o.scope for o in report.opaque_execution_obligations], ['opaque-prefix', 'opaque-suffix'])
        self.assertEqual(report.forming_prefix_top_certificates, 2)
        self.assertGreater(report.allowed_boundary_pairs, 0)
        self.assertFalse(report.issues)
        self.assertFalse(report.physical_authority)

    def test_penetrating_opaque_suffix_cannot_claim_whole_job_complete(self):
        from hashlib import sha256
        from io import BytesIO
        from zipfile import ZipFile
        from tools.conditional_nominal_body import pin_nominal_producer
        arguments = fixture()
        source, project, producer, descriptor, entry, motion = arguments['inputs']
        # This downstream travel crosses the newly deposited nominal body.
        suffix = b'G1 X10.5 Y11 Z3.04 F6000\n'
        from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
        from tools.audit_provisional_tip_sweep import audit_provisional_tip_sweep
        frozen = arguments['job'].groups[0].paths[0].frozen_emission
        bead = ExactNominalTopSegment('candidate', *frozen.path.points_mm[:2],
            F(str(frozen.physical_width_mm[0])), frozen.path.height_mm, 'structural')
        point = (F('10.5'), F(11), F('3.04'))
        penetration = audit_provisional_tip_sweep(point, point, ProvisionalPlanarTip(), bead,
            policy=PlanarTipSweepPolicy(128, 4096, 128), cancelled=lambda: False)
        self.assertEqual(penetration.state, 'positive-penetration')
        source = source[:descriptor.body_end_offset]+suffix
        output = BytesIO()
        with ZipFile(BytesIO(project)) as old, ZipFile(output, 'w') as new:
            for info in old.infolist():
                new.writestr(info, source if info.filename == 'Metadata/plate_1.gcode' else old.read(info.filename))
        project = output.getvalue()
        descriptor = pin_nominal_producer(source, project, producer, expected_source_sha256=sha256(source).hexdigest(),
            expected_project_sha256=sha256(project).hexdigest(), expected_producer_sha256=descriptor.producer_sha256,
            body_start_offset=descriptor.body_start_offset, body_end_offset=descriptor.body_end_offset,
            expected_object_token=descriptor.expected_object_token, fan_channels=descriptor.fan_channels)
        motion = replace(motion, source_sha256=descriptor.source_sha256, project_sha256=descriptor.project_sha256,
                         profile_identity=descriptor.profile_identity)
        inputs = (source, project, producer, descriptor, entry, motion)
        insertion = insertion_fixture(inputs)
        group = arguments['job'].groups[0]
        arguments['inputs'] = inputs
        arguments['model'] = extract_conditional_nominal_model(inputs, arguments['model'].premise,
            policy=arguments['model'].policy, cancelled=lambda: False)
        arguments['job'] = replace(arguments['job'], copy=compose_conditional_nominal_copy(*inputs, (insertion,)),
            groups=(replace(group, insertion=insertion, paths=(replace(group.paths[0], frozen_emission=insertion.paths[0].frozen_emission),)),))
        arguments['contact_policy'] = replace(arguments['contact_policy'], source_anchor_top_pairs=((insertion.anchor.byte_offset,
            arguments['model'].spans[0].original_geometry.segment_id),))
        report = audit_conditional_tool_chronology(**arguments)
        self.assertTrue(report.body_moving_material_interactions_complete)
        self.assertFalse(report.whole_original_job_interactions_complete)
        obligation = report.opaque_execution_obligations[-1]
        self.assertEqual((obligation.byte_start, obligation.byte_end, obligation.sha256),
                         (descriptor.body_end_offset, len(source), sha256(suffix).hexdigest()))
        self.assertEqual(report.state, 'incomplete')

    def test_unlisted_contact_and_future_or_forged_material_permissions_reject(self):
        arguments = fixture()
        missing = replace(arguments['contact_policy'], own_prior_top_pairs=())
        report = audit_conditional_tool_chronology(**dict(arguments, contact_policy=missing))
        self.assertEqual(report.reason, 'forbidden-boundary-contact')
        self.assertFalse(report.moving_material_interactions_complete)
        bad = replace(arguments['contact_policy'], own_prior_top_pairs=(('thin', 0, 1),))
        with self.assertRaises(ValueError):
            audit_conditional_tool_chronology(**dict(arguments, contact_policy=bad))
        group = arguments['job'].groups[0]
        path = group.paths[0]
        forged = replace(path, frozen_emission=replace(path.frozen_emission, physical_width_mm=(.01, .01)))
        with self.assertRaisesRegex(ValueError, 'compiled paths differ'):
            audit_conditional_tool_chronology(**dict(arguments, job=replace(arguments['job'], groups=(replace(group, paths=(forged,)),))))

    def test_stationary_surplus_is_unknown_material_without_an_invented_blob(self):
        report = audit_conditional_tool_chronology(**fixture(True))
        self.assertEqual(report.state, 'incomplete')
        self.assertTrue(report.moving_material_interactions_complete)
        self.assertEqual(len(report.unmodeled_stationary_deposition_lines), 1)
        self.assertIn('unmodeled-stationary', report.reason)

    def test_resource_and_cancel_never_become_complete(self):
        arguments = fixture()
        for changes in (dict(cancelled=lambda: True), dict(policy=replace(arguments['policy'], max_pairs=1)),
                        dict(policy=replace(arguments['policy'], max_motions=1))):
            report = audit_conditional_tool_chronology(**dict(arguments, **changes))
            self.assertEqual(report.state, 'incomplete')
            self.assertFalse(report.moving_material_interactions_complete)


if __name__ == '__main__':
    unittest.main()
