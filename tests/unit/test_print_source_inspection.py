"""Source association, resolved-setting precedence and physical modal arithmetic."""
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
from io import BytesIO
import json
import unittest
import warnings
from zipfile import ZipFile

from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution
from orca_plugin.gcode.source_profile import (
    SourceProfileError, read_sliced_profile, TEXT_KEYS, POSITIVE_KEYS,
    NONNEGATIVE_KEYS, OVERRIDES,
)
from tools.inspect_print_source import inspect_source


def settings_fixture():
    settings = {key: "fixture" for key in TEXT_KEYS}
    settings.update({key: "1" for key in POSITIVE_KEYS})
    settings.update({key: "0" for key in NONNEGATIVE_KEYS})
    for key in TEXT_KEYS:
        if "gcode" in key:
            settings[key] = "" if key != "gcode_flavor" else "marlin"
    for key in OVERRIDES:
        settings[key] = ["30" if key.endswith("speed") else "0.8"]
        settings[f"filament_{key}"] = ["nil"]
    settings["retract_restart_extra"] = ["0"]
    settings["nozzle_diameter"] = ["0.4"]
    return settings


def fixture(settings=None, *, json_bytes=None, duplicate=False, extra_config=()):
    settings = settings_fixture() if settings is None else settings
    lines = ["; CONFIG_BLOCK_START"]
    for key, value in settings.items():
        if isinstance(value, list):
            value = ",".join(value)
        lines.append(f"; {key} = {value}")
    lines.extend(extra_config)
    lines.extend(("; CONFIG_BLOCK_END", "G21", "G90", "M83", "M200 D0", "G92 E0", "G1 X1 Y2 Z3 F600"))
    source = ("\n".join(lines) + "\n").encode("ascii")
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("Metadata/project_settings.config",
                         json.dumps(settings).encode() if json_bytes is None else json_bytes)
        archive.writestr("Metadata/plate_1.gcode", source)
        if duplicate:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr("Metadata/plate_1.gcode", source)
    return buffer.getvalue(), source


class SlicedSourceTests(unittest.TestCase):
    def test_immutable_settings_and_embedded_source_association(self):
        project, source = fixture()
        profile = read_sliced_profile(project, source)
        self.assertEqual(profile.setting("nozzle_diameter").number(), F(".4"))
        self.assertEqual(profile.setting("effective_printable_height").source_key, "printable_height")
        with self.assertRaises(FrozenInstanceError):
            profile.source_sha256 = "other"
        with self.assertRaisesRegex(SourceProfileError, "differ"):
            read_sliced_profile(project, source + b"; changed\n")

    def test_filament_override_and_nil_inheritance_record_provenance(self):
        settings = settings_fixture()
        settings["filament_retraction_length"] = ["1.2"]
        profile = read_sliced_profile(*fixture(settings))
        self.assertEqual(profile.setting("retraction_length").number(), F("1.2"))
        self.assertEqual(profile.setting("retraction_length").source_key, "filament_retraction_length")
        self.assertEqual(profile.setting("retraction_speed").source_key, "retraction_speed")

    def test_explicit_per_extruder_height_is_retained(self):
        settings = settings_fixture()
        settings["extruder_printable_height"] = ["123"]
        profile = read_sliced_profile(*fixture(settings))
        self.assertEqual(profile.setting("effective_printable_height").number(), 123)
        self.assertEqual(profile.setting("effective_printable_height").source_key, "extruder_printable_height")

    def test_missing_numeric_nil_percentage_nonfinite_multiple_material_rejected(self):
        cases = (None, ["nil"], ["100%"], ["NaN"], ["inf"], ["0.4", "0.6"], 0.4, ["0"])
        for value in cases:
            with self.subTest(value=value):
                settings = settings_fixture()
                if value is None:
                    del settings["nozzle_diameter"]
                else:
                    settings["nozzle_diameter"] = value
                with self.assertRaises(SourceProfileError):
                    read_sliced_profile(*fixture(settings))

    def test_missing_override_is_not_assumed_nil(self):
        settings = settings_fixture()
        del settings["filament_z_hop"]
        with self.assertRaisesRegex(SourceProfileError, "filament_z_hop"):
            read_sliced_profile(*fixture(settings))

    def test_duplicate_members_and_json_keys_rejected(self):
        with self.assertRaisesRegex(SourceProfileError, "duplicate ZIP"):
            read_sliced_profile(*fixture(duplicate=True))
        with self.assertRaisesRegex(SourceProfileError, "duplicate JSON"):
            read_sliced_profile(*fixture(json_bytes=b'{"a":"1","a":"2"}'))

    def test_configuration_mismatch_even_with_matching_embedded_source_rejected(self):
        settings = settings_fixture()
        inconsistent = dict(settings, nozzle_diameter=["0.6"])
        with self.assertRaisesRegex(SourceProfileError, "mismatch: nozzle_diameter"):
            read_sliced_profile(*fixture(settings, json_bytes=json.dumps(inconsistent).encode()))

    def test_readonly_report_never_authorizes_printing(self):
        report = inspect_source(*fixture())
        self.assertFalse(report["printable_authorized"])
        self.assertIsNone(report["trace_failure"])
        self.assertTrue(report["unresolved"])
        self.assertTrue(any("travel_speed_z=0" in x for x in report["unresolved"]))

    def test_duplicate_consumed_key_rejected_unconsumed_duplicates_reported(self):
        with self.assertRaisesRegex(SourceProfileError, "duplicate consumed"):
            read_sliced_profile(*fixture(extra_config=("; nozzle_diameter = 0.4",)))
        report = inspect_source(*fixture(extra_config=("; wipe_tower_x = 1", "; wipe_tower_x = 2")))
        self.assertEqual(report["unconsumed_duplicate_config_keys"], ("wipe_tower_x",))
        self.assertTrue(any("duplicate unconsumed" in x for x in report["unresolved"]))


class LinearTraceTests(unittest.TestCase):
    def trace(self, program, *, debt=None):
        state = MachineState(retraction_debt_mm=None if debt is None else F(debt))
        return trace_linear_execution(b"G21\r\nG90\r\nM83\r\nM200 D0\r\n" + program, initial_state=state)

    def test_retract_g92_unretract_and_deposition_are_separate(self):
        trace = self.trace(b"G92 E8\nG1 E-0.8 F1800\nG92 E0\nG1 E0.3\nG1 E0.7\n", debt=0)
        self.assertIsNone(trace.failure)
        self.assertEqual(trace.records[-3].after.retraction_debt_mm, F(".8"))
        self.assertEqual(trace.records[-2].extruded_filament_mm, 0)
        self.assertEqual(trace.records[-1].extruded_filament_mm, F(".2"))
        self.assertEqual(trace.final_state.retraction_debt_mm, 0)
        self.assertEqual(trace.final_state.logical_e_mm, 1)
        self.assertEqual(trace.final_state.feed_mm_min, 1800)

    def test_unknown_origin_and_debt_never_become_assumed_zero(self):
        trace = self.trace(b"G92 E0\nG1 X4 F600\nG1 E1\n")
        self.assertEqual(trace.final_state.xyz_mm, (F(4), None, None))
        self.assertIsNone(trace.final_state.retraction_debt_mm)
        self.assertIsNone(trace.records[-1].extruded_filament_mm)

    def test_raw_offsets_and_original_chronology(self):
        program = b"; layer marker\r\nG1X1Y2Z3F1200\r\nG1Z2\r\nG1Z4\n"
        trace = self.trace(program)
        moves = [r for r in trace.records if r.command == "G1"]
        self.assertEqual([r.after.xyz_mm[2] for r in moves], [3, 2, 4])
        source = b"G21\r\nG90\r\nM83\r\nM200 D0\r\n" + program
        for record in trace.records:
            self.assertEqual(source[record.byte_offset:record.byte_offset + len(record.raw)], record.raw)
        self.assertEqual(moves[0].line_number, 6)

    def test_unsupported_lines_stop_prefix_without_interpreting_later_moves(self):
        for bad in (b"G91", b"G20", b"M82", b"G2 X1", b"G10", b"G92 X0",
                    b"M220 S99", b"M221 S101", b"M200 D1.75", b"M981 S1",
                    b"G1 X1 X2", b"G1 XNaN", b"G1 X1 ;\xff",
                    b"G1 X1 A2", b"G1 F0", b"G90 X0", b"N1 G1 X2*42",
                    b"G1 X2\x0b", b"G1 X2\x00", b"G1 X2\x7f"):
            with self.subTest(bad=bad):
                trace = self.trace(b"G1 X1 Y2 Z3 F600\n" + bad + b"\nG1 X999\n")
                self.assertIsNotNone(trace.failure)
                self.assertEqual(trace.final_state.xyz_mm[0], 1)

    def test_no_implicit_initial_modes(self):
        trace = trace_linear_execution(b"G1 X1\n")
        self.assertIn("G21/G90/M83", trace.failure.reason)
        self.assertEqual(trace.records, ())

    def test_override_modes_must_be_explicit(self):
        trace = self.trace(b"M200 D0\nM220 S100\nM221 S100\n")
        self.assertIsNone(trace.failure)
        self.assertTrue(trace.final_state.volumetric_disabled)
        self.assertTrue(trace.final_state.speed_override_100)
        self.assertTrue(trace.final_state.flow_override_100)

    def test_decimal_arithmetic_does_not_accumulate_float_drift(self):
        trace = self.trace(b"G92 E0\nG1 E-0.3 F60\n" + b"G1 E0.1\n" * 4, debt=0)
        self.assertEqual(trace.final_state.logical_e_mm, F(".1"))
        self.assertEqual(trace.records[-1].extruded_filament_mm, F(".1"))

    def test_invalid_initial_state_is_rejected(self):
        for state in (MachineState(xyz_mm=(F(1),)), MachineState(feed_mm_min=F(0)),
                      MachineState(retraction_debt_mm=F(-1)), MachineState(absolute_xyz=1),
                      MachineState(logical_e_mm=0.1)):
            with self.subTest(state=state), self.assertRaises(ValueError):
                trace_linear_execution(b"", initial_state=state)

    def test_g90_requires_renewed_relative_e_and_unknown_e_units_reject(self):
        self.assertIsNotNone(self.trace(b"G90\nG1 E1\n").failure)
        self.assertIsNone(self.trace(b"G90\nM83\nG1 E1\n").failure)
        for program in (b"G21\nG90\nM83\nG1 E1\n", b"G92 E0\n"):
            with self.subTest(program=program):
                self.assertIsNotNone(trace_linear_execution(program).failure)


if __name__ == "__main__":
    unittest.main()
