"""Conditional interpretation/copy never promotes opaque startup to real state."""
from collections import Counter
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from hashlib import sha256
from io import BytesIO
import tempfile
from pathlib import Path
import unittest
from zipfile import ZipFile

from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.conditional_nominal_body import (
    ASSUMPTION_NAMES, DeclaredNominalAssumption, NominalEntryContext, NominalMotionEnvelope,
    fingerprint, interpret_nominal_body, pin_nominal_producer,
)
from tools.conditional_nominal_copy import (
    ConditionalInsertion, ConditionalPathInput, associate_derived_path, compose_conditional_nominal_copy,
    propose_nominal_body_anchor, write_conditional_copy,
)
from tools.freeze_supplemental_emission import freeze_numeric_emission
from tools.supplemental_z_hop import policy_from_slice
from tools.supplemental_copy import compose_supplemental_copy, synthetic_anchor
from tests.unit.test_print_source_inspection import fixture, settings_fixture
from tests.unit.test_supplemental_z_hop import anchor_fixture, path_fixture, policy_fixture


BODY = (b'; FEATURE: Outer wall\r\nM624 AQAAAAAAAAA=\r\nM204 S5000\r\n'
        b'G1 X1 Y2 Z3 F6000\r\nG1 E.8 F1800\r\nG1 X2 Y2 E.1 F6000\r\n'
        b'G1 E-.8 F1800\r\nM106 S204\r\nM73 L1\r\nM73 P50 R1\r\nM991 S0 P0\r\nM625\r\n')


def conditional_fixture(body=BODY, *, state=None):
    settings = settings_fixture()
    settings.update(time_lapse_gcode='', outer_wall_speed=['100'], outer_wall_acceleration=['5000'], outer_wall_jerk=['9'],
        layer_height='0.2', printable_height='180', travel_speed='200', travel_speed_z='30',
        filament_diameter=['1.75'], filament_flow_ratio=['0.98'], z_hop=['0.4'],
        machine_max_jerk_x=['9', '9'], machine_max_jerk_y=['9', '9'],
        machine_max_speed_x=['500', '200'], machine_max_speed_y=['500', '200'], machine_max_speed_z=['30', '30'])
    original_project, prefix = fixture(settings)
    prefix += b'M981 S1 P20000 ; opaque startup suffix\n'
    suffix = b'M981 S0 P20000 ; opaque end prefix\n; original unterminated tail'
    source = prefix+body+suffix
    output = BytesIO()
    with ZipFile(BytesIO(original_project)) as archive, ZipFile(output, 'w') as rebuilt:
        for member in archive.infolist():
            rebuilt.writestr(member, source if member.filename == 'Metadata/plate_1.gcode' else archive.read(member.filename))
    project, producer = output.getvalue(), b'pinned synthetic producer'
    descriptor = pin_nominal_producer(source, project, producer,
        expected_source_sha256=sha256(source).hexdigest(), expected_project_sha256=sha256(project).hexdigest(),
        expected_producer_sha256=sha256(producer).hexdigest(), body_start_offset=len(prefix),
        body_end_offset=len(prefix)+len(body), expected_object_token='AQAAAAAAAAA=', fan_channels=(0,))
    entry = NominalEntryContext(anchor_fixture() if state is None else state,
        tuple(DeclaredNominalAssumption(name, 'Explicit unverified synthetic premise', descriptor.prefix_sha256)
              for name in ASSUMPTION_NAMES))
    motion = NominalMotionEnvelope(descriptor.source_sha256, descriptor.project_sha256, descriptor.profile_identity,
        F(6000), F(9), F(5000), F(9), F(5000), F(9), 'classic-jerk', descriptor.prefix_sha256,
        'Opaque prefix / synthetic entry witness', 'Declared M204 S acceleration and isotropic classic XY jerk')
    return source, project, producer, descriptor, entry, motion


def insertion_fixture(inputs):
    source, project, producer, descriptor, entry, motion = inputs
    trace = interpret_nominal_body(*inputs)
    retract = next(event for event in trace.events if event.command == 'G1' and dict(event.parameters).get('E') == F('-.8'))
    anchor = propose_nominal_body_anchor(*inputs, retract.byte_offset+len(retract.raw))
    policy = policy_from_slice(read_sliced_profile(project, source, include_motion_caps=True),
        policy_fixture().bounds, xyz_places=3, e_places=5)
    frozen = freeze_numeric_emission(path_fixture(), policy)
    line = next(event.line_number for event in trace.events if event.deposited_filament_mm == F('.1'))
    recipe, originals, evidence = b'exact immutable synthetic recipe', (b'original source input',), b'conditional geometry input witness; no acceptance transfer'
    association = associate_derived_path(trace, descriptor, frozen, original_recipe=recipe,
        original_inputs=originals, geometry_evidence=evidence, matched_source_lines=(line,))
    path_input = ConditionalPathInput(frozen, association, recipe, originals, evidence)
    return ConditionalInsertion(anchor, (path_input,), F('3.2'), policy)


class ConditionalNominalCopyTests(unittest.TestCase):
    def test_omitted_slow_same_floor_external_wall_still_caps_fast_selected_witness(self):
        body = BODY.replace(b'G1 E-.8 F1800', b'G1 X3 Y2 E.1 F3000\r\nG1 E-.8 F1800')
        inputs = conditional_fixture(body)
        insertion = insertion_fixture(inputs)
        association = insertion.paths[0].association
        self.assertEqual(len(association.matched_source_lines), 1)
        self.assertEqual(len(association.speed_cap_source_lines), 2)
        self.assertEqual(association.source_speed_cap_mm_s, 50)
        with self.assertRaisesRegex(ValueError, 'source external-wall feed'):
            compose_conditional_nominal_copy(*inputs, (insertion,))

    def test_typed_body_accounts_for_every_original_line_scope_and_nonmotion_effect(self):
        inputs = conditional_fixture()
        trace = interpret_nominal_body(*inputs)
        self.assertEqual(b''.join(event.raw for event in trace.events), BODY)
        counts = Counter(event.kind for event in trace.events)
        self.assertEqual(counts['object-scope-open'], 1)
        self.assertEqual(counts['object-scope-close'], 1)
        self.assertEqual(counts['progress-notification'], 2)
        self.assertEqual(counts['layer-notification'], 1)
        self.assertEqual(next(e for e in trace.events if e.command == 'M106').fans_after, ((0, 204),))
        material = next(e for e in trace.events if e.deposited_filament_mm == F('.1'))
        self.assertEqual(material.scope_after.predicate, 'object_not_cancelled')
        self.assertEqual(material.feature, 'Outer wall')
        self.assertEqual(trace.state_status, 'conditional_nominal')
        self.assertEqual(len(trace.unresolved_premises), 6)
        self.assertFalse(trace.printable_authorized)

    def test_unknown_debt_survives_g92_and_cannot_compose(self):
        body = BODY.replace(b'M204 S5000\r\n', b'M204 S5000\r\nG92 E0\r\n')
        inputs = conditional_fixture(body, state=replace(anchor_fixture(), retraction_debt_mm=None))
        trace = interpret_nominal_body(*inputs)
        reset = next(e for e in trace.events if e.command == 'G92')
        self.assertIsNone(reset.after.retraction_debt_mm)
        self.assertIsNone(trace.final_state.retraction_debt_mm)
        retract = next(e for e in trace.events if e.command == 'G1' and dict(e.parameters).get('E') == F('-.8'))
        proposal = propose_nominal_body_anchor(*inputs, retract.byte_offset+len(retract.raw))
        self.assertIn('unknown-position-feed-logicalE-or-physical-debt', proposal.eligibility_issues)

    def test_entry6000_can_trace_but_anchor_rejects_until_supported_m204_5000(self):
        inputs = conditional_fixture()
        trace = interpret_nominal_body(*inputs)
        opening = next(e for e in trace.events if e.command == 'M624')
        early = propose_nominal_body_anchor(*inputs, opening.byte_offset+len(opening.raw))
        self.assertIn('inherited-acceleration-exceeds-supplemental-cap', early.eligibility_issues)
        insertion = insertion_fixture(inputs)
        self.assertEqual(insertion.anchor.acceleration_mm_s2, 5000)
        self.assertFalse(insertion.anchor.eligibility_issues)
        with self.assertRaisesRegex(ValueError, 'ineligible'):
            compose_conditional_nominal_copy(*inputs, (replace(insertion, anchor=early),))

    def test_copy_preserves_all_source_bytes_prefix_tail_predicate_and_exact_cycle(self):
        inputs = conditional_fixture()
        insertion = insertion_fixture(inputs)
        copy = compose_conditional_nominal_copy(*inputs, (insertion,))
        source, _, _, descriptor, _, _ = inputs
        span = copy.insertion_spans[0]
        self.assertEqual(copy.output_bytes[:span.output_start]+copy.output_bytes[span.output_end:], source)
        self.assertTrue(copy.output_bytes.startswith(source[:descriptor.body_start_offset]))
        self.assertTrue(copy.output_bytes.endswith(source[descriptor.body_end_offset:]))
        block = copy.output_bytes[span.output_start:span.output_end]
        self.assertNotIn(b'\n', block.replace(b'\r\n', b''))
        self.assertIn(b'object_not_cancelled=AQAAAAAAAAA=', block)
        self.assertNotIn(b'M204', block)
        replay = trace_linear_execution(block, initial_state=insertion.anchor.saved_state)
        self.assertIsNone(replay.failure)
        self.assertEqual(replay.final_state, insertion.anchor.saved_state)
        self.assertEqual(span.object_scope, insertion.anchor.object_scope)
        for field in ('printable_authorized', 'runtime_injection_authorized', 'physical_print_authorized'):
            self.assertFalse(getattr(copy, field))
        with self.assertRaises(FrozenInstanceError):
            copy.printable_authorized = True

    def test_changed_premise_stale_anchor_forged_state_and_recipe_reject(self):
        inputs = conditional_fixture()
        insertion = insertion_fixture(inputs)
        entry = inputs[4]
        changed = replace(entry, assumptions=(replace(entry.assumptions[0], statement='Different startup premise'), *entry.assumptions[1:]))
        changed_inputs = (*inputs[:4], changed, inputs[5])
        with self.assertRaisesRegex(ValueError, 'stale'):
            compose_conditional_nominal_copy(*changed_inputs, (insertion,))
        forged = replace(insertion.anchor, saved_state=replace(insertion.anchor.saved_state, logical_e_mm=F(999)))
        with self.assertRaises(ValueError):
            compose_conditional_nominal_copy(*inputs, (replace(insertion, anchor=forged),))
        path_input = replace(insertion.paths[0], original_recipe=b'changed recipe bytes')
        with self.assertRaisesRegex(ValueError, 'association'):
            compose_conditional_nominal_copy(*inputs, (replace(insertion, paths=(path_input,)),))

    def test_unretracted_unknown_cornering_unsafe_caps_and_actual_source_feed_reject(self):
        inputs = conditional_fixture()
        trace = interpret_nominal_body(*inputs)
        event = next(e for e in trace.events if e.deposited_filament_mm == F('.1'))
        anchor = propose_nominal_body_anchor(*inputs, event.byte_offset+len(event.raw))
        self.assertIn('positive-saved-feed-and-retraction-required', anchor.eligibility_issues)
        insertion = insertion_fixture(inputs)
        with self.assertRaises(ValueError):
            compose_conditional_nominal_copy(*inputs, (replace(insertion, anchor=anchor),))
        with self.assertRaises(ValueError):
            replace(inputs[5], cornering_dialect='junction-deviation')
        with self.assertRaises(ValueError):
            replace(inputs[5], supplemental_acceleration_cap_mm_s2=F(5001))
        with self.assertRaisesRegex(ValueError, 'saved source profile'):
            compose_conditional_nominal_copy(*inputs, (replace(insertion, policy=replace(policy_fixture(), candidate_speed_mm_s=F(101))),))

    def test_unknown_commands_payloads_params_comments_and_scope_fail_closed(self):
        invalid = (BODY.replace(b'M106 S204', b'M106 P3 S204'), BODY.replace(b'M204 S5000', b'M204 P5000'),
            BODY.replace(b'M73 L1', b'M73 L1 X0'), BODY.replace(b'M991 S0 P0', b'M991 S1 P0'),
            BODY.replace(b'M624 AQAAAAAAAAA=', b'M624 AgAAAAAAAAA='),
            BODY.replace(b'M624 AQAAAAAAAAA=', b'M624 AQAAAAAAAAA=\r\nM624 AQAAAAAAAAA='),
            BODY+b'M625\r\n', BODY.replace(b'M625\r\n', b''),
            BODY.replace(b'M106 S204', b'M622 S1'), BODY.replace(b'M106 S204', b'M981 S0 P20000'),
            BODY.replace(b'M106 S204', b'G2 X1 Y2'), BODY.replace(b'M106 S204', b'M205 X9'),
            BODY.replace(b'M106 S204', b'M106 S204 ; bad\x00comment'))
        for body in invalid:
            with self.subTest(body=body[:60]), self.assertRaises(ValueError):
                interpret_nominal_body(*conditional_fixture(body))

    def test_stale_producer_boundary_duplicate_offsets_and_strict_api_remain_closed(self):
        inputs = conditional_fixture()
        insertion = insertion_fixture(inputs)
        with self.assertRaisesRegex(ValueError, 'pins'):
            interpret_nominal_body(inputs[0], inputs[1], b'changed producer', *inputs[3:])
        with self.assertRaises(ValueError):
            propose_nominal_body_anchor(*inputs, insertion.anchor.byte_offset-1)
        with self.assertRaisesRegex(ValueError, 'unique chronological'):
            compose_conditional_nominal_copy(*inputs, (insertion, insertion))
        with self.assertRaises(ValueError):
            synthetic_anchor(inputs[0], insertion.anchor.byte_offset, initial_state=inputs[4].state)
        with self.assertRaises(ValueError):
            compose_supplemental_copy(inputs[0], (insertion,))

    def test_atomic_separate_unverified_publication_rebuilds_and_never_overwrites(self):
        inputs = conditional_fixture()
        insertion = insertion_fixture(inputs)
        copy = compose_conditional_nominal_copy(*inputs, (insertion,))
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source, project, target = folder/'source.gcode', folder/'source.3mf', folder/'conditional.UNVERIFIED.txt'
            source.write_bytes(inputs[0])
            project.write_bytes(inputs[1])
            arguments = dict(source_path=source, project_path=project, producer=inputs[2], descriptor=inputs[3],
                             entry=inputs[4], motion=inputs[5], insertions=(insertion,))
            self.assertEqual(write_conditional_copy(copy, target, **arguments), copy.output_sha256)
            self.assertEqual(target.read_bytes(), copy.output_bytes)
            self.assertEqual(source.read_bytes(), inputs[0])
            self.assertEqual(project.read_bytes(), inputs[1])
            with self.assertRaises(ValueError):
                write_conditional_copy(copy, target, **arguments)
            with self.assertRaises(ValueError):
                write_conditional_copy(copy, folder/'unlabeled.txt', **arguments)
            self.assertFalse(tuple(folder.glob('.conditional-UNVERIFIED-*')))
