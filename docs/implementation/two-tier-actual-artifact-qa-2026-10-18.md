# Actual two-tier artifact and causal-stream QA, 2026-10-18

Disposition: no material finding within the stated moving-body/view-only scope. **Overall incomplete**; this is not print/runtime authority, original-CAD acceptance, or full support/head clearance. This independent artifact QA is separate from the primary implementation and the independent blind code review.

## Frozen actual identity

Actual14-v1 and actual14-v2 G-code bytes are identical, SHA256 `e27dc89c57ef9d6a125db5d29984e3d9f1b6ad11708bcd20ed4b4dd815c05906`. Final file: `artifacts/two-tier-review/actual14-v2/two-tier.UNVERIFIED_VIEW_ONLY.gcode`. SourceSHA `f64cf8a3f2f4ef626906fa7ee336481baf614aa5d519a6f65b787472f80fcb10`, exported projectSHA `715e13c70f1139fafa113eb3d3347963168507733aa57c3bf634191a632d44b5`. v2 receiptSHA `bacfdc281ed6f5856678b34a1a66e0e716a6ef1f92c05cd83096108a258dcb90`.

The interpreted body ends after M625 line5785. Its opaque suffix retains actual positive original material, including terminal width0.121244/height0.2 Gap infill line5953, plus OEM routines. No source bytes, Brim settings, templates, model owner, tests or reusable code were changed by this QA.

## Byte, state and emitted geometry checks

`artifacts/two-tier-review/independent_actual_QA.py` rebuilt the source-bound actual context and independently replayed all14 insertion blocks with the strict linear reader. Removing the actual insertion spans reconstructs the complete original source byte-for-byte. All14 anchors freshly rebuild eligible; each lower/upper single-path cycle restores exact original XYZ/feed/logical E/debt/modal state. All28 actual extrusion XYZ/E/feed values reproduce the shared numeric freezer and E-implied widths. All14 lower paths precede their explicitly identified children. Generated physical-height metadata and original metadata restoration remain present. Geometry is identical to the pinned proposal, so repeating the earlier contact/future material loops was unnecessary for this check.

Initial QA harness field/tag-name assumptions were corrected before the final successful run; no product change was made. Final exit0 evidence: `actual14-v1/independent-byte-state-geometry-QA.UNVERIFIED.json`, SHA256 `5b5f7870f0f8cfc4addabb365631d1d0e12f5792aa1a2b95029041e3cbb20d56`.

New explicit proof binding preserves that v1 record and binds its command-level conclusions to identical v2 bytes: `actual14-v2/independent-v1-proof-binding.UNVERIFIED.json`, SHA256 `f8d5b99ec6a162e5bcbf0e941c0298afd25fa8a2164b3f4a02bfae32ad18e939`. It does not claim receipt metadata equality.

A separate exact current-group diagnostic proves all saved-anchor vertical returns are laterally separated from the completed lower/upper material using provisional tip radius0.2mm; minimum Y-projection margin0.3254973279593892mm. Upper path tip Z is0.08mm above completed lower top. This limited diagnostic does not replace the complete causal audit below.

## Independent causal audit

Read `artifacts/two-tier-review/audit_actual_tool.py` and its actual-emission reconstruction. Candidate material enters the chronological ledger only after its actual positive XY extrusion. The newly completed lower therefore participates in its own return and every upper approach/print/return; both remain present in all later original body moves. No original motion is skipped once any new material exists. Initial original×original motion before new material is explicitly baseline-only, without fabricated XYZ. All subsequent unknown moving XYZ fails closed.

`artifacts/two-tier-review/independent_causal_QA.py` independently regenerated the stream and exact ledger coverage, reconstructed conservative AABB exclusions, and freshly called the public tip-sweep certificate owner for **all348 near certificates**. It checked actual proof XYZ/material identity, strict separation or a valid top-contact witness and its narrowly declared allowance. Original/source-anchor contact requires a fixed anchor disc, own-end contact requires the current path endpoint disc, and forming-prefix contact is the explicit straight current extrusion top-plane superset; no general support-pair exemption was accepted.

Result:1658 modeled motions,478098 pairs,477750 exact conservative-box exclusions,348 fresh verified near certificates,308 exact inserted ledger records,28 forming-prefix checks. Included140 upper-motion×completed-lower pairs and19510 later-original-motion×prior-candidate pairs. The2294 initial original motions before first new material remain the stated baseline-only scope. No missing insertion, early admission, disappeared lower bead, accepted unknown, or uncovered later-body pair was found. Owner pins matched before/after. Independent run completed37.578s, exit0.

Source causal receipt `actual14-v2/fresh-causal-tip.UNVERIFIED.json` SHA256 `12aa4d6da9b4c3427f2d55785c43af28c5144774e93e249165b8b8dce887ba7f`. New independent evidence `actual14-v2/independent-causal-stream-QA.UNVERIFIED.json` SHA256 `f6dc917a9f9efe3ca43b088e6c704d088e9a2f6fba4463b27bf284d734c5a576`. Independent driverSHA `3e1bf6f5551de5a714df5d6321f3c3cd28731eb4bde7b020d022862642541336`.

Commands used with verified Python3.12.10:

- `.venv\Scripts\python.exe artifacts/two-tier-review/independent_actual_QA.py` — final exit0.
- `.venv\Scripts\python.exe artifacts/two-tier-review/independent_causal_QA.py` — final exit0.
- Exact-byte v1/v2 binding and current-group projection research commands — exit0; persisted receipts above.

## Limits retained

The caller triangle is the source-layer-rise/contour-gap surrogate. Its successful finite spill/error comparison is not CAD equivalence. Failed original-CAD diagnostics remain explicit; SPEC5A/7/19 are unchanged. The0.4mm planar disc is an authorized provisional assumption, not a measured whole head. Centerline support is not full footprint support. Two stationary positive material events (2081,5617), opaque prefix and material-bearing suffix remain unverified. Original tool×original material is the unchanged baseline premise. Native Orca preview and broader software gates are parent-owned evidence and were not independently claimed by this QA.
