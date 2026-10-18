"""Explicit causal support graph and private local-plane numeric adapters."""
from dataclasses import dataclass, field, replace
from fractions import Fraction as F
import re

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from orca_plugin.gcode.linear_trace import trace_linear_execution
from tools.audit_continuous_path_contact import (
    ContactPath, ContactPolicy, ContactReport, ChronologicalSource, audit_continuous_path_contact,
)
from tools.conditional_nominal_body import fingerprint
from tools.freeze_supplemental_emission import FrozenSupplementalEmission, freeze_numeric_emission, emission_policy_identity
from tools.supplemental_z_hop import SupplementalPath, compose_retracted_cycle


@dataclass(frozen=True)
class SupportedPathIntent:
    path_id: str
    source_context_identity: str
    original_source_floor_z_mm: F
    original_next_layer_z_mm: F
    support_plane_z_mm: F
    width_mm: F
    physical_height_mm: F
    remaining_height_mm: F
    points_mm: tuple[tuple[F, F, F], ...]
    parent_path_id: str | None


@dataclass(frozen=True)
class TwoTierGraphPolicy:
    max_paths: int
    max_coordinate_bits: int
    max_contact_queries: int
    contact: ContactPolicy

    def __post_init__(self):
        if (any(type(n) is not int or n < 1 for n in
                (self.max_paths, self.max_coordinate_bits, self.max_contact_queries)) or type(self.contact) is not ContactPolicy):
            raise ValueError('explicit exact graph/contact limits required')


@dataclass(frozen=True)
class SupportedFrozenPath:
    intent: SupportedPathIntent
    local_support_numeric_adapter: FrozenSupplementalEmission
    parent_frozen_identity: str | None


@dataclass(frozen=True)
class ImmediateSupportSlab:
    parent_path_id: str
    child_path_id: str
    parent_frozen_identity: str
    child_frozen_identity: str
    bottom_z_mm: F
    top_z_mm: F
    depth_mm: F
    child_height_fraction: F
    centerline_contact: ContactReport


@dataclass(frozen=True)
class FrozenTwoTierPlan:
    source_context_identity: str
    original_source_floor_z_mm: F
    original_next_layer_z_mm: F
    emission_policy_identity: str
    graph_policy: TwoTierGraphPolicy
    paths: tuple[SupportedFrozenPath, ...]
    execution_order: tuple[str, ...]
    immediate_support_slabs: tuple[ImmediateSupportSlab, ...]
    schema: str = field(default='explicit-two-tier-supported-intents-v1', init=False)
    physical_authority: bool = field(default=False, init=False)


def supported_bead(path):
    """Actual quantized straight bead; never labeled original structural source."""
    if type(path) is not SupportedFrozenPath:
        raise ValueError('exact frozen supported path required')
    numeric = path.local_support_numeric_adapter
    return ExactNominalTopSegment(path.intent.path_id, *numeric.path.points_mm,
        F(str(numeric.physical_width_mm[0])), numeric.path.height_mm, 'candidate')


def _checkpoint(cancelled):
    answer = cancelled()
    if type(answer) is not bool or answer:
        raise ValueError('supported graph cancelled or invalid cancellation result')


def freeze_supported_graph(intents, *, source_context_identity, policy, graph_policy, cancelled):
    """Only one-parent straight parallel tier2 paths; original floor stays explicit."""
    if (type(source_context_identity) is not str or re.fullmatch('[0-9a-f]{64}', source_context_identity) is None
            or type(graph_policy) is not TwoTierGraphPolicy or type(intents) is not tuple
            or not 0 < len(intents) <= graph_policy.max_paths or not callable(cancelled)
            or any(type(p) is not SupportedPathIntent for p in intents)):
        raise ValueError('exact pinned bounded supported intents required')
    _checkpoint(cancelled)
    policy_identity = emission_policy_identity(policy)
    original_floor, original_next = intents[0].original_source_floor_z_mm, intents[0].original_next_layer_z_mm
    by_id = {}
    for intent in intents:
        _checkpoint(cancelled)
        if (type(intent.path_id) is not str or re.fullmatch('[A-Za-z0-9_-]+', intent.path_id) is None
                or intent.path_id in by_id or type(intent.source_context_identity) is not str
                or intent.source_context_identity != source_context_identity
                or type(intent.points_mm) is not tuple or len(intent.points_mm) != 2
                or intent.parent_path_id is not None and type(intent.parent_path_id) is not str):
            raise ValueError('unique same-context straight path and parent identities required')
        numbers = (intent.original_source_floor_z_mm, intent.original_next_layer_z_mm, intent.support_plane_z_mm,
                   intent.width_mm, intent.physical_height_mm, intent.remaining_height_mm)
        if any(type(point) is not tuple or len(point) != 3 for point in intent.points_mm):
            raise ValueError('exact immutable XYZ points required')
        for number in (*numbers, *intent.points_mm[0], *intent.points_mm[1]):
            if type(number) is not F or max(number.numerator.bit_length(), number.denominator.bit_length()) > graph_policy.max_coordinate_bits:
                raise ValueError('exact graph coordinate bit budget exceeded')
        if ((intent.original_source_floor_z_mm, intent.original_next_layer_z_mm) != (original_floor, original_next)
                or not 0 <= original_floor < original_next
                or intent.support_plane_z_mm < original_floor
                or any(point[2] != intent.support_plane_z_mm+intent.remaining_height_mm for point in intent.points_mm)
                or not intent.points_mm[0][2] < original_next):
            raise ValueError('original interval/support/top must be explicit and strictly below next layer')
        if intent.parent_path_id is None and intent.support_plane_z_mm != original_floor:
            raise ValueError('tier1 support plane must be actual original floor')
        by_id[intent.path_id] = intent
    for intent in intents:
        if intent.parent_path_id is not None:
            parent = by_id.get(intent.parent_path_id)
            if parent is None or parent.parent_path_id is not None or parent is intent:
                raise ValueError('missing/cyclic/third-tier parent is unsupported')
            if intent.support_plane_z_mm != parent.points_mm[0][2] or intent.points_mm[0][2] <= parent.points_mm[0][2]:
                raise ValueError('parent top/support plane and strictly increasing world top required')
    completed, order, slabs, queries = {}, [], [], 0
    while len(completed) < len(intents):
        _checkpoint(cancelled)
        ready = [p for p in intents if p.path_id not in completed and
                 (p.parent_path_id is None or p.parent_path_id in completed)]
        if not ready:
            raise ValueError('causal graph has no ready node')
        intent = min(ready, key=lambda p: (p.points_mm[0][2], p.physical_height_mm, p.path_id))
        # This private adapter's floor is explicitly LOCAL support, never an
        # original-floor association. The public intent retains both meanings.
        adapter = SupplementalPath(intent.path_id, intent.support_plane_z_mm, intent.width_mm,
                                   intent.physical_height_mm, intent.points_mm)
        numeric = freeze_numeric_emission(adapter, policy)
        if numeric.path.points_mm[0][2] >= original_next:
            raise ValueError('quantized top reaches original next layer')
        parent = completed.get(intent.parent_path_id)
        frozen = SupportedFrozenPath(intent, numeric, fingerprint(parent) if parent else None)
        if parent is not None:
            a, b = supported_bead(parent), supported_bead(frozen)
            dx, dy = a.end_xyz_mm[0]-a.start_xyz_mm[0], a.end_xyz_mm[1]-a.start_xyz_mm[1]
            ex, ey = b.end_xyz_mm[0]-b.start_xyz_mm[0], b.end_xyz_mm[1]-b.start_xyz_mm[1]
            squared = dx*dx+dy*dy
            if dx*ey-dy*ex != 0:
                raise ValueError('only parallel straight immediate support is supported')
            half_difference = (a.width_mm-b.width_mm)/2
            for point in (b.start_xyz_mm, b.end_xyz_mm):
                px, py = point[0]-a.start_xyz_mm[0], point[1]-a.start_xyz_mm[1]
                if not 0 <= px*dx+py*dy <= squared or half_difference < 0 or (dx*py-dy*px)**2 > half_difference**2*squared:
                    raise ValueError('actual E-implied child rectangle is not contained in parent interval/span')
            contact = audit_continuous_path_contact(ContactPath(b.segment_id, 1,
                (b.start_xyz_mm[:2], b.end_xyz_mm[:2]), b.start_xyz_mm[2]-b.height_mm),
                (ChronologicalSource(a, 0),), policy=replace(graph_policy.contact,
                    max_queries=min(graph_policy.contact.max_queries, graph_policy.max_contact_queries-queries)), cancelled=cancelled)
            queries += contact.query_count
            if queries > graph_policy.max_contact_queries or not contact.nominal_centerline_contact_proven:
                raise ValueError('upper parent contact not proven within graph query budget')
            bottom, parent_top = b.start_xyz_mm[2]-b.height_mm, a.start_xyz_mm[2]
            depth = parent_top-bottom
            if not 0 <= depth <= b.height_mm*F('.3'):
                raise ValueError('immediate-support intersection slab exceeds0..30 percent')
            slabs.append(ImmediateSupportSlab(a.segment_id, b.segment_id, fingerprint(parent), fingerprint(frozen),
                bottom, parent_top, depth, depth/b.height_mm, contact))
        completed[intent.path_id] = frozen
        order.append(intent.path_id)
    return FrozenTwoTierPlan(source_context_identity, original_floor, original_next, policy_identity, graph_policy,
        tuple(completed[name] for name in sorted(completed)), tuple(order), tuple(slabs))


def _supported_cycle_blocks(anchor, plan, policy, *, cancelled):
    """Execute graph order through existing one-path cycles, restoring each time."""
    if type(plan) is not FrozenTwoTierPlan:
        raise ValueError('exact supported frozen plan required')
    rebuilt = freeze_supported_graph(tuple(p.intent for p in plan.paths), source_context_identity=plan.source_context_identity,
        policy=policy, graph_policy=plan.graph_policy, cancelled=cancelled)
    if rebuilt != plan:
        raise ValueError('stale/forged supported plan or parent frozen identities')
    by_id = {p.intent.path_id: p for p in plan.paths}
    blocks = []
    for name in plan.execution_order:
        _checkpoint(cancelled)
        path = by_id[name]
        block = compose_retracted_cycle(anchor, (path.local_support_numeric_adapter.path,), plan.original_next_layer_z_mm, policy)
        replay = trace_linear_execution(block, initial_state=anchor)
        if replay.failure is not None or replay.final_state != anchor:
            raise ValueError('supported path cycle failed exact original-anchor restoration')
        expected = tuple(zip(path.local_support_numeric_adapter.relative_e_mm, path.local_support_numeric_adapter.feed_mm_min))
        actual = tuple(
            (e.extruded_filament_mm, e.after.feed_mm_min) for e in replay.records
            if e.extruded_filament_mm and e.before.xyz_mm[:2] != e.after.xyz_mm[:2])
        if actual != expected:
            raise ValueError('supported emitted E/F differs from numeric freeze')
        blocks.append(block)
    return tuple(blocks)


def compose_supported_cycle(anchor, plan, policy, *, cancelled):
    return b''.join(_supported_cycle_blocks(anchor, plan, policy, cancelled=cancelled))
