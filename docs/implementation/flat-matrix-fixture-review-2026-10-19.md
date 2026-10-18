# Compact flat matrix fixture — independent review

Date2026-10-19. Latest user/parent scope supersedes the old25-tile/75-line/underside-text draft: ONE common flat substrate,25 cells in5x5, ONE10mm experimental line each. One original-source-layer-high numeral01..25 sits above each line in XY. Central6mm is evaluated;2mm at each end reserved for start/end effects. Rows h_cmd=.010/.015/.020/.030/.040; columns final commanded volume/mm=.000075/.000150/.000300/.000600/.001200. Physical line width/thickness are not asserted by independent clearance/volume settings. No GUI/printing by this reviewer.

## Compact layout recommendation

A64x64mm common base, provisionally.6mm high, is sufficient without crowding.12mm cell pitch gives line-center localX8/20/32/44/56 and localY6/18/30/42/54;10mm lines run ±5mm. Place each two-digit number centered above its line, with lowest actual label material at least3mm above lineY. A.6mm stroke, roughly3mm-high seven-segment font or4.2mm-high5x7 pixel font yields distinguishable25 IDs and fits inside the last row. Freeze exact glyph grammar/spacing/condition mapping in the manifest;01..05 are lowest-clearance row,01/06/11/16/21 lowest-volume column. External CSV/diagram shows all units/conditions and orientation. Numeric IDs are sufficient under the user's simplification.

The exact saved profile inspected from `gui-angle0to45-zero-overlap-v1/source-gui-project.3mf` has printable_area0..180 in both axes, maxheight180, global/initialH.2, nozzle.4, line/top-surface width.42, top_shell_layers5/top_shell_thickness1. A64mm square centered atworld90 occupies58..122mm and remains bed-contained. This is evidence for selected settings, not permission to guess actual sliced material or first-layer behavior. Base.6 means3 original layers;.8 is a possible explicit fallback if actual slice requires it, not a silent change.

## Geometry and actual source verification

Use a single deterministic closed connected mesh: common flat base plus exactly one.2mm-high source label layer. Do not export overlapping bar/voxel boxes with duplicate/internal faces. A bounded per-cell heightfield/stitch construction or exact known union is preferable; test manifold oriented edges, volume, normals and bounds. Labels stay outside all test-line/sample envelopes and declared travel corridors. No label stroke crosses a sample line.

Genuinely slice with the pinned Orca/runtime and exact saved settings, keeping input/output/source/settings hashes. Verify actual emitted base topZ and complete filled original support under every10mm sample centerline. Infill/top-shell mesh assumptions are not proof of support. Confirm label deposition occupies exactly the next original.2mm layer and all25 glyphs01..25 survive actual.42mm source-width slicing. Render actual positive-deposition paths (with source widths) into a25-cell overview and enlarged label crops, then inspect readable/distinct numerals; a mesh-only picture is insufficient. Record absent/merged/open/malformed strokes and revise the glyph geometry before native test output if needed. Verify no original positive-E source deposit remains after matrix insertion.

## Important native anchor mismatch

Actual labels above a.6mm sample base finish at sourceZ.8. Existing native route `gui_native_trial_copy.py:337` requires plan original floor equal saved anchorZ; its posthop route also requires an earlier same-floor witness with a very constrained intervening hop. Consequently the ordinary route cannot simply label the whole sample floor.6 after source labels at.8. Do not claim sample support at.8, inject before later original labels, alter the source to synthesize an anchor, or weaken the legacy gate.

The explicitly reviewed independent-clearance matrix adapter must bind two distinct facts: sample source top=.6 from actual source deposition/contact, and saved source anchor=.8 (or actual higher parked/hopped state). It must enter sample commandZ=.6+h_cmd using certified safe travel, preserve the source plane without downshift, hop above every source label/deposited test line between samples, and exactly restore the genuine post-label XYZ/E/debt/modes/feed/acceleration state. This new source-floor/experimental-clearance representation requires scoped specification/repository approval. All labels/base remain material/tool obstacles; sorting rows low-to-high alone is no collision proof.

## Volume and comparison limits

At h=.01 and maximum area.0012, a stadium-equivalent width is about.122mm, but low-area/high-clearance cells may not admit any stadium geometry. Do not use that estimate to certify the physical bead or lower ordinary inverse-width gates. The selected independent-variable experiment must have its own conservative material/nozzle envelope and final rounded E/rate proof. Freeze source surface, speed, source ratios/material, retraction1.6/wipe1 and10mm length across all25 conditions. Label samples using commanded clearance and final commanded volume/mm; central6mm and both2mm ends must be identifiable in the diagram. Physical adhesion/continuity/ridge response remains a user observation.

Disposition: compact fixture/layout proposal is suitable for a bounded genuine-slice trial. Production matrix injection remains blocked on its explicit independently reviewed experimental representation and actual source-label/support/anchor evidence. No production or shared source files edited by this reviewer; exact recommendations sent to parent and emission owner early.

## Accepted exact specimen supersession

Parent subsequently accepted ADR0072 and `docs/specs/flat-microextrusion-matrix-trial.md`: exact64x64mm world58..122, base0..0.8, four original.2layers, labels.8..1.0, one original layer. This supersedes this review's provisional.6base choice. Labels begin lineY+3mm, exact3.5mm height/.6mm stroke; all other12mm-pitch/10mm-line/central6mm layout values match. The spec explicitly separates source anchor1.0 from actual sample supportfloor.8 through the new experimental adapter, with no legacy-floor relabeling. Source/profile/tool/state and all-label material checks remain required. Reviewer has read this accepted contract and will perform independent changed-code execution review only after frozen source/test list, without receiving primary findings.

## Genuine original source/label review completed

Independent review read the actual generated fixture, genuine CLI sliced archive and separate raw G-code. `verify_flat_matrix` exactly associates all actual saved binary32-serialized vertices/faces with the known fixture. Separately enumerated mesh edges are closed/oriented in opposite pairs; signed volume3316.214mm³,4246vertices/8488faces. Embedded archive G-code equals separate source byte-for-byte. Source SHA256 `68b2b643da4766c5b94e89cf503ba5c3f961d82225f922a5a9e6719bd7315c7d`; actual sliced geometry/archive SHA256 `1fd57a23c41dbcc7c6a307f6a4c8e1fc547bacbe3ac3ac3f819d1437edab38ef`.

Independent relative-E/XYZ source-path extraction found model positive-XY deposition only at Z.2/.4/.6/.8/1.0, counts388/471/471/742/434, no positive-deposition arcs. All434Z1.0 deposits uniquely belong to the25 label bounding regions; no label is over any sample line. Actual positive-deposition-width rendering was inspected:01..25 are legible/distinct, including11/17/20/25. This is actual sliced-path readability, not measured printed-text quality.

All25 full10mm planned lines are covered by the XY projections of actual declared-width source-top beads at commandZ.8; no uncovered planar intervals were found. This is a nominal XY projection diagnostic, not proof that every physical bead top is a mathematically flat.8 plane, nor physical contact/adhesion measurement. The independent-clearance experiment must retain that source-surface limitation and its conservative material/tool assumptions.

Evidence/scripts: `artifacts/flat-microextrusion-matrix-v1/independent-fixture-review/actual-source-fixture-review.json`, `review_actual_source.py`, `check_sample_zones.py`, `render_actual_source.py`, `actual-source-label-overview.png`, `actual-source-label-crops.png`. The crops were inspected through image viewer. An initial independent parser omitted leading-dot numerical tokens and was corrected before evidence generation; final extraction handles .2/.42 etc explicitly. Initial module-import path was also corrected; no production code changed.

Disposition: fixture/source-label stage validated, no confirmed fixture finding. Native independent-clearance adapter execution review remains a separate blind task.


Actual anchor clarification: the new fixture's genuine source finishes label deposition at1.0, then original G3 raises to1.4 before M625 offset198905. The adapter inherits/restores actual XYZ63.989/69.833/1.4 and uses ceiling1.8; supportfloor.8 is separate. Provisional anchor1.0 discussion above is superseded by actual source evidence, not an extra touching/clearance obligation.
