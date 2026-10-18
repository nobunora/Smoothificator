"""Typed nominal model provenance separates raw E, debt and deposited support."""
from dataclasses import replace
from fractions import Fraction as F
from hashlib import sha256
import unittest

from tests.unit.test_conditional_nominal_copy import BODY, conditional_fixture
from tests.unit.test_conditional_nominal_actual import actual_inputs
from tools.conditional_nominal_body import interpret_nominal_body
from tools.conditional_nominal_model import (
    ConditionalModelPolicy, NominalDepositionPremise, extract_conditional_nominal_model, reassociate_raw_nominal_geometry,
    _project_nominal_model,
)
from tools.exponential_top_fixture import ROOT


def extract(inputs, **changes):
    kwargs = dict(policy=ConditionalModelPolicy(25000, 20000, 4096), cancelled=lambda: False)
    kwargs.update(changes)
    return extract_conditional_nominal_model(inputs,
        NominalDepositionPremise('Declared unverified linear E over affine XYZ.'), **kwargs)


class ConditionalNominalModelTests(unittest.TestCase):
    def test_partial_full_and_unknown_debt_never_invent_support(self):
        body = b'; LAYER_HEIGHT: 0.2\n; LINE_WIDTH: 0.4\n'+BODY
        for debt, crop, deposited in ((F('.05'), F('.5'), F('.05')), (F('.2'), F(1), F(0)), (None, None, None)):
            inputs = conditional_fixture(body)
            trace = interpret_nominal_body(*inputs)
            material = next(e for e in trace.events if e.deposited_filament_mm == F('.1'))
            altered = replace(material, before=replace(material.before, retraction_debt_mm=debt),
                              deposited_filament_mm=deposited)
            changed = replace(trace, events=tuple(altered if e is material else e for e in trace.events))
            model = _project_nominal_model(changed, inputs[3], NominalDepositionPremise('Declared linearE.'),
                policy=ConditionalModelPolicy(1000, 1000, 4096), cancelled=lambda: False)
            span = model.spans[0]
            self.assertEqual(span.raw_commanded_e_mm, F('.1'))
            self.assertEqual(span.entry_debt_mm, debt)
            self.assertEqual(span.deposition_start_parameter, crop)
            if crop is not None and crop < 1:
                self.assertEqual(span.support_geometry.start_xyz_mm[0], F('1.5'))
            else:
                self.assertIsNone(span.support_geometry)
            self.assertEqual(span.original_geometry.start_xyz_mm[0], F(1))

    def test_missing_malformed_metadata_resources_and_cancellation_reject(self):
        for prefix in (b'', b'; LINE_WIDTH: bad\n; LAYER_HEIGHT: 0.2\n'):
            with self.assertRaises(ValueError):
                extract(conditional_fixture(prefix+BODY))
        inputs = conditional_fixture(b'; LINE_WIDTH: 0.4\n; LAYER_HEIGHT: 0.2\n'+BODY)
        for kwargs in (dict(cancelled=lambda: True), dict(cancelled=lambda: 1),
                       dict(policy=ConditionalModelPolicy(1, 100, 4096)),
                       dict(policy=ConditionalModelPolicy(1000, 100, 1))):
            with self.assertRaises(ValueError):
                extract(inputs, **kwargs)

    def test_private_projection_rejects_known_unknown_numeric_contradictions(self):
        inputs = conditional_fixture(b'; LINE_WIDTH: 0.4\n; LAYER_HEIGHT: 0.2\n'+BODY)
        trace = interpret_nominal_body(*inputs)
        material = next(e for e in trace.events if e.deposited_filament_mm == F('.1'))
        variants = (replace(material, deposited_filament_mm=None),
            replace(material, deposited_filament_mm=.1),
            replace(material, before=replace(material.before, retraction_debt_mm=None)),
            replace(material, before=replace(material.before, retraction_debt_mm=True)),
            replace(material, after=replace(material.after, feed_mm_min=True)),
            replace(material, after=replace(material.after, feed_mm_min=F(2**100))),
            replace(material, before=replace(material.before, retraction_debt_mm=F(2**100)), deposited_filament_mm=F(0)),
            replace(material, before=replace(material.before, retraction_debt_mm=F(1, 2**100)),
                deposited_filament_mm=F('.1')-F(1, 2**100)))
        for altered in variants:
            with self.subTest(altered=altered), self.assertRaises(ValueError):
                _project_nominal_model(replace(trace, events=tuple(altered if e is material else e for e in trace.events)),
                    inputs[3], NominalDepositionPremise('Declared linearE.'),
                    policy=ConditionalModelPolicy(1000, 1000, 32), cancelled=lambda: False)
        with self.assertRaisesRegex(ValueError, 'complete source'):
            extract_conditional_nominal_model(trace, NominalDepositionPremise('Declared linearE.'),
                policy=ConditionalModelPolicy(1000, 1000, 4096), cancelled=lambda: False)

    def test_actual_complete_raw_bijection_keeps21_debt_crops_and_feed_changes(self):
        inputs = actual_inputs()
        model = extract(inputs)
        old = ROOT/'artifacts/revolved-exponential-derived5000-9-seam0-v2-research'
        source = (old/'original-slice/plate_1.gcode').read_bytes()
        project = (old/'original-slice/sliced.3mf').read_bytes()
        rows = (old/'nominal-model-rows.json').read_bytes()
        kwargs = dict(inputs=inputs, cancelled=lambda: False, old_source=source, old_project=project, old_rows=rows,
            expected_old_source_sha256=sha256(source).hexdigest(), expected_old_project_sha256=sha256(project).hexdigest(),
            expected_old_rows_sha256=sha256(rows).hexdigest())
        association = reassociate_raw_nominal_geometry(model, **kwargs)
        self.assertEqual(len(model.spans), 14985)
        self.assertEqual(association.changed_feed_count, 14253)
        self.assertEqual(len(association.debt_cropped_new_lines), 21)
        self.assertEqual(association.ordered_raw_geometry_sha256, 'efc398515a96ba55c1935adda08e4641c05d1c35d54a717eca71e418ef940282')
        by_line = {s.line_number: s for s in model.spans}
        for line in (10972, 12949):
            span = by_line[line]
            self.assertEqual(span.entry_debt_mm, F(1, 100000))
            self.assertEqual(span.deposition_start_parameter, span.entry_debt_mm/span.raw_commanded_e_mm)
            self.assertNotEqual(span.support_geometry.start_xyz_mm, span.original_geometry.start_xyz_mm)
        with self.assertRaises(ValueError):
            reassociate_raw_nominal_geometry(replace(model, spans=model.spans[:-1]), **kwargs)
        forged = replace(model, spans=(replace(model.spans[0], raw_commanded_e_mm=F(99)),)+model.spans[1:])
        with self.assertRaisesRegex(ValueError, 'stale/forged'):
            reassociate_raw_nominal_geometry(forged, **kwargs)
        with self.assertRaises(ValueError):
            reassociate_raw_nominal_geometry(model, **dict(kwargs, old_rows=rows+b' '))


if __name__ == '__main__':
    unittest.main()
