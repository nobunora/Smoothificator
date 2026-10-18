"""Explicit offline ordinary-unretract derivation; never a compositor rewrite."""
from copy import copy
from dataclasses import dataclass, field, replace
from fractions import Fraction as F
from hashlib import md5, sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
import tempfile
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED

from orca_plugin.gcode.linear_trace import _advance, WORD
from orca_plugin.gcode.source_profile import _scalar, _unique_object, _configuration, SliceSetting, read_sliced_profile
from tools.conditional_nominal_body import (
    NominalProducerDescriptor, NominalMotionEnvelope, interpret_nominal_body, pin_nominal_producer, fingerprint,
)


@dataclass(frozen=True)
class ExactDebtDerivationPolicy:
    max_source_bytes: int
    max_project_bytes: int
    max_producer_bytes: int
    max_archive_uncompressed_bytes: int
    max_events: int
    max_changes: int
    max_number_bits: int
    e_places: int

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            number = getattr(self, name)
            if type(number) is not int or number < (0 if name == 'e_places' else 1):
                raise ValueError('finite positive exact derivation limits required')
        if self.e_places > 18:
            raise ValueError('bounded E decimal precision required')


@dataclass(frozen=True)
class ReviewedNegativeRetraction:
    line_number: int
    raw_sha256: str
    relative_e_mm: F


@dataclass(frozen=True)
class ReviewedOrdinaryRestore:
    line_number: int
    raw_sha256: str
    scope_occurrence: int
    original_debt_mm: F
    sequential_repayment_mm: F
    negative_chain: tuple[ReviewedNegativeRetraction, ...]


@dataclass(frozen=True)
class ReviewedOrdinaryRestoreFamily:
    original_source_sha256: str
    original_project_sha256: str
    producer_sha256: str
    evidence_sha256: str
    review_reference: str
    retract_length_mm: F
    retract_speed_mm_min: F
    deretract_speed_mm_min: F
    e_places: int
    restores: tuple[ReviewedOrdinaryRestore, ...]


@dataclass(frozen=True)
class OrdinaryRestoreEvidence:
    line_number: int
    original_byte_offset: int
    scope_occurrence: int
    negative_chain_lines: tuple[int, ...]
    negative_chain_amounts_mm: tuple[F, ...]
    old_e_token: bytes
    new_e_token: bytes
    original_debt_mm: F
    repaid_debt_mm: F
    logical_e_delta_after_mm: F


@dataclass(frozen=True)
class DerivedEStateDifference:
    line_number: int
    old_logical_e_mm: F
    new_logical_e_mm: F
    old_debt_mm: F
    new_debt_mm: F


@dataclass(frozen=True)
class ExactDebtSourceDerivation:
    original_source_sha256: str
    original_project_sha256: str
    producer_sha256: str
    source_bytes: bytes
    project_bytes: bytes
    source_sha256: str
    project_sha256: str
    current_descriptor: NominalProducerDescriptor
    current_motion: NominalMotionEnvelope
    restores: tuple[OrdinaryRestoreEvidence, ...]
    changed_lines: tuple[int, ...]
    archive_changed_members: tuple[str, ...]
    archive_flag_changes: tuple[tuple[str, int, int], ...]
    moving_event_count: int
    final_logical_e_delta_mm: F
    final_debt_mm: F
    state_differences: tuple[DerivedEStateDifference, ...]
    reviewed_family_identity: str
    physical_authority: bool = field(default=False, init=False)


def _checkpoint(cancelled):
    answer = cancelled()
    if type(answer) is not bool or answer:
        raise ValueError('exact-debt derivation cancelled or invalid cancellation result')


def _number(number, policy):
    if (type(number) is not F or max(number.numerator.bit_length(), number.denominator.bit_length()) > policy.max_number_bits):
        raise ValueError('exact bounded numeric derivation state required')


def _identity(digest):
    if type(digest) is not str or re.fullmatch('[0-9a-f]{64}', digest) is None:
        raise ValueError('exact lowercase SHA256 reviewed identity required')


def _decimal(number, places):
    scaled = number*10**places
    if scaled.denominator != 1:
        raise ValueError('debt not exactly representable at declared E precision')
    digits = str(scaled.numerator).zfill(places+1)
    return (digits[:-places]+'.'+digits[-places:] if places else digits).encode('ascii')


def _archive(project, source, policy):
    with ZipFile(BytesIO(project)) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if (len(names) != len(set(names)) or len(names) > policy.max_events
                or sum(i.file_size for i in infos) > policy.max_archive_uncompressed_bytes):
            raise ValueError('duplicate or oversized archive')
        member, checksum = 'Metadata/plate_1.gcode', 'Metadata/plate_1.gcode.md5'
        if member not in names or checksum not in names:
            raise ValueError('required source and MD5 members missing')
        for info in infos:
            if info.flag_bits & ~(0x0008 | 0x0800) or info.compress_type not in (ZIP_STORED, ZIP_DEFLATED):
                raise ValueError('unsupported archive flags or compression')
            if info.flag_bits & 0x0800 and not info.filename.isascii():
                raise ValueError('unsupported non-ASCII UTF8 archive normalization')
            if re.search(r'(?:checksum|\.(?:md5|sha\d*))', info.filename, re.I) and info.filename != checksum:
                raise ValueError('unknown dependent checksum member')
        if archive.read(member) != source or archive.read(checksum) != md5(source).hexdigest().upper().encode('ascii'):
            raise ValueError('stale embedded source or required uppercase MD5')
        if archive.testzip() is not None:
            raise ValueError('invalid archive CRC')
        return infos, archive.comment, tuple(archive.read(i.filename) for i in infos)


def _clone_project(project, old_source, new_source, policy):
    infos, comment, members = _archive(project, old_source, policy)
    output = BytesIO()
    with ZipFile(output, 'w') as target:
        target.comment = comment
        for info, content in zip(infos, members):
            cloned = copy(info)
            if info.filename == 'Metadata/plate_1.gcode':
                content = new_source
            elif info.filename == 'Metadata/plate_1.gcode.md5':
                content = md5(new_source).hexdigest().upper().encode('ascii')
            target.writestr(cloned, content)
            cloned.external_attr = info.external_attr
    result = output.getvalue()
    after_infos, after_comment, after_members = _archive(result, new_source, policy)
    changed, flags = [], []
    if after_comment != comment:
        raise ValueError('archive comment changed')
    for before, after, a, b in zip(infos, after_infos, members, after_members):
        for name in ('filename', 'date_time', 'comment', 'extra', 'compress_type', 'internal_attr', 'external_attr',
                     'create_system', 'create_version', 'extract_version', 'reserved', 'volume'):
            if getattr(before, name) != getattr(after, name):
                raise ValueError('unsupported ZIP metadata change: '+name)
        if before.flag_bits != after.flag_bits:
            if (before.flag_bits ^ after.flag_bits) & ~(0x0008 | 0x0800):
                raise ValueError('unsupported ZIP flag change')
            flags.append((before.filename, before.flag_bits, after.flag_bits))
        if a != b:
            changed.append(before.filename)
    if set(changed) - {'Metadata/plate_1.gcode', 'Metadata/plate_1.gcode.md5'}:
        raise ValueError('unrelated archive content changed')
    return result, tuple(changed), tuple(flags)


def _ordinary_profile(source, project):
    profile = read_sliced_profile(project, source)
    with ZipFile(BytesIO(project)) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'), object_pairs_hook=_unique_object)
    config = _configuration(source)
    for key in ('retraction_length', 'retraction_speed', 'deretraction_speed', 'retract_restart_extra',
                'retract_restart_extra_toolchange'):
        override = 'filament_'+key
        saved = _scalar(settings, override)
        exported = config.get(override, ())
        # Orca omits inherited filament overrides from the exported config.
        # A present override must still agree with the saved resolved project.
        if exported and (len(exported) != 1 or exported[0] != saved) or not exported and saved != 'nil':
            raise ValueError('ambiguous saved/source filament override: '+override)
    key = 'retract_restart_extra_toolchange'
    override = 'filament_'+key
    selected = key if _scalar(settings, override) == 'nil' else override
    extra = SliceSetting(key, selected, _scalar(settings, selected)).number()
    if len(config.get(selected, ())) != 1 or F(config[selected][0]) != extra:
        raise ValueError('unresolved toolchange restart extra')
    if extra != 0 or profile.setting('retract_restart_extra').number() != 0:
        raise ValueError('ordinary/toolchange extra prime must be exactly zero')
    if profile.setting('use_firmware_retraction').number() != 0:
        raise ValueError('ordinary explicit retraction required')
    length = profile.setting('retraction_length').number()
    speed = profile.setting('deretraction_speed').number()*60
    if length <= 0:
        raise ValueError('positive saved ordinary retract length required')
    return length, speed, profile.setting('retraction_speed').number()*60


def derive_exact_debt_source(inputs, *, family, policy, cancelled):
    """Rebuild actual inputs, classify ordinary chains, then repay sequential debt."""
    if (type(inputs) is not tuple or len(inputs) != 6 or type(policy) is not ExactDebtDerivationPolicy
            or type(family) is not ReviewedOrdinaryRestoreFamily
            or not callable(cancelled)):
        raise ValueError('complete pinned inputs and exact bounded policy required')
    _checkpoint(cancelled)
    source, project, producer, descriptor, entry, motion = inputs
    if (any(type(b) is not bytes for b in (source, project, producer)) or len(source) > policy.max_source_bytes
            or len(project) > policy.max_project_bytes or len(producer) > policy.max_producer_bytes
            or source.count(b'\n') > policy.max_events):
        raise ValueError('source/project/event budget exceeded')
    for digest in (family.original_source_sha256, family.original_project_sha256, family.producer_sha256, family.evidence_sha256):
        _identity(digest)
    _archive(project, source, policy)
    length, speed, retract_speed = _ordinary_profile(source, project)
    trace = interpret_nominal_body(*inputs)
    if ((family.original_source_sha256, family.original_project_sha256, family.producer_sha256)
            != (descriptor.source_sha256, descriptor.project_sha256, descriptor.producer_sha256)
            or type(family.evidence_sha256) is not str or re.fullmatch('[0-9a-f]{64}', family.evidence_sha256) is None
            or type(family.review_reference) is not str or not family.review_reference.strip()
            or (family.retract_length_mm, family.retract_speed_mm_min, family.deretract_speed_mm_min, family.e_places)
            != (length, retract_speed, speed, policy.e_places)
            or type(family.e_places) is not int or type(family.restores) is not tuple
            or not 0 < len(family.restores) <= policy.max_events):
        raise ValueError('explicit pinned reviewed ordinary-restore family/profile required')
    negative_count = 0
    for expected in family.restores:
        _checkpoint(cancelled)
        if (type(expected) is not ReviewedOrdinaryRestore or type(expected.line_number) is not int
                or type(expected.scope_occurrence) is not int or expected.scope_occurrence < 1
                or type(expected.negative_chain) is not tuple or not expected.negative_chain
                or len(expected.negative_chain) > policy.max_events):
            raise ValueError('complete immutable reviewed restore chain required')
        _identity(expected.raw_sha256)
        for number in (expected.original_debt_mm, expected.sequential_repayment_mm):
            _number(number, policy)
        for negative in expected.negative_chain:
            if type(negative) is not ReviewedNegativeRetraction or type(negative.line_number) is not int:
                raise ValueError('exact reviewed negative chain identity required')
            _identity(negative.raw_sha256)
            _number(negative.relative_e_mm, policy)
        negative_count += len(expected.negative_chain)
        if negative_count > policy.max_events:
            raise ValueError('reviewed negative chain event budget exceeded')
    for number in (family.retract_length_mm, family.retract_speed_mm_min, family.deretract_speed_mm_min):
        _number(number, policy)
    if len(trace.events) > policy.max_events:
        raise ValueError('body event budget exceeded')
    state, chain, evidence, changed = entry.state, [], [], []
    if state.logical_e_mm is None or state.retraction_debt_mm != 0:
        raise ValueError('known logical E and initially zero debt required for complete chain provenance')
    lines = source.splitlines(keepends=True)
    moving = 0
    wiping = False
    for event in trace.events:
        _checkpoint(cancelled)
        marker = event.raw.strip()
        if marker == b'; WIPE_START':
            if wiping:
                raise ValueError('nested wipe role')
            wiping = True
        elif marker == b'; WIPE_END':
            if not wiping:
                raise ValueError('unmatched wipe role')
            wiping = False
        for number in (*state.xyz_mm, state.feed_mm_min, state.logical_e_mm, state.retraction_debt_mm,
                       *dict(event.parameters).values()):
            if number is not None:
                _number(number, policy)
        values = dict(event.parameters)
        amount = values.get('E', F(0))
        before = state
        if event.command in ('G0', 'G1') and amount > 0 and event.before.xyz_mm[:2] == event.after.xyz_mm[:2]:
            debt = state.retraction_debt_mm
            if (event.before.xyz_mm != event.after.xyz_mm or event.command != 'G1'
                    or set(values) != {'E', 'F'} or values['F'] != speed or amount != length
                    or wiping or event.scope_before is None or debt is None or debt <= 0 or not chain
                    or chain[0][2] != 0 or -sum((q[1] for q in chain), F(0)) != debt
                    or any(q[3] is not None and q[3].object_token != event.scope_before.object_token for q in chain)):
                raise ValueError('unsupported or ambiguous ordinary restore/negative chain')
            if len(evidence) >= len(family.restores):
                raise ValueError('additional restore outside reviewed family')
            expected = family.restores[len(evidence)]
            actual_chain = tuple(ReviewedNegativeRetraction(q[0], q[4], q[1]) for q in chain)
            if (expected != ReviewedOrdinaryRestore(event.line_number, sha256(event.raw).hexdigest(),
                    event.scope_before.occurrence, event.before.retraction_debt_mm, debt, actual_chain)):
                raise ValueError('fresh ordinary restore/chain differs from reviewed family')
            text = event.raw.split(b';', 1)[0].decode('ascii')
            tokens = [m for m in WORD.finditer(text) if m[1] == 'E']
            if len(tokens) != 1:
                raise ValueError('unique numeric E token required')
            token = tokens[0]
            old_token = token[2].encode('ascii')
            new_token = old_token if amount == debt else _decimal(debt, policy.e_places)
            if new_token != old_token:
                raw = event.raw
                lines[event.line_number-1] = raw[:token.start(2)]+new_token+raw[token.end(2):]
                changed.append(event.line_number)
                if len(changed) > policy.max_changes:
                    raise ValueError('change budget exceeded')
            values['E'] = debt
            state, deposited = _advance(state, event.command, values)
            if deposited != 0 or state.retraction_debt_mm != 0:
                raise ValueError('sequential exact repayment failed')
            evidence.append(OrdinaryRestoreEvidence(event.line_number, event.byte_offset, event.scope_before.occurrence,
                tuple(q[0] for q in chain), tuple(q[1] for q in chain), old_token, new_token,
                event.before.retraction_debt_mm, debt, state.logical_e_mm-event.after.logical_e_mm))
            chain = []
        elif event.command in ('G0', 'G1', 'G21', 'G90', 'M83', 'G92', 'M200', 'M220', 'M221'):
            state, deposited = _advance(state, event.command, values)
            if amount < 0:
                _decimal(-amount, policy.e_places)
                if event.command != 'G1' or before.retraction_debt_mm is None:
                    raise ValueError('unsupported negative retraction chain')
                if not wiping and (set(values) != {'E', 'F'} or values['F'] != retract_speed or -amount > length):
                    raise ValueError('negative command is neither ordinary retract nor explicit wipe')
                if wiping and (set(values)-set('XYEF') or event.scope_before is None):
                    raise ValueError('unsupported wipe retraction role')
                chain.append((event.line_number, amount, before.retraction_debt_mm, event.scope_before, sha256(event.raw).hexdigest()))
            elif amount > 0:
                if before.retraction_debt_mm != 0 or deposited != amount:
                    raise ValueError('moving deposition retains unintended debt')
                moving += 1
                chain = []
        if replace(state, logical_e_mm=event.after.logical_e_mm, retraction_debt_mm=event.after.retraction_debt_mm) != event.after:
            raise ValueError('non-E state changed')
    if wiping:
        raise ValueError('unclosed wipe role')
    if len(evidence) != len(family.restores):
        raise ValueError('missing restore from complete reviewed family')
    derived_source = b''.join(lines)
    derived_project, member_changes, flags = _clone_project(project, source, derived_source, policy)
    new_descriptor = pin_nominal_producer(derived_source, derived_project, producer,
        expected_source_sha256=sha256(derived_source).hexdigest(), expected_project_sha256=sha256(derived_project).hexdigest(),
        expected_producer_sha256=descriptor.producer_sha256,
        body_start_offset=descriptor.body_start_offset,
        body_end_offset=descriptor.body_end_offset+len(derived_source)-len(source),
        expected_object_token=descriptor.expected_object_token, fan_channels=descriptor.fan_channels)
    new_motion = replace(motion, source_sha256=new_descriptor.source_sha256, project_sha256=new_descriptor.project_sha256,
                         profile_identity=new_descriptor.profile_identity)
    fresh = interpret_nominal_body(derived_source, derived_project, producer, new_descriptor, entry, new_motion)
    if (fresh.final_state != state or new_descriptor.prefix_sha256 != descriptor.prefix_sha256
            or new_descriptor.suffix_sha256 != descriptor.suffix_sha256 or len(fresh.events) != len(trace.events)):
        raise ValueError('fresh replay/prefix/suffix changed')
    differences = []
    for old, new in zip(trace.events, fresh.events):
        _checkpoint(cancelled)
        if old.line_number != new.line_number or old.command != new.command:
            raise ValueError('event ordering changed')
        if old.line_number not in changed and old.raw != new.raw:
            raise ValueError('unrelated source bytes changed')
        if (replace(old.after, logical_e_mm=new.after.logical_e_mm, retraction_debt_mm=new.after.retraction_debt_mm) != new.after
                or old.scope_after != new.scope_after or old.fans_after != new.fans_after
                or old.acceleration_after_mm_s2 != new.acceleration_after_mm_s2 or old.feature != new.feature):
            raise ValueError('fresh non-E state differs')
        if (old.after.logical_e_mm, old.after.retraction_debt_mm) != (new.after.logical_e_mm, new.after.retraction_debt_mm):
            differences.append(DerivedEStateDifference(old.line_number, old.after.logical_e_mm, new.after.logical_e_mm,
                old.after.retraction_debt_mm, new.after.retraction_debt_mm))
        if dict(new.parameters).get('E', F(0)) > 0:
            stationary = new.before.xyz_mm[:2] == new.after.xyz_mm[:2]
            if stationary and new.deposited_filament_mm != 0 or not stationary and new.before.retraction_debt_mm != 0:
                raise ValueError('residual stationary material or moving debt')
    return ExactDebtSourceDerivation(descriptor.source_sha256, descriptor.project_sha256, descriptor.producer_sha256,
        derived_source, derived_project, new_descriptor.source_sha256, new_descriptor.project_sha256, new_descriptor,
        new_motion, tuple(evidence), tuple(changed), member_changes, flags, moving,
        state.logical_e_mm-trace.final_state.logical_e_mm, state.retraction_debt_mm, tuple(differences), fingerprint(family))


def write_exact_debt_source(derivation, directory: Path, *, source_path: Path, project_path: Path,
                            producer, descriptor, entry, motion, family, policy, cancelled):
    """Atomically publish a new directory containing both verified outputs."""
    if (type(derivation) is not ExactDebtSourceDerivation or directory.exists() or 'UNVERIFIED' not in directory.name
            or not directory.parent.is_dir()):
        raise ValueError('new explicitly UNVERIFIED directory required')
    for original, digest in ((source_path, derivation.original_source_sha256), (project_path, derivation.original_project_sha256)):
        if directory.resolve() == original.resolve() or sha256(original.read_bytes()).hexdigest() != digest:
            raise ValueError('aliased or stale original input')
    rebuilt = derive_exact_debt_source((source_path.read_bytes(), project_path.read_bytes(), producer, descriptor, entry, motion),
                                     family=family, policy=policy, cancelled=cancelled)
    if rebuilt != derivation:
        raise ValueError('stale or forged derivation receipt')
    with tempfile.TemporaryDirectory(prefix='.exact-debt-', dir=directory.parent) as temporary:
        staging = Path(temporary)/directory.name
        staging.mkdir()
        for name, content in (('source.UNVERIFIED.gcode', rebuilt.source_bytes), ('project.UNVERIFIED.3mf', rebuilt.project_bytes)):
            with (staging/name).open('xb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        _checkpoint(cancelled)
        # Windows rename refuses an existing destination, including racing peers.
        if os.name != 'nt':
            raise ValueError('atomic no-replace directory publication requires Windows')
        os.rename(staging, directory)
    return rebuilt.source_sha256, rebuilt.project_sha256
