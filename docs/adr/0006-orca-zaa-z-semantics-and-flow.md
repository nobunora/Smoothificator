# ADR-0006: Normalize Orca ZAA path Z offsets and local flow

Status: Accepted
Date: 2026-09-29

## Context
Orca ContourZ stores ZAA path point Z as an offset d from the layer nominal print Z, not as absolute machine Z.

GCode.cpp emits:
- z_abs = nominal_z + d
- for non-ironing paths, extrusion is multiplied by (path.height + d) / path.height

Treating bound ExtrusionPath point Z as absolute, or treating mm3_per_mm as spatially constant after ZAA, would produce incorrect surface predictions.

## Decision
Orca Adapter owns conversion.

For each ZAA/ordinary path segment:
- raw path z is preserved for diagnostics
- absolute nozzle Z is normalized as layer.print_z + z_offset
- effective local bead height for ZAA non-ironing is layer/path height + z_offset
- effective local mm3_per_mm is nominal mm3_per_mm multiplied by effective_height / nominal_height

Normal planar paths with zero offset keep nominal values.

v1 printable mode requires:
- ironing disabled
- scarf/sloped seam disabled
so nonzero path-Z offsets have an unambiguous ZAA interpretation.

## Test impact
Create parity fixtures from Orca source behavior and verify normalized absolute Z/flow.
