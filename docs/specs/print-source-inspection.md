# Print-source inspection contract

This is a bounded read-only prerequisite for the user's 2026-10-18 request to
implement printable output. Canonical basis: SPECIFICATION sections 22–29 and
32, and ARCHITECTURE adapter boundaries. It grants no injection authority.

## Resolved slice settings

Consume the exported sliced 3MF, not an installed preset with possible later
changes. Require one unambiguous project settings member and the selected
embedded plate G-code. Require exact byte equality with the separate source
G-code. Hash both inputs. Reject duplicate ZIP members, duplicate JSON keys,
non-object settings, unsupported multiple nozzles/materials and non-ASCII G-code.
Store immutable string-valued settings with their source key; no guessed values.
Read required numeric settings as exact rational decimal values. Missing, nil,
percentage-valued or malformed required values are errors, not defaults.
Retraction overrides use the filament value when non-nil, otherwise require the
printer value. Preserve the effective source key. Per-extruder height 0 means
use the required positive global printable height. Travel Z speed 0 is an
unresolved profile sentinel, never interpreted as a zero-duration move.

Compare explicitly selected critical G-code CONFIG_BLOCK entries with the
resolved 3MF values, including numeric equivalence of singleton serialized
arrays. Missing or differing entries reject the association. This limited
comparison is not the canonical full settings/geometry fingerprint.
Repeated consumed CONFIG_BLOCK keys reject even if equal. Repeated unconsumed
keys are listed as unresolved evidence, not silently chosen or treated as a
validated full configuration. The actual fixture repeats wipe_tower_x/y.

## Linear execution trace

The G-code reader preserves original bytes, offsets, line numbers and order.
It accepts a small explicit grammar: G0/G1, G21, G90, M83, G92 E, M200 D0,
M220 S100 and M221 S100. Reject unknown commands, malformed or duplicate words,
extra parameters, XYZ resets, firmware retract, arcs and unsupported modes.
Initial position, modes, feed, logical E and physical retraction debt are
unknown; do not invent a homed origin or zero debt. A caller may supply an
explicit initial debt for arithmetic tests/context reconstruction; this alone
is not physical validation. G92 E never changes debt. Positive E repays known
debt before counting deposition. Feed remains modal. All motion requires
known millimetres/absolute XYZ/relative E. Missing coordinates stay unknown.
No records beyond the first unsupported line may be treated as interpreted.
E-bearing moves and G92 E also require explicitly known linear-E units (M200
D0). Unknown volumetric state cannot be interpreted as filament millimetres.
G90 conservatively invalidates the previous relative-E assertion; require M83
again instead of assuming firmware-specific G90/M83 precedence.
Non-motion printer commands need separate firmware-specific review before
this grammar can be extended. No broad ignore-M-command rule is allowed.

## Output

A CLI emits JSON inspection evidence only, never G-code. All export/injection
authority remains false. Report unsupported source commands and unresolved
profile semantics. Printer settings do not prove a nozzle/hotend collision
envelope, continuous support, converged surface errors, thermal startup,
immutable executable Plan or restoration correctness. Those remain separate
hard gates; inspection success cannot satisfy them.
