"""Bounded request parsing and one cancellable research computation."""
from dataclasses import dataclass
import json
from math import isfinite
from threading import Event, Thread
from time import monotonic

from adaptive_subedge.engine.convex_chords import propose_convex_chord_preview
from adaptive_subedge.domain.errors import ContractError
from .limits import (MAX_REQUEST_BYTES, MAX_POSITIONS, MAX_VERTICES, MAX_TRIANGLES,
                     MAX_PAIRS, MAX_SECTION_SEGMENTS, MAX_RAYS, DEADLINE_SECONDS)


@dataclass(frozen=True, slots=True)
class PreviewRequest:
    z_mm: float
    axis: str
    width_mm: float
    end_trim_mm: float
    positions_mm: tuple[float, ...]


def parse_request(message):
    fields = {"command", "z", "axis", "width", "trim", "positions"}
    if (type(message) is not dict or set(message) != fields
            or any(type(v) is not str for v in message.values())
            or len(json.dumps(message).encode("utf-8")) > MAX_REQUEST_BYTES
            or message["command"] != "generate" or message["axis"] not in ("X", "Y")):
        raise ValueError("invalid-request")
    positions = message["positions"].split(",")
    if not 1 <= len(positions) <= MAX_POSITIONS:
        raise ValueError("position-limit")
    z, width, trim = (float(message[k]) for k in ("z", "width", "trim"))
    values = tuple(float(p.strip()) for p in positions)
    if (any(not isfinite(v) for v in (z, width, trim, *values))
            or width <= 0 or trim <= 0 or len(set(values)) != len(values)):
        raise ValueError("invalid-numeric-input")
    return PreviewRequest(z, message["axis"], width, trim, values)


def compute(snapshot, request, cancelled):
    return propose_convex_chord_preview(snapshot.mesh, request.z_mm,
        axis=request.axis, width_mm=request.width_mm, end_trim_mm=request.end_trim_mm,
        chord_positions_mm=request.positions_mm, algorithm_version="convex_axis_chords_v1",
        max_positions=MAX_POSITIONS, max_vertices=MAX_VERTICES, max_triangles=MAX_TRIANGLES,
        max_mesh_pair_checks=MAX_PAIRS, max_section_segments=MAX_SECTION_SEGMENTS,
        max_section_pair_checks=MAX_PAIRS, max_ray_directions=MAX_RAYS, cancelled=cancelled)


class PreviewJob:
    """Worker owns copies only; caller owns window/generation and marshals results."""
    def __init__(self, snapshot, request, completed, *, clock=monotonic):
        self.snapshot, self.request, self.completed = snapshot, request, completed
        self.clock = clock
        self.stop = Event()
        self.thread = Thread(target=self._run, name="Smoothificator preview", daemon=True)

    def start(self):
        self.thread.start()

    def cancel(self):
        self.stop.set()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self):
        deadline = self.clock() + DEADLINE_SECONDS
        def cancelled():
            return self.stop.is_set() or self.clock() >= deadline
        try:
            result = compute(self.snapshot, self.request, cancelled)
            if self.stop.is_set():
                self.completed("cancelled", "cancelled", None)
            elif self.clock() >= deadline:
                self.completed("incomplete", "time-limit", None)
            else:
                self.completed(result.proposals.state, result.proposals.reason, result)
        except ContractError as error:
            self.completed("rejected", str(error.reason.value), None)
        except Exception as error:
            # Contain the host callback; do not leak model text or private paths.
            self.completed("error", type(error).__name__, None)
