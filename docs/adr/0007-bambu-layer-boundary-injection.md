# ADR-0007: Inject at validated Bambu structural layer boundary using safe-ceiling travel

Status: Accepted
Date: 2026-09-29

## Context
Sub-edge G-code must be inserted without changing assumptions of Orca/Bambu layer-change custom G-code.

Current Orca GCode.cpp emits, in order:
1. reserved layer-change/Z/height tags
2. before_layer_change_gcode
3. change_layer(print_z) (actual structural Z transition/retraction behavior)
4. layer_change_gcode
5. ;_SET_FAN_SPEED_CHANGING_LAYER

Current stock Bambu A1/P1P/P1S/X1 Carbon 0.4 mm layer_change_gcode templates contain progress/notification M73/M991 only and no XYZ/E motion. before_layer_change_gcode is empty through the inspected inheritance chain.

## Decision
Initial printable dialect is a validated Bambu/Orca single-tool profile family.

Injection anchor for interval [Z0,Z1] is inside the validated supported Bambu layer-boundary block, identified with structural tags and the changing-layer marker/state. ADR-0013 supersedes the earlier assumption that the physical upper-layer Z transition has necessarily completed at this point; actual emitted machine state is authoritative.

Before any injection, validate the configured custom layer-change environment. Unknown/motion-producing before/layer-change behavior disables injection.

## Safe-ceiling travel invariant
Let Zsafe >= Z1 + configured travel lift.

For every added path:
1. remain/retract at safe state
2. raise to Zsafe before non-extruding XY travel
3. travel XY to path start at Zsafe
4. descend vertically to planned nozzle Z
5. unretract/print path
6. retract
7. raise to Zsafe before any next XY travel

After final path:
- return at Zsafe to the saved layer-boundary XY
- restore the exact parsed physical machine state required by ADR-0013
- restore E/feed/retraction/modal state according to ADR-0018
- resume original G-code

No non-extruding XY travel below Zsafe is allowed in v1.

## Bambu profile gates
Initial physical PoC requires:
- supported Bambu 0.4 mm single-tool profile
- arc fitting disabled
- no G-code line numbering/checksum mode
- firmware retraction disabled unless explicitly implemented/tested
- spiral vase off
- ironing off
- scarf seam off
- support/raft off
- classic post_process empty
- no other slicing-pipeline plugin

Timelapse/custom code after the anchor is left untouched because the injector restores the exact saved boundary state before resuming.

## Test impact
Golden G-code fixtures for A1/P1S/X1 Carbon profiles and layer-change state restoration are required before physical printing.


Partial supersession: ADR-0013 replaces the old restore-Z semantics. ADR-0018 defines the v1 retraction-state procedure. The safe-ceiling/no-low-Z-XY invariant remains authoritative.
