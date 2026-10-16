"""Closed immutable research graph; declarations never authorize physical execution."""
from dataclasses import dataclass

from .analysis_evidence import DirectionalErrorEvidence, TimeEstimateAvailable, TimeEstimateUnavailable
from .errors import ContractError, ReasonCode
from .insertion_anchor_v2 import InsertionAnchorV2
from .numeric import finite_binary64
from .plan import IdentityReference, SubEdgePath
from .structural_loop_v2 import StructuralLoopReferenceV2


def _require(valid: bool, message: str) -> None:
    if not valid:
        raise ContractError(ReasonCode.INVALID_CANONICAL_VALUE, message)


def _text(value: object) -> bool:
    return type(value) is str and bool(value.strip())


def _identity(value: object, kind: str, version: str = "1") -> None:
    _require(type(value) is IdentityReference, "exact typed identity required")
    _require((value.identity_type, value.schema_version, value.canonical_encoding_version)
             == (kind, version, "1"), "unsupported reference role/version")


def _ids(values: object) -> None:
    _require(type(values) is tuple and all(_text(x) for x in values), "immutable nonblank IDs required")
    _require(tuple(sorted(set(values))) == values, "IDs must be unique and sorted")


def _tuple(values: object, cls: type) -> None:
    _require(type(values) is tuple and all(type(x) is cls for x in values), "exact immutable nested DTOs required")


def _registry(values: tuple, key) -> dict:
    keys = tuple(key(x) for x in values)
    _require(tuple(sorted(set(keys))) == keys, "registry must be unique and canonically ordered")
    return dict(zip(keys, values))


@dataclass(frozen=True, slots=True)
class GeometryRegionReferenceV2:
    identity: IdentityReference
    source_geometry: IdentityReference
    coordinate_frame: str

    def __post_init__(self):
        _require(type(self.identity) is IdentityReference, "region identity required")
        _require(self.identity.identity_type in ("surface-boundary", "residual-error-region"), "invalid region role")
        _identity(self.identity, self.identity.identity_type)
        _identity(self.source_geometry, "source-geometry")
        _require(type(self.coordinate_frame) is str and self.coordinate_frame == "centered_printobject_mm_v1", "invalid region frame")


@dataclass(frozen=True, slots=True)
class SupportReferenceV2:
    reference_id: str
    contributor_kind: str
    contributor_id: str

    def __post_init__(self):
        _require(_text(self.reference_id) and _text(self.contributor_id), "support identifiers required")
        _require(type(self.contributor_kind) is str and self.contributor_kind in ("structural-loop", "candidate-path"), "invalid support kind")


@dataclass(frozen=True, slots=True)
class SurfaceBandV2:
    surface_band_id: str
    source_geometry: IdentityReference
    target_boundary_ref: GeometryRegionReferenceV2
    residual_error_region_ref: GeometryRegionReferenceV2
    chronological_support_reference_ids: tuple[str, ...]
    nesting_parent_band_id: str | None

    def __post_init__(self):
        _require(_text(self.surface_band_id), "band ID required")
        _identity(self.source_geometry, "source-geometry")
        for region, kind in ((self.target_boundary_ref, "surface-boundary"),
                             (self.residual_error_region_ref, "residual-error-region")):
            _require(type(region) is GeometryRegionReferenceV2, "exact band region required")
            _identity(region.identity, kind)
            _require(region.source_geometry == self.source_geometry, "band region source mismatch")
        _ids(self.chronological_support_reference_ids)
        _require(self.nesting_parent_band_id is None or _text(self.nesting_parent_band_id), "invalid band parent")


@dataclass(frozen=True, slots=True)
class StructuralLoopContextV2:
    loop_id: str
    structural_interval_id: str
    layer_index: int
    execution_order: int
    maximum_path_z_mm: float

    def __post_init__(self):
        _require(_text(self.loop_id) and _text(self.structural_interval_id), "loop context IDs required")
        _require(all(type(x) is int and x >= 0 for x in (self.layer_index, self.execution_order)), "nonnegative exact context indices required")
        _require(finite_binary64(self.maximum_path_z_mm), "finite maximum path Z required")


@dataclass(frozen=True, slots=True)
class SegmentSupportIntentV2:
    support_reference_ids: tuple[str, ...]
    settings_identity: IdentityReference
    evidence_reference: str | None

    def __post_init__(self):
        _ids(self.support_reference_ids)
        _identity(self.settings_identity, "plugin-settings", "2")
        _require(self.evidence_reference is None or _text(self.evidence_reference), "invalid support evidence reference")


@dataclass(frozen=True, slots=True)
class SubEdgePathV2:
    path: SubEdgePath
    surface_band_id: str
    insertion_anchor_id: str
    segment_support: tuple[SegmentSupportIntentV2, ...]

    def __post_init__(self):
        _require(type(self.path) is SubEdgePath, "exact base path required")
        _require(all(_text(x) for x in (self.path.path_id, self.path.interval_id, self.surface_band_id, self.insertion_anchor_id)), "nonblank path identifiers required")
        _ids(self.path.support_dependency_path_ids)
        _tuple(self.segment_support, SegmentSupportIntentV2)
        _require(len(self.segment_support) == len(self.path.segments), "one support intent per segment required")


@dataclass(frozen=True, slots=True)
class PlannedTransitionV2:
    from_path_id: str
    to_path_id: str
    kind: str
    policy_version: str

    def __post_init__(self):
        _require(_text(self.from_path_id) and _text(self.to_path_id), "transition endpoints required")
        _require(type(self.kind) is str and self.kind in ("continuous", "travel", "restart", "travel-restart"), "invalid transition kind")
        _require(type(self.policy_version) is str and self.policy_version == "declared_interpath_intent_v1", "invalid transition policy")


@dataclass(frozen=True, slots=True)
class PlannedVolumesV2:
    geometric_volume_mm3: float
    commanded_volume_mm3: float

    def __post_init__(self):
        _require(all(finite_binary64(x) and x >= 0 for x in (self.geometric_volume_mm3, self.commanded_volume_mm3)), "finite nonnegative planned volumes required")


@dataclass(frozen=True, slots=True)
class ResearchPlanOutcomeV2:
    injectable: bool
    reason: str

    def __post_init__(self):
        _require(type(self.injectable) is bool and not self.injectable, "research plans cannot authorize injection")
        _require(type(self.reason) is str and self.reason in ("phase05-analysis-only", "ranking-incomplete", "unverified-geometry", "infeasible"), "invalid research outcome")


@dataclass(frozen=True, slots=True)
class PlanSemanticContentV2:
    schema_version: str
    plugin_version: str
    compatibility_descriptor_id: str
    source_geometry: IdentityReference
    execution_config: IdentityReference
    plugin_settings: IdentityReference
    geometry_regions: tuple[GeometryRegionReferenceV2, ...]
    support_references: tuple[SupportReferenceV2, ...]
    surface_bands: tuple[SurfaceBandV2, ...]
    structural_loops: tuple[StructuralLoopReferenceV2, ...]
    structural_loop_contexts: tuple[StructuralLoopContextV2, ...]
    candidate_paths: tuple[SubEdgePathV2, ...]
    anchors: tuple[InsertionAnchorV2, ...]
    transitions: tuple[PlannedTransitionV2, ...]
    directional_error: DirectionalErrorEvidence
    added_time: TimeEstimateUnavailable | TimeEstimateAvailable
    volumes: PlannedVolumesV2
    analysis_outcome: ResearchPlanOutcomeV2

    def __post_init__(self):
        _require(type(self.schema_version) is str and self.schema_version == "2", "Plan schema 2 required")
        _require(_text(self.plugin_version) and _text(self.compatibility_descriptor_id), "plan declaration identifiers required")
        for value, kind, version in ((self.source_geometry, "source-geometry", "1"), (self.execution_config, "execution-config", "1"), (self.plugin_settings, "plugin-settings", "2")):
            _identity(value, kind, version)
        for values, cls in ((self.geometry_regions, GeometryRegionReferenceV2), (self.support_references, SupportReferenceV2), (self.surface_bands, SurfaceBandV2), (self.structural_loops, StructuralLoopReferenceV2), (self.structural_loop_contexts, StructuralLoopContextV2), (self.candidate_paths, SubEdgePathV2), (self.anchors, InsertionAnchorV2), (self.transitions, PlannedTransitionV2)):
            _tuple(values, cls)
        _require(type(self.directional_error) is DirectionalErrorEvidence and type(self.volumes) is PlannedVolumesV2 and type(self.analysis_outcome) is ResearchPlanOutcomeV2, "exact plan evidence/outcome required")
        _require(type(self.added_time) in (TimeEstimateAvailable, TimeEstimateUnavailable), "tagged time required")
        _require(self.directional_error.pred_to_src.estimator_policy == self.plugin_settings and self.directional_error.src_to_pred.estimator_policy == self.plugin_settings, "directional Settings mismatch")
        if type(self.added_time) is TimeEstimateAvailable:
            _require(self.added_time.resolved_execution_config == self.execution_config, "time execution identity mismatch")
        else:
            _require(self.analysis_outcome.reason in ("ranking-incomplete", "infeasible", "unverified-geometry"), "unavailable time cannot claim complete ranking")
        self._validate_graph()

    @property
    def injectable(self) -> bool:
        return self.analysis_outcome.injectable

    @property
    def complexity_counts(self) -> tuple[int, int, int]:
        return (len(self.candidate_paths), sum(len(p.path.segments) for p in self.candidate_paths),
                sum(t.kind != "continuous" for t in self.transitions))

    def _validate_graph(self) -> None:
        regions = _registry(self.geometry_regions, lambda r: (r.identity.identity_type, r.identity.digest_hex))
        supports = _registry(self.support_references, lambda s: s.reference_id)
        bands = _registry(self.surface_bands, lambda b: b.surface_band_id)
        loops = _registry(self.structural_loops, lambda l: l.loop_id)
        contexts = _registry(self.structural_loop_contexts, lambda c: c.loop_id)
        anchors = _registry(self.anchors, lambda a: a.anchor_id)
        _registry(self.candidate_paths, lambda p: p.path.execution_order)
        paths = {p.path.path_id: p for p in self.candidate_paths}
        _require(len(paths) == len(self.candidate_paths), "duplicate candidate path ID")
        _require(loops.keys() == contexts.keys(), "loop contexts must cover loops exactly")
        events = [c.execution_order for c in contexts.values()] + [p.path.execution_order for p in paths.values()]
        _require(len(events) == len(set(events)), "global event orders must be unique")
        for region in regions.values():
            _require(region.source_geometry == self.source_geometry, "foreign region source")
        for band in bands.values():
            _require(band.source_geometry == self.source_geometry, "foreign band source")
            for region in (band.target_boundary_ref, band.residual_error_region_ref):
                _require(regions.get((region.identity.identity_type, region.identity.digest_hex)) == region, "unregistered band region")
            _require(set(band.chronological_support_reference_ids) <= supports.keys(), "unknown band support")
            seen = {band.surface_band_id}
            parent = band.nesting_parent_band_id
            while parent is not None:
                _require(parent in bands and parent not in seen, "unknown/cyclic band parent")
                seen.add(parent)
                parent = bands[parent].nesting_parent_band_id
        for loop_id, context in contexts.items():
            _require(float(context.maximum_path_z_mm) == max(float(p.z_mm) for p in loops[loop_id].points), "loop maximum path Z mismatch")
        for support in supports.values():
            registry = contexts if support.contributor_kind == "structural-loop" else paths
            _require(support.contributor_id in registry, "unknown support contributor")
        for anchor in anchors.values():
            for loop_id in anchor.structural_loop_ids:
                _require(loop_id in contexts, "unknown anchor loop")
                context = contexts[loop_id]
                _require(context.structural_interval_id == anchor.target_structural_interval_id and context.layer_index == anchor.layer_index, "anchor context mismatch")
        for candidate in paths.values():
            path = candidate.path
            _require(candidate.surface_band_id in bands and candidate.insertion_anchor_id in anchors, "unknown candidate band/anchor")
            anchor = anchors[candidate.insertion_anchor_id]
            _require(path.interval_id == anchor.target_structural_interval_id, "candidate anchor interval mismatch")
            _require(all(contexts[i].execution_order < path.execution_order for i in anchor.structural_loop_ids), "anchor loop must precede candidate")
            support_ids = set(bands[candidate.surface_band_id].chronological_support_reference_ids)
            for intent in candidate.segment_support:
                _require(intent.settings_identity == self.plugin_settings, "support Settings mismatch")
                _require(set(intent.support_reference_ids) <= supports.keys(), "unknown segment support")
                support_ids.update(intent.support_reference_ids)
            dependencies = set()
            for support_id in support_ids:
                support = supports[support_id]
                if support.contributor_kind == "structural-loop":
                    contributor = contexts[support.contributor_id]
                    order, height = contributor.execution_order, contributor.maximum_path_z_mm
                else:
                    contributor = paths[support.contributor_id].path
                    order, height = contributor.execution_order, contributor.command_z_mm
                    dependencies.add(contributor.path_id)
                _require(order < path.execution_order and float(height) < float(path.command_z_mm), "support must precede candidate at strictly lower Z")
            _require(dependencies == set(path.support_dependency_path_ids), "candidate support dependency mismatch")
        expected_pairs = tuple((left.path.path_id, right.path.path_id) for left, right in zip(self.candidate_paths, self.candidate_paths[1:]))
        _require(tuple((t.from_path_id, t.to_path_id) for t in self.transitions) == expected_pairs, "transitions must exactly cover adjacent candidates")


@dataclass(frozen=True, slots=True)
class SubEdgePlanV2:
    content: PlanSemanticContentV2
    plan_hash: str
    plan_id: str

    def __post_init__(self):
        _require(type(self.content) is PlanSemanticContentV2, "exact Plan v2 content required")
        _require(type(self.plan_hash) is str and type(self.plan_id) is str and self.plan_id == self.plan_hash
                 and len(self.plan_hash) == 64 and all(c in "0123456789abcdef" for c in self.plan_hash), "matching full lowercase Plan hashes required")
