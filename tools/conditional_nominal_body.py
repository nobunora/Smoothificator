"""Conditional nominal body interpretation; opaque startup is never validated."""
import base64
from dataclasses import asdict, dataclass, field
from fractions import Fraction as F
from hashlib import sha256
from io import BytesIO
import json
import re
from zipfile import ZipFile

from orca_plugin.gcode.linear_trace import MachineState, _advance, _words, trace_linear_execution
from orca_plugin.gcode.source_profile import _configuration, _scalar, _unique_object, read_sliced_profile


EFFECTS_CONTRACT = 'declared-single-object-body-effects-v1'
ASSUMPTION_NAMES = ('manufacturer_startup_completed', 'source_machine_frame_and_tool',
    'linear_relativeE_envelope', 'startup_retraction_reference', 'live_overrides_100',
    'active_object_not_cancelled')


def fingerprint(value):
    return sha256(json.dumps(asdict(value), sort_keys=True, separators=(',', ':'), default=str).encode('ascii')).hexdigest()


def _digest(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('exact lowercase SHA256 identity required')


def _profile(source, project):
    profile = read_sliced_profile(project, source, include_motion_caps=True)
    with ZipFile(BytesIO(project)) as archive:
        raw = archive.read('Metadata/project_settings.config')
    settings = json.loads(raw, object_pairs_hook=_unique_object)
    if _scalar(settings, 'time_lapse_gcode') != '':
        raise ValueError('this conditional producer requires separately identified empty time-lapse hook')
    config = _configuration(source)
    resolved = []
    for key in ('outer_wall_acceleration', 'outer_wall_jerk'):
        value = F(_scalar(settings, key))
        if (value < 0 or key == 'outer_wall_acceleration' and value == 0
                or len(config.get(key, ())) != 1 or F(config[key][0]) != value):
            raise ValueError('matching positive acceleration/nonnegative classic jerk cap required')
        resolved.append(value)
    jerk_limits = []
    for key in ('machine_max_jerk_x', 'machine_max_jerk_y'):
        vector = settings.get(key)
        if type(vector) is not list or not vector or any(type(v) is not str or F(v) < 0 for v in vector):
            raise ValueError('explicit saved classic XY jerk vectors required')
        if len(config.get(key, ())) != 1 or tuple(map(F, config[key][0].split(','))) != tuple(map(F, vector)):
            raise ValueError('saved/G-code classic jerk vectors differ')
        jerk_limits.extend(map(F, vector))
    return profile, sha256(raw).hexdigest(), resolved[0], min(resolved[1], *jerk_limits)


@dataclass(frozen=True)
class DeclaredNominalAssumption:
    name: str
    statement: str
    evidence_reference: str
    status: str = field(default='declared-unverified', init=False)

    def __post_init__(self):
        if any(type(v) is not str or not v.strip() for v in (self.name, self.statement, self.evidence_reference)):
            raise ValueError('separately named explicit nominal premise and provenance required')


@dataclass(frozen=True)
class NominalEntryContext:
    state: MachineState
    assumptions: tuple[DeclaredNominalAssumption, ...]

    def __post_init__(self):
        if type(self.state) is not MachineState:
            raise ValueError('exact immutable nominal entry state required')
        trace_linear_execution(b'', initial_state=self.state)
        if (type(self.assumptions) is not tuple or any(type(a) is not DeclaredNominalAssumption for a in self.assumptions)
                or len(self.assumptions) != len(ASSUMPTION_NAMES)
                or set(a.name for a in self.assumptions) != set(ASSUMPTION_NAMES)):
            raise ValueError('all separately named startup/frame/E/retraction/override/object premises required')


@dataclass(frozen=True)
class NominalProducerDescriptor:
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    profile_identity: str
    external_wall_speed_cap_mm_s: F
    body_start_offset: int
    body_end_offset: int
    prefix_sha256: str
    body_sha256: str
    suffix_sha256: str
    expected_object_token: str
    fan_channels: tuple[int, ...]
    effects_contract: str = EFFECTS_CONTRACT


def pin_nominal_producer(source, project, producer, *, expected_source_sha256, expected_project_sha256,
        expected_producer_sha256, body_start_offset, body_end_offset, expected_object_token, fan_channels):
    if any(type(content) is not bytes for content in (source, project, producer)):
        raise ValueError('exact source/project/producer bytes required')
    for digest in (expected_source_sha256, expected_project_sha256, expected_producer_sha256):
        _digest(digest)
    hashes = tuple(sha256(content).hexdigest() for content in (source, project, producer))
    if hashes != (expected_source_sha256, expected_project_sha256, expected_producer_sha256):
        raise ValueError('source/project/producer pins differ from actual bytes')
    boundaries, offset = {0}, 0
    for raw in source.splitlines(keepends=True):
        offset += len(raw)
        if raw.endswith(b'\n'):
            boundaries.add(offset)
    if (type(body_start_offset) is not int or type(body_end_offset) is not int
            or body_start_offset not in boundaries or body_end_offset not in boundaries
            or not 0 <= body_start_offset < body_end_offset <= len(source)):
        raise ValueError('complete-line nonempty body boundaries required')
    _object_token(expected_object_token)
    if (type(fan_channels) is not tuple or not fan_channels or len(set(fan_channels)) != len(fan_channels)
            or any(type(channel) is not int or channel < 0 for channel in fan_channels)):
        raise ValueError('explicit unique fan channel identities required')
    profile, profile_identity, _, _ = _profile(source, project)
    return NominalProducerDescriptor(*hashes, profile_identity, profile.setting('outer_wall_speed').number(), body_start_offset, body_end_offset,
        sha256(source[:body_start_offset]).hexdigest(), sha256(source[body_start_offset:body_end_offset]).hexdigest(),
        sha256(source[body_end_offset:]).hexdigest(), expected_object_token, fan_channels)


def _object_token(token):
    if type(token) is not str:
        raise ValueError('canonical single-object payload required')
    try:
        decoded = base64.b64decode(token, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError('malformed object payload') from exc
    if (len(decoded) != 8 or int.from_bytes(decoded, 'little').bit_count() != 1
            or base64.b64encode(decoded).decode('ascii') != token):
        raise ValueError('canonical single-object bitmap payload required')


@dataclass(frozen=True)
class NominalMotionEnvelope:
    source_sha256: str
    project_sha256: str
    profile_identity: str
    entry_acceleration_mm_s2: F
    classic_jerk_xy_mm_s: F
    external_wall_acceleration_cap_mm_s2: F
    external_wall_jerk_cap_mm_s: F
    supplemental_acceleration_cap_mm_s2: F
    supplemental_jerk_cap_mm_s: F
    cornering_dialect: str
    entry_witness_sha256: str
    entry_provenance: str
    firmware_interpretation: str

    def __post_init__(self):
        for digest in (self.source_sha256, self.project_sha256, self.profile_identity, self.entry_witness_sha256):
            _digest(digest)
        accelerations = (self.entry_acceleration_mm_s2, self.external_wall_acceleration_cap_mm_s2,
                         self.supplemental_acceleration_cap_mm_s2)
        jerks = (self.classic_jerk_xy_mm_s, self.external_wall_jerk_cap_mm_s, self.supplemental_jerk_cap_mm_s)
        if (any(type(v) is not F or v <= 0 for v in accelerations)
                or any(type(v) is not F or v < 0 for v in jerks)
                or self.supplemental_acceleration_cap_mm_s2 > self.external_wall_acceleration_cap_mm_s2
                or self.supplemental_jerk_cap_mm_s > self.external_wall_jerk_cap_mm_s):
            raise ValueError('exact known entry motion and requested caps within resolved wall caps required')
        if (self.cornering_dialect != 'classic-jerk' or any(type(v) is not str or not v.strip()
                for v in (self.entry_provenance, self.firmware_interpretation))):
            raise ValueError('explicit supported classic-jerk interpretation/provenance required')


@dataclass(frozen=True)
class ObjectExecutionScope:
    object_token: str
    occurrence: int
    predicate: str = field(default='object_not_cancelled', init=False)


@dataclass(frozen=True)
class NominalBodyEvent:
    line_number: int
    byte_offset: int
    raw: bytes
    kind: str
    command: str | None
    parameters: tuple[tuple[str, F], ...]
    before: MachineState
    after: MachineState
    acceleration_before_mm_s2: F
    acceleration_after_mm_s2: F
    scope_before: ObjectExecutionScope | None
    scope_after: ObjectExecutionScope | None
    fans_after: tuple[tuple[int, int], ...]
    deposited_filament_mm: F | None
    feature: str | None


@dataclass(frozen=True)
class NominalBodyTrace:
    descriptor_identity: str
    entry_identity: str
    motion_identity: str
    events: tuple[NominalBodyEvent, ...]
    final_state: MachineState
    final_acceleration_mm_s2: F
    unresolved_premises: tuple[str, ...]
    state_status: str = field(default='conditional_nominal', init=False)
    printable_authorized: bool = field(default=False, init=False)
    runtime_injection_authorized: bool = field(default=False, init=False)


def interpret_nominal_body(source, project, producer, descriptor, entry, motion):
    """Interpret exactly the pinned body under declared premises, never the prefix."""
    if (type(descriptor) is not NominalProducerDescriptor or type(entry) is not NominalEntryContext
            or type(motion) is not NominalMotionEnvelope or descriptor.effects_contract != EFFECTS_CONTRACT):
        raise ValueError('exact supported descriptor/entry/motion contract required')
    rebuilt = pin_nominal_producer(source, project, producer, expected_source_sha256=descriptor.source_sha256,
        expected_project_sha256=descriptor.project_sha256, expected_producer_sha256=descriptor.producer_sha256,
        body_start_offset=descriptor.body_start_offset, body_end_offset=descriptor.body_end_offset,
        expected_object_token=descriptor.expected_object_token, fan_channels=descriptor.fan_channels)
    if rebuilt != descriptor:
        raise ValueError('producer descriptor or raw span identity changed')
    _, profile_identity, acceleration_cap, jerk_cap = _profile(source, project)
    if ((motion.source_sha256, motion.project_sha256, motion.profile_identity, motion.entry_witness_sha256)
            != (descriptor.source_sha256, descriptor.project_sha256, profile_identity, descriptor.prefix_sha256)
            or motion.external_wall_acceleration_cap_mm_s2 != acceleration_cap
            or motion.external_wall_jerk_cap_mm_s != jerk_cap):
        raise ValueError('nominal motion/profile/prefix association mismatch')
    state, acceleration, scope, fans, feature = entry.state, motion.entry_acceleration_mm_s2, None, {}, None
    events, occurrence = [], 0
    first_line = source[:descriptor.body_start_offset].count(b'\n')+1
    offset = descriptor.body_start_offset
    for number, raw in enumerate(source[descriptor.body_start_offset:descriptor.body_end_offset].splitlines(keepends=True), first_line):
        if any((byte < 32 and byte not in (9, 10, 13)) or byte == 127 for byte in raw):
            raise ValueError(f'malformed body control/comment at line {number}')
        decoded = raw.decode('ascii').strip()
        text = decoded.split(';', 1)[0].strip()
        before, old_acceleration, old_scope = state, acceleration, scope
        command, values, deposited = None, {}, F(0)
        kind = 'comment' if decoded else 'blank'
        if decoded.startswith('; FEATURE:'):
            match = re.fullmatch(r'; FEATURE: ([A-Za-z][A-Za-z /_-]*)', decoded)
            if match is None:
                raise ValueError('malformed producer feature metadata')
            feature = match[1]
        if text:
            if text.startswith('M624'):
                match = re.fullmatch(r'M624 ([A-Za-z0-9+/]+={0,2})', text)
                if match is None or match[1] != descriptor.expected_object_token or scope is not None:
                    raise ValueError('malformed/nested/multiple-object scope')
                _object_token(match[1])
                occurrence += 1
                scope = ObjectExecutionScope(match[1], occurrence)
                command, kind = 'M624', 'object-scope-open'
            else:
                command, values = _words(text)
                if command in ('G0', 'G1', 'G21', 'G90', 'M83', 'G92', 'M200', 'M220', 'M221'):
                    state, deposited = _advance(state, command, values)
                    kind = 'linear-motion' if command in ('G0', 'G1') else 'linear-modal'
                    if values.get('E', F(0)) > 0 and scope is None:
                        raise ValueError('positive material/unretract command outside declared object scope')
                elif command == 'M204':
                    if set(values) != {'S'} or values['S'] <= 0:
                        raise ValueError('only positive exact M204 S acceleration supported')
                    acceleration, kind = values['S'], 'acceleration'
                elif command == 'M106':
                    if set(values) not in ({'S'}, {'P', 'S'}) or any(v.denominator != 1 for v in values.values()):
                        raise ValueError('unsupported fan parameters')
                    channel, pwm = int(values.get('P', F(0))), int(values['S'])
                    if channel not in descriptor.fan_channels or not 0 <= pwm <= 255:
                        raise ValueError('unsupported fan channel/PWM')
                    fans[channel], kind = pwm, 'fan'
                elif command == 'M73':
                    if any(v.denominator != 1 for v in values.values()) or not (
                            set(values) == {'L'} and values['L'] > 0 or set(values) == {'P', 'R'}
                            and 0 <= values['P'] <= 100 and values['R'] >= 0):
                        raise ValueError('unsupported producer progress notification')
                    kind = 'progress-notification'
                elif command == 'M991':
                    if set(values) != {'S', 'P'} or values['S'] != 0 or values['P'] < 0 or values['P'].denominator != 1:
                        raise ValueError('unsupported producer layer notification')
                    kind = 'layer-notification'
                elif command == 'M625':
                    if values or scope is None:
                        raise ValueError('unmatched/malformed object scope close')
                    scope, kind = None, 'object-scope-close'
                else:
                    raise ValueError(f'unsupported conditional body command: {command}')
        events.append(NominalBodyEvent(number, offset, raw, kind, command, tuple(values.items()), before, state,
            old_acceleration, acceleration, old_scope, scope, tuple(sorted(fans.items())), deposited, feature))
        offset += len(raw)
    if scope is not None or occurrence == 0:
        raise ValueError('unclosed or missing single-object execution scope')
    return NominalBodyTrace(fingerprint(descriptor), fingerprint(entry), fingerprint(motion), tuple(events),
        state, acceleration, tuple(a.name for a in entry.assumptions))
