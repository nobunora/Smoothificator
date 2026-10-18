# Branch-free nominal body: one offline experiment and adapter contract — 2026-10-18

## Actual experiment and decision

Executed exactly one Orca offline slice in new artifacts/branch-free-seam0-nominal-research. Only saved time_lapse_gcode was emptied; layer_change_gcode was retained unchanged. All other setting values/types, non-settings archive members, geometry/transforms and manufacturer startup/load/homing/end templates were preserved. This explicitly removes both timelapse camera macros **and head-wrap/G39/G39.3 detection macros embedded in the same hook**. This is an experimental feature-loss profile, not a physical protection recommendation or print authorization.

Result: all recurring runtime branch/detection macros disappear from the model body without rebuilding Orca. However reslicing does **not** preserve original F: all14,985 positive-XY-relativeE events retain exact startXYZ/endXYZ/E, but14,253 have changed modal feed. The first differs13933→12042 mm/min at unchanged geometry/E. The source has layer-cooling slowdown enabled with6-second threshold; reduced optional-motion time is consistent with the speed changes, but no isolated causal rerun was performed. No second slice was authorized or run. Ordinary travel commands also compact/reorder, giving18,080→18,073 retained G0/G1 token rows. Therefore do not claim byte/XYZ/E/F identity from this derived-profile reslice.

**Concrete recommendation when all original modelXYZ/E/F must remain exact:** build a separately identified source-feature transformation that removes only verified complete optional timelapse/head-wrap blocks from the original generated source, preserving every retained command byte. This avoids re-running the producer's timing/cooling pipeline. It is an explicit feature removal/new baseline, not interpreting those operations as no-ops. The actual profile experiment proves optional-block ownership/removability; it is not the exact-F-preservation baseline.

## Pins and receipts

- Input seam0 unsliced project: `5fe681683d03d9b79f17a69fa6a74b3b5c740c14fd5bba76b781991fa483ee61`.
- Original seam0-v2 source/project: `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60` / `dd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b`.
- New source/project: `f917caf88191253f22004d47545daa4e6f78f4b4132d61529101271e4d3ba288` / `6fe38676704d886a0aa82b1179343629ff612ccb55e2ee534811d1011008e567`.
- Executable SHA256: `480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba`.
- Receipt: artifacts/branch-free-seam0-nominal-research/experiment-receipt.json; includes exact command, template feature loss, pins, preservation checks and comparisons. Embedded/separate new G-code bytes agree. Input project remains unchanged.

Expanded startup/end execution spans are identical after excluding producer-injected M73 estimates; their raw spans differ by recalculated/relocated M73 progress. Saved manufacturer templates themselves remain exactly equal. A future source-level transformer can and should preserve the original expanded startup/end bytes, including original M73, without reslicing.

Initial ad hoc ZIP validation hit CRC mismatch because ZipFile.writestr mutates reused in-memory ZipInfo objects; validation was repeated against a freshly reopened original archive and passed before launching the sole slice. Original file bytes never changed. Exact .venv Python3.12.10 was used; slice returned0. No tool source code edited, printer operation, identity spoof or security bypass.

## M981 and body boundary

New source M981 appears exactly twice:

- Line1245: `M981 S1 P20000` immediately before first CHANGE_LAYER at1247.
- Line20797: `M981 S0 P20000` immediately before filament-end section at20799.

Thus it can be owned as startup-suffix/end-prefix opaque events outside the nominal model-body interval. Do not assert it has no effects; entry evidence explicitly includes it. Official upstream [GCode.cpp4487–4490](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L4487) emits open for Bambu independently of the commented detector preference. [4689–4693](https://github.com/OrcaSlicer/OrcaSlicer/blob/fd28f6c1894a7fb09af2af0d8a8c935d98467e2d/src/libslic3r/GCode.cpp#L4689) says close also notifies xcam of final-layer completion. This is producer evidence, not firmware implementation proof or proof the pinned binary exactly matches that upstream commit.

Excluding M981 close, actual branch-free model body has only G1, M73, M991, M204, M624, M625 and M106. No M622/M623/M622.1/M1002/G39/G39.3/G392 remains. M624/M625 remain31 pairs despite saved exclude_object=0, consistent with the forced Bambu emitter logic identified in the earlier proposal. No printer_model or manufacturer identity was changed.

## Minimal nominal functional pipeline without rebuild

1. **Feature-removal baseline**: exact source/project pins; recognize31 complete SKIPPABLE timelapse/head-wrap spans against pinned producer/template identity; validate all nested scopes and reject unexpected material extrusion, templates or block patterns. Remove those entire spans only, keep every other byte including startup/end. Record every removed span/raw digest and explicit feature loss. Reconstruct original exactly from retained+removed spans. Create new associated source/project baseline and update only explicitly authorized metadata/settings, with before/after identities. Plan geometry only against that new baseline, never reuse old source anchors.
2. **Nominal event parser**: exact immutable source bytes/offsets, G0/G1 endpoints and signed relativeE/F, typed M204 acceleration, typed fan/progress/notification events, layer and object identity. Each supported nonmotion opcode has an explicit state-effects contract. No blanket unknown-command skip. Source/profile association and source/config setting agreement remain mandatory.
3. **Typed object predicate**: represent M624/M625 as `ObjectExecutionScope(object_id, predicate=object_not_cancelled)` rather than no-op. Retain the source's single-object31 repeated scopes. Every geometry/material event and candidate insertion inherits its scope. Nominal active-object projection requires named `object_not_cancelled` assumption. If external state is unknown, report conditional execution; cancellation never silently creates guaranteed support. Reject malformed payload, multiple objects/tools, unmatched scopes, crossing candidate predicate, or material dependency outside the candidate's guaranteed predicate. Alternatively an explicitly adjudicated new-baseline transform may remove the whole object-cancellation feature, with its loss recorded; do not hide it in parsing.
4. **Startup handoff and anchor DTO**: compute conditional nominal states now, while separating validated versus declared startup evidence. Do not weaken existing strict whole-source synthetic_anchor. The new adapter returns `NominalAnchorProposal` with full provenance, unresolved fields and assumption IDs; it is not accepted by real-anchor/composer-copy gates as verified state.

Small named assumptions and requirements:

| Name | Meaning/status |
| --- | --- |
| manufacturer_startup_completed | Original opaque manufacturer prefix completed normally; retain exact prefix identity. Not inferred by parsing. |
| source_machine_frame_and_tool | Homing/mesh/tool basis corresponds to parsed source coordinates; firmware fixture required for validation. |
| active_object_not_cancelled | Nominal model projection executes this object; retain predicate on all events. Unknown external cancellation gives conditional results. |
| linear_relativeE_envelope | G21/G90/M83 plus firmware-supported volumetric/override semantics; missing M200 and firmware support remain explicit, not guessed from marlin flavor. |
| startup_retraction_reference | Logical ordinary-retraction reference after manufacturer prime; declared/synthetic evidence can exercise software, but no physical debt-zero assertion. |
| live_overrides_100 | External runtime condition, separately named and unverified offline. |

Suggested frozen DTO fields: source/project/derived-profile/producer hashes; startup/body/end byte-span hashes; exact source offset; exact XYZ/feed/logicalE where derivable; `retraction_debt` as Known(Fraction)/Unknown(reason); units/XYZ/E/volumetric/override state with provenance; M204 state; object predicate tuple; typed assumption/evidence records; unresolved reasons; `state_status=conditional_nominal|validated`; physical/runtime flags alwaysfalse for this phase.

G92E resets only logicalE. An explicit reset suffix can establish individual nominal fields, but physical debt remains unknown without startup reference evidence. A bounded purge proves zero only from a justified finite incoming bound B and supported ordinaryE semantics (P>=B); neither an arbitrary purge nor G92 supplies B. This does not prevent implementing deterministic conditional nominal codeflows, evidence validation, scope-aware geometry and standalone program assembly now. Physical validation remains a separate explicit transition, not a fabricated flag.

## Required acceptance before new planning

Exact original retained modelXYZ/E/F command bytes and startup/end bytes; complete feature-removal receipt; new embedded/separate source association; no runtime M622/G39 branches in body; typed M624/M625 predicates; deterministic immutable geometry events covering every model command; malformed/unknown opcode rejection; unknown debt survives G92; symbolic/declared entry never becomes verified anchor; cancellation scope cannot disappear from support chronology. Full chronological bead/support/volume/tool validators remain unchanged. Configurable provisional0.4 geometry can drive software sweep diagnostics now without pretending it supplies measured head CAD or physical clearance.

This is a legitimate bounded offline functional pipeline without rebuilding Orca. Its new-baseline feature removal needs an approved handoff and independent review because it intentionally changes executable features. The authorized reslice experiment supplies concrete producer evidence and also establishes why exact-feed preservation requires source transformation rather than a simple profile reslice.
