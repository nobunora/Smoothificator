# Supplemental explicit Z-hop contract

User instruction (2026-10-18): defer geometric error improvement, preserve the
original slicer's Z-hop behavior, and emit explicit Z-hop code for supplemental
travel. Thickness order is ascending **within one original-layer batch**;
never reorder original layers or the original G-code. This is an offline
execution-block experiment, not physical-print authorization. Quality-error
improvement is not a prerequisite for this experiment. Support, actual absolute
height, tool-body clearance and downstream collision are separate questions.

## Bounded contract / repository disposition

Validated for a standalone offline block composer in tools only. Canonical
sources: SPECIFICATION sections 23–27 and 29. Existing source-profile inspection
and MachineState types supply immutable inputs. Production hooks, injection
gates and original bytes remain unchanged. The current full-source interpreter
still stops at unsupported commands; never invent a real insertion anchor.

Inputs require fully declared mm/absolute XYZ/relative E, disabled volumetric
mode, 100% file overrides, actual XYZ/feed/logical E and positive saved physical
retraction debt. Restart-extra must be zero and firmware retract disabled.
Profiles provide hop, retract speeds, diameter, flow factors, speed/volume caps
and positive printable height. Explicit positive XY/Z speed caps are required.
The requested bead-height bound must not exceed 90 percent of saved layer
height. Read machine XYZ speed vectors from the same sliced profile and require
their complete equality with the G-code CONFIG_BLOCK. Use their minimum across
exported modes as conservative requested caps, without guessing a current mode.
For explicit supplemental vertical travel, a saved travel_speed_z of zero
selects the saved XY travel request, then caps it by the machine Z-speed vector.
This defines our explicit moves, not the original slicer's motion timing.
Formatting precisions are explicit research inputs, not claims of Orca parity.

Within a batch, each candidate must have the same supporting original-layer
floor. Sort by physical height, breaking ties by ID. Top Z must be between the
floor and the next original-layer Z; ordering does not prove noninterference.

`Zsafe=max(saved_actual_z, target_upper_z)+profile_z_hop`. Round the ceiling
**up**, ensure it is within the tool height limit and strictly above every
emitted candidate top and saved Z. Never clamp to the machine ceiling. For
each path: raise vertically while retracted, travel XY at Zsafe, descend,
unretract exactly the saved debt, print, retract the same debt, raise. Return
XY at Zsafe, descend to actual saved Z, restore logical E without changing
physical debt, and restore the exact saved modal F. Never use the nominal
upper-layer Z as a substitute for actual saved Z.

Quantize XY/Z before computing emitted lengths and E; reject collapsed moves
or E=0. Apply existing stadium/command-flow formulas. Recompute the volume-rate
cap from quantized E. Restore values must be exactly representable. Final
profile/family quantization parity, matched external-wall speed, chronological
support and nozzle-body/downstream sweeps are not certified by this composer.

Actual review artifacts may contain candidate-to-candidate transition JSON only;
entry/exit anchors remain unresolved. A real insertion block is not generated
from guessed anchor state. Synthetic blocks are test fixtures, marked unverified.
