# Restored source adapter research — 2026-10-18

## Decision

Implement a **read-only nominal body event adapter**, not a full firmware interpreter or a real insertion-anchor factory. The current restored source has no dominating reset that establishes the complete execution envelope after opaque startup. A sound adapter can preserve exact source association, tokenize the supported body, retain control-flow/unknown state, and route nominal structural geometry. It must not produce a MachineState accepted as execution evidence merely by ignoring unsupported commands.

A complete modal execution certificate remains blocked on explicit missing firmware/profile assumptions and fixture evidence. The strict linear_trace contract should remain unchanged. No implementation, reslicing, source mutation or printer operation was performed during this investigation.

## Inputs verified

- Restored source: artifacts/revolved-exponential-execution/original-slice/plate_1.gcode, SHA256 `8bd04a71933ddef80372014d8bec8d9fe71674a416f1e8efdd1e53c0816726f3`.
- Sliced project: same folder/sliced.3mf, SHA256 `6355256385beac751ac3659463bf109e3cee9dadada1b5bad51b62b917e51050`.
- Independently verified Metadata/plate_1.gcode equals separate source bytes.
- Existing source_profile reads exact association/resolved settings; linear_trace rejects unknown commands and preserves initial uncertainty. Canonical SPECIFICATION24A–27 requires known units, XYZ/E modes, volumetric state, overrides and saved positive retraction, with exact restoration. Sections18/23–24/29/30 retain association, quantization, clearance and profile gates.

The ring-intent stage is associated with the older research source/project, not this restored source. Never reuse its line numbers or offsets as restored-source anchors. Rebuild association and structural references from these exact restored bytes.

## Why the body prologue is insufficient

At source lines1242–1244, unconditional G90/G21/M83 establishes explicit millimeters, absolute XYZ and relative-E tokens in a nominal model. Lines1261–1263 write absolute X/Y and Z, so logical coordinates converge in that model despite unknown earlier coordinate values. This does not settle origin/mesh/tool/firmware execution mapping.

Missing assertions persist:

- No M200 occurs anywhere: firmware volumetric-E disabled state cannot be inferred from absence or profile preference.
- Startup M220 S100/M221 S100 at818–819 precedes opaque manufacturer operations. No firmware evidence establishes every intervening operation preserves those states; live overrides remain external assumptions.
- Unconditional startup G92 E0 exists at860/867/871/875, but is followed by proprietary operations. A G92 resets logical E only, never physical retraction debt. The positive startup extrusion sequence1199–1209 may exhaust a *bounded* known debt, but no such bound/initial debt is established. Treating arbitrary unknown debt as zero would invent evidence.
- All62 in-body G92 E resets lie inside conditionals (depth1). No unconditional G92 E occurs again until23016, at shutdown. Thus they cannot universally establish body logical-E identity.
- Branches include motion and opaque detection operations. They can differ in XYZ/feed/logicalE/acceleration and possibly hidden physical state. An unconditional later XYZ/feed write can recover those specific nominal fields; it does not recover debt, volumetric units, tool context, hidden coordinate mappings or unknown firmware side effects.
- Existing MachineState does not own acceleration/jerk/envelope state. Source M204 must be tracked in a separate richer nominal state if the adapter reports timing/restoration context; do not silently extend the composer’s guarantees.

Therefore no present body entry is a proven fully specified real anchor. A caller-supplied synthetic debt/volumetric assertion remains synthetic, even if nominal body replay is otherwise exact.

## Actual control flow and body scope

Whole source has130 balanced M622/M623 pairs, maximum nesting3, final depth0. Body interval1242–23015 has124 pairs. It contains31 timelapse branches and nested head-wrap/detection branches. M622.1 is a distinct opcode, not another opening delimiter. M1002 carries nonstandard textual payload such as `judge_flag timelapse_record_flag`; preserve it, do not force it through generic numeric-word parsing.

Example8199–8212 conditionally performs G92, Z/XY travel, shutter/camera operations and feed changes. Example8215–8244 contains three nested judged scopes and G392/G90/M83/M204/G0/G39.3. G39.3 can neither be treated as ordinary Z motion nor assumed to preserve all state: no firmware contract was obtained. After8250–8253, explicit acceleration/XY/Z/E commands can converge selected nominal fields, but unknown logicalE/debt/path execution remain distinct.

Startup G91 at1011 precedes20 G2 wiping arcs (1013–1033); G90 follows1035. These arcs are outside the chosen nominal body. G380 startup motions at801–802 and945–984 likewise remain opaque startup operations; their S2/S3 behavior must not be reconstructed as ordinary linear motion. Skipping startup is allowed only by representing unknown startup effects, not by certifying them harmless.

Comments `SKIPPABLE_START`/`SKIPTYPE` are routing metadata, not permission to discard blocks from original bytes or proof that printer execution skips them. Object selection M624/M625 can also alter actual executed paths when external exclusion state is enabled; preserve object scope and mark external decision unresolved.

## Exhaustive lexical inventory and semantic obligations

Counts below are nominal tokens, not firmware proof. Groups are investigation routing, not a harmless-command allowlist. Every opcode in the66-opcode receipt is accounted for.

| Family | Exact tokens and counts | Required handling |
| --- | --- | --- |
| Motion/modes/detection | G0:84, G1:18354, G2:20, G21:1, G28:6, G29:1, G29.2:4, G39:1, G39.3:28, G39.4:1, G90:44, G91:6, G92:67, G380:16, G392:61 | Parse supported linear body commands; arcs/homing/mesh/probe/manufacturer detection outside proven subset retain opaque effects. |
| E/flow | M83:40, M220:2, M221:1, M900:1 | Track explicit modes/overrides; pressure-advance command is not a debt reset. M200 is absent. |
| Dynamics/calibration | M17:8, M18:3, M201:1, M201.2:1, M203:1, M204:884, M205:1, M975:6, M970:1, M970.3:1, M974:2, M982.2:1, M983:2, M9833.2:1, M984:1, M211:5 | Track known explicit acceleration/limits separately; motor, calibration, soft-limit and manufacturer effects unresolved unless fixture-owned semantics are supplied. |
| Control/tool/config | M1002:145, M622:130, M622.1:124, M623:130, M620:3, M620.1:1, M620.3:1, M621:2, M624:31, M625:31, T0:1, T1000:2, T255:1, M630:1, M500:1 | Explicit balanced control/object scopes; opaque tool/remap/config effects, no presumed tool equivalence. |
| Thermal/fans/auxiliary | M104:11, M109:8, M140:2, M190:1, M106:28, M960:3 | Retain immutable events/parameters; no inference of temperature attainment or physical no-op. |
| Progress/wait/sensors/camera/sound | M73:90, M73.2:2, M400:157, M412:1, M971:61, M981:2, M991:32, M1004:31, M1006:38, M1007:1 | Preserve event and provenance; distinction between nominal geometry projection and execution guarantee. |

Body1243–23015 inventory is narrower: G21:1, M83:30, M981:2, M106:10, G1:18239, M73:79, M991:31, M204:882, M624:31, M622.1:124, M1002:124, M622:124, G92:62, M400:92, M1004:31, M971:31, M623:124, M625:31, G90:29, G0:59, G39:1, G392:57, G39.3:28. There is no body G2/G91/G380, so implementing their motion geometry is unnecessary for the smallest body-only adapter.

## Ready-to-implement bounded contract

1. **Immutable association**: accept exact source/project bytes with expected hashes; validate unique archive/settings and exact embedded source through existing source_profile. Freeze both hashes, saved setting identities, adapter schema/version, byte-level body interval and body selection evidence. No filesystem mutation or output G-code.
2. **Exact immutable events**: each event retains line number, complete-line byte offset/end, raw bytes, exact opcode including decimal suffix, parsed exact Fraction words where its supported grammar applies, raw textual manufacturer payload, layer/object identifiers and a tuple of enclosing conditional scope IDs. Preserve comments and chronological order. No generic unknown-opcode skip; emit OpaqueEffect events with explicit reason/scope.
3. **Scope AST/control flow**: parse M622/M623 nesting, bind preceding M1002 judge_flag expressions without claiming runtime flag truth, retain M622.1 mode events; reject malformed/unbalanced/unsupported scope patterns. Emit both possible branch paths as alternatives, never choose flags from comments or settings alone. Object-exclusion scope is a separate external predicate.
4. **Nominal partial state**: per-field Known(exact value) or Unknown(reason/provenance), not fabricated MachineState. Unknown units/volumetric/debt/tool/live overrides survive until an authoritative explicit operation proves that exact field. At branch joins keep a field known only when every modeled path agrees. Opaque manufacturer effects invalidate the fields their fixture-owned semantics do not establish; absent effects specification means conservative invalidation, not universal preservation.
5. **Narrow geometry projection**: extract supported unconditional G0/G1 body segments only where nominal units/absolute-XYZ and XYZ endpoints are known. Track relativeE tokens and signed E deltas as *commanded nominal deltas*, distinct from deposited filament while debt/volumetric state is unknown. Track modal F and explicit M204 independently. Conditional geometry remains conditional; opaque gaps prevent chronology/support certification. Structural contact research may opt into an explicitly labeled nominal source-geometry hypothesis, never convert it into an anchor.
6. **Anchor eligibility API**: return typed rejection/reason lists for unresolved complete state. Do not return SyntheticInsertionAnchor, grant printable flags, normalize source, bypass strict whole-source validation or call compose_supplemental_copy on invented context. Keep all authority flags false and include unresolved fields/control predicates in the receipt.
7. **Tests**: exact real byte association and deterministic full event coverage; all124 body scopes/maxdepth3; reject unmatched closers, nested scope corruption, unknown decimal opcode and malformed words; G90 then M83 ordering; conditional branch XYZ/feed/logicalE/acceleration divergence and selective convergence; G92 preserving unknown debt; missing M200 remaining unresolved; unknown startup debt never becoming known by a finite extrusion without a bound; external object exclusion; exact event offsets/comments/newlines; no input mutation, frozen nested output and false authority. Add synthetic fixtures with explicit complete initial conditions only to verify nominal transfer rules, labeled synthetic.

## Primary-source research and limits

Reviewed official upstream Orca source at commit `fd28f6c1894a7fb09af2af0d8a8c935d98467e2d`, fetched read-only from GitHub on this investigation:

- [GCodeProcessor.cpp](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode/GCodeProcessor.cpp#L6195): G90/G91 nominal positioning, M83 E mode, and M204 acceleration tracking are modeled by the slicer processor.
- [M622/M623 processor](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode/GCodeProcessor.cpp#L6602): these functions toggle a bed-level timing measurement flag; this is **not a firmware branch interpreter**, so using this preview implementation to certify actual conditional execution would be unsound.
- [A1 mini profile](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/resources/profiles/BBL/machine/Bambu%20Lab%20A1%20mini%200.4%20nozzle.json) establishes upstream profile provenance only; it does not certify this executable build or firmware.

This upstream commit is not proven to be the source revision of the pinned local2.5.0-dev binary. No primary firmware implementation/fixture was obtained for proprietary probes, conditionals, detection or remapping. Do not broaden open-ended search or substitute community opcode lists. The concrete next step is specification/repository validation for the bounded event adapter above; a full modal interpreter remains gated on the missing execution facts, and physical clearance/printing remains separately closed.

## Commands/evidence

Used exact repository Python3.12.10 for read-only source/project hash/embedded comparison, lexical inventory, scope-depth/balance/G92 dominance analysis. All final probes exited0. An initial upstream source display hit Windows cp932 UnicodeEncodeError after fetching; repeated ASCII-safe targeted output exited0. Browser/urllib access was limited to official upstream source/profile; no downloaded code executed. No tests or production implementation were changed.
