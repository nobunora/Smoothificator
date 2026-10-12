# ADR-0008: Restrict v1 G-code execution to relative-E Bambu profile family

Status: Accepted
Date: 2026-09-29

## Context
The injector can theoretically preserve both absolute and relative extrusion state, firmware retract, arc fitting and line-number/checksum output. Supporting all of them before the first physical PoC increases the safety-critical parser/emitter surface substantially.

Orca's default `use_relative_e_distances` is true. Firmware retraction and line numbering default off. Current Bambu process profiles inspected use arc fitting off.

## Decision
Initial printable v1 requires:
- `use_relative_e_distances = true`
- `use_firmware_retraction = false`
- `gcode_add_line_number = false`
- `enable_arc_fitting = false`
- spiral vase off
- ironing off
- scarf/sloped seam off
- support/raft off
- single tool
- supported current Bambu 0.4 mm machine profile family
- validated motion-neutral before/layer-change template environment

Parser still tracks M82/M83/G92 and unsupported states for diagnostics, but Injection is disabled outside the above contract.

## Rationale
This reduces the first physical injector to the state model actually needed by the target profile family. General absolute-E, firmware retract, arcs and other printer dialects are later ADRs after successful PoC.

## Test impact
Golden fixtures must cover A1, P1S/P1P and X1 Carbon current stock 0.4 mm profiles with relative extrusion.
