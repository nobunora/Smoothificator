"""Import restrictions, ADR identity and legacy behavior boundaries."""
import ast
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _module_name(path: pathlib.Path) -> str:
    parts = path.relative_to(ROOT).with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _import_targets(node: ast.AST, package: str) -> tuple[str, ...]:
    """Resolve explicit absolute/relative imports, including 'from .. import x'."""
    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if not isinstance(node, ast.ImportFrom):
        return ()
    parent = package.split(".")
    if node.level:
        if node.level - 1 > len(parent):
            raise AssertionError("relative import escaped the package root")
        parent = parent[:len(parent) - node.level + 1]
    else:
        parent = []
    prefix = ".".join(parent + (node.module.split(".") if node.module else []))
    names = tuple(prefix + "." + alias.name if prefix else alias.name
                  for alias in node.names if alias.name != "*")
    return ((prefix,) if node.module else ()) + names


def _import_forbidden(source_module: str, imported_module: str) -> bool:
    def in_prefix(value, prefix):
        return value == prefix or value.startswith(prefix + ".")
    if in_prefix(source_module, "adaptive_subedge.domain"):
        return any(in_prefix(imported_module, x) for x in
                   ("orca_plugin", "adaptive_subedge.engine",
                    "adaptive_subedge.application", "adaptive_subedge.ports"))
    if in_prefix(source_module, "adaptive_subedge.engine"):
        return in_prefix(imported_module, "orca_plugin")
    if in_prefix(source_module, "adaptive_subedge.application"):
        return in_prefix(imported_module, "orca_plugin")
    if in_prefix(source_module, "orca_plugin.gcode"):
        return in_prefix(imported_module, "adaptive_subedge.engine")
    if in_prefix(source_module, "orca_plugin.ui"):
        return any(in_prefix(imported_module, x) for x in
                   ("adaptive_subedge.engine", "orca_plugin.gcode",
                    "orca_plugin.adapters"))
    return False


def _check_module_init_acyclic(graph: dict[str, set[str]]) -> None:
    visiting = set()
    visited = set()
    def walk(node):
        if node in visiting:
            raise ValueError("module-level import dependency cycle")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            walk(dep)
        visiting.remove(node)
        visited.add(node)
    for module in sorted(graph):
        walk(module)


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

    def test_resolved_relative_and_absolute_import_boundaries(self):
        source_paths = sorted((ROOT / "adaptive_subedge").rglob("*.py")) + sorted(
            (ROOT / "orca_plugin").rglob("*.py"))
        self.assertTrue(source_paths)
        for path in source_paths:
            module = _module_name(path)
            package = module if path.name == "__init__.py" else module.rpartition(".")[0]
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                for target in _import_targets(node, package):
                    self.assertFalse(_import_forbidden(module, target),
                                     f"forbidden dependency: {module} -> {target}")

    def test_boundary_resolver_detects_synthetic_relative_import(self):
        module = "adaptive_subedge.domain.plan"
        parent = "adaptive_subedge.domain"
        examples = ("from .. import application",
                    "from ... import orca_plugin",
                    "import orca_plugin.gcode.injector")
        for script in examples:
            root = ast.parse(script)
            imports = tuple(target for node in ast.walk(root)
                            for target in _import_targets(node, parent))
            self.assertTrue(any(_import_forbidden(module, item) for item in imports),
                            script)

    def test_module_level_dependency_graph_has_no_cycle(self):
        paths = sorted((ROOT / "adaptive_subedge").rglob("*.py")) + sorted(
            (ROOT / "orca_plugin").rglob("*.py"))
        modules = {_module_name(path): path for path in paths}
        graph = {module: set() for module in modules}
        for module, path in modules.items():
            package = module if path.name == "__init__.py" else module.rpartition(".")[0]
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                for target in _import_targets(node, package):
                    if target in modules and target != module:
                        graph[module].add(target)
        _check_module_init_acyclic(graph)
        with self.assertRaises(ValueError):
            _check_module_init_acyclic({"a": {"b"}, "b": {"a"}})

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
