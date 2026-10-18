"""Bounded experimental native-source trace; no firmware or print authority."""
from dataclasses import dataclass, field, fields, replace
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
import re
from io import BytesIO
from zipfile import ZipFile

from orca_plugin.gcode.linear_trace import MachineState, _advance
from tools.conditional_nominal_body import fingerprint
from tools.native_used_material_profile import read_native_used_material_profile,NativeMaterialProfileLimits


@dataclass(frozen=True)
class NativeTrialLimits:
    max_source_bytes: int
    max_project_bytes: int
    max_producer_bytes: int
    max_events: int
    max_branch_depth: int
    max_number_bits: int
    max_archive_members: int
    max_archive_uncompressed_bytes: int

    def __post_init__(self):
        if any(type(getattr(self, f.name)) is not int or getattr(self, f.name) < 1 for f in fields(self)):
            raise ValueError('positive exact native trial limits required')


@dataclass(frozen=True)
class NativeTrialState:
    machine: MachineState
    xy_plane: bool | None
    acceleration_mm_s2: F | None
    classic_jerk_xy_mm_s: F | None
    object_token: str | None = None


@dataclass(frozen=True)
class NativeTrialContext:
    source_sha256: str
    project_sha256: str
    producer_sha256: str
    body_start_offset: int
    body_end_offset: int
    entry: NativeTrialState
    expected_object_token: str
    judge_flags: tuple[str, ...]
    opaque_command_texts: tuple[str, ...]
    unresolved_premises: tuple[str, ...]
    geometry_project_sha256: str
    effective_profile_identity: str


@dataclass(frozen=True)
class NativeArcBounds:
    clockwise: bool
    center_xy_mm: tuple[F, F]
    radius_upper_mm: F
    xyz_min_mm: tuple[F, F, F]
    xyz_max_mm: tuple[F, F, F]
    turns: F
    support_available: bool = field(default=False, init=False)


@dataclass(frozen=True)
class NativeTrialEvent:
    line_number: int
    byte_offset: int
    raw: bytes
    command: str
    before: NativeTrialState
    after: NativeTrialState
    branch_depth: int
    relative_e_mm: F
    deposited_filament_mm: F | None
    arc: NativeArcBounds | None
    feature: str | None
    physical_height_mm: F | None
    nominal_width_mm: F | None


@dataclass(frozen=True)
class NativeUnmodeledEffect:
    line_number: int
    byte_offset: int
    raw_sha256: str
    reason: str


@dataclass(frozen=True)
class NativeTrialTrace:
    context_identity: str
    events: tuple[NativeTrialEvent, ...]
    final_state: NativeTrialState
    unmodeled_effects: tuple[NativeUnmodeledEffect, ...]
    unresolved_premises: tuple[str, ...]
    physical_authority: bool = field(default=False, init=False)
    whole_original_job_complete: bool = field(default=False, init=False)


@dataclass(frozen=True)
class NativeTrialAnchor:
    context_identity: str
    byte_offset: int
    saved_state: NativeTrialState
    eligibility_issues: tuple[str, ...]


def checkpoint(cancelled):
    answer = cancelled()
    if type(answer) is not bool or answer:
        raise ValueError('native trial cancelled or invalid cancellation result')


def exact_number(number, limits):
    if type(number) is not F or max(number.numerator.bit_length(), number.denominator.bit_length()) > limits.max_number_bits:
        raise ValueError('bounded exact native trial number required')


def _identity(digest):
    if type(digest) is not str or re.fullmatch('[0-9a-f]{64}', digest) is None:
        raise ValueError('exact lowercase SHA256 identity required')


def native_profile_caps(source, project, geometry_project, limits, *, cancelled=lambda:False):
    """Bind native trial motion caps without requiring empty OEM hooks."""
    profile=read_native_used_material_profile(project,source,geometry_project,limits=NativeMaterialProfileLimits(
        limits.max_source_bytes,limits.max_project_bytes,limits.max_archive_members,
        limits.max_archive_uncompressed_bytes,limits.max_events,limits.max_number_bits),cancelled=cancelled)
    jerk=min(profile.setting('outer_wall_jerk').number(),*(F(v) for key in
        ('machine_max_jerk_x','machine_max_jerk_y') for v in profile.setting(key).full_saved_vector))
    return profile,profile.setting('outer_wall_acceleration').number(),jerk


def _validate_state(state, limits):
    if type(state) is not NativeTrialState or type(state.machine) is not MachineState:
        raise ValueError('immutable native trial state required')
    machine = state.machine
    if type(machine.xyz_mm) is not tuple or len(machine.xyz_mm) != 3:
        raise ValueError('immutable XYZ required')
    for number in (*machine.xyz_mm, machine.feed_mm_min, machine.logical_e_mm, machine.retraction_debt_mm,
                   state.acceleration_mm_s2, state.classic_jerk_xy_mm_s):
        if number is not None:
            exact_number(number, limits)
    for name in ('millimetres','absolute_xyz','relative_e','volumetric_disabled','speed_override_100','flow_override_100'):
        if getattr(machine, name) is not None and type(getattr(machine, name)) is not bool:
            raise ValueError('exact modal bool or unknown required')
    if state.xy_plane is not None and type(state.xy_plane) is not bool:
        raise ValueError('exact XY plane state required')
    if state.object_token is not None and type(state.object_token) is not str:
        raise ValueError('exact object token required')
    if (machine.retraction_debt_mm is not None and machine.retraction_debt_mm<0
            or machine.feed_mm_min is not None and machine.feed_mm_min<=0
            or state.acceleration_mm_s2 is not None and state.acceleration_mm_s2<=0
            or state.classic_jerk_xy_mm_s is not None and state.classic_jerk_xy_mm_s<0):
        raise ValueError('nonnegative debt/jerk and positive feed/acceleration required')


def _join(a, b):
    known = lambda x,y: x if x == y else None
    machine = MachineState(**{f.name: (tuple(known(x,y) for x,y in zip(a.machine.xyz_mm,b.machine.xyz_mm))
        if f.name == 'xyz_mm' else known(getattr(a.machine,f.name),getattr(b.machine,f.name))) for f in fields(MachineState)})
    return NativeTrialState(machine,known(a.xy_plane,b.xy_plane),known(a.acceleration_mm_s2,b.acceleration_mm_s2),
                            known(a.classic_jerk_xy_mm_s,b.classic_jerk_xy_mm_s),known(a.object_token,b.object_token))


def _words(text, limits):
    match = re.match(r'([GM]\d+(?:\.\d+)?)',text,re.ASCII)
    if match is None:
        raise ValueError('explicit native G/M command required')
    command, position, words = match[1], match.end(), {}
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        word = re.match(r'([A-Z])([+-]?(?:\d+(?:\.\d*)?|\.\d+))',text[position:],re.ASCII)
        if word is None or word[1] in words:
            raise ValueError('malformed or duplicate native command word')
        number = F(word[2]); exact_number(number,limits)
        words[word[1]] = number
        position += word.end()
    return command, words


def _arc(state, command, words, limits):
    if words.keys()-set('XYZEFIJP') or not {'I','J'} <= words.keys() or state.xy_plane is not True:
        raise ValueError('declared XY incremental-IJ arc required')
    if any(type(v) is not F for v in state.machine.xyz_mm):
        raise ValueError('known arc start XYZ required')
    turns = words.get('P',F(1))
    if turns != 1:
        raise ValueError('only declared single-turn native arcs supported')
    machine, deposited = _advance(state.machine,'G1',{k:v for k,v in words.items() if k in 'XYZEF'})
    start, end = state.machine.xyz_mm, machine.xyz_mm
    center = start[0]+words['I'],start[1]+words['J']
    for number in (*center,turns): exact_number(number,limits)
    squared = max(sum((point[i]-center[i])**2 for i in (0,1)) for point in (start,end))
    exact_number(squared,limits)
    if squared <= 0:
        raise ValueError('nonzero native arc radius required')
    # Conservative whole-circle disk, regardless of angular sweep/handedness.
    scale = 1 << min(128,limits.max_number_bits)
    scaled = squared*scale*scale
    integer = isqrt(scaled.numerator//scaled.denominator)
    radius = F(integer if F(integer*integer) == scaled else integer+1,scale)
    bounds = NativeArcBounds(command=='G2',center,radius,(center[0]-radius,center[1]-radius,min(start[2],end[2])),
                             (center[0]+radius,center[1]+radius,max(start[2],end[2])),turns)
    for number in (radius,*bounds.xyz_min_mm,*bounds.xyz_max_mm): exact_number(number,limits)
    return replace(state,machine=machine),deposited,bounds


def interpret_native_trial(source, project, producer_bytes, context, *, geometry_project, limits, cancelled):
    if type(limits) is not NativeTrialLimits or type(context) is not NativeTrialContext:
        raise ValueError('immutable native trial context/limits required')
    for content, maximum, digest in ((source,limits.max_source_bytes,context.source_sha256),
            (project,limits.max_project_bytes,context.project_sha256),(producer_bytes,limits.max_producer_bytes,context.producer_sha256),
            (geometry_project,limits.max_project_bytes,context.geometry_project_sha256)):
        _identity(digest)
        if type(content) is not bytes or len(content)>maximum or sha256(content).hexdigest()!=digest:
            raise ValueError('stale or oversized native trial input')
    for name in ('judge_flags','opaque_command_texts','unresolved_premises'):
        entries = getattr(context,name)
        if (type(entries) is not tuple or len(entries)>limits.max_events
                or any(type(v) is not str or not v for v in entries)
                or sum(len(v) for v in entries)>limits.max_source_bytes or len(set(entries))!=len(entries)):
            raise ValueError('immutable unique declared native context strings required')
    if any(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',flag) is None for flag in context.judge_flags):
        raise ValueError('explicit native flag identifier required')
    opaque_opcodes={'M106','M73','M991','M400','M1004','M971','G39','G392','G39.3'}
    for text in context.opaque_command_texts:
        if not text.isascii() or any(ord(character)<32 for character in text):
            raise ValueError('single-line ASCII opaque command declaration required')
        command,_=_words(text,limits)
        if command not in opaque_opcodes:
            raise ValueError('opaque whitelist cannot hide state-bearing commands')
    if type(context.expected_object_token) is not str or re.fullmatch(r'[A-Za-z0-9+/]+={0,2}',context.expected_object_token) is None:
        raise ValueError('explicit native object token required')
    start,end=context.body_start_offset,context.body_end_offset
    if any(type(v) is not int for v in (start,end)) or not 0<=start<end<=len(source):
        raise ValueError('bounded body offsets required')
    if (start and source[start-1:start]!=b'\n') or source[end-1:end]!=b'\n':
        raise ValueError('complete LF-terminated body boundaries required')
    body=source[start:end]
    if len(body.splitlines())>limits.max_events:
        raise ValueError('native event budget exceeded')
    checkpoint(cancelled)
    with ZipFile(BytesIO(project)) as archive:
        infos=archive.infolist()
        if len(infos)>limits.max_archive_members or sum(info.file_size for info in infos)>limits.max_archive_uncompressed_bytes:
            raise ValueError('native project archive work budget exceeded')
    _identity(context.effective_profile_identity)
    profile,_,_=native_profile_caps(source,project,geometry_project,limits,cancelled=cancelled)
    if profile.projection_identity!=context.effective_profile_identity:
        raise ValueError('stale/forged native effective material profile identity')
    state=context.entry; _validate_state(state,limits)
    stack=[]; events=[]; effects=[]; position=start
    branch_default=False; branch_flag=False
    feature=height=width=None
    for line_number,raw in enumerate(body.splitlines(keepends=True),source[:start].count(b'\n')+1):
        checkpoint(cancelled)
        before=state; arc=None; deposited=F(0); delta=F(0); depth=len(stack)
        try:
            text=raw.split(b';',1)[0].strip().decode('ascii')
        except UnicodeDecodeError as exc:
            raise ValueError('ASCII native execution syntax required') from exc
        comment=raw.partition(b';')[2].strip()
        for prefix,name in ((b'FEATURE:', 'feature'),(b'LAYER_HEIGHT:','height'),(b'LINE_WIDTH:','width')):
            if comment.startswith(prefix):
                if stack: raise ValueError('branch-local geometry metadata unsupported')
                token=comment[len(prefix):].strip().decode('ascii')
                if name=='feature': feature=token
                else:
                    number=F(token); exact_number(number,limits)
                    if number<=0: raise ValueError('positive native geometry metadata required')
                    if name=='height': height=number
                    else: width=number
        command=''
        if text.startswith('M1002 judge_flag '):
            flag=text[len('M1002 judge_flag '):]
            if flag not in context.judge_flags or not branch_default or branch_flag:
                raise ValueError('undeclared or unmatched native judge flag')
            branch_flag=True
            command='M1002'
        elif text.startswith('M624 '):
            if text != 'M624 '+context.expected_object_token or state.object_token is not None:
                raise ValueError('foreign or malformed native object token')
            command='M624'
            state=replace(state,object_token=context.expected_object_token)
        elif text:
            command,words=_words(text,limits) if text not in context.opaque_command_texts else (text.split()[0],{})
            delta=words.get('E',F(0)) if command in ('G0','G1','G2','G3') else F(0)
            if command=='M622.1':
                if words not in ({'S':F(0)},{'S':F(1)}) or branch_default:
                    raise ValueError('invalid or unmatched branch default syntax')
                branch_default=True
            elif command=='M622':
                if words not in ({'J':F(0)},{'J':F(1)}) or len(stack)>=limits.max_branch_depth or not branch_flag:
                    raise ValueError('invalid or excessive branch nesting')
                stack.append(state)
                branch_default=branch_flag=False
            elif command=='M623':
                if words or not stack: raise ValueError('unmatched native branch close')
                state=_join(stack.pop(),state)
            elif command in ('G2','G3'):
                state,deposited,arc=_arc(state,command,words,limits)
                effects.append(NativeUnmodeledEffect(line_number,position,sha256(raw).hexdigest(),'arc-material-unavailable-as-linear-support' if delta>0 else 'native-arc-full-disk-bounds'))
            elif command=='G17':
                if words: raise ValueError('G17 parameters unsupported')
                state=replace(state,xy_plane=True)
            elif command=='M204':
                if set(words)!={'S'} or words['S']<=0: raise ValueError('explicit M204 S required')
                state=replace(state,acceleration_mm_s2=words['S'])
            elif command=='M625':
                if words or state.object_token!=context.expected_object_token: raise ValueError('unmatched native object close')
                state=replace(state,object_token=None)
            elif text in context.opaque_command_texts:
                effects.append(NativeUnmodeledEffect(line_number,position,sha256(raw).hexdigest(),'opaque-native-command-hidden-effects-premise'))
                if command in ('G39','G39.3','G392','M1004','M971'):
                    state=replace(state,machine=replace(state.machine,xyz_mm=(None,None,None),feed_mm_min=None),
                                  acceleration_mm_s2=None)
            else:
                if command=='M82': raise ValueError('absolute E forbidden in relative-E trial')
                machine,deposited=_advance(state.machine,command,words)
                state=replace(state,machine=machine)
        _validate_state(state,limits)
        events.append(NativeTrialEvent(line_number,position,raw,command,before,state,depth,delta,deposited,arc,feature,height,width))
        position+=len(raw)
    if stack or branch_default or branch_flag: raise ValueError('unclosed native branch or setup')
    checkpoint(cancelled)
    return NativeTrialTrace(fingerprint(context),tuple(events),state,tuple(effects),context.unresolved_premises)


def _anchor_from_native_trace(trace, context, byte_offset, *, acceleration_cap_mm_s2, jerk_cap_mm_s):
    if type(trace) is not NativeTrialTrace or trace.context_identity!=fingerprint(context) or type(byte_offset) is not int:
        raise ValueError('native trace/context boundary required')
    state=context.entry; depth=0; boundaries={context.body_start_offset}
    for event in trace.events:
        boundary=event.byte_offset+len(event.raw)
        if event.raw.endswith(b'\n'): boundaries.add(boundary)
        if boundary<=byte_offset:
            state=event.after
            depth=event.branch_depth+(1 if event.command=='M622' else -1 if event.command=='M623' else 0)
    if byte_offset not in boundaries: raise ValueError('complete native line boundary required')
    issues=[]; machine=state.machine
    if depth: issues.append('active-native-branch')
    if state.object_token!=context.expected_object_token: issues.append('outside-native-object')
    if not all(getattr(machine,k) is True for k in ('millimetres','absolute_xyz','relative_e','volumetric_disabled','speed_override_100','flow_override_100')):
        issues.append('unknown-native-modal-envelope')
    if any(type(v) is not F for v in (*machine.xyz_mm,machine.feed_mm_min,machine.retraction_debt_mm)):
        issues.append('unknown-native-physical-state')
    elif machine.feed_mm_min<=0 or machine.retraction_debt_mm<=0: issues.append('positive-native-feed-debt-required')
    if state.acceleration_mm_s2 is None or state.acceleration_mm_s2>acceleration_cap_mm_s2:
        issues.append('native-acceleration-cap-exceeded-or-unknown')
    if state.classic_jerk_xy_mm_s is None or state.classic_jerk_xy_mm_s>jerk_cap_mm_s:
        issues.append('native-jerk-cap-exceeded-or-unknown')
    return NativeTrialAnchor(trace.context_identity,byte_offset,state,tuple(issues))


def propose_native_trial_anchor(source,project,producer_bytes,context,byte_offset,*,geometry_project,limits,cancelled):
    trace=interpret_native_trial(source,project,producer_bytes,context,geometry_project=geometry_project,limits=limits,cancelled=cancelled)
    _,acceleration_cap,jerk_cap=native_profile_caps(source,project,geometry_project,limits,cancelled=cancelled)
    return _anchor_from_native_trace(trace,context,byte_offset,
        acceleration_cap_mm_s2=acceleration_cap,jerk_cap_mm_s=jerk_cap)
