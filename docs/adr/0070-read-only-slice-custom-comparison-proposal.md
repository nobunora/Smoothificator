# ADR-0070: Read-only sliced-baseline Custom comparison proposal

Status: Proposed
Date: 2026-10-17

## Decision to review

The separate research preview may eventually display its candidate bands beside
the original sliced paths in one standard Orca G-code Preview. This requires a
new, disposable viewer file derived from a specific sliced source. ADR-0069
continues to govern the Custom-only scene; its prohibition on reading and
appending original G-code remains in force until this proposal is accepted.

This proposal gives no printable Plan or postprocess authority. The candidate
bands are unscored and unvalidated for support, clearance and physical output.
The derivative must be labeled VIEW_ONLY and print-unvalidated. It must never
replace the source, enter an export/postprocess path, or be sent to a printer.

## Bounded native behavior

The pinned Orca source increments layer identity at layer-change tags, rather
than merging moves by equal Z. An end-of-file append inherits the last layer
identity, so it cannot recover an earlier target layer by matching Z and may
also follow end-of-print commands. Native plugin APIs expose no viewer reload.
The only proposed standard Preview route is to copy source bytes into a separate
unique file while inserting a Custom block inside the exact target layer, then
open that derivative manually in a separate Orca process.

The first supported input must be a single-tool, millimetre, conventional
linear-motion slice with a uniquely identified nonfinal target layer and known
modal XYZ/E, feed, role, forced-width/height, extrusion/retraction, unit and
flow state at the insertion point. Inactive wipe, flushing and skippable
contexts must be proven. Unknown
commands, machine-frame offsets, tool changes, nonstandard line/checksum
formats, ambiguous layers or source-to-model coordinate association fail closed.
The candidate coordinates must be proven to match the sliced model instance;
matching a filename or model label is insufficient.

The adapter would insert before the next layer-change tag, without adding a
layer-change tag. It must preserve the exact original byte stream as ordered
segments, all original moves and comments, and restore modal XYZ/E, feed,
position, role, forced-width/height and extrusion state after the Custom block.
Orca's extruded-last-Z state must also remain equivalent. The candidate
block is not allowed to alter the interpretation of any later original line.
The parser must reject any state that cannot be established or restored.

Before publication, verify the source's identity and digest again, verify that
removing only the inserted byte interval from the derivative reproduces the
source byte-for-byte, and parse the derivative for target-layer placement,
Custom classification, positive width/E and unchanged later original moves.
Use exclusive creation in plugin-owned storage, bounded streaming I/O,
deadline/cancellation checks and deletion of failed or stale derivatives.
Opening in the current modeling window can replace the project, so the user
must manually open the unique derivative in a separate viewer process.

## Evidence and open issues

Pinned source 86905a8a20d5887f3b13017e66cd897766334bd3:
`GCodeProcessor.cpp:4558-4561,7273` assigns layer IDs;
`GCodeProcessor.cpp:4062,5104,7223-7249` assigns parsed line/move IDs;
`GCodeProcessor.cpp:5090-5098,6220-6286` owns movement and E modes;
`GCodeProcessor.cpp:4296-4302,4446-4456,5070-5079,5150-5164,5182-5183`
owns viewer role, height/width, extrusion and last-extruded-Z behavior;
`PluginHostApp.cpp:158-188` has no viewer open API;
`Plater.cpp:18075-18106` skips same-name reload and may close the project.

Before acceptance, review the actual source acquisition API, modal-state parser
coverage, byte-preserving insertion grammar, coordinate provenance, and whether
a viewer derivative containing normal printer commands creates unacceptable
accidental-output exposure. If any cannot be closed, retain separate baseline
and Custom-only views and do not claim same-plan comparison.
