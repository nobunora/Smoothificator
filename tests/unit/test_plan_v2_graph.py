"""Research graph consistency is not geometry or physical feasibility proof."""
from dataclasses import FrozenInstanceError, fields, replace
import unittest

from adaptive_subedge.domain.analysis_evidence import DirectionalErrorEvidence, ErrorConvergenceEvidence, TimeEstimateAvailable, TimeEstimateUnavailable
from adaptive_subedge.domain.errors import ContractError
from adaptive_subedge.domain.geometry import PrintPoint2, PrintPoint3
from adaptive_subedge.domain.insertion_anchor_v2 import InsertionAnchorV2
from adaptive_subedge.domain.metrics import BidirectionalSurfaceErrorMetrics
from adaptive_subedge.domain.plan import IdentityReference, SubEdgePath, SubEdgeSegment
from adaptive_subedge.domain.plan_v2 import (GeometryRegionReferenceV2, SupportReferenceV2, SurfaceBandV2,
    StructuralLoopContextV2, SegmentSupportIntentV2, SubEdgePathV2, PlannedTransitionV2,
    PlannedVolumesV2, ResearchPlanOutcomeV2, PlanSemanticContentV2, SubEdgePlanV2)
from adaptive_subedge.domain.structural_loop_v2 import StructuralLoopReferenceV2


def plan_content_v2() -> PlanSemanticContentV2:
    source = IdentityReference("source-geometry", "1", "1", "a" * 64)
    execution = IdentityReference("execution-config", "1", "1", "b" * 64)
    settings = IdentityReference("plugin-settings", "2", "1", "c" * 64)
    frame = "centered_printobject_mm_v1"
    target = GeometryRegionReferenceV2(IdentityReference("surface-boundary", "1", "1", "d" * 64), source, frame)
    residual = GeometryRegionReferenceV2(IdentityReference("residual-error-region", "1", "1", "e" * 64), source, frame)
    points = (PrintPoint3(0, 0, 0.1), PrintPoint3(2, 0, 0.2), PrintPoint3(0, 2, 0.1))
    loop = StructuralLoopReferenceV2("loop", points, 0, 7, (0, 2, 0, 2, 0.1, 0.2), frame,
        "unknown", "declared_xy_winding_v1", "research-side", points,
        "exact_binary64_cross_product_v1", "research-shape", "f" * 64)
    anchor = InsertionAnchorV2("anchor", ("loop",), 1, "boundary", "interval",
        "opaque_boundary_signature_v1", 0.01, "research-profile")
    def candidate(name, z, order, dependencies, support_ids):
        segment = SubEdgeSegment(PrintPoint2(0, 0), PrintPoint2(1, 0), z, z - 0.1, 0.1, 0.4, 0.04, 0.04, 20)
        path = SubEdgePath(name, "interval", z, 0, order, (segment,), dependencies)
        return SubEdgePathV2(path, "band", "anchor", (SegmentSupportIntentV2(support_ids, settings, None),))
    error = ErrorConvergenceEvidence("unknown", settings, 0, None, None)
    return PlanSemanticContentV2("2", "research-1", "unverified", source, execution, settings,
        (residual, target),
        (SupportReferenceV2("s-loop", "structural-loop", "loop"), SupportReferenceV2("s-path", "candidate-path", "path-a")),
        (SurfaceBandV2("band", source, target, residual, ("s-loop",), None),),
        (loop,), (StructuralLoopContextV2("loop", "interval", 1, 0, 0.2),),
        (candidate("path-a", 0.3, 1, (), ()), candidate("path-b", 0.4, 2, ("path-a",), ("s-path",))),
        (anchor,), (PlannedTransitionV2("path-a", "path-b", "travel-restart", "declared_interpath_intent_v1"),),
        DirectionalErrorEvidence(BidirectionalSurfaceErrorMetrics(1, 2, 0.5, 1, 0.5, 1), error, error),
        TimeEstimateUnavailable("unavailable", "time-model-unavailable", ("model",)),
        PlannedVolumesV2(0.08, 0.08), ResearchPlanOutcomeV2(False, "ranking-incomplete"))


class PlanV2GraphTests(unittest.TestCase):
    def setUp(self):
        self.plan = plan_content_v2()

    def reject(self, **changes):
        with self.assertRaises(ContractError):
            replace(self.plan, **changes)

    def test_nonplanar_graph_frozen_and_derived_counts(self):
        self.assertEqual(len(fields(self.plan)), 18)
        self.assertFalse(self.plan.injectable)
        self.assertEqual(self.plan.complexity_counts, (2, 2, 1))
        with self.assertRaises(FrozenInstanceError):
            self.plan.schema_version = "1"
        self.assertFalse(hasattr(self.plan, "__dict__"))
        for field in fields(self.plan):
            values = {f.name: getattr(self.plan, f.name) for f in fields(self.plan) if f != field}
            with self.subTest(field=field.name), self.assertRaises(TypeError):
                PlanSemanticContentV2(**values)

    def test_empty_graph_is_explicit_research(self):
        empty = replace(self.plan, geometry_regions=(), support_references=(), surface_bands=(),
            structural_loops=(), structural_loop_contexts=(), candidate_paths=(), anchors=(), transitions=())
        self.assertEqual(empty.complexity_counts, (0, 0, 0))
        self.assertFalse(empty.injectable)

    def test_nested_shapes_and_exact_classes(self):
        for name in ("geometry_regions", "support_references", "surface_bands", "structural_loops", "structural_loop_contexts", "candidate_paths", "anchors", "transitions"):
            self.reject(**{name: list(getattr(self.plan, name))})
            self.reject(**{name: ({},)})
        for name in ("directional_error", "added_time", "volumes", "analysis_outcome"):
            self.reject(**{name: {}})
        class DerivedRegion(GeometryRegionReferenceV2):
            pass
        region = self.plan.geometry_regions[0]
        self.reject(geometry_regions=(DerivedRegion(region.identity, region.source_geometry, region.coordinate_frame), self.plan.geometry_regions[1]))

    def test_closed_versions_and_nonblank_metadata(self):
        for value in (1, "1", "", True):
            self.reject(schema_version=value)
        for name in ("plugin_version", "compatibility_descriptor_id"):
            for value in (" ", None, 1):
                self.reject(**{name: value})
        for name in ("source_geometry", "execution_config", "plugin_settings"):
            self.reject(**{name: replace(getattr(self.plan, name), schema_version="9")})

    def test_registry_order_duplicates_and_context_coverage(self):
        for name in ("geometry_regions", "support_references", "candidate_paths"):
            self.reject(**{name: tuple(reversed(getattr(self.plan, name)))})
        for name in ("geometry_regions", "support_references", "surface_bands", "structural_loops", "structural_loop_contexts", "candidate_paths", "anchors"):
            values = getattr(self.plan, name)
            self.reject(**{name: values + (values[-1],)})
        self.reject(structural_loop_contexts=())
        self.reject(structural_loop_contexts=(replace(self.plan.structural_loop_contexts[0], loop_id="other"),))
        self.reject(structural_loop_contexts=(replace(self.plan.structural_loop_contexts[0], execution_order=1),))
        self.reject(structural_loop_contexts=(replace(self.plan.structural_loop_contexts[0], maximum_path_z_mm=0.1),))

    def test_regions_and_band_parent_forest(self):
        band = self.plan.surface_bands[0]
        self.reject(geometry_regions=(self.plan.geometry_regions[0],))
        foreign = replace(self.plan.geometry_regions[0], source_geometry=replace(self.plan.source_geometry, digest_hex="9" * 64))
        self.reject(geometry_regions=(foreign, self.plan.geometry_regions[1]))
        for parent in ("missing", "band"):
            self.reject(surface_bands=(replace(band, nesting_parent_band_id=parent),))
        self.reject(surface_bands=(replace(band, nesting_parent_band_id="second"), replace(band, surface_band_id="second", nesting_parent_band_id="band")))
        replace(self.plan, surface_bands=(band, replace(band, surface_band_id="second", nesting_parent_band_id="band")))

    def test_support_resolution_and_dependency_equality(self):
        first, second = self.plan.candidate_paths
        for kind in ("structural-loop", "candidate-path"):
            self.reject(support_references=(SupportReferenceV2("s-loop", kind, "missing"), self.plan.support_references[1]))
        self.reject(surface_bands=(replace(self.plan.surface_bands[0], chronological_support_reference_ids=("missing",)),))
        self.reject(candidate_paths=(first, replace(second, segment_support=(replace(second.segment_support[0], support_reference_ids=("missing",)),))))
        self.reject(candidate_paths=(first, replace(second, path=replace(second.path, support_dependency_path_ids=()))))
        self.reject(candidate_paths=(first, replace(second, segment_support=(replace(second.segment_support[0], support_reference_ids=()),))))

    def test_self_future_same_height_support(self):
        first, second = self.plan.candidate_paths
        self.reject(candidate_paths=(replace(first, segment_support=(replace(first.segment_support[0], support_reference_ids=("s-path",)),)), second))
        self.reject(support_references=(self.plan.support_references[0], replace(self.plan.support_references[1], contributor_id="path-b")))
        future_first = replace(first, path=replace(first.path, support_dependency_path_ids=("path-b",)),
            segment_support=(replace(first.segment_support[0], support_reference_ids=("s-path",)),))
        self.reject(candidate_paths=(future_first, second),
            support_references=(self.plan.support_references[0], replace(self.plan.support_references[1], contributor_id="path-b")))
        same_z = replace(second.path, command_z_mm=first.path.command_z_mm,
            segments=(replace(second.path.segments[0], command_z_mm=first.path.command_z_mm),))
        self.reject(candidate_paths=(first, replace(second, path=same_z)))
        # The structural maximum, not one lower point in a ZAA loop, controls chronology.
        same_loop_z = replace(first.path, command_z_mm=0.2, segments=(replace(first.path.segments[0], command_z_mm=0.2),))
        self.reject(candidate_paths=(replace(first, path=same_loop_z), second))

    def test_anchor_interval_layer_and_chronology(self):
        anchor = self.plan.anchors[0]
        for change in ({"structural_loop_ids": ("missing",)}, {"layer_index": 2}, {"target_structural_interval_id": "foreign"}):
            self.reject(anchors=(replace(anchor, **change),))
        first, second = self.plan.candidate_paths
        for change in ({"insertion_anchor_id": "missing"}, {"surface_band_id": "missing"}, {"path": replace(first.path, interval_id="foreign")}):
            self.reject(candidate_paths=(replace(first, **change), second))
        self.reject(structural_loop_contexts=(replace(self.plan.structural_loop_contexts[0], execution_order=3),))

    def test_transitions_exact_adjacency_and_complexity(self):
        transition = self.plan.transitions[0]
        for transitions in ((), (transition, transition), (replace(transition, from_path_id="missing"),), (replace(transition, from_path_id="path-b", to_path_id="path-a"),)):
            self.reject(transitions=transitions)
        for kind, count in (("continuous", 0), ("travel", 1), ("restart", 1), ("travel-restart", 1)):
            self.assertEqual(replace(self.plan, transitions=(replace(transition, kind=kind),)).complexity_counts, (2, 2, count))

    def test_evidence_identities_and_time_availability(self):
        other = replace(self.plan.plugin_settings, digest_hex="9" * 64)
        error = replace(self.plan.directional_error.pred_to_src, estimator_policy=other)
        self.reject(directional_error=replace(self.plan.directional_error, pred_to_src=error, src_to_pred=error))
        first, second = self.plan.candidate_paths
        self.reject(candidate_paths=(replace(first, segment_support=(replace(first.segment_support[0], settings_identity=other),)), second))
        self.reject(analysis_outcome=ResearchPlanOutcomeV2(False, "phase05-analysis-only"))
        available = TimeEstimateAvailable("available", 0, "research-model", self.plan.execution_config, "evidence")
        replace(self.plan, added_time=available, analysis_outcome=ResearchPlanOutcomeV2(False, "phase05-analysis-only"))
        self.reject(added_time=replace(available, resolved_execution_config=replace(self.plan.execution_config, digest_hex="9" * 64)))

    def test_numeric_and_closed_leaf_contracts(self):
        for bad in (True, -1, float("inf"), float("nan"), 10**400):
            with self.assertRaises(ContractError):
                PlannedVolumesV2(bad, 0)
        for bad in (True, -1, float("inf"), float("nan"), 1.5):
            with self.assertRaises(ContractError):
                StructuralLoopContextV2("loop", "interval", bad, 0, 0)
        for bad in (True, float("inf"), float("nan"), 10**400):
            with self.assertRaises(ContractError):
                StructuralLoopContextV2("loop", "interval", 0, 0, bad)
        for injectable in (True, 0, None):
            with self.assertRaises(ContractError):
                ResearchPlanOutcomeV2(injectable, "infeasible")
        for ids in (("b", "a"), ("a", "a"), (" ",), []):
            with self.assertRaises(ContractError):
                SegmentSupportIntentV2(ids, self.plan.plugin_settings, None)
        with self.assertRaises(ContractError):
            replace(self.plan.candidate_paths[0], segment_support=())
        with self.assertRaises(ContractError):
            replace(self.plan.transitions[0], policy_version="other")
        with self.assertRaises(ContractError):
            replace(self.plan.geometry_regions[0], coordinate_frame="machine")

    def test_envelope_hash_shape_without_claiming_hash_verification(self):
        envelope = SubEdgePlanV2(self.plan, "a" * 64, "a" * 64)
        self.assertFalse(envelope.content.injectable)
        for digest in ("A" * 64, "a" * 63, None):
            with self.assertRaises(ContractError):
                SubEdgePlanV2(self.plan, digest, digest)
        with self.assertRaises(ContractError):
            SubEdgePlanV2(self.plan, "a" * 64, "b" * 64)

    def test_standalone_projection_remains_closed(self):
        from adaptive_subedge.application.serialization import semantic_tree
        for value in (self.plan, SubEdgePlanV2(self.plan, "a" * 64, "a" * 64),
                      self.plan.geometry_regions[0], self.plan.surface_bands[0],
                      self.plan.candidate_paths[0], self.plan.directional_error):
            with self.subTest(type=type(value).__name__), self.assertRaises(ContractError):
                semantic_tree(value)


if __name__ == "__main__":
    unittest.main()
