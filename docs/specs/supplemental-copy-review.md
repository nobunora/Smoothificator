# Byte-preserving supplemental copy contract

2026-10-18 scope: subsequent bounded development after
`supplemental-z-hop-review.md`. Canonical basis: SPECIFICATION sections 24–27,
29, 32 and ADR-0031. This tools-only experiment does not mutate the source or
grant physical-print authority; geometric quality improvement remains deferred
by user instruction. Existing production hook/print-readiness gates stay closed.

The parent repository review validates this bounded pure-bytes implementation:
existing cycle composer accepts immutable saved state; existing strict reader
can independently replay the supported synthetic source and composed blocks;
the real research source is still outside that reader's supported grammar.
No real anchors may be invented to bypass this limitation.

## Inputs and ownership

Use frozen insertion requests anchored to SHA256 of the full original source,
an exact complete-line byte boundary, and an independently reconstructed saved
MachineState. Caller initial-state assertions are synthetic context only. The
anchor factory must trace the entire source and reject unknown or malformed
commands anywhere, then derive saved state at the boundary. Verify supplied
anchor objects again at composition; a dataclass constructor is not proof.
Multiple offsets must be unique and chronological. No insertion may split
CRLF, a command, or an unterminated final line. Existing markers reject repeat
insertion. No source/parser safety weakening is authorized by this task.

## Assembly and verification

Compose each existing unverified retracted supplemental cycle and independently
replay it from saved state, requiring exact final state identity. Concatenate
untouched original byte slices with inserted ASCII blocks. Record output spans
and source/output hashes; deleting precisely those spans must reconstruct the
original bytes. Preserve original newline sequences, comments and ordering.
Unsupported source encodings still reject through the current reader contract.
No output file write, atomic original replacement, runtime hook or printer I/O.
All result authority flags remain false. This is copy-composition evidence, not
canonical immutable PlanStore publication or final tool-clearance validation.

## Tests

Mixed LF/CRLF, intact comments, unchanged original chronology, complete and
incomplete final lines, multiple insertions, replay/restoration, stale hashes,
forged state, unsafe/interior offsets, unknown commands after an anchor, duplicate
offsets, repeated marker and exact source reconstruction. Run focused checks,
architecture, full regression; parent review and independent review follow.
