"""Read-only inspection must not acquire mutation, engine or printer hooks."""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class PrintInspectionBoundaryTests(unittest.TestCase):
    def test_inspection_dependencies_and_io_are_closed(self):
        allowed = {"dataclasses", "fractions", "hashlib", "io", "json", "re", "zipfile"}
        for name in ("source_profile.py", "linear_trace.py"):
            tree = ast.parse((ROOT / "orca_plugin/gcode" / name).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertTrue(all(alias.name in allowed for alias in node.names))
                if isinstance(node, ast.ImportFrom):
                    self.assertIn(node.module, allowed)
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, ("open", "exec", "eval", "__import__"))
                        if node.func.id == "ZipFile":
                            self.assertEqual(len(node.args), 1)
                            self.assertEqual(node.keywords, [])
                    if isinstance(node.func, ast.Attribute):
                        self.assertNotIn(node.func.attr, ("write", "write_bytes", "write_text",
                                                         "writestr", "extract", "extractall",
                                                         "unlink", "replace", "rename"))

    def test_production_entrypoint_does_not_register_inspection_as_runtime_hook(self):
        tree = ast.parse((ROOT / "orca_plugin/__init__.py").read_text())
        self.assertTrue(all(isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                            and isinstance(node.value.value, str) for node in tree.body))
