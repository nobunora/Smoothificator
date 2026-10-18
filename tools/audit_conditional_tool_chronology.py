"""Causal new-interaction audit for an explicitly assumed zero-height planar tip."""
from dataclasses import asdict, dataclass, field
from fractions import Fraction as F
from hashlib import sha256
import json

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from adaptive_subedge.engine.support_cell import _sqrt_bounds
from orca_plugin.gcode.linear_trace import _words, trace_linear_execution
from tools.audit_provisional_tip_sweep import PlanarTipSweepPolicy, _closest_xy_parameters, audit_provisional_tip_sweep
from tools.audit_nominal_bead_overlap import _envelope
from tools.compile_conditional_job import CompiledConditionalJob
from tools.conditional_nominal_body import fingerprint, interpret_nominal_body
from tools.conditional_nominal_copy import compose_conditional_nominal_copy
from tools.conditional_nominal_model import ConditionalNominalModel, extract_conditional_nominal_model
from tools.provisional_tool_geometry import ProvisionalPlanarTip, swept_planar_disc_bounds


@dataclass(frozen=True)
class NominalTipContactPolicy:
    own_prior_top_pairs: tuple[tuple[str, int, int], ...]
    path_end_top_pairs: tuple[tuple[str, int], ...]
    source_anchor_top_pairs: tuple[tuple[int, str], ...]
    allow_current_deposition_top_superset: bool


@dataclass(frozen=True)
class ToolChronologyPolicy:
    max_motions: int
    max_materials: int
    max_pairs: int
    max_near_pairs: int
    max_total_axis_queries: int
    max_total_point_queries: int
    pair: PlanarTipSweepPolicy

    def __post_init__(self):
        if (any(type(v) is not int or v < 1 for v in (self.max_motions, self.max_materials, self.max_pairs,
                self.max_near_pairs, self.max_total_axis_queries, self.max_total_point_queries))
                or type(self.pair) is not PlanarTipSweepPolicy):
            raise ValueError('explicit exact chronological resource limits required')


@dataclass(frozen=True)
class ChronologicalTipAxisProposal:
    start_xyz_mm: tuple[F, F, F]
    end_xyz_mm: tuple[F, F, F]
    material_id: str
    axis: tuple[F, F, F]


@dataclass(frozen=True)
class ChronologicalTipPairProof:
    motion_id: str
    material_id: str
    relation: str
    state: str
    reason: str
    axis: tuple[F, F, F] | None
    margin: F | None
    witness_xyz_mm: tuple[F, F, F] | None


@dataclass(frozen=True)
class OpaqueExecutionObligation:
    scope: str
    byte_start: int
    byte_end: int
    sha256: str


@dataclass(frozen=True)
class ConditionalToolChronologyReport:
    source_sha256: str
    output_sha256: str
    model_identity: str
    geometry_identity: str
    contact_policy_identity: str
    axis_proposals_identity: str
    policy: ToolChronologyPolicy
    state: str
    reason: str
    motions_audited: int
    causal_pair_count: int
    strict_box_pairs: int
    strict_projection_pairs: int
    allowed_boundary_pairs: int
    forming_prefix_top_certificates: int
    axis_queries: int
    point_queries: int
    proofs: tuple[ChronologicalTipPairProof, ...]
    issues: tuple[ChronologicalTipPairProof, ...]
    unmodeled_stationary_deposition_lines: tuple[int, ...]
    moving_material_interactions_complete: bool
    unresolved_or_unchecked_pairs: int
    body_moving_material_interactions_complete: bool
    whole_original_job_interactions_complete: bool
    opaque_execution_obligations: tuple[OpaqueExecutionObligation, ...]
    physical_authority: bool = field(default=False, init=False)


def _top_proposals(start, end, material, sqrt_bits):
    """Propose rational flat-top points; only the public kernel can certify them."""
    t, _, _ = _closest_xy_parameters(start[:2], end[:2], material.start_xyz_mm[:2], material.end_xyz_mm[:2])
    tips = (start, end, tuple(a+t*(b-a) for a, b in zip(start, end)))
    a, b = material.start_xyz_mm, material.end_xyz_mm
    dx, dy = b[0]-a[0], b[1]-a[1]
    squared_length = dx*dx+dy*dy
    length_upper = _sqrt_bounds(squared_length, sqrt_bits)[1]
    limit = (material.width_mm-material.height_mm)/2/length_upper
    candidates = []
    for tip in tips:
        u = max(F(0), min(F(1), ((tip[0]-a[0])*dx+(tip[1]-a[1])*dy)/squared_length))
        q = (a[0]+u*dx, a[1]+u*dy)
        beta = ((tip[0]-q[0])*(-dy)+(tip[1]-q[1])*dx)/squared_length
        k = max(-limit, min(limit, beta))
        candidates.extend(((q[0], q[1], a[2]), (q[0]-k*dy, q[1]+k*dx, a[2])))
    return tuple(dict.fromkeys(candidates))


def audit_conditional_tool_chronology(*, inputs, model, job, geometry, contact_policy, policy, cancelled, axis_proposals=()):
    """Audit all inserted motions/prior material and original motions/new material.

    Unchanged original-tool/original-material behavior is a declared baseline
    premise. Each own/junction/trail contact is checked, never blanket excluded.
    Current forming material is only a labeled full-bead superset certificate;
    it joins chronological material after its extrusion command completes.
    """
    if (type(geometry) is not ProvisionalPlanarTip or type(contact_policy) is not NominalTipContactPolicy
            or type(policy) is not ToolChronologyPolicy or not callable(cancelled)
            or type(contact_policy.allow_current_deposition_top_superset) is not bool
            or type(model) is not ConditionalNominalModel or type(job) is not CompiledConditionalJob
            or type(inputs) is not tuple or len(inputs) != 6):
        raise ValueError('exact provisional tip/contact/resource policies required')
    trace = interpret_nominal_body(*inputs)
    source, _, _, descriptor, _, _ = inputs
    if type(axis_proposals) is not tuple or len(axis_proposals) > policy.max_near_pairs:
        raise ValueError('bounded immutable chronological axis proposals required')
    axes_by_pair = {}
    for proposal in axis_proposals:
        if (type(proposal) is not ChronologicalTipAxisProposal or type(proposal.material_id) is not str
                or any(type(v) is not tuple or len(v) != 3 or any(type(c) is not F for c in v)
                       for v in (proposal.start_xyz_mm, proposal.end_xyz_mm, proposal.axis))):
            raise ValueError('exact geometry-associated chronological axis proposal required')
        axes_by_pair.setdefault((proposal.start_xyz_mm, proposal.end_xyz_mm, proposal.material_id), []).append(proposal.axis)
    # Source authentication is independently bounded by model.policy; cancellation
    # is polled immediately afterward and throughout the chronological audit.
    if extract_conditional_nominal_model(inputs, model.premise, policy=model.policy, cancelled=lambda: False) != model:
        raise ValueError('stale/forged chronological model')
    if compose_conditional_nominal_copy(*inputs, tuple(g.insertion for g in job.groups)) != job.copy:
        raise ValueError('chronological copy does not reconstruct from actual inputs')
    by_path = {p.emitted_path_id: p.frozen_emission for g in job.groups for p in g.paths}
    if (len(by_path) != sum(len(g.paths) for g in job.groups)
            or any(tuple(p.frozen_emission for p in g.paths) != tuple(p.frozen_emission for p in g.insertion.paths)
                   or any(p.emitted_path_id != p.frozen_emission.path.path_id for p in g.paths) for g in job.groups)):
        raise ValueError('chronological compiled paths differ from source-rebuilt insertion emissions')
    source_spans = {s.line_number: s for s in model.spans}
    stationary = tuple(e.line_number for e in trace.events if e.command in ('G0', 'G1')
        and e.deposited_filament_mm is not None and e.deposited_filament_mm > 0
        and e.before.xyz_mm[:2] == e.after.xyz_mm[:2])
    event_offsets = {e.line_number: e.byte_offset for e in trace.events}
    own, endpoints, anchors = set(), set(), set()
    for collection, length in ((contact_policy.own_prior_top_pairs, 3), (contact_policy.path_end_top_pairs, 2), (contact_policy.source_anchor_top_pairs, 2)):
        if (type(collection) is not tuple or any(type(entry) is not tuple or len(entry) != length for entry in collection)
                or any(any(type(v) not in (str, int) for v in entry) for entry in collection)
                or len(collection) != len(set(collection))):
            raise ValueError('unique immutable explicit top-contact permissions required')
    if sum(len(c) for c in (contact_policy.own_prior_top_pairs, contact_policy.path_end_top_pairs, contact_policy.source_anchor_top_pairs)) > policy.max_near_pairs:
        raise ValueError('explicit contact permission input budget')
    for path_id, current, prior in contact_policy.own_prior_top_pairs:
        if type(path_id) is not str or path_id not in by_path or type(current) is not int or type(prior) is not int or not 0 <= prior < current < len(by_path[path_id].relative_e_mm):
            raise ValueError('own-top permission does not identify a real causal prior pair')
        own.add((path_id, current, prior))
    for path_id, prior in contact_policy.path_end_top_pairs:
        if type(path_id) is not str or path_id not in by_path or type(prior) is not int or not 0 <= prior < len(by_path[path_id].relative_e_mm):
            raise ValueError('endpoint permission does not identify actual earlier material')
        endpoints.add((path_id, prior))
    group_by_offset = {g.insertion.anchor.byte_offset: g for g in job.groups}
    for offset, source_id in contact_policy.source_anchor_top_pairs:
        if (type(offset) is not int or offset not in group_by_offset or type(source_id) is not str
                or not source_id.isascii() or not source_id.isdecimal() or source_id != str(int(source_id))):
            raise ValueError('anchor permission requires an actual insertion/source identity')
        span = source_spans.get(int(source_id))
        anchor = group_by_offset[offset].insertion.anchor
        if (span is None or span.support_geometry is None or event_offsets[span.line_number] >= offset
                or span.support_geometry.start_xyz_mm[2] != anchor.saved_state.xyz_mm[2]
                or span.support_geometry.end_xyz_mm[2] != anchor.saved_state.xyz_mm[2]):
            raise ValueError('anchor permission material is not actual earlier constant-top source')
        anchors.add((offset, source_id))
    motions = pairs = boxes = projections = boundaries = prefixes = axis_queries = point_queries = near = 0
    proofs, issues = [], []
    original_batches, candidate_batches = {}, {}
    material_count = 0

    def report(state, reason, moving_complete=False):
        # The legacy moving_material_interactions_complete field is body-only.
        # Neither startup material nor downstream opaque execution is certified.
        opaque = tuple(OpaqueExecutionObligation(scope, start, end, sha256(source[start:end]).hexdigest())
            for scope, start, end in (('opaque-prefix', 0, descriptor.body_start_offset),
                                     ('opaque-suffix', descriptor.body_end_offset, len(source))) if start < end)
        if moving_complete and opaque:
            state = 'incomplete'
            reason = 'opaque-execution-outside-body; '+reason
        return ConditionalToolChronologyReport(model.source_sha256, job.copy.output_sha256, fingerprint(model),
            geometry.identity, fingerprint(contact_policy), sha256(json.dumps([asdict(a) for a in axis_proposals],
                sort_keys=True, separators=(',', ':'), default=str).encode('ascii')).hexdigest(), policy, state, reason, motions, pairs, boxes,
            projections, boundaries, prefixes, axis_queries, point_queries, tuple(proofs), tuple(issues), stationary, moving_complete,
            pairs-boxes-projections-boundaries, moving_complete, moving_complete and not stationary and not opaque, opaque)

    def checkpoint():
        answer = cancelled()
        if type(answer) is not bool:
            raise ValueError('exact bool chronology cancellation required')
        return answer

    def add_material(batches, segment, path_id=None, index=None):
        nonlocal material_count
        material_count += 1
        if material_count > policy.max_materials:
            return False
        top = max(segment.start_xyz_mm[2], segment.end_xyz_mm[2])
        batches.setdefault(top, []).append((segment, path_id, index))
        return True

    def audit_motion(motion_id, start, end, kind, offset=None, path_id=None, index=None):
        nonlocal motions, pairs, boxes, projections, boundaries, axis_queries, point_queries, near
        if checkpoint():
            return 'cancelled'
        motions += 1
        if motions > policy.max_motions:
            return 'motion-limit'
        swept = swept_planar_disc_bounds(start, end, geometry)
        batches = tuple(candidate_batches.items())
        if kind != 'original':
            batches += tuple(original_batches.items())
        for top, batch in batches:
            if pairs+len(batch) > policy.max_pairs:
                return 'causal-pair-limit'
            pairs += len(batch)
            if min(start[2], end[2]) > top:
                boxes += len(batch)
                continue
            for material, material_path, prior in batch:
                if checkpoint():
                    return 'cancelled'
                if any(swept.upper_xyz_mm[i] < interval[0] or interval[1] < swept.lower_xyz_mm[i]
                       for i, interval in enumerate(_envelope(material))):
                    boxes += 1
                    continue
                result = audit_provisional_tip_sweep(start, end, geometry, material, policy=policy.pair,
                    cancelled=cancelled, proposed_top_witnesses=_top_proposals(start, end, material, policy.pair.sqrt_fraction_bits),
                    proposed_axes=tuple(axes_by_pair.get((start, end, material.segment_id), ())))
                axis_queries += result.axis_queries
                point_queries += result.point_queries
                if axis_queries > policy.max_total_axis_queries or point_queries > policy.max_total_point_queries:
                    return 'total-query-limit'
                if result.state == 'strictly-separated' and result.reason == 'conservative-full-sweep-box':
                    boxes += 1
                    continue
                near += 1
                if near > policy.max_near_pairs:
                    return 'near-pair-limit'
                relation = 'unrelated'
                allowed = False
                if kind == 'candidate-extrusion' and material_path == path_id and prior < index:
                    relation = 'own-adjacent-top' if prior == index-1 else 'own-local-trail-or-seam-top'
                    allowed = (path_id, index, prior) in own
                elif kind != 'original' and material_path is not None:
                    endpoint = by_path[material_path].path.points_mm[-1]
                    if (start[:2] == end[:2] == endpoint[:2] and min(start[2], end[2]) == endpoint[2]
                            and material.start_xyz_mm[2] == material.end_xyz_mm[2] == endpoint[2]):
                        relation = 'declared-path-end-lift-disc-top'
                        allowed = (material_path, prior) in endpoints
                elif kind != 'original' and material_path is None and offset in group_by_offset:
                    saved = group_by_offset[offset].insertion.anchor.saved_state.xyz_mm
                    if start[:2] == end[:2] == saved[:2] and min(start[2], end[2]) == saved[2]:
                        relation = 'declared-source-anchor-endpoint-disc-top'
                        allowed = (offset, material.segment_id) in anchors
                proof = ChronologicalTipPairProof(motion_id, material.segment_id, relation, result.state,
                    result.reason, result.separating_axis, result.strict_margin, result.boundary_or_penetration_witness_xyz_mm)
                proofs.append(proof)
                if result.state == 'strictly-separated':
                    projections += 1
                elif result.state == 'boundary-contact' and allowed:
                    boundaries += 1
                else:
                    issues.append(proof)
                    return 'forbidden-boundary-contact' if result.state == 'boundary-contact' else result.state
        return None

    def insert_group(group, span):
        nonlocal prefixes
        block = job.copy.output_bytes[span.output_start:span.output_end]
        anchor = group.insertion.anchor
        replay = trace_linear_execution(block, initial_state=anchor.saved_state)
        if replay.failure is not None or replay.final_state != anchor.saved_state:
            raise ValueError('chronological cycle replay does not restore actual nominal state')
        emission = [(p.frozen_emission, i) for p in sorted(group.paths,
            key=lambda p: (p.frozen_emission.path.height_mm, p.emitted_path_id)) for i in range(len(p.frozen_emission.relative_e_mm))]
        cursor, ordinal = 0, 0
        for command in replay.records:
            opcode, words = _words(command.raw.decode('ascii').strip())
            if opcode not in ('G0', 'G1'):
                continue
            ordinal += 1
            start, end = command.before.xyz_mm, command.after.xyz_mm
            depositing = words.get('E', F(0)) > 0 and start[:2] != end[:2]
            frozen, index = emission[cursor] if depositing else (None, None)
            path_id = frozen.path.path_id if depositing else None
            if depositing:
                if (start != frozen.path.points_mm[index] or end != frozen.path.points_mm[index+1]
                        or words['E'] != frozen.relative_e_mm[index]):
                    raise ValueError('tool command/frozen candidate geometry association mismatch')
                if not contact_policy.allow_current_deposition_top_superset:
                    return 'current-deposition-top-premise-not-declared'
                prefixes += 1
            failure = audit_motion(f'supplemental:{anchor.byte_offset}:{ordinal}', start, end,
                'candidate-extrusion' if depositing else 'supplemental-travel', anchor.byte_offset, path_id, index)
            if failure:
                return failure
            if depositing:
                material = ExactNominalTopSegment(f'{path_id}:{index}', start, end,
                    F(str(frozen.physical_width_mm[index])), frozen.path.height_mm, 'candidate')
                if not add_material(candidate_batches, material, path_id, index):
                    return 'material-limit'
                cursor += 1
        if cursor != len(emission):
            raise ValueError('incomplete candidate causal deposition coverage')
        return None

    spans_by_offset = {s.source_byte_offset: s for s in job.copy.insertion_spans}
    inserted = set()
    for event in trace.events:
        if checkpoint():
            return report('incomplete', 'cancelled')
        if event.byte_offset in group_by_offset:
            group = group_by_offset[event.byte_offset]
            failure = insert_group(group, spans_by_offset[event.byte_offset])
            inserted.add(event.byte_offset)
            if failure:
                return report('incomplete', failure)
        if event.command in ('G0', 'G1') and candidate_batches:
            if any(type(v) is not F for v in (*event.before.xyz_mm, *event.after.xyz_mm)):
                return report('incomplete', 'unknown-original-motion-position')
            failure = audit_motion(f'original:{event.line_number}', event.before.xyz_mm, event.after.xyz_mm, 'original')
            if failure:
                return report('incomplete', failure)
        span = source_spans.get(event.line_number)
        if span is not None and span.support_geometry is not None:
            if not add_material(original_batches, span.support_geometry):
                return report('incomplete', 'material-limit')
    if inserted != set(group_by_offset):
        return report('incomplete', 'unvisited-source-insertion-boundary')
    if stationary:
        return report('incomplete', 'unmodeled-stationary-deposition; moving-material-new-interactions-complete', True)
    return report('complete', 'body-moving-material-new-interactions-separated-or-declared-exact-top-contact', True)
