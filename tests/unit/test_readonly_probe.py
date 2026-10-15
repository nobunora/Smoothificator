"""Mock-boundary tests, not evidence of actual Orca installation or callbacks."""

import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.base = type("Capability", (), {"get_config": lambda self: "{}"})
        self.orca = SimpleNamespace(
            slicing=SimpleNamespace(SlicingPipelineCapabilityBase=self.base,
                                    Step=SimpleNamespace(psGCodePostProcess="post")),
            script=SimpleNamespace(ScriptPluginCapabilityBase=self.base),
            base=object, plugin=lambda cls: cls,
            ExecutionResult=SimpleNamespace(skipped=lambda reason: reason,
                                            success=lambda reason: reason),
        )
        path = Path(__file__).resolve().parents[2] / "diagnostics/smoothificator_readonly_probe.py"
        spec = importlib.util.spec_from_file_location("isolated_probe", path)
        self.probe = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"orca": self.orca}):
            spec.loader.exec_module(self.probe)
        self.probe._verified_build = True
        self.capability = self.probe.ReadOnlyExportProbe()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "synthetic.gcode"
        self.original = b"; opaque \xff\xfe\r\nG1 X1 Y2 E0.03\r\n; no final newline"
        self.file.write_bytes(self.original)
        self.ctx = SimpleNamespace(orca_version="2.5.0-dev", step="post", host="File",
                                   gcode_path=str(self.file), print=None, object=None,
                                   config_value=lambda key: None, cancelled=lambda: False)

    def run_probe(self):
        with patch("sys.stderr"):
            result = self.capability.execute(self.ctx)
        self.assertEqual(self.file.read_bytes(), self.original)
        return result

    def test_repeated_callbacks_preserve_opaque_bytes_and_report_matching_hashes(self):
        for _ in range(3):
            self.assertEqual(self.run_probe(), "READ_ONLY_UNCHANGED")
        reports = self.probe._observations
        self.assertEqual(len(reports), 3)
        self.assertEqual(reports[0]["sha256_before"], reports[2]["sha256_after"])
        self.assertEqual(reports[0]["bytes"], len(self.original))

    def test_every_file_open_is_read_only(self):
        original_open = open
        def guarded_open(path, mode="r", *args, **kwargs):
            self.assertEqual(mode, "rb")
            return original_open(path, mode, *args, **kwargs)
        with patch("builtins.open", guarded_open):
            self.assertEqual(self.run_probe(), "READ_ONLY_UNCHANGED")

    def test_unsupported_or_unverified_runtime_never_opens_file(self):
        for armed, version in ((False, "2.5.0-dev"), (True, "2.4.2")):
            self.probe._verified_build = armed
            self.ctx.orca_version = version
            with patch.object(self.probe, "_digest_file") as digest:
                self.assertEqual(self.run_probe(), "UNSUPPORTED_OR_UNVERIFIED_RUNTIME")
                digest.assert_not_called()

    def test_disabled_and_invalid_settings(self):
        cases = (({"enabled": False}, "DISABLED"),
                 ({"enabled": 1}, "INVALID_CONTEXT_OR_SETTINGS"),
                 ({"unexpected": True}, "INVALID_CONTEXT_OR_SETTINGS"),
                 ([], "INVALID_CONTEXT_OR_SETTINGS"))
        for settings, expected in cases:
            self.capability.get_config = lambda: json.dumps(settings)
            with patch.object(self.probe, "_digest_file") as digest:
                self.assertEqual(self.run_probe(), expected)
                digest.assert_not_called()
        self.capability.get_config = lambda: "{broken"
        self.assertEqual(self.run_probe(), "INVALID_CONTEXT_OR_SETTINGS")

    def test_missing_context_or_path(self):
        self.ctx.gcode_path = ""
        self.assertEqual(self.run_probe(), "MISSING_GCODE_PATH")
        del self.ctx.gcode_path
        self.assertEqual(self.run_probe(), "INVALID_CONTEXT_OR_SETTINGS")

    def test_non_file_export_never_opens_file(self):
        for host in ("OctoPrint", "", "Bambu"):
            self.ctx.host = host
            with patch.object(self.probe, "_digest_file") as digest:
                self.assertEqual(self.run_probe(), "OFFLINE_FILE_EXPORT_REQUIRED")
                digest.assert_not_called()

    def test_geometry_step_and_unknown_step_are_noops(self):
        for step in ("posSimplifyPath", "unknown", None):
            self.ctx.step = step
            with patch.object(self.probe, "_digest_file") as digest:
                self.assertEqual(self.run_probe(), "READ_ONLY_NO_GEOMETRY_ACTION")
                digest.assert_not_called()

    def test_cancellation_before_and_during_read(self):
        self.ctx.cancelled = lambda: True
        self.assertEqual(self.run_probe(), "CANCELLED")
        answers = iter((False, True))
        self.ctx.cancelled = lambda: next(answers)
        self.assertEqual(self.run_probe(), "CANCELLED")

    def test_changed_source_is_not_reported_unchanged(self):
        with patch.object(self.probe, "_digest_file", side_effect=[("a", 1, (1,)), ("b", 1, (1,))]):
            self.assertEqual(self.run_probe(), "SOURCE_CHANGED")

    def test_read_and_unexpected_callback_failure_are_contained(self):
        for error, expected in ((PermissionError(), "READ_FAILED"),
                                (RuntimeError(), "CALLBACK_FAILED")):
            with patch.object(self.probe, "_digest_file", side_effect=error):
                self.assertEqual(self.run_probe(), expected)

    def test_oversized_file_rejects_without_writing(self):
        with patch.object(self.probe, "MAX_BYTES", 4):
            self.assertEqual(self.run_probe(), "INVALID_CONTEXT_OR_SETTINGS")

    def test_runtime_diagnostic_and_unload_revoke_wrong_build(self):
        diagnostics = self.probe.RuntimeDiagnostics()
        self.orca.host = SimpleNamespace(
            app_info=lambda: {"version": "2.5.0-dev", "build": "86905a8a"},
            ui=SimpleNamespace(message=lambda *args, **kwargs: None))
        with patch("sys.stderr"):
            diagnostics.execute()
        self.assertTrue(self.probe._verified_build)
        self.orca.host.app_info = lambda: {"version": "2.5.0-dev", "build": "other"}
        with patch("sys.stderr"):
            diagnostics.execute()
        self.assertFalse(self.probe._verified_build)
        self.probe._verified_build = True
        diagnostics.on_unload()
        self.assertFalse(self.probe._verified_build)
