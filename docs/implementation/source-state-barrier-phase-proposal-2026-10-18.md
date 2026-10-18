# Source-state barrier: concrete derived-body phase proposal — 2026-10-18

## Decision and practical route

A separate derived saved profile can remove the repeated runtime timelapse/detection branches without modifying manufacturer startup/loading/homing/end programs. It cannot, by settings alone, establish a complete known physical body anchor or eliminate all Bambu body hooks. The smallest implementable path is two explicit stages: (1) derive and re-slice a branch-free-body research profile with exact template differences; (2) assemble a separately identified, narrowly transformed body and explicit state-handoff evidence. Preserve original programs/inputs, keep software checks progressing with the provisional configurable0.4 planar model, and keep missing firmware/state evidence visible rather than replacing it with guessed debt zero. No implementation or slicing was performed here.

## Actual inputs and decisive producer evidence

Restored baseline source/project identities remain `8bd04a71933ddef80372014d8bec8d9fe71674a416f1e8efdd1e53c0816726f3` / `6355256385beac751ac3659463bf109e3cee9dadada1b5bad51b62b917e51050`.

The actual derived5000-9-seam0-v2 source is `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`; project is `dd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b`. Its machine_start_gcode, machine_end_gcode, change_filament_gcode and filament start/end values equal the restored baseline exactly. It still has the original time_lapse_gcode/layer_change_gcode. Its saved timelapse_type=0, enable_wrapping_detection=0, farthest_point_timelapse=0 and exclude_object=0 nevertheless produce runtime branches and object labels. Therefore toggling those booleans is not a proven remedy.

The saved **time_lapse_gcode** owns the entire repeated branch template: timelapse M622.1/M1002/M622, G92/camera travel, and nested head-wrap G39/G39.3 detection. Emptying this one explicit derived template disables that body feature rather than interpreting unknown branches as harmless. **layer_change_gcode** owns M73 L/M991 progress notifications and can be separately cleared. before_layer_change_gcode, role hooks and wrapping_detection_gcode are already empty in the inspected baseline. Preserve filament programs; they are not the branch source.

Primary producer source consulted read-only at official upstream commit `fd28f6c1894a7fb09af2af0d8a8c935d98467e2d`:

- [GCode.cpp6324–6341](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L6324): nonempty time_lapse_gcode invokes its template. This supports the proposed saved-template change.
- [GCode.cpp4119–4136](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L4119): ordinary Bambu generation forces object exclusion enabled outside calibration, overriding the ordinary exclude_object setting. [7491 onward](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L7491) emits M624 object wrappers. gcode_label_objects changes comments, not this execution guard. Do not switch to calibration to defeat it.
- [GCode.cpp4487–4490](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L4487) and [4689–4693](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L4689): Bambu M981 open/close are unconditionally emitted; the producer explicitly notes the close also notifies last-layer completion. No saved detector boolean can be promised to remove them.
- [GCodeWriter.cpp721–742](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCodeWriter.cpp#L721): reset_e changes writer bookkeeping and does not emit G92 for relativeE mode; neither its omission nor its emission establishes physical retraction debt.

This upstream commit is not proven to build the pinned local2.5.0-dev executable. The first offline derived slice must therefore verify actual output, not assume source parity from these references. No primary A1 mini firmware implementation was obtained for volumetric mode, hidden reset side effects, probes or retraction initialization. Generic Marlin documentation would not establish those facts for Bambu.

## Phase A: exact separate saved-profile derivative

Create a new unsliced project in a new folder; pin source model/seed/executable. Preserve all non-settings member bytes and transforms. Keep current seam0/flow/motion values explicit, rather than conflating them with the restored-original profile. Allowed delta:

| Setting | Proposed derived value | Purpose |
| --- | --- | --- |
| time_lapse_gcode | empty string | Remove entire recurring camera/head-wrap runtime-branch feature. |
| layer_change_gcode | empty string | Remove M991/layer progress template hook; optionally retain only reviewed ordinary progress command later. |
| before_layer_change_gcode, process/role/wrapping hooks | retain existing empty values | Do not accidentally introduce replacement behavior. |
| machine_start_gcode/machine_end_gcode/change_filament_gcode/filament programs | exact original values/types | Preserve manufacturer startup, load, homing, prime and shutdown. |
| exclude_object/timelapse/wrapping booleans | record explicitly, no claimed efficacy | Actual producer may ignore them for emitted wrappers. |

No global preset changes, no printer_model/gcode_flavor spoofing, no calibration-mode switch. Isolated datadir and unchanged orientation/arrangement contract. Receipt includes old/new setting value hashes, template provenance, geometry/member equality, resulting exact source/project hashes and execution feature inventory partitioned into startup/body/end.

Acceptance: re-sliced body contains no M622/M623/M622.1/M1002-judge/G39/G39.3/G392 from removed feature. Fail if any remain; do not delete arbitrary unknown commands after the fact. M624/M625/M981 residuals must be explicitly routed to Phase B, not blanket skipped.

## Phase B: reviewed source partition and explicit feature transform

Prefer a tools-owned **derived-body exporter** over a broad firmware interpreter or an Orca fork. It recognizes exact source/project association and producer grammar, verifies single tool/object and exact balanced object wrappers, and separates:

- immutable manufacturer startup/load/homing/prime prefix;
- linear model body;
- unchanged manufacturer end suffix.

M981 open/close can be retained verbatim outside the model-body analysis interval, as startup suffix/end prefix, with opaque effects still explicit in entry evidence. Object cancellation wrappers require an explicit whole-feature transform: remove verified matching M624/M625 object guards from the separate derived program, disabling cancellation for that single object. This is an intentional, receipted semantic change, not a parser no-op assumption. The alternative is a narrowly pinned producer patch exposing a real disable-object-wrappers option; its higher build/toolchain burden is unnecessary for an offline export prototype.

Reject unexpected wrapper payloads, multiple objects/tools, interleaved scopes, any remaining runtime branch, unrecognized command or new template digest. Never alter original source in place. Reconstruct the original from changed-span records and retain before/after hashes. Because this transforms executable G-code, its implementation needs its own approved handoff, repository validation, focused regression and independent review; no physical enablement follows from successful export.

Body parser supports exact G0/G1, G21/G90/M83/G92E, explicit override resets and separately typed M204, plus narrowly specified thermal/fan/progress/wait events. Each non-motion command needs a fixture-owned effects contract, not generic harmless-opcode classification. It tracks all promised restoration state including acceleration/limits, or declines to claim restoration of fields it does not model. Keep existing strict linear_trace whole-source behavior unchanged; new partitioned API must not masquerade as its full-source success.

## Phase C: state handoff contract and the debt barrier

An explicit **state-reset suffix after the final opaque startup command and before analyzed motion** can establish individual nominal fields:

`G21`, `G90`, `M83`, firmware-supported `M200 D0`, `M220 S100`, `M221 S100`, `G92 E0`, explicit feed, and absolute XYZ motion after a reviewed safe travel/coordinate transition.

This is a proposed derived program change, not permission to emit these commands before validating their A1 firmware semantics. Preserve all original manufacturer prefix bytes; append rather than replace its homing/prime. G92E restores only logical coordinate, not debt. Absolute XYZ writes cannot certify mesh/tool frame without the firmware/profile mapping contract. M200D0 cannot be assumed supported because flavor says marlin.

**A bounded purge is sound only with an explicit finite incoming debt bound.** If independent startup handoff evidence establishes 0<=D<=B and ordinary positive relativeE semantics, a reviewed purge of P>=B derives debt=max(0,D-P)=0. Additional controlled retract R then establishes debt R. Without B, no finite purge proves zero for arbitrary unknown D; software must not assume it. The source's existing prime is producer evidence of intended successful-print handoff, not a mathematical bound on hidden firmware or physical extrusion state. Do not add an arbitrary large purge to paper over this gap.

Implement an immutable `StartupHandoffEvidence` with exact startup/program/firmware/profile identities, supported modal-reset semantics, machine frame/mesh policy, tool context, `incoming_retraction_debt_bound_mm` plus its evidence reference, purge command witness and derived outgoing debt. Missing bound/semantics → explicit unresolved status. Distinguish the logical ordinary-retraction obligation model from actual material pressure/deformation; do not rename the latter into a proven numeric zero.

A proposed API may produce a `NominalBodyExecution` conditional on that evidence while hardware validation remains pending. Real-anchor factory accepts only validated evidence, exact current source hash, a complete-line boundary outside every control scope, and reconstructed complete state. It returns typed missing-evidence reasons otherwise. This lets complete software/fixture paths be built now using explicit synthetic evidence, without calling it real-device proof.

## Required specification/API extension and verification

New handoff/ADR needed for partitioned startup/body/end semantics, intentional object-cancellation feature removal, startup-handoff trust/evidence boundary and richer restoration state. Canonical SPEC18/24A–27/29 gates remain authoritative; no inference from successful slice or nominal geometry may override them. Current synthetic_anchor validates the whole source and cannot be silently relaxed for this feature.

Proposed pure functions:

- `derive_branch_free_profile(project_bytes, approved_template_changes, expected_hashes)` → frozen project/changed-key receipt.
- `partition_and_transform_body(project, source, producer_descriptor)` → exact immutable source spans, transformed copy, feature-change receipt, unknown-effect inventory.
- `derive_body_entry_state(reset_witness, startup_handoff_evidence)` → known state or typed unresolved evidence.
- `reconstruct_body_anchor(body_execution, source_boundary)` → immutable anchor or explicit rejection.

Tests must cover actual branch removal from the pinned producer, preserved machine templates/member bytes, M624/M625 transformation with changed semantics documented, M981 outside-body ownership, unexpected opcodes rejection, exact source reconstruction, logicalE/debt separation, symbolic unknown debt surviving G92, bounded-purge proof with D=0/B and P<B/P=B, full command-state restoration, stale evidence/fingerprints, no runtime scope at anchor, atomic separate output and no original mutation. Recompute all candidate structural associations under the new source identity. Full bead/support/future-volume and tool sweep checks use the complete chronological material model; the user-approved provisional0.4 geometry supports software diagnostics but is not a fabricated complete-head profile.

This is the smallest concrete path found: clear one real saved branch template, explicitly handle forced producer features, and make a verifiable startup handoff rather than inventing physical debt. Missing firmware/fixture assertions remain precisely named, while profile/export/interpreter/collision software can proceed without head CAD or printer contact.
