"""Four deterministic literal importlib alias-boundary cases."""
import ast
import unittest

from tests.architecture.test_boundaries import _import_forbidden
from tests.architecture.test_dynamic_import_boundaries import _literal_dynamic_targets, _scan_package


class ImportlibAliasBoundaryTests(unittest.TestCase):
    def test_import_from_alias_exposes_forbidden_orca_dependency(self):
        tree = ast.parse('from importlib import import_module as load\n'
                         'load("orca_plugin.adapters.geometry_snapshot")')
        targets = list(_literal_dynamic_targets(tree, "adaptive_subedge.domain.geometry"))
        self.assertEqual(targets, ["orca_plugin.adapters.geometry_snapshot"])
        self.assertTrue(_import_forbidden("adaptive_subedge.domain.geometry", targets[0]))

    def test_importlib_module_alias_exposes_forbidden_application_dependency(self):
        tree = ast.parse('import importlib as mod\n'
                         'mod.import_module("adaptive_subedge.application.plan_store")')
        targets = list(_literal_dynamic_targets(tree, "adaptive_subedge.ports.cancellation"))
        self.assertEqual(targets, ["adaptive_subedge.application.plan_store"])
        self.assertTrue(_import_forbidden("adaptive_subedge.ports.cancellation", targets[0]))

    def test_from_importlib_literal_relative_alias_resolves_package(self):
        tree = ast.parse('from importlib import import_module\n'
                         'import_module("..application.plan_store",package="adaptive_subedge.domain")')
        targets = tuple(_literal_dynamic_targets(tree, "adaptive_subedge.domain.plan"))
        self.assertEqual(targets, ("adaptive_subedge.application.plan_store",))
        self.assertTrue(_import_forbidden("adaptive_subedge.domain.plan", targets[0]))

    def test_computed_name_is_not_falsely_described_as_checked_and_existing_packages_pass(self):
        tree = ast.parse('from importlib import import_module as load\n'
                         'target = "orca_plugin.adapters.geometry_snapshot"\n'
                         'load(target)')
        self.assertEqual(list(_literal_dynamic_targets(tree, "adaptive_subedge.domain.plan")), [])
        for package in ("adaptive_subedge.domain", "adaptive_subedge.engine",
                        "adaptive_subedge.ports", "adaptive_subedge.application", "orca_plugin"):
            with self.subTest(package=package):
                _scan_package(package)


if __name__ == "__main__":
    unittest.main()
