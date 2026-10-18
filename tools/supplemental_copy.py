"""Pure byte-copy experiment for synthetic sources; never print authorization."""
from dataclasses import dataclass, field
from fractions import Fraction
from hashlib import sha256

from orca_plugin.gcode.linear_trace import MachineState, trace_linear_execution
from tools.supplemental_z_hop import HopPolicy, SupplementalPath, compose_retracted_cycle


@dataclass(frozen=True)
class SyntheticInsertionAnchor:
    source_sha256: str
    byte_offset: int
    initial_state: MachineState
    saved_state: MachineState


@dataclass(frozen=True)
class SupplementalInsertion:
    anchor: SyntheticInsertionAnchor
    paths: tuple[SupplementalPath, ...]
    upper_z_mm: Fraction
    policy: HopPolicy


@dataclass(frozen=True)
class InsertionSpan:
    source_byte_offset: int
    output_start: int
    output_end: int


@dataclass(frozen=True)
class SupplementalCopy:
    output_bytes: bytes
    source_sha256: str
    output_sha256: str
    insertion_spans: tuple[InsertionSpan, ...]
    printable_authorized: bool = field(default=False, init=False)
    runtime_injection_authorized: bool = field(default=False, init=False)


def _validated_source(source, initial_state):
    if type(source) is not bytes:
        raise ValueError("exact source bytes required")
    if type(initial_state) is not MachineState:
        raise ValueError("explicit synthetic MachineState required")
    if any(marker in source for marker in (b'SUPPLEMENTAL_CYCLE_', b'ADAPTIVE_SUBEDGE_')):
        raise ValueError("existing supplemental/plugin marker")
    trace = trace_linear_execution(source, initial_state=initial_state)
    if trace.failure is not None:
        raise ValueError(f"unsupported source at byte {trace.failure.byte_offset}: {trace.failure.reason}")
    boundaries = {0}
    offset = 0
    for raw in source.splitlines(keepends=True):
        offset += len(raw)
        if raw.endswith(b'\n'):
            boundaries.add(offset)
    return trace, boundaries


def synthetic_anchor(source: bytes, byte_offset: int, *, initial_state: MachineState):
    """Reconstruct an anchor; explicit initial state is synthetic evidence only."""
    trace, boundaries = _validated_source(source, initial_state)
    if type(byte_offset) is not int or byte_offset not in boundaries:
        raise ValueError("complete-line byte boundary required")
    saved = initial_state
    for record in trace.records:
        if record.byte_offset >= byte_offset:
            break
        saved = record.after
    return SyntheticInsertionAnchor(sha256(source).hexdigest(), byte_offset, initial_state, saved)


def compose_supplemental_copy(source: bytes, insertions: tuple[SupplementalInsertion, ...]):
    """Return an unverified copy, validating anchors and exact byte reconstruction."""
    if type(insertions) is not tuple or not insertions:
        raise ValueError("nonempty immutable insertion tuple required")
    blocks = []
    previous_offset = -1
    initial_state = None
    for insertion in insertions:
        if type(insertion) is not SupplementalInsertion or type(insertion.anchor) is not SyntheticInsertionAnchor:
            raise ValueError("exact immutable insertion and anchor required")
        anchor = insertion.anchor
        rebuilt = synthetic_anchor(source, anchor.byte_offset, initial_state=anchor.initial_state)
        if rebuilt != anchor:
            raise ValueError("source hash or reconstructed anchor state mismatch")
        if initial_state is None:
            initial_state = anchor.initial_state
        if anchor.initial_state != initial_state:
            raise ValueError("one synthetic initial context required")
        if anchor.byte_offset <= previous_offset:
            raise ValueError("unique chronological insertion offsets required")
        previous_offset = anchor.byte_offset
        block = compose_retracted_cycle(anchor.saved_state, insertion.paths, insertion.upper_z_mm, insertion.policy)
        # Follow the preceding complete line; at byte zero use the first line.
        local_line = source[:anchor.byte_offset].splitlines(keepends=True)[-1:] if anchor.byte_offset else source.splitlines(keepends=True)[:1]
        if local_line and local_line[0].endswith(b'\r\n'):
            block = block.replace(b'\n', b'\r\n')
        replay = trace_linear_execution(block, initial_state=anchor.saved_state)
        if replay.failure is not None or replay.final_state != anchor.saved_state:
            raise ValueError("supplemental cycle did not restore exact anchor state")
        blocks.append((anchor.byte_offset, block))
    chunks, spans = [], []
    source_cursor = output_cursor = 0
    for offset, block in blocks:
        original = source[source_cursor:offset]
        chunks.extend((original, block))
        output_cursor += len(original)
        spans.append(InsertionSpan(offset, output_cursor, output_cursor + len(block)))
        output_cursor += len(block)
        source_cursor = offset
    chunks.append(source[source_cursor:])
    output = b''.join(chunks)
    recovered, cursor = [], 0
    for span in spans:
        recovered.append(output[cursor:span.output_start])
        cursor = span.output_end
    recovered.append(output[cursor:])
    if b''.join(recovered) != source:
        raise ValueError("source reconstruction failed")
    replay = trace_linear_execution(output, initial_state=initial_state)
    original = trace_linear_execution(source, initial_state=initial_state)
    if replay.failure is not None or replay.final_state != original.final_state:
        raise ValueError("composed copy execution mismatch")
    return SupplementalCopy(output, sha256(source).hexdigest(), sha256(output).hexdigest(), tuple(spans))
