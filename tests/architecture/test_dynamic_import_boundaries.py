"""Five import-boundary checks for literal runtime imports missed by AST Import nodes."""
import ast
from importlib.util import resolve_name
import pathlib
import unittest

from tests.architecture.test_boundaries import ROOT, _module_name, _import_forbidden


def _literal_dynamic_targets(tree, module):
    """Inspect explicit literal module names; computed imports require separate review."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        fn = node.func
        is_builtin = isinstance(fn, ast.Name) and fn.id == "__import__"
        is_importlib = (isinstance(fn, ast.Attribute) and fn.attr == "import_module"
                        and isinstance(fn.value, ast.Name) and fn.value.id == "importlib")
        if not (is_builtin or is_importlib):
            continue
        first = node.args[0]
        if not isinstance(first, ast.Constant) or type(first.value) is not str:
            continue
        name = first.value
        if name.startswith("."):
            package = module.rpartition(".")[0]
            for keyword in node.keywords:
                if keyword.arg == "package" and isinstance(keyword.value, ast.Constant):
                    package = keyword.value.value
            yield resolve_name(name, package)
        else:
            yield name


def _scan_package(package):
    root = ROOT / package.replace(".", "/")
    files = sorted(root.rglob("*.py"))
    if not files:
        raise AssertionError("package has no Python modules: " + package)
    for path in files:
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for target in _literal_dynamic_targets(tree, module):
            if _import_forbidden(module, target):
                raise AssertionError("forbidden dynamic import: " + module + " -> " + target)


class DynamicImportBoundaries(unittest.TestCase):
    def test_explicit_builtin_and_importlib_imports_are_identified(self):
        code = ast.parse('importlib.import_module("orca_plugin.ui.preview_renderer")\n'
                         '__import__("adaptive_subedge.application.plan_store")\n')
        targets = set(_literal_dynamic_targets(code, "adaptive_subedge.domain.plan"))
        self.assertEqual(targets, {
            "orca_plugin.ui.preview_renderer", "adaptive_subedge.application.plan_store"})
        self.assertTrue(all(_import_forbidden("adaptive_subedge.domain.plan", x)
                            for x in targets))

    def test_literal_relative_runtime_imports_resolve_to_full_module_path(self):
        sample = ast.parse('importlib.import_module("..application.plan_store", '
                           'package="adaptive_subedge.domain")')
        targets = tuple(_literal_dynamic_targets(sample, "adaptive_subedge.domain.plan"))
        self.assertEqual(targets, ("adaptive_subedge.application.plan_store",))
        self.assertTrue(_import_forbidden("adaptive_subedge.domain.plan", targets[0]))

    def test_domain_and_engine_have_no_forbidden_literal_dynamic_import(self):
        _scan_package("adaptive_subedge.domain")
        _scan_package("adaptive_subedge.engine")

    def test_ports_and_application_have_no_forbidden_literal_dynamic_import(self):
        _scan_package("adaptive_subedge.ports")
        _scan_package("adaptive_subedge.application")

    def test_adapters_ui_and_gcode_have_no_forbidden_literal_dynamic_import(self):
        # These packages may be absent in the Phase 0.5 skeleton;
        # inspect the present orca_plugin Python tree without requiring
        # unapproved adapter implementation.
        _scan_package("orca_plugin")


if __name__ == "__main__":
    unittest.main()
