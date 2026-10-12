"""Import restrictions, ADR identity and legacy behavior boundaries."""
import ast
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class BoundaryTests(unittest.TestCase):
    def test_no_forbidden_imports_or_gcode_mutation(self):
        paths = sorted((ROOT / "adaptive_subedge").rglob("*.py"))
        self.assertTrue(paths)
        for path in paths:
            relative = path.relative_to(ROOT).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.extend(x.name for x in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.append(node.module)
            if relative.startswith(("adaptive_subedge/domain/", "adaptive_subedge/engine/")):
                self.assertFalse(any(x.startswith(("orca_plugin", "bambu", "slicer")) for x in imported), relative)
            if relative.startswith("adaptive_subedge/engine/"):
                self.assertFalse(any("gcode" in x for x in imported), relative)
        self.assertFalse((ROOT / "orca_plugin" / "gcode").exists(), "no G-code executor may be implemented in this milestone")

    def test_adr_identifiers_unique(self):
        names = list((ROOT / "docs" / "adr").glob("[0-9][0-9][0-9][0-9]-*.md"))
        numbers = [int(p.name[:4]) for p in names]
        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertEqual(sorted(numbers), list(range(1, 66)))
        legacy = (ROOT / "docs" / "adr" / "0010-orca-filament-flow-ratio-e-conversion.md").read_text(encoding="utf-8")
        self.assertIn("Status: Superseded", legacy)

    def test_no_production_gcode_hooks(self):
        for path in (ROOT / "adaptive_subedge").rglob("*.py"):
            data = path.read_text(encoding="utf-8")
            self.assertNotIn("psGCodePostProcess", data)
            self.assertNotIn("atomic_replace(ctx.gcode_path", data)


if __name__ == "__main__":
    unittest.main()
