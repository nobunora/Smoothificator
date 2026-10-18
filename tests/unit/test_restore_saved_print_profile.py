"""Saved program restoration preserves project content and rejects ambiguity."""
from hashlib import sha256
from decimal import Decimal
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
import warnings
from zipfile import ZipFile

from tools.restore_saved_print_profile import (
    ProfileRestorationError, SETTINGS_MEMBER, command_inventory, restore_saved_profile, validate_output_paths,
)


def project(settings=None, *, settings_bytes=None, extra=()):
    if settings is None:
        settings = {'machine_start_gcode': '', 'emit_machine_limits_to_gcode': '',
                    'filament_start_gcode': [''], 'post_process': [],
                    'enable_arc_fitting': '0', 'geometry_setting': ['exact', 1]}
    buffer = BytesIO()
    with ZipFile(buffer, 'w') as archive:
        archive.writestr(SETTINGS_MEMBER, json.dumps(settings).encode() if settings_bytes is None else settings_bytes)
        archive.writestr('3D/3dmodel.model', b'<model transform="1 0 0 0 1 0 0 0 1 90 90 0"/>')
        for name, content in extra:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                archive.writestr(name, content)
    return buffer.getvalue()


def restore(model, seed):
    return restore_saved_profile(model, seed, expected_model_sha256=sha256(model).hexdigest(),
                                 expected_seed_sha256=sha256(seed).hexdigest())


class SavedProfileTests(unittest.TestCase):
    def test_integral_exponents_and_signed_zero_retain_decimal_token_category(self):
        for numeric_text in ('1e0', '-0e0', '0e0', '-12e0'):
            settings = ('{"machine_start_gcode":"","emit_machine_limits_to_gcode":'+numeric_text+
                        ',"filament_start_gcode":[""],"post_process":[],"untouched_number":'+numeric_text+'}').encode()
            numeric_project = project(settings_bytes=settings)
            for model in (numeric_project, project()):
                restored_project = restore(model, numeric_project)
                with ZipFile(BytesIO(restored_project.project_bytes)) as output:
                    restored = json.loads(output.read(SETTINGS_MEMBER), parse_float=Decimal)
                for key in ('emit_machine_limits_to_gcode', 'untouched_number'):
                    if key not in restored:
                        continue
                    self.assertIs(type(restored[key]), Decimal)
                    self.assertEqual(restored[key], Decimal(numeric_text))
                    self.assertEqual(restored[key].is_signed(), Decimal(numeric_text).is_signed())

    def test_fractional_and_tiny_decimal_numbers_preserved_in_copied_and_untouched_settings(self):
        for numeric_text in ('0.123456789012345678901', '1e-400'):
            settings = ('{"machine_start_gcode":"","emit_machine_limits_to_gcode":'+numeric_text+
                        ',"filament_start_gcode":[""],"post_process":[],"untouched_number":'+numeric_text+'}').encode()
            model = project(settings_bytes=settings)
            result = restore(model, model)
            with ZipFile(BytesIO(result.project_bytes)) as output:
                restored = json.loads(output.read(SETTINGS_MEMBER), parse_float=Decimal)
            for key in ('emit_machine_limits_to_gcode', 'untouched_number'):
                self.assertIs(type(restored[key]), Decimal)
                self.assertEqual(restored[key], Decimal(numeric_text))
            self.assertEqual(result.changes, ())
            copied = restore(project(), model)
            with ZipFile(BytesIO(copied.project_bytes)) as output:
                restored = json.loads(output.read(SETTINGS_MEMBER), parse_float=Decimal)
            self.assertEqual(restored['emit_machine_limits_to_gcode'], Decimal(numeric_text))
            change, = copied.changes
            self.assertEqual(change.new_value_sha256, sha256(str(Decimal(numeric_text)).encode('ascii')).hexdigest())

    def test_inventory_keeps_manufacturer_decimal_opcodes(self):
        source = b'; fixture\nM622.1 S1\nM622 S1\nG1X1Y2\nT1000\nUNKNOWN\n'
        self.assertEqual(command_inventory(source),
                         {'M622.1': 1, 'M622': 1, 'G1': 1, 'T1000': 1, 'UNRECOGNIZED': 1})

    def test_exact_saved_values_types_non_template_key_and_other_content(self):
        saved = {'machine_start_gcode': 'G28\nM104 S200', 'emit_machine_limits_to_gcode': '1',
                 'filament_start_gcode': ['M83', 'G92 E0'], 'post_process': [],
                 'enable_arc_fitting': '1', 'geometry_setting': ['seed differs', 2]}
        model, seed = project(), project(saved)
        result = restore(model, seed)
        with ZipFile(BytesIO(result.project_bytes)) as output, ZipFile(BytesIO(model)) as original:
            settings = json.loads(output.read(SETTINGS_MEMBER))
            for key in result.restored_keys:
                self.assertEqual(settings[key], saved[key])
                self.assertIs(type(settings[key]), type(saved[key]))
            self.assertEqual(settings['enable_arc_fitting'], '0')
            self.assertEqual(settings['geometry_setting'], ['exact', 1])
            self.assertEqual(output.read('3D/3dmodel.model'), original.read('3D/3dmodel.model'))
        self.assertEqual({change.key for change in result.changes}, set(result.restored_keys))
        self.assertEqual(result.model_sha256, sha256(model).hexdigest())
        self.assertEqual(result.seed_sha256, sha256(seed).hexdigest())

    def test_actual_json_numeric_type_and_value_hashes(self):
        saved = {'machine_start_gcode': '', 'emit_machine_limits_to_gcode': 1,
                 'filament_start_gcode': [''], 'post_process': []}
        result = restore(project(), project(saved))
        with ZipFile(BytesIO(result.project_bytes)) as output:
            value = json.loads(output.read(SETTINGS_MEMBER))['emit_machine_limits_to_gcode']
        self.assertIs(type(value), int)
        self.assertEqual(value, 1)
        change, = result.changes
        self.assertEqual(change.new_value_sha256, sha256(b'1').hexdigest())
        self.assertEqual(change.old_value_sha256, sha256(b'""').hexdigest())

    def test_stale_model_seed_pins_reject(self):
        model = project()
        digest = sha256(model).hexdigest()
        for pins in (('0' * 64, digest), (digest, '0' * 64)):
            with self.subTest(pins=pins), self.assertRaisesRegex(ProfileRestorationError, 'stale'):
                restore_saved_profile(model, model, expected_model_sha256=pins[0], expected_seed_sha256=pins[1])

    def test_malformed_duplicate_and_sliced_inputs_reject_on_either_side(self):
        bad_inputs = (b'not zip', project(settings_bytes=b'{'), project(settings_bytes=b'[]'),
            project(settings_bytes=b'{"x":1,"x":2}'), project(settings_bytes=b'{"x":NaN}'),
            project(extra=((SETTINGS_MEMBER, b'{}'),)),
            project(extra=(('Metadata/plate_1.GCODE', b'G28\n'),)))
        good = project()
        for bad in bad_inputs:
            for model, seed in ((good, bad), (bad, good)):
                with self.subTest(length=len(bad)), self.assertRaises(ProfileRestorationError):
                    restore(model, seed)

    def test_external_postprocessing_rejects_both_inputs(self):
        for key, value in (('post_process', ['script.py']), ('post_process', ['']),
                           ('post_process', None), ('external_postprocess', 'command')):
            with ZipFile(BytesIO(project())) as archive:
                settings = json.loads(archive.read(SETTINGS_MEMBER))
            settings[key] = value
            bad = project(settings)
            for model, seed in ((project(), bad), (bad, project())):
                with self.subTest(key=key, value=value), self.assertRaisesRegex(ProfileRestorationError, 'postprocessing'):
                    restore(model, seed)

    def test_missing_or_additional_program_key_rejects(self):
        for settings in ({'post_process': []}, {'extra_gcode': '', 'post_process': []}):
            with self.assertRaisesRegex(ProfileRestorationError, 'key sets'):
                restore(project(), project(settings))

    def test_unchanged_program_values_do_not_create_changed_key_receipts(self):
        result = restore(project(), project())
        self.assertEqual(result.changes, ())
        self.assertEqual(len(result.restored_keys), 3)

    def test_path_alias_input_output_rejects(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / 'model.3mf'
            seed = Path(folder) / 'seed.3mf'
            model.write_bytes(project())
            seed.write_bytes(project())
            for output in (model, seed, model.parent / 'sub/../model.3mf'):
                with self.subTest(output=output), self.assertRaisesRegex(ProfileRestorationError, 'alias'):
                    validate_output_paths(model, seed, output)
            validate_output_paths(model, seed, Path(folder) / 'new.3mf')
