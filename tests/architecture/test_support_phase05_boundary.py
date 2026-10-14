"""Phase 0.5 boundary assertions for approved standalone support value types."""
import ast
from dataclasses import fields, is_dataclass
import unittest

from adaptive_subedge.application.serialization import _FIELDS
from adaptive_subedge.domain.metrics import ConservativeSupportBounds
from adaptive_subedge.domain.settings import (
    SupportCoverageThresholds, SupportRefinementPolicy, CandidateBeadBounds, PluginSettings,
)
from tests.architecture.test_boundaries import ROOT, _module_name, _import_targets, _import_forbidden
from tests.architecture.test_dynamic_import_boundaries import _literal_dynamic_targets


class Phase05SupportOwnership(unittest.TestCase):
    def test_all_support_value_dtos_are_frozen_registered_and_owned_by_domain(self):
        required=(SupportCoverageThresholds,SupportRefinementPolicy,
                  ConservativeSupportBounds,CandidateBeadBounds)
        for cls in required:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls.__module__.split(".")[:2],["adaptive_subedge","domain"])
                self.assertTrue(is_dataclass(cls))
                self.assertTrue(cls.__dataclass_params__.frozen)
                self.assertEqual(_FIELDS[cls],tuple(f.name for f in fields(cls)))

    def test_support_dtos_do_not_mutate_settings_v1_full_schema(self):
        exact=("schema_version","surface_error_tolerance_mm",
               "minimum_effective_bead_height_mm","candidate_seam_gap_mm",
               "regularity_policy","tool_clearance_profile","physical_injection_requested")
        self.assertEqual(tuple(f.name for f in fields(PluginSettings)),exact)
        self.assertEqual(_FIELDS[PluginSettings],exact)
        self.assertTrue(all(v not in fields(PluginSettings) for v in (
           SupportCoverageThresholds,SupportRefinementPolicy,ConservativeSupportBounds)))

    def test_import_edges_of_domain_settings_and_metrics_are_inward(self):
        for name in ("settings.py","metrics.py"):
            path=ROOT/"adaptive_subedge"/"domain"/name
            self.assertTrue(path.is_file())
            module=_module_name(path)
            package=module.rpartition(".")[0]
            tree=ast.parse(path.read_text(encoding="utf-8"))
            targets=[target for node in ast.walk(tree) for target in _import_targets(node,package)]
            targets.extend(_literal_dynamic_targets(tree,module))
            for target in targets:
                with self.subTest(path=name,target=target):
                    self.assertFalse(_import_forbidden(module,target))

    def test_phase05_adds_no_runtime_orca_gcode_execution_modules(self):
        # Handoff forbids live Orca, G-code and optimizer execution in this phase.
        self.assertFalse((ROOT/"orca_plugin"/"gcode").exists())
        self.assertFalse((ROOT/"orca_plugin"/"capabilities").exists())
        self.assertFalse((ROOT/"orca_plugin"/"adapters").exists())
        self.assertFalse((ROOT/"adaptive_subedge"/"application"/"analyzer.py").exists())
        self.assertFalse((ROOT/"adaptive_subedge"/"engine"/"candidate_generator.py").exists())


if __name__=="__main__":
    unittest.main()
