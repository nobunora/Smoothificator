"""Strict read-only linear modal trace; never a printable-output certificate."""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import re


WORD = re.compile(r"([A-Z])([+-]?(?:\d+(?:\.\d*)?|\.\d+))", re.ASCII)
COMMAND = re.compile(r"([GM])([0-9]+)", re.ASCII)


@dataclass(frozen=True)
class MachineState:
    xyz_mm: tuple[F | None, F | None, F | None] = (None, None, None)
    millimetres: bool = False
    absolute_xyz: bool = False
    relative_e: bool = False
    feed_mm_min: F | None = None
    logical_e_mm: F | None = None
    retraction_debt_mm: F | None = None
    volumetric_disabled: bool = False
    speed_override_100: bool = False
    flow_override_100: bool = False


@dataclass(frozen=True)
class ExecutionRecord:
    line_number: int
    byte_offset: int
    raw: bytes
    command: str
    before: MachineState
    after: MachineState
    extruded_filament_mm: F | None


@dataclass(frozen=True)
class TraceFailure:
    line_number: int
    byte_offset: int
    reason: str


@dataclass(frozen=True)
class ExecutionTrace:
    records: tuple[ExecutionRecord, ...]
    failure: TraceFailure | None
    final_state: MachineState


def _words(text):
    match = COMMAND.match(text)
    if not match:
        raise ValueError("explicit supported G/M command required")
    command = match[1] + str(int(match[2]))
    position = match.end()
    values = {}
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        word = WORD.match(text, position)
        if word is None:
            raise ValueError("malformed/unsupported command word")
        key, number = word.groups()
        if key in values:
            raise ValueError(f"duplicate word: {key}")
        values[key] = F(number)
        position = word.end()
    return command, values


def _advance(state, command, values):
    if command in ("G0", "G1"):
        if values.keys() - set("XYZEF"):
            raise ValueError("unsupported motion parameter")
        if not (state.millimetres and state.absolute_xyz and state.relative_e):
            raise ValueError("motion requires explicit G21/G90/M83")
        xyz = tuple(values.get(key, old) for key, old in zip("XYZ", state.xyz_mm))
        feed = values.get("F", state.feed_mm_min)
        if feed is not None and feed <= 0:
            raise ValueError("positive feed required")
        delta = values.get("E", F(0))
        if "E" in values and not state.volumetric_disabled:
            raise ValueError("linear E requires explicitly disabled volumetric mode")
        debt = state.retraction_debt_mm
        if debt is None:
            deposited = None if delta > 0 else F(0)
        else:
            deposited = max(F(0), delta - debt)
            debt = max(F(0), debt - delta)
        logical = state.logical_e_mm
        if logical is not None:
            logical += delta
        return replace(state, xyz_mm=xyz, feed_mm_min=feed,
                       logical_e_mm=logical, retraction_debt_mm=debt), deposited
    if command == "G92":
        if set(values) != {"E"}:
            raise ValueError("only G92 E is supported; XYZ origin remap rejected")
        if not (state.millimetres and state.volumetric_disabled):
            raise ValueError("G92 E requires known millimetres and linear-E units")
        return replace(state, logical_e_mm=values["E"]), F(0)
    if command in ("G21", "G90", "M83"):
        if values:
            raise ValueError("mode command takes no parameters")
        if command == "G90":
            # Firmware differs on whether G90 clears M83. Require M83 again;
            # do not reuse a potentially stale relative-E assertion.
            return replace(state, absolute_xyz=True, relative_e=False), F(0)
        key = {"G21": "millimetres", "G90": "absolute_xyz", "M83": "relative_e"}[command]
        return replace(state, **{key: True}), F(0)
    expected = {"M200": ("D", F(0), "volumetric_disabled"),
                "M220": ("S", F(100), "speed_override_100"),
                "M221": ("S", F(100), "flow_override_100")}
    if command in expected:
        key, number, field = expected[command]
        if values != {key: number}:
            raise ValueError(f"unsupported {command} execution envelope")
        return replace(state, **{field: True}), F(0)
    raise ValueError(f"unsupported command: {command}")


def trace_linear_execution(source: bytes, *, initial_state: MachineState | None = None) -> ExecutionTrace:
    """Stop at first unknown command, retaining only the interpreted prefix.

    A supplied initial state is caller evidence, not inferred physical truth.
    Initial uncertainty is retained rather than assuming homing or zero debt.
    """
    state = MachineState() if initial_state is None else initial_state
    if type(state) is not MachineState:
        raise TypeError("exact MachineState required")
    if type(state.xyz_mm) is not tuple or len(state.xyz_mm) != 3:
        raise ValueError("three-coordinate initial XYZ tuple required")
    for value in (state.millimetres, state.absolute_xyz, state.relative_e,
                  state.volumetric_disabled, state.speed_override_100, state.flow_override_100):
        if type(value) is not bool:
            raise ValueError("exact bool initial mode required")
    for value in (*state.xyz_mm, state.feed_mm_min, state.logical_e_mm, state.retraction_debt_mm):
        if value is not None and type(value) is not F:
            raise ValueError("initial numeric state requires exact Fraction")
    if state.retraction_debt_mm is not None and state.retraction_debt_mm < 0:
        raise ValueError("negative initial retraction debt")
    if state.feed_mm_min is not None and state.feed_mm_min <= 0:
        raise ValueError("positive initial feed required")
    records = []
    offset = 0
    for number, raw in enumerate(source.splitlines(keepends=True), 1):
        try:
            if any((byte < 32 and byte not in (9, 10, 13)) or byte == 127 for byte in raw):
                raise ValueError("unsupported control character")
            text = raw.decode("ascii").split(";", 1)[0].strip()
            if text:
                command, values = _words(text)
                after, deposited = _advance(state, command, values)
                records.append(ExecutionRecord(number, offset, raw, command,
                                                state, after, deposited))
                state = after
        except ValueError as exc:
            return ExecutionTrace(tuple(records), TraceFailure(number, offset, str(exc)), state)
        offset += len(raw)
    return ExecutionTrace(tuple(records), None, state)
