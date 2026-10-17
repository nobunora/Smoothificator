"""The research preview is isolated from printable plan/export authority."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PreviewBoundaryTests(unittest.TestCase):
    def test_preview_layers(self):
        for path in (ROOT / "smoothificator_preview").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = [name for node in ast.walk(tree) for name in (
                [a.name for a in node.names] if isinstance(node, ast.Import) else
                [node.module or ""] if isinstance(node, ast.ImportFrom) else [])]
            self.assertFalse(any("plan_store" in name or "gcode" in name for name in imports))
            if path.name == "ui.py":
                self.assertFalse(any(name.startswith(("orca", "adaptive_subedge.engine"))
                                     or name in ("adapters", "application") for name in imports))
            if path.name not in ("entrypoint.py", "__init__.py", "adapters.py"):
                self.assertNotIn("orca", imports)
            self.assertNotIn("SlicingPipelineCapabilityBase", path.read_text(encoding="utf-8"))

    def test_engine_never_imports_preview(self):
        for package in ("domain", "engine", "application", "ports"):
            for path in (ROOT / "adaptive_subedge" / package).glob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        self.assertFalse(any(a.name.startswith("smoothificator_preview") for a in node.names))
                    elif isinstance(node, ast.ImportFrom):
                        self.assertFalse((node.module or "").startswith("smoothificator_preview"))
