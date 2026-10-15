"""Four structural tests of Phase 0.5 application/domain ownership."""
import ast
from pathlib import Path
import unittest

from tests.architecture.test_boundaries import (
    ROOT, _module_name, _import_targets, _import_forbidden, _check_module_init_acyclic
)
from tests.architecture.test_dynamic_import_boundaries import _literal_dynamic_targets


class OwnerGraphMatrix(unittest.TestCase):
    def test_domain_sources_never_import_application_engine_or_adapter(self):
        srcs = sorted((ROOT/"adaptive_subedge"/"domain").rglob("*.py"))
        self.assertTrue(srcs)
        for file in srcs:
            name = _module_name(file)
            pkg = name if file.name == "__init__.py" else name.rpartition(".")[0]
            for node in ast.walk(ast.parse(file.read_text(encoding="utf-8"))):
                for target in _import_targets(node,pkg):
                    self.assertFalse(_import_forbidden(name,target),f"{name}->{target}")

    def test_application_domain_dependency_initialization_graph_has_no_cycles(self):
        roots = (ROOT/"adaptive_subedge"/"application",ROOT/"adaptive_subedge"/"domain",
                 ROOT/"adaptive_subedge"/"ports",ROOT/"adaptive_subedge"/"engine")
        files = [x for root in roots for x in root.rglob("*.py")]
        names = {_module_name(x): x for x in files}
        graph = {}
        for name,file in names.items():
            pkg = name if file.name == "__init__.py" else name.rpartition(".")[0]
            graph[name] = {target for node in ast.parse(file.read_text(encoding="utf-8")).body
                           for target in _import_targets(node,pkg) if target in names and target != name}
        _check_module_init_acyclic(graph)
        with self.assertRaises(ValueError):
            _check_module_init_acyclic({"first":{"second"},"second":{"first"}})

    def test_identity_crypto_ownership_is_application_hashing_only(self):
        production_roots = (ROOT/"adaptive_subedge"/"domain",
                            ROOT/"adaptive_subedge"/"engine",
                            ROOT/"adaptive_subedge"/"ports")
        for root in production_roots:
            for file in root.rglob("*.py"):
                imports = [target for node in ast.walk(ast.parse(file.read_text(encoding="utf-8")))
                           for target in _import_targets(node,_module_name(file).rpartition(".")[0])]
                self.assertNotIn("hashlib", imports, str(file))
                self.assertNotIn("hmac", imports, str(file))
        hashing = (ROOT/"adaptive_subedge"/"application"/"hashing.py").read_text(encoding="utf-8")
        self.assertIn("hashlib.sha256",hashing)
        self.assertIn("hmac.compare_digest",hashing)

    def test_literal_runtime_imports_cannot_bypass_domain_and_port_boundaries(self):
        examples = (
            ("adaptive_subedge.domain.plan", '__import__("orca_plugin.adapters.geometry_snapshot")'),
            ("adaptive_subedge.ports.cancellation", 'importlib.import_module("adaptive_subedge.application.plan_store")'),
            ("adaptive_subedge.engine.support", 'importlib.import_module("..application.plan_store",package="adaptive_subedge.engine")'),
        )
        for module,code in examples:
            with self.subTest(module=module):
                targets = list(_literal_dynamic_targets(ast.parse(code),module))
                self.assertTrue(targets)
                self.assertTrue(any(_import_forbidden(module,target) for target in targets))
        for package in ("domain","ports","engine"):
            root = ROOT/"adaptive_subedge"/package
            for file in root.rglob("*.py"):
                self.assertFalse(any(_import_forbidden(_module_name(file),target)
                  for target in _literal_dynamic_targets(
                      ast.parse(file.read_text(encoding="utf-8")),_module_name(file))),
                  str(file))


if __name__=="__main__":
    unittest.main()
