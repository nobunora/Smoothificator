"""Distinct conditional copy flow; these anchors are never production tokens."""
from dataclasses import dataclass, field, replace
from fractions import Fraction as F
from hashlib import sha256
import os
from pathlib import Path
import tempfile

from orca_plugin.gcode.linear_trace import MachineState, _words, trace_linear_execution
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.conditional_nominal_body import (
    ObjectExecutionScope, fingerprint, interpret_nominal_body,
)
from tools.freeze_supplemental_emission import FrozenSupplementalEmission, freeze_numeric_emission
from tools.conditional_preview_annotations import ConditionalPreviewAnnotationPolicy, annotate_conditional_cycle
from tools.supplemental_z_hop import HopPolicy, _validate_policy, compose_retracted_cycle, policy_from_slice


@dataclass(frozen=True)
class DerivedPathAssociation:
    original_recipe_sha256: str
    original_input_sha256: tuple[str, ...]
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    profile_identity: str
    nominal_context_identity: str
    frozen_emission_identity: str
    geometry_evidence_sha256: str
    matched_source_lines: tuple[int, ...]
    matched_geometry_feed_identity: str
    speed_cap_source_lines: tuple[int, ...]
    speed_cap_geometry_feed_identity: str
    minimum_source_feed_mm_min: F
    source_speed_cap_mm_s: F
    object_token: str
    status: str = field(default='conditional-input-association-only', init=False)


def _context_identity(trace):
    return sha256((trace.descriptor_identity+trace.entry_identity+trace.motion_identity).encode('ascii')).hexdigest()


def associate_derived_path(trace, descriptor, frozen_emission, *, original_recipe, original_inputs,
                           geometry_evidence, matched_source_lines):
    """Rebind recipe input to this trace; no old acceptance or chronology transfer."""
    if type(frozen_emission) is not FrozenSupplementalEmission:
        raise ValueError('exact immutable frozen numeric intent required')
    if (type(original_recipe) is not bytes or not original_recipe or type(geometry_evidence) is not bytes
            or not geometry_evidence or type(original_inputs) is not tuple or not original_inputs
            or any(type(content) is not bytes for content in original_inputs)):
        raise ValueError('actual recipe/original inputs and geometry comparison evidence bytes required')
    if (type(matched_source_lines) is not tuple or not matched_source_lines
            or any(type(line) is not int or line < 1 for line in matched_source_lines)
            or tuple(sorted(set(matched_source_lines))) != matched_source_lines):
        raise ValueError('unique ordered actual source material line witnesses required')
    if trace.descriptor_identity != fingerprint(descriptor):
        raise ValueError('trace/producer descriptor mismatch')
    by_line = {event.line_number: event for event in trace.events}
    matched = []
    for line in matched_source_lines:
        event = by_line.get(line)
        if (event is None or event.command not in ('G0', 'G1') or event.feature != 'Outer wall'
                or event.deposited_filament_mm is None or event.deposited_filament_mm <= 0
                or event.before.xyz_mm[:2] == event.after.xyz_mm[:2]
                or event.before.xyz_mm[2] != frozen_emission.path.floor_z_mm
                or event.after.xyz_mm[2] != frozen_emission.path.floor_z_mm
                or event.after.feed_mm_min is None or event.scope_after is None
                or event.scope_after.object_token != descriptor.expected_object_token):
            raise ValueError('matched witness is not conditional scoped positive-E external-wall geometry')
        matched.append(event)
    floor = frozen_emission.path.floor_z_mm
    cap_events = tuple(event for event in trace.events if event.command in ('G0', 'G1') and event.feature == 'Outer wall'
        and event.deposited_filament_mm is not None and event.deposited_filament_mm > 0
        and event.before.xyz_mm[:2] != event.after.xyz_mm[:2]
        and event.before.xyz_mm[2] == floor and event.after.xyz_mm[2] == floor
        and event.scope_after is not None and event.scope_after.object_token == descriptor.expected_object_token)
    minimum_feed = min(event.after.feed_mm_min for event in cap_events)
    # Include reconstructed modal F/XYZ as well as original bytes in the witness.
    material_identity = sha256(''.join(fingerprint(event) for event in matched).encode('ascii')).hexdigest()
    cap_identity = sha256(''.join(fingerprint(event) for event in cap_events).encode('ascii')).hexdigest()
    return DerivedPathAssociation(sha256(original_recipe).hexdigest(), tuple(sha256(b).hexdigest() for b in original_inputs),
        descriptor.source_sha256, descriptor.project_sha256, descriptor.producer_sha256, descriptor.profile_identity,
        _context_identity(trace), fingerprint(frozen_emission), sha256(geometry_evidence).hexdigest(), matched_source_lines,
        material_identity, tuple(event.line_number for event in cap_events), cap_identity,
        minimum_feed, min(minimum_feed/60, descriptor.external_wall_speed_cap_mm_s), descriptor.expected_object_token)


@dataclass(frozen=True)
class NominalBodyAnchorProposal:
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    descriptor_identity: str
    entry_identity: str
    motion_identity: str
    byte_offset: int
    saved_state: MachineState
    acceleration_mm_s2: F
    object_scope: ObjectExecutionScope | None
    unresolved_premises: tuple[str, ...]
    eligibility_issues: tuple[str, ...]
    state_status: str = field(default='conditional_nominal', init=False)


def _anchor_from_trace(descriptor, trace, entry, motion, byte_offset):
    if type(byte_offset) is not int:
        raise ValueError('exact nominal body byte boundary required')
    boundaries = {descriptor.body_start_offset}
    for event in trace.events:
        if event.raw.endswith(b'\n'):
            boundaries.add(event.byte_offset+len(event.raw))
    if byte_offset not in boundaries:
        raise ValueError('complete original body line boundary required')
    state, acceleration, scope = entry.state, motion.entry_acceleration_mm_s2, None
    for event in trace.events:
        if event.byte_offset >= byte_offset:
            break
        state, acceleration, scope = event.after, event.acceleration_after_mm_s2, event.scope_after
    issues = []
    if not all((state.millimetres, state.absolute_xyz, state.relative_e, state.volumetric_disabled,
                state.speed_override_100, state.flow_override_100)):
        issues.append('incomplete-linear-modal-envelope')
    if any(type(v) is not F for v in (*state.xyz_mm, state.feed_mm_min, state.logical_e_mm, state.retraction_debt_mm)):
        issues.append('unknown-position-feed-logicalE-or-physical-debt')
    elif state.feed_mm_min <= 0 or state.retraction_debt_mm <= 0:
        issues.append('positive-saved-feed-and-retraction-required')
    if acceleration > motion.supplemental_acceleration_cap_mm_s2:
        issues.append('inherited-acceleration-exceeds-supplemental-cap')
    if motion.classic_jerk_xy_mm_s > motion.supplemental_jerk_cap_mm_s:
        issues.append('inherited-classic-jerk-exceeds-supplemental-cap')
    if scope is None:
        issues.append('outside-declared-object-predicate')
    return NominalBodyAnchorProposal(descriptor.source_sha256, descriptor.project_sha256, descriptor.producer_sha256,
        trace.descriptor_identity, trace.entry_identity, trace.motion_identity, byte_offset, state, acceleration,
        scope, trace.unresolved_premises, tuple(issues))


def propose_nominal_body_anchor(source, project, producer, descriptor, entry, motion, byte_offset):
    trace = interpret_nominal_body(source, project, producer, descriptor, entry, motion)
    return _anchor_from_trace(descriptor, trace, entry, motion, byte_offset)


@dataclass(frozen=True)
class ConditionalPathInput:
    frozen_emission: FrozenSupplementalEmission
    association: DerivedPathAssociation
    original_recipe: bytes
    original_inputs: tuple[bytes, ...]
    geometry_evidence: bytes


@dataclass(frozen=True)
class ConditionalInsertion:
    anchor: NominalBodyAnchorProposal
    paths: tuple[ConditionalPathInput, ...]
    upper_z_mm: F
    policy: HopPolicy


@dataclass(frozen=True)
class ConditionalInsertionSpan:
    source_byte_offset: int
    output_start: int
    output_end: int
    object_scope: ObjectExecutionScope
    path_association_identities: tuple[str, ...]
    preview_annotation_identity: str | None = None


@dataclass(frozen=True)
class ConditionalNominalCopy:
    output_bytes: bytes
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    descriptor_identity: str
    entry_identity: str
    motion_identity: str
    output_sha256: str
    insertion_spans: tuple[ConditionalInsertionSpan, ...]
    unresolved_premises: tuple[str, ...]
    preview_annotation_policy_identity: str | None = None
    state_status: str = field(default='conditional_nominal', init=False)
    printable_authorized: bool = field(default=False, init=False)
    runtime_injection_authorized: bool = field(default=False, init=False)
    physical_print_authorized: bool = field(default=False, init=False)


def validate_profile_bound_policy(profile, policy):
    """Bind every source-owned motion/flow field; permit only lower candidate feed."""
    _validate_policy(policy)
    canonical = policy_from_slice(profile, policy.bounds, xyz_places=policy.xyz_places, e_places=policy.e_places)
    if (replace(policy, candidate_speed_mm_s=canonical.candidate_speed_mm_s) != canonical
            or policy.candidate_speed_mm_s > canonical.candidate_speed_mm_s):
        raise ValueError('supplemental policy differs from current saved source profile')


def compose_conditional_nominal_copy(source, project, producer, descriptor, entry, motion, insertions, *, annotation_policy=None):
    if annotation_policy is not None and type(annotation_policy) is not ConditionalPreviewAnnotationPolicy:
        raise ValueError('immutable opt-in conditional preview annotation policy required')
    if any(marker in source for marker in (b'SUPPLEMENTAL_CYCLE_', b'ADAPTIVE_SUBEDGE_', b'CONDITIONAL_NOMINAL_')):
        raise ValueError('existing injection marker rejects repeated conditional copy')
    if type(insertions) is not tuple or not insertions or any(type(i) is not ConditionalInsertion for i in insertions):
        raise ValueError('nonempty immutable conditional insertion tuple required')
    trace = interpret_nominal_body(source, project, producer, descriptor, entry, motion)
    profile = read_sliced_profile(project, source, include_motion_caps=True)
    blocks, previous, all_path_ids, annotation_count = [], -1, set(), 0
    for insertion in insertions:
        validate_profile_bound_policy(profile, insertion.policy)
        anchor = insertion.anchor
        if type(anchor) is not NominalBodyAnchorProposal:
            raise ValueError('conditional anchor proposal required; synthetic/real tokens are not interchangeable')
        rebuilt = _anchor_from_trace(descriptor, trace, entry, motion, anchor.byte_offset)
        if rebuilt != anchor or anchor.eligibility_issues:
            raise ValueError(f'reconstructed conditional anchor is ineligible/stale: {rebuilt.eligibility_issues}')
        if anchor.byte_offset <= previous:
            raise ValueError('unique chronological conditional insertion boundaries required')
        previous = anchor.byte_offset
        if type(insertion.paths) is not tuple or not insertion.paths or any(type(p) is not ConditionalPathInput for p in insertion.paths):
            raise ValueError('immutable conditional path inputs required')
        associations, paths, expected_emission = [], [], []
        for path_input in insertion.paths:
            frozen, association = path_input.frozen_emission, path_input.association
            if type(association) is not DerivedPathAssociation:
                raise ValueError('exact derived-path association required')
            rebuilt_association = associate_derived_path(trace, descriptor, frozen,
                original_recipe=path_input.original_recipe, original_inputs=path_input.original_inputs,
                geometry_evidence=path_input.geometry_evidence, matched_source_lines=association.matched_source_lines)
            if rebuilt_association != association or association.object_token != anchor.object_scope.object_token:
                raise ValueError('stale source/recipe/geometry/object association')
            by_line = {event.line_number: event for event in trace.events}
            if any(by_line[line].byte_offset >= anchor.byte_offset for line in association.matched_source_lines):
                raise ValueError('recipe source material witnesses are not strictly earlier than insertion')
            if insertion.policy.candidate_speed_mm_s > association.source_speed_cap_mm_s:
                raise ValueError('requested supplemental speed exceeds actual matched source external-wall feed')
            if freeze_numeric_emission(frozen.path, insertion.policy) != frozen:
                raise ValueError('frozen path/emission/policy identity mismatch')
            if frozen.path.path_id in all_path_ids:
                raise ValueError('duplicate frozen path identity in copy')
            all_path_ids.add(frozen.path.path_id)
            paths.append(frozen.path)
            expected_emission.append(frozen)
            associations.append(fingerprint(association))
        block = compose_retracted_cycle(anchor.saved_state, tuple(paths), insertion.upper_z_mm, insertion.policy)
        preceding_line = source[:anchor.byte_offset].splitlines(keepends=True)[-1]
        if preceding_line.endswith(b'\r\n'):
            block = block.replace(b'\n', b'\r\n')
        annotation_identity = None
        if annotation_policy is not None:
            annotated = annotate_conditional_cycle(block, trace=trace, anchor_offset=anchor.byte_offset,
                frozen_paths=tuple(sorted(expected_emission, key=lambda f: (f.path.height_mm, f.path.path_id))), policy=annotation_policy)
            annotation_count += len(annotated.generated_line_indices)
            if annotation_count > annotation_policy.max_generated_comments:
                raise ValueError('whole-copy generated preview comment budget')
            block, annotation_identity = annotated.block, annotated.identity
        warning = b'; CONDITIONAL_NOMINAL_UNVERIFIED object_not_cancelled='+anchor.object_scope.object_token.encode('ascii')
        block = warning+(b'\r\n' if preceding_line.endswith(b'\r\n') else b'\n')+block
        replay = trace_linear_execution(block, initial_state=anchor.saved_state)
        if replay.failure is not None or replay.final_state != anchor.saved_state:
            raise ValueError('conditional cycle did not exactly restore nominal XYZ/F/E/debt/modes')
        emitted = []
        for event in replay.records:
            _, words = _words(event.raw.decode('ascii').strip())
            if words.get('E', F(0)) > 0 and event.before.xyz_mm[:2] != event.after.xyz_mm[:2]:
                emitted.append((words['E'], event.after.feed_mm_min))
        expected = tuple(pair for frozen in sorted(expected_emission, key=lambda f: (f.path.height_mm, f.path.path_id))
                         for pair in zip(frozen.relative_e_mm, frozen.feed_mm_min))
        if tuple(emitted) != expected:
            raise ValueError('cycle commands differ from immutable frozen E/F intent')
        blocks.append((anchor, block, tuple(associations), annotation_identity))
    chunks, spans, source_cursor, output_cursor = [], [], 0, 0
    for anchor, block, identities, annotation_identity in blocks:
        original = source[source_cursor:anchor.byte_offset]
        chunks.extend((original, block))
        output_cursor += len(original)
        spans.append(ConditionalInsertionSpan(anchor.byte_offset, output_cursor, output_cursor+len(block), anchor.object_scope, identities, annotation_identity))
        output_cursor += len(block)
        source_cursor = anchor.byte_offset
    chunks.append(source[source_cursor:])
    output = b''.join(chunks)
    recovered, cursor = [], 0
    for span in spans:
        recovered.append(output[cursor:span.output_start])
        cursor = span.output_end
    recovered.append(output[cursor:])
    if b''.join(recovered) != source:
        raise ValueError('conditional copy does not reconstruct original source bytes')
    return ConditionalNominalCopy(output, descriptor.source_sha256, descriptor.project_sha256, descriptor.producer_sha256,
        trace.descriptor_identity, trace.entry_identity, trace.motion_identity, sha256(output).hexdigest(), tuple(spans), trace.unresolved_premises,
        fingerprint(annotation_policy) if annotation_policy is not None else None)


def write_conditional_copy(copy, target: Path, *, source_path: Path, project_path: Path,
                           producer, descriptor, entry, motion, insertions, annotation_policy=None):
    """Publish a separate UNVERIFIED file atomically without replacing any file."""
    if (type(copy) is not ConditionalNominalCopy or type(copy.output_bytes) is not bytes
            or sha256(copy.output_bytes).hexdigest() != copy.output_sha256):
        raise ValueError('exact conditional copy receipt required')
    if 'UNVERIFIED' not in target.name or target.exists():
        raise ValueError('new explicitly UNVERIFIED output name required')
    for original, digest in ((source_path, copy.source_sha256), (project_path, copy.project_sha256)):
        if target.resolve() == original.resolve() or sha256(original.read_bytes()).hexdigest() != digest:
            raise ValueError('aliased or stale original input path')
    rebuilt = compose_conditional_nominal_copy(source_path.read_bytes(), project_path.read_bytes(), producer,
        descriptor, entry, motion, insertions, annotation_policy=annotation_policy)
    if rebuilt != copy:
        raise ValueError('conditional copy cannot be rebuilt from original source/entry/path inputs')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.conditional-UNVERIFIED-', dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(copy.output_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic no-replace publication: a racing existing target is never lost.
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink()
    return copy.output_sha256
