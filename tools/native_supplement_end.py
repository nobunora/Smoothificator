"""Opt-in native trial end retraction; never changes the legacy formatter."""
from dataclasses import dataclass
from fractions import Fraction as F

from tools.supplemental_z_hop import _text


@dataclass(frozen=True)
class NativeSupplementEndPolicy:
    retract_mm: F = F('.8')
    retract_speed_mm_s: F = F(30)
    deretract_speed_mm_s: F = F(30)
    wipe_mm: F = F('.5')
    stationary_fraction: F = F('.5')

    def __post_init__(self):
        if any(type(v) is not F or v <= 0 for v in
               (self.retract_mm, self.retract_speed_mm_s, self.deretract_speed_mm_s, self.wipe_mm)):
            raise ValueError('positive exact native end parameters required')
        if type(self.stationary_fraction) is not F or not 0 < self.stationary_fraction < 1:
            raise ValueError('strict staged retraction fraction required')


def apply_native_end_policy(block, frozen, anchor, hop, end, *, start_deretract_speed_mm_s=None):
    """Replace a single known cycle end, rejecting unsupported reverse geometry.

    Wipe follows only the last axis-aligned deposited segment, clipped to it.
    Debt is reconciled at the raised ceiling before returning to source XYZ.
    """
    if type(end) is not NativeSupplementEndPolicy:
        raise ValueError('immutable native end policy required')
    if end.retract_speed_mm_s > hop.retract_speed_mm_s or end.deretract_speed_mm_s > hop.deretract_speed_mm_s:
        raise ValueError('native end E speed exceeds saved profile cap')
    start_speed = end.deretract_speed_mm_s if start_deretract_speed_mm_s is None else start_deretract_speed_mm_s
    if type(start_speed) is not F or not 0 < start_speed <= hop.deretract_speed_mm_s:
        raise ValueError('native start E speed exceeds saved profile cap')
    points = frozen.path.points_mm
    a, b = points[-2:]
    changed = [i for i in range(3) if a[i] != b[i]]
    if len(changed) != 1 or changed[0] == 2:
        raise ValueError('native reverse wipe requires axis-aligned final deposited segment')
    axis = changed[0]
    distance = min(end.wipe_mm, abs(b[axis]-a[axis]))
    target = list(b)
    target[axis] += distance if a[axis] > b[axis] else -distance
    xyz = lambda number: _text(number, hop.xyz_places)
    e = lambda number: _text(number, hop.e_places)
    feed = lambda speed: _text(speed*60, 3)
    debt = anchor.retraction_debt_mm
    old_start = f'G1 E{e(debt)} F{feed(hop.deretract_speed_mm_s)}\n'.encode()
    old_end = f'G1 E-{e(debt)} F{feed(hop.retract_speed_mm_s)}\n'.encode()
    if block.count(old_start) != 1 or block.count(old_end) != 1:
        raise ValueError('native end formatter contract drift')
    stationary = end.retract_mm*end.stationary_fraction
    moving = end.retract_mm-stationary
    # Both XY and E speeds are bounded independently for the coordinated move.
    wipe_speed = min(hop.xy_speed_mm_s, distance*end.retract_speed_mm_s/moving)
    # Floor coordinated F to the formatter lattice; never raise either cap.
    exact_feed = wipe_speed*60*1000
    emitted_feed = F(exact_feed.numerator//exact_feed.denominator,1000)
    if emitted_feed <= 0:
        raise ValueError('native wipe feed collapsed at command precision')
    replacement = (f'G1 E-{e(stationary)} F{feed(end.retract_speed_mm_s)}\n'
        f'G1 X{xyz(target[0])} Y{xyz(target[1])} E-{e(moving)} F{_text(emitted_feed,3)}\n').encode()
    block = block.replace(old_start, f'G1 E{e(debt)} F{feed(start_speed)}\n'.encode())
    block = block.replace(old_end, replacement)
    # Reconcile only after the immediately following Z hop; preserve physical debt.
    lines = block.splitlines(keepends=True)
    wipe_index = next(i for i, line in enumerate(lines) if line == replacement.splitlines(keepends=True)[1])
    if not lines[wipe_index+1].startswith(b'G1 Z'):
        raise ValueError('native end ceiling transition drift')
    adjustment = end.retract_mm-debt
    if adjustment:
        speed = end.deretract_speed_mm_s if adjustment > 0 else end.retract_speed_mm_s
        lines.insert(wipe_index+2, f'G1 E{e(adjustment)} F{feed(speed)}\n'.encode())
    return b''.join(lines)
