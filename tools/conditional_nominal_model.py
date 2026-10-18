"""Typed body deposition geometry, with explicit conditional debt crop provenance."""
from dataclasses import dataclass, field
from fractions import Fraction as F
from hashlib import sha256
import json
import re

from adaptive_subedge.domain.support_cell import ExactNominalTopSegment
from orca_plugin.gcode.linear_trace import MachineState, _advance, _words
from orca_plugin.gcode.source_profile import read_sliced_profile
from tools.conditional_nominal_body import NominalBodyTrace, NominalProducerDescriptor, fingerprint, interpret_nominal_body


@dataclass(frozen=True)
class NominalDepositionPremise:
    statement: str
    model: str = 'linear-E-over-affine-XYZ'

    def __post_init__(self):
        if type(self.statement) is not str or not self.statement.strip() or self.model != 'linear-E-over-affine-XYZ':
            raise ValueError('explicit declared conditional linear-E/distance premise required')


@dataclass(frozen=True)
class ConditionalModelPolicy:
    max_events: int
    max_segments: int
    max_coordinate_bits: int

    def __post_init__(self):
        if any(type(v) is not int or v < 1 for v in (self.max_events, self.max_segments, self.max_coordinate_bits)):
            raise ValueError('explicit positive exact model resource limits required')


@dataclass(frozen=True)
class NominalModelSpan:
    line_number: int
    event_identity: str
    original_geometry: ExactNominalTopSegment
    support_geometry: ExactNominalTopSegment | None
    raw_commanded_e_mm: F
    feed_mm_min: F
    deposited_e_mm: F | None
    entry_debt_mm: F | None
    deposition_start_parameter: F | None
    scope_identity: str
    feature: str


@dataclass(frozen=True)
class ConditionalNominalModel:
    source_sha256: str
    project_sha256: str
    descriptor_identity: str
    entry_identity: str
    premise: NominalDepositionPremise
    policy: ConditionalModelPolicy
    spans: tuple[NominalModelSpan, ...]
    physical_authority: bool = field(default=False, init=False)


def extract_conditional_nominal_model(inputs, premise, *, policy, cancelled):
    """Public source-bound extraction always rebuilds actual typed execution."""
    if type(inputs) is not tuple or len(inputs) != 6:
        raise ValueError('complete source/project/producer/descriptor/entry/motion inputs required')
    return _project_nominal_model(interpret_nominal_body(*inputs), inputs[3], premise,
        policy=policy, cancelled=cancelled)


def _project_nominal_model(trace, descriptor, premise, *, policy, cancelled):
    """Use typed events, not another G-code interpreter; metadata defines sections."""
    if (type(trace) is not NominalBodyTrace or type(descriptor) is not NominalProducerDescriptor
            or type(premise) is not NominalDepositionPremise or trace.descriptor_identity != fingerprint(descriptor)
            or type(policy) is not ConditionalModelPolicy or not callable(cancelled)):
        raise ValueError('associated typed trace/descriptor and declared deposition premise required')
    width = height = None
    spans = []
    if len(trace.events) > policy.max_events:
        raise ValueError('model event resource limit')
    for event in trace.events:
        stopped = cancelled()
        if type(stopped) is not bool:
            raise ValueError('exact bool model cancellation required')
        if stopped:
            raise ValueError('nominal model extraction cancelled')
        if event.command is None:
            text = event.raw.decode('ascii').strip()
            for name in ('LINE_WIDTH', 'LAYER_HEIGHT'):
                if text.startswith('; '+name+':'):
                    match = re.fullmatch('; '+name+r': ([0-9]+(?:\.[0-9]+)?)', text)
                    if match is None or F(match[1]) <= 0:
                        raise ValueError('malformed positive exact section metadata')
                    if name == 'LINE_WIDTH':
                        width = F(match[1])
                    else:
                        height = F(match[1])
        words = dict(event.parameters)
        raw_e = words.get('E', F(0))
        if type(raw_e) is not F:
            raise ValueError('exact typed raw commanded E required')
        if event.command not in ('G0', 'G1') or raw_e <= 0 or event.before.xyz_mm[:2] == event.after.xyz_mm[:2]:
            continue
        if width is None or height is None or event.scope_after is None:
            raise ValueError('positive model motion requires explicit section metadata/object scope')
        if any(type(c) is not F for c in (*event.before.xyz_mm, *event.after.xyz_mm)):
            raise ValueError('unknown nominal deposition XYZ')
        original = ExactNominalTopSegment(str(event.line_number), event.before.xyz_mm, event.after.xyz_mm,
            width, height, 'structural')
        debt = event.before.retraction_debt_mm
        if debt is not None and (type(debt) is not F or debt < 0):
            raise ValueError('nonnegative exact or unknown physical debt required')
        if type(event.after.feed_mm_min) is not F or event.after.feed_mm_min <= 0:
            raise ValueError('positive exact typed model feed required')
        parameter = min(F(1), debt/raw_e) if debt is not None else None
        expected_deposited = raw_e*(1-parameter) if parameter is not None else None
        if ((expected_deposited is None and event.deposited_filament_mm is not None)
                or (expected_deposited is not None and (type(event.deposited_filament_mm) is not F
                    or event.deposited_filament_mm != expected_deposited))):
            raise ValueError('typed deposited E disagrees with known/unknown debt crop')
        support = None
        if parameter is not None and parameter < 1:
            start = tuple(a+parameter*(b-a) for a, b in zip(original.start_xyz_mm, original.end_xyz_mm))
            support = ExactNominalTopSegment(original.segment_id, start, original.end_xyz_mm, width, height, 'structural')
        coordinates = (*original.start_xyz_mm, *original.end_xyz_mm, width, height, raw_e, event.after.feed_mm_min)
        coordinates += tuple(v for v in (debt, parameter, event.deposited_filament_mm) if v is not None)
        if support is not None:
            coordinates += support.start_xyz_mm
        if any(max(v.numerator.bit_length(), v.denominator.bit_length()) > policy.max_coordinate_bits for v in coordinates):
            raise ValueError('nominal model coordinate bit limit')
        spans.append(NominalModelSpan(event.line_number, fingerprint(event), original, support,
            raw_e, event.after.feed_mm_min, event.deposited_filament_mm, debt, parameter, fingerprint(event.scope_after), event.feature))
        if len(spans) > policy.max_segments:
            raise ValueError('nominal model segment resource limit')
    if not spans:
        raise ValueError('empty typed nominal model')
    return ConditionalNominalModel(descriptor.source_sha256, descriptor.project_sha256,
        trace.descriptor_identity, trace.entry_identity, premise, policy, tuple(spans))


@dataclass(frozen=True)
class RawGeometryReassociation:
    old_source_sha256: str
    old_project_sha256: str
    old_rows_sha256: str
    new_source_sha256: str
    new_project_sha256: str
    ordered_raw_geometry_sha256: str
    old_to_new_lines: tuple[tuple[int, int], ...]
    changed_feed_count: int
    debt_cropped_new_lines: tuple[int, ...]


def reassociate_raw_nominal_geometry(model, *, inputs, cancelled, old_source, old_project, old_rows,
        expected_old_source_sha256, expected_old_project_sha256, expected_old_rows_sha256):
    """Compare complete pinned nominal reference tuples; never transfer execution.

    Old rows are an explicitly pinned nominal geometry reference, not a firmware
    trace. Their individual raw source commands are checked with existing strict
    arithmetic using the declared row start. Current spans always come from the
    freshly reconstructed typed conditional trace, with separate deposited E.
    """
    if type(model) is not ConditionalNominalModel:
        raise ValueError('immutable current conditional nominal model required')
    if extract_conditional_nominal_model(inputs, model.premise, policy=model.policy, cancelled=cancelled) != model:
        raise ValueError('stale/forged model differs from source-bound typed extraction')
    for content, digest in ((old_source, expected_old_source_sha256), (old_project, expected_old_project_sha256),
                            (old_rows, expected_old_rows_sha256)):
        if type(content) is not bytes or sha256(content).hexdigest() != digest:
            raise ValueError('stale pinned original nominal reference')
    read_sliced_profile(old_project, old_source, include_motion_caps=True)
    rows = json.loads(old_rows)
    if type(rows) is not list or len(rows) != len(model.spans):
        raise ValueError('complete ordered raw geometry bijection required')
    lines, mapping, canonical, changed, previous = old_source.splitlines(keepends=True), [], [], 0, 0
    for row, span in zip(rows, model.spans):
        stopped = cancelled()
        if type(stopped) is not bool or stopped:
            raise ValueError('raw geometry reassociation cancelled or invalid callback')
        if (type(row) is not dict or type(row.get('line')) is not int
                or not previous < row['line'] <= len(lines)):
            raise ValueError('unique ordered original source line references required')
        previous = row['line']
        start, end = tuple(map(F, row['start'])), tuple(map(F, row['end']))
        width, height, raw_e = F(row['width']), F(row['height']), F(row['E'])
        command, words = _words(lines[row['line']-1].decode('ascii').strip())
        initial = MachineState(start, True, True, True, F(row['F']), F(0), F(0), True, True, True)
        after, _ = _advance(initial, command, words)
        if command not in ('G0', 'G1') or words.get('E') != raw_e or after.xyz_mm != end:
            raise ValueError('original reference row differs from exact raw source command')
        original = span.original_geometry
        if (start, end, width, height, raw_e) != (original.start_xyz_mm, original.end_xyz_mm,
                original.width_mm, original.height_mm, span.raw_commanded_e_mm):
            raise ValueError('ordered nominal raw geometry/source bijection mismatch')
        canonical.append(tuple(map(str, (*start, *end, width, height, raw_e))))
        mapping.append((row['line'], span.line_number))
        changed += F(row['F']) != span.feed_mm_min
    digest = sha256(json.dumps(canonical, separators=(',', ':')).encode('utf-8')).hexdigest()
    return RawGeometryReassociation(expected_old_source_sha256, expected_old_project_sha256,
        expected_old_rows_sha256, model.source_sha256, model.project_sha256, digest, tuple(mapping), changed,
        tuple(s.line_number for s in model.spans if s.deposition_start_parameter not in (None, F(0))))
