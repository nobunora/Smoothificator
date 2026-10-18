# Floor3.2 spaced repacking — independent audit and handoff validation, 2026-10-18

## Repository dispositions

Independently reviewed localized-source-joint-detours-review.md and radial-rectangle-spill-bounds-review.md against existing factory, finite-area owner and prior3.8 evidence. Both are **validated for bounded tools-only implementation**. No material input contradiction found. Detour spec preserves original joint/edge provenance, bounded source walks, selected-joint survival, default parity and pre-freeze-only edits. Spill spec's exact common-subrectangle lower intersection, largest-area denominator, complete parameter partition and incomplete-without-bound semantics are mathematically sufficient; fixed parameter ranges are handled explicitly. No source-solid, physical gate or50% threshold is redefined.

## Actual floor3.2 result

Independently audited floor32-repacked-spaced-circle-exact-proposals.json, construction script, floor32-repacked-outer-future-separation.json and area comparison against actual seam0-v2 source/project and exact kernel owners. No reusable edits, artifact overwrite, slicing or printer operation; only this report written.

All five192-chord lanes independently reproduce geometry, numeric E/width and whole-span contact. All960 chords prove nominal centerline contact, zero gap/incomplete, using1,608 queries. All four full-footprint radial packing bounds are positive. Future model volume is separated by radial/Z bounds for inner lanes and a complete1,668,480-pair audit with722 exact noncardinal certificates for the outer lane. One Low provenance-label finding below must be corrected before receipt reuse; it does not invalidate the independently reconstructed geometry certificates.

## Finding FR32-1 — stale candidate_source metadata

- Severity: Low.
- Location: artifacts/print-source-inspection/floor32-repacked-outer-future-separation.json, candidate_source; corresponding research_floor32_repacked_outer_future.py receipt construction.
- Behavior: receipt names source-offset-candidate-budget100k.json although it proves the last lane of floor32-repacked-spaced-circle-exact-proposals.json. The former has64 source-offset edges, while this proof covers192 circle edges.
- Evidence: script actually reads the spaced floor3.2 file and lanes[-1]; independent recomputation against that exact geometry reproduces all722 near pairs and fractions. The label therefore points to a different candidate rather than identifying the proven one.
- Requirement: explicit source/candidate association and no certificate transfer across geometry variants.
- Failure scenario: a downstream consumer follows candidate_source or reuses the receipt by its label and attributes these bounds to the wrong candidate.
- Remediation: publish corrected metadata naming the actual spaced proposal file, outer lane ID/radius and candidate content/geometry hash. Preserve this audit's distinction rather than modifying earlier geometry to fit the proof.
- Confidence: High; confirmed, awaiting parent disposition/fix. No reusable source changed by this audit.

## Pins, geometry and emission

Verified source SHA256 `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`, project `dd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b` and embedded/separate source equality. Before-first3.4 deposition source order is10486. Complete nominal source rows were previously independently reconstructed from these actual bytes.

Reconstructed all quantized circle points from declared radius/phase/count and refroze emission through authoritative flow/freezer with actual saved policy. All960 endpoints/E/physical-width values match artifact. Ring9 uses h0.137,remaining0.096; remaining rings use h0.18,remaining0.126, with width intent0.251. All dimensions/overlap/nearestE widths satisfy existing bounds. No frozen reference geometry was modified.

## Rigorous finite spill certificates

Near-limit decisions were not accepted from the stored endpoint radius/width matrix. For each actual chord separately, computed exact center-radius enclosure over the entire segment, retained its fixed actual E-implied width, and partitioned that radius interval into32 exact bins. In each bin, the common horizontal rectangle contained in every possible posed rectangle is intersected with the authoritative finite triangle; dividing that guaranteed area by the actual full rectangle area yields a rigorous spill upper bound. Max over all bins/all192 chords gives:

| Lane | Stored endpoint diagnostic | Independent whole-segment upper bound |
| --- | ---: | ---: |
|ring9|0.4966016685|**0.4966334359**|
|ring10|0.4540042534|0.4540376981|
|ring11|0.3159239734|0.3159687240|
|ring12|0.3000000000|0.3000793029|
|ring13|0.3233050945|0.3230550956|

All strictly satisfy<=0.5, with tightest remaining fraction0.0033665641. These are sufficient radial-rectangle parameter bounds, not exact maxima,3D area/volume fractions or complete source error. Ring13's tighter per-segment bound can be below the global endpoint diagnostic because width/radius extrema need not occur together.

## Contact, packing and future sets

Reconstructed every earlier-source local query and reran real exact span owner. Contact queries by ring:376/312/336/296/288, matching all stored per-chord states. Whole-source order, full source height and conservative source XY filtering were retained.

Exact full-footprint radial packing lower gaps reproduce as approximately0.0008486910,0.0012049165,0.0011202218,0.0008140695 mm. These are positive mathematical nominal gaps with no epsilon threshold or physical margin claim.

Recomputed future radial lower bound for every source bead that can vertically intersect these candidates; all higher source beads separate by full bead lowerZ. Inner four lanes have positive full-footprint radial gap, matching artifact. Outer ring13's simple radial bound is negative and was **not** accepted via radial ordering. Enumerated all192×8,690=1,668,480 outer/future pairs:1,667,758 full-bead XYZ AABB exclusions and exactly722 remaining IDs. Every stored axis reproduces public exact projection intervals with positive exact margin equal to its receipt fraction. No missing, duplicate or unresolved near pair remains for the actual spaced outer geometry.

## Quality tradeoff explicitly changed

Independently recomputed finite radial-rectangle surrogate symmetric difference under the same finite triangle. Original reference error is1294694681/60204500000 (~0.0215049487 mm²); spaced intended reference is2550411739/21650000000 (~0.1178019279 mm²). The stored comparison exactly matches the **spaced** recipe and correctly has quality_gate=false. This is substantially worse on that surrogate, despite solved numeric/contact/packing/future constraints. It must not be called unchanged quality, optimized shape or a selected complete solution. Full affected-domain bead error remains a separate canonical evaluation.

## Evidence/limits

Exact repository Python3.12.10 read-only independent probes exited0 for geometry/freezing/contact, per-chord spill bins, packing/future enumeration and area comparison. No existing artifact was changed. Source branches/state, conditional anchors, full footprint support, original travel, physical head geometry/clearance and all remaining groups are not certified. Physical flags remain false. One Low provenance finding requires disposition; no Critical/High geometric certificate defect found within this declared nominal set.

## FR32-1 independent correction verification — 2026-10-18

A new provenance-corrected receipt preserves the old file and supersedes only its incorrect candidate label. Independently verified actual candidate file SHA256 `6c61e8fc7044463cf69aa54e400a05bc31d412944923b1b3157126455175ca55`, zero-based lane4=ring13 with192 edges, and canonical stored-segments path SHA256 `6c9ca45203a3db77cde1d209d305bea25a820a9623ebf8036a8f5d667c981a4f`. Every recorded source/project/unsliced/rows pin matches actual bytes. All722 certificates, full pair counts, exact margins, unknown list and physical-false flag are unchanged from the independently reviewed mathematics.

Read-only exact repository Python3.12.10 probe exited0. FR32-1 disposition: **confirmed, fixed in new receipt, independently verified**. No remaining finding from this audit; all earlier geometry/quality/physical limitations continue to apply. No artifact or code was changed by verification.
