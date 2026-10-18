"""Opt-in comment-only Orca standard-preview metadata for conditional cycles."""
from dataclasses import asdict, dataclass
from fractions import Fraction as F
from hashlib import sha256
import json
import re

from orca_plugin.gcode.linear_trace import _words


@dataclass(frozen=True)
class ConditionalPreviewAnnotationPolicy:
    max_metadata_events: int
    max_generated_comments: int
    max_decimal_places: int
    max_metadata_line_bytes: int = 256
    supplemental_feature: str = 'Outer wall'

    def __post_init__(self):
        if (any(type(v) is not int or v < 1 for v in (self.max_metadata_events, self.max_generated_comments, self.max_metadata_line_bytes))
                or type(self.max_decimal_places) is not int or not 0 <= self.max_decimal_places <= 32):
            raise ValueError('explicit bounded annotation event/comment/decimal limits required')
        if self.supplemental_feature not in ('Outer wall', 'Custom'):
            raise ValueError('consumer-supported supplemental preview role required')


@dataclass(frozen=True)
class ConditionalAnnotatedCycle:
    block: bytes
    generated_line_indices: tuple[int, ...]
    prior_comment_state: tuple[tuple[str, bytes], ...]
    identity: str


def _decimal_text(number, limit):
    if type(number) is not F or number < 0:
        raise ValueError('nonnegative exact preview dimension required')
    denominator, twos, fives = number.denominator, 0, 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    places = max(twos, fives)
    if denominator != 1 or places > limit:
        raise ValueError('preview dimension not representable in bounded decimal grammar')
    scaled = number*10**places
    digits = str(scaled.numerator).zfill(places+1)
    return digits if places == 0 else (digits[:-places]+'.'+digits[-places:]).rstrip('0').rstrip('.')


def annotate_conditional_cycle(block, *, trace, anchor_offset, frozen_paths, policy):
    """Rebuild recognized preview state and add only precisely tracked comments."""
    if (type(policy) is not ConditionalPreviewAnnotationPolicy or type(block) is not bytes
            or type(anchor_offset) is not int or type(frozen_paths) is not tuple or not frozen_paths):
        raise ValueError('exact bounded conditional annotation inputs required')
    keys = ('LAYER_HEIGHT', 'LINE_WIDTH', 'Z_HEIGHT', 'FEATURE')
    prior = {}
    if len(trace.events) > policy.max_metadata_events:
        raise ValueError('preview metadata event budget')
    for event in trace.events:
        if event.byte_offset >= anchor_offset:
            break
        text = event.raw.decode('ascii').strip()
        for key in keys:
            if not text.startswith('; '+key+':'):
                continue
            if len(event.raw) > policy.max_metadata_line_bytes:
                raise ValueError('prior preview metadata line byte budget')
            if key == 'FEATURE':
                valid = re.fullmatch(r'; FEATURE: [A-Za-z][A-Za-z /_-]*', text)
            else:
                valid = re.fullmatch('; '+key+r': ([0-9]+(?:\.[0-9]+)?)', text)
                if valid is not None and (F(valid[1]) < 0 or key != 'Z_HEIGHT' and F(valid[1]) == 0):
                    valid = None
            if valid is None:
                raise ValueError('malformed prior recognized preview metadata')
            prior[key] = event.raw.rstrip(b'\r\n')
    if set(prior) != set(keys):
        raise ValueError('unknown prior required preview metadata; restoration cannot be invented')
    newline = b'\r\n' if b'\r\n' in block else b'\n'
    paths = {f.path.path_id: f for f in frozen_paths}
    if len(paths) != len(frozen_paths):
        raise ValueError('unique frozen annotation path identities required')
    output, generated, seen = [], [], set()
    current, segment = None, 0

    def comment(content):
        if len(generated) >= policy.max_generated_comments:
            raise ValueError('generated preview comment budget')
        if len(content)+len(newline) > policy.max_metadata_line_bytes:
            raise ValueError('generated preview metadata line byte budget')
        generated.append(len(output))
        output.append(content+newline)

    for line in block.splitlines(keepends=True):
        text = line.decode('ascii').strip()
        if text.startswith('; PATH '):
            if current is not None and segment != len(current.relative_e_mm):
                raise ValueError('previous preview path emission count mismatch')
            match = re.fullmatch(r'; PATH ([A-Za-z0-9_-]+) HEIGHT .+', text)
            if match is None or match[1] not in paths or match[1] in seen:
                raise ValueError('preview marker/frozen path association mismatch')
            current, segment = paths[match[1]], 0
            seen.add(match[1])
            output.append(line)
            comment(('; FEATURE: '+policy.supplemental_feature).encode('ascii'))
            comment(('; LAYER_HEIGHT: '+_decimal_text(current.path.height_mm, policy.max_decimal_places)).encode('ascii'))
            comment(('; Z_HEIGHT: '+_decimal_text(current.path.points_mm[0][2], policy.max_decimal_places)).encode('ascii'))
            continue
        if not text or text.startswith(';'):
            output.append(line)
            continue
        command, words = _words(text)
        if command in ('G0', 'G1') and words.get('E', F(0)) > 0 and ('X' in words or 'Y' in words):
            if current is None or segment >= len(current.relative_e_mm) or words['E'] != current.relative_e_mm[segment]:
                raise ValueError('preview width does not correspond to exact frozen E segment')
            width = F(str(current.physical_width_mm[segment]))
            comment(('; LINE_WIDTH: '+_decimal_text(width, policy.max_decimal_places)).encode('ascii'))
            segment += 1
        output.append(line)
    if seen != set(paths) or current is None or segment != len(current.relative_e_mm):
        raise ValueError('incomplete frozen path annotation coverage')
    for key in keys:
        comment(prior[key])
    generated_set = set(generated)
    if b''.join(line for index, line in enumerate(output) if index not in generated_set) != block:
        raise ValueError('preview annotations changed motion-only cycle bytes')
    identity = sha256(json.dumps({'policy': asdict(policy), 'prior_state': {k: v.decode('ascii') for k, v in prior.items()},
        'paths': [asdict(f) for f in frozen_paths], 'generated_line_indices': generated},
        sort_keys=True, separators=(',', ':'), default=str).encode('ascii')).hexdigest()
    return ConditionalAnnotatedCycle(b''.join(output), tuple(generated), tuple((k, prior[k]) for k in keys), identity)
