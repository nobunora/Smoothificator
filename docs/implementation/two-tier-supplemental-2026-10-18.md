# Opt-in two-tier supplemental review — 2026-10-18

Approved contract: [two-tier handoff](../specs/two-tier-supplemental-review.md).
User approved a wide lower bead with a narrower supported upper bead. This is
an opt-in tools experiment; defaults and the previous28-path job are unchanged.
Original source/project bytes and log_iotc.txt remain untouched. No printer,
commit/push/merge/release or new dependency.

## Implementation and ownership

- `tools/solve_two_tier_rectangles.py`: exact finite section search. Caller fixes
  overlap and X/physical-height families. Child X interval lies inside parent;
  different blocks have disjoint X interiors. Exact union symmetric difference
  subtracts parent/child overlap once and clips against the finite ORIGINAL
  caller triangle. Every rectangle spills at most half its area. A separate
  stronger floor comparator uses the same X lattice and continuous median
  heights; nonzero-overlap poses are re-evaluated, never assigned zero-overlap
  scores. Partial/cancelled searches claim no lattice optimum.
- `tools/prepare_two_tier_intents.py`: immutable explicit original-floor/support-
  plane graph, one straight parallel parent per child, maximum depth2, actual
  parent identity, ready ordering by world top/physical height/ID. Private
  local-support adapters reuse the existing numeric freezer and one-path cycle
  formatter. Upper thickness/remaining/overlap are relative to its parent top,
  not the original floor. Exact-span parent contact and per-parent slab bounds
  use actual frozen XYZ/E-implied widths. Each path restores the original anchor
  before the next path; saved-hop ceiling uses ORIGINAL next-layer Z.
- `tools/compose_two_tier_copy.py`: source-bound opt-in composer/writer. Genuine
  original-floor root associations own source speed/profile limits; children
  bind actual frozen parents, never invented raised structural walls. Exact
  source replay, anchor, first future original material plane and saved90%-layer
  physical-height cap are checked. Original XYZ/feed/logicalE/debt/modes and
  recognized preview metadata restore exactly. Fresh rebuild, aliases,
  no-overwrite and atomic view-only publication remain mandatory.
- `tools/audit_two_tier_material.py`: every candidate pair is accounted. Only
  individually rebuilt immediate-parent support slabs may contain intended
  overlap. All unrelated positive intersections fail/unknown; there is no
  blanket support-pair exemption.

Four new corresponding unit-test modules cover section/graph/copy/material.
Existing numeric, formatter, parser, engine, default-copy and annotation owners
were reused without edits. Rejected alternatives were changing old floor field
meaning, fabricating structural sources at parent height, duplicating extrusion
conversion, and global physical-thickness sorting across dependencies.

## Reviewed findings and convergence status

TTR-1 Medium confirmed: initial O(H²) height-pair prefilter was outside event/
cancellation accounting. Fixed by polling and charging input/height/pair
iterations; report exposes height_pair_tests. Regression100heights, max_events100
and second-poll cancellation proves zero unaccounted pair tests; larger budgets
charge partial comparisons. Independent follow-up verified. Frozen hashes:
`artifacts/two-tier-review/pure-freeze-v2.json`.

TTC-1 Medium confirmed: LF-only precheck missed CR-only parsed comment events.
Fixed with splitlines-compatible physical-line precheck and actual trace-event
count. Regression1000CRcomments rejects BEFORE interpretation at the old LF-only
budget, then accepts a sufficient true budget and exactly preserves all source
bytes. Independent follow-up8PASS0.518s. Frozen hashes:
`artifacts/two-tier-review/copy-material-freeze-v3.json`.

Initial reports: `two-tier-supplemental-blind-review-2026-10-18.md` and
`two-tier-copy-material-blind-review-2026-10-18.md`. Parent primary review and
independent code follow-up found no other material finding. Final actual artifact
review and combined regression are pending; no completion/print-ready claim.

## Genuine source and explicit scope

The accepted concrete fixture is a newly sliced flat-bottom block with flat and
20degree sloped top, using the pinned saved profile/producer. It is not the old
10degree adapter. Preliminary wholly tilted20degree fixtures remain separate and
were not promoted. Genuine source SHA256:
`f64cf8a3f2f4ef626906fa7ee336481baf614aa5d519a6f65b787472f80fcb10`;
project SHA256:
`715e13c70f1139fafa113eb3d3347963168507733aa57c3bf634191a632d44b5`.
Source context hook:
`artifacts/print-source-inspection/flat_partial_ramp20_bounded_context.py`.
The unchanged public model admits4541bodyevents/1808moving spans, ending after
complete M625 line5785, before a terminal width<height Gap infill. That gap and
ALL later positive material/OEM commands remain byte-identical in opaque suffix,
not erased or accepted by a widened model.

Two stationary surplus deposits at lines2081/5617 and5moving debt crops remain.
Root support uses actual debt-cropped moving spans. Future-solid exclusions may
use full source beads only as conservative supersets. No blob is invented for
stationary deposits. Prefix `[0,55180)` and suffix `[164522,171685)` are immutable
unresolved execution/material obligations. Body moving-pair proofs therefore do
not establish complete actual material or whole-job execution.

## Actual fourteen-step file and quality meaning

Final view-only file:
[two-tier.UNVERIFIED_VIEW_ONLY.gcode](../../artifacts/two-tier-review/actual14-v2/two-tier.UNVERIFIED_VIEW_ONLY.gcode),
SHA256 `e27dc89c57ef9d6a125db5d29984e3d9f1b6ad11708bcd20ed4b4dd815c05906`.
14steps/28straight paths, floors2.2..4.8. Each root/child physical and remaining
height is0.08mm with0% overlap, intent widths0.449/0.251mm. Actual E-implied widths
are0.44900534408122167/0.2510029929463209mm. Upper top stays0.04mm below each next
original plane. All28 formatted XYZ/E/F/physical heights are independently
reconstructed via the existing numeric owner; all14root-before-child cycles
restore source state and metadata. Removing14inserted spans recovers original
source exactly. V1/V2 copy hashes match; V2 binds final TTC-1-fixed owner hashes.

The executed layout is an explicit finite posed proposal: nominal0.449/0.251
widths, source-right inset0.006mm and XYZ3 quantization. It is NOT the original
DP optimum. Proposal pin:
`30e1e8b4155866399f2a9df4b9af3b5e3afdc187cbb3395c562c03405e24c387`.
Fresh actual rectangle-union errors improve the stronger floor48 comparator for
all14steps. At floor3, source-step surrogate error is0.012441048017456099mm² vs
0.01275471875mm². Individual surrogate spills remain≤50% (maximum≈19.52%).

The caller triangle uses one source layer height and the current/next slice-edge
gap. It is NOT equivalent to the original CAD cross-section. Actual floor3 CAD
spill diagnostic FAILS (roughly64.6% lower/97.8% upper). This remains a failed
original-mesh/physical gate, not repaired by passing the permitted surrogate.
[Source-step versus CAD diagnostic](../../artifacts/two-tier-review/section-source-vs-cad.png).

## Fresh emitted audits

[Geometry receipt](../../artifacts/two-tier-review/actual14-v2/fresh-emitted-geometry.UNVERIFIED.json),
SHA256 `70ea1ddb29062d1d9fdd166423ecc70e619a0bba27aded17aead16504b4e33e7`:
28fresh exact-span contacts/28queries; all14finite-spill/union-error comparisons
pass;14immediate-parent slabs,364cross-step candidate pairs disjoint;5160future
moving-body pairs disjoint using existing exact whole-bead envelopes. No old
certificate booleans transfer. Projection proposals were available but none
needed after full XYZ envelope checks. Runtime4.000s.

[Causal tip receipt](../../artifacts/two-tier-review/actual14-v2/fresh-causal-tip.UNVERIFIED.json),
SHA256 `12aa4d6da9b4c3427f2d55785c43af28c5144774e93e249165b8b8dce887ba7f`:
1658motions/478098pairs =477750strict box exclusions+348fresh near proofs.
Near proofs:180strict projection separations and168exact boundary contacts:
84source-anchor fixed-disc TOP,28current-forming-prefix TOP and56own-path-end
TOP.2178axisqueries,0pointqueries,0issues,32.938s. Every completed root is in the
ledger during its own return, upper approach/printing/return and all later
original body motions. Full current-forming bead is only a conservative prefix
superset certificate and enters chronological material AFTER extrusion completes.
Original motions before any new material remain the explicit original×original
baseline premise; unknown coordinates after new material fail. A0.4mm zero-height
disc assumption is consumed in whole swept paths. This is not full-head clearance.

All scoped known-moving checks complete; overall status remains INCOMPLETE for
stationary/opaque/CAD/footprint/calibration/physical obligations. Every physical,
runtime-injection, print and whole-original-job completion flag remains false.
Final driver hashes: `actual14-v2/driver-freeze-v1.json`; historical state there
said causal computing, completed receipts above are separate, never overwritten.

Independent actual14 QA separately recovered source bytes/state/geometry and
regenerated the causal ledger:1658motions/478098pairs/477750box exclusions;
all348near certificates freshly re-queried,308inserted ledger records matched,
140upper-motion×lower-material pairs and19510later-original×candidate pairs
included,28forming-prefix checks. Source owners remained unchanged. Receipt:
`actual14-v2/independent-causal-stream-QA.UNVERIFIED.json`. This independent
agreement applies only to the explicit scoped nominal statements above.

## Section table and native preview

`angles-overlap0.UNVERIFIED.json` and `angles-overlap30.UNVERIFIED.json` each
cover angles0..30: flat0,29complete finite-family cases, strict-short-base30.
Each uses X48, physical heights0.08:0.02:0.18, a single configured overlap.
Stacking selected at11angles for0%,28angles for30%; no stack is forced when the
floor comparator is better. Each angle base is an explicitly declared decimal
rationalization of stdlib tan, not exact CAD angle geometry. Every subsequent
area calculation is exact for that declared triangle. Coarse-lattice infeasibility
is not continuous-position infeasibility. Runtime33.125s/67.094s CLI timers.
Initial runs invalidated by the TTR-1 owner-hash change were rejected before
publication and are not evidence of success.

Parent native preview loaded V1 exact e27… bytes, identical to final V2, using the
pinned installed Orca. Height mode shows0.08blue supplemental versus0.2green
source stairs. Ctrl5 side+zoom was viewed; attempted drag/cube corner did not
establish an oblique view and occlusion limits remain. No visual contact proof.
User-authorized Pillow capture was used and images viewed.
[Native preview receipt](../../artifacts/two-tier-review/parent-native-preview.UNVERIFIED.json),
[side detail](../../artifacts/two-tier-review/orca-two-tier-side-detail.png),
[height zoom](../../artifacts/two-tier-review/orca-two-tier-height-zoom1.png),
[loaded view](../../artifacts/two-tier-review/orca-two-tier-loaded.png).

## Exact checks and reproduction

ONLY `C:\VSC\Smoothificator\.venv\Scripts\python.exe` Python3.12.10:

- `-m py_compile` newsection/graph/copy/material owners and direct tests:exit0.
- `-m unittest tests.unit.test_two_tier_sections tests.unit.test_two_tier_intents -q`:9PASS17.211s afterTTR-1.
- `-m unittest tests.unit.test_two_tier_copy tests.unit.test_two_tier_material -q`:8PASS0.456s afterTTC-1.
- Copy/material/legacy annotation/hop focused combination:25PASS0.495s beforeTTC-1; independent final code follow-up verified the delta.
- Architecture:45PASS10.656s; parent final syntax236filesPASS and architecture45PASS4.084s.
- Parent fullsuiteV1 was deliberately interrupted for confirmedTTC-1 and is NOT a pass. Final fullsuiteV2:925 tests PASS428.594s, exit0 (harness430.718s), Python3.12.10. Source/test hashes unchanged; unchanged old current copy and log_iotc.txt verified.

Reproduce with NEW output targets (existing artifacts must not be overwritten):

```powershell
.\.venv\Scripts\python.exe artifacts/two-tier-review/reproduce_actual.py --output-directory artifacts/two-tier-review/NEW-actual
.\.venv\Scripts\python.exe artifacts/two-tier-review/section_angles.py --output artifacts/two-tier-review/NEW-angles0.UNVERIFIED.json --overlap-percent 0
.\.venv\Scripts\python.exe artifacts/two-tier-review/section_angles.py --output artifacts/two-tier-review/NEW-angles30.UNVERIFIED.json --overlap-percent 30
```

Frozen actual audits use the preserved actual14-v2 input and atomic no-overwrite
JSON targets; on this workspace their outputs already exist. Exact executed
commands were `artifacts/two-tier-review/audit_actual_geometry.py` and
`artifacts/two-tier-review/audit_actual_tool.py` with the required interpreter,
both exit0. Do not remove old receipts merely to rerun. Standalone first artifact
attempts exposed a tuple-envelope indexing bug and baseline-only unknown entry
XYZ in diagnostic drivers; each failed before receipt publication, then was
corrected without reusable-owner changes. Their corrected algorithms are frozen
and independently reviewable. Rollback selects unchanged original/default flows;
there is no original source or project restoration to perform.

## Final regression and preservation checkpoint

Parent executed `.\.venv\Scripts\python.exe artifacts/two-tier-review/run_final_tests.py`;
its unittest discovery completed925tests in428.594s, exit0 (harness430.718s).
[Final receipt](../../artifacts/two-tier-review/final-tests-v2/receipt.json)
SHA256 `16fc94cbddd66cb007b266a1b40285b5b7d244b117d4b4537f9d4f8f2c5e5ca0`;
[full log](../../artifacts/two-tier-review/final-tests-v2/full-tests.log)
SHA256 `4c166aad120ebadc1516e63f144364db63ffa6772d9bdb2258fbc07acb51a6bd`.
All source/test hashes remained unchanged. Prior current copy
`e9b160e5386ea05380fc56021e20bb35dbb3105076cd5e22575567d8d8912839`
and unrelated log_iotc.txt
`d1cc340b699ee4366dcf0d17c80e3a3bdc4dcbeadce80f41090dc7c7f6196af4`
were preserved. Parent final invariant audit additionally checked all236 source/test
files and4 artifact drivers without changes; final view-only output remains e27dc89c….
See [parent audit](two-tier-supplemental-parent-audit-2026-10-18.md).
Independent actual artifact final report remains pending; these passing software
checks do not clear the documented CAD, stationary-material, opaque-execution,
physical-head or printer-calibration obligations.

## Independent actual artifact review disposition

Independent review completed with no material finding within the bounded nominal
scope. Both complete fresh geometry and causal receipts were independently
reproduced exactly except timing, with publication writes captured in memory.
Source-edge/frame, causal and future inventories were separately checked; all4
drivers and pure-v2/copy-v3 owner/test hashes stayed stable.
[Blind review](two-tier-actual14-blind-review-2026-10-18.md).
Previously pending independent review is now complete. Stationary material,
opaque execution, failed CAD diagnostics, full footprint, physical head and
printer calibration remain unresolved; output is still UNVERIFIED_VIEW_ONLY.

Parent reconciliation agrees the bounded feature has converged: TTR-1 and TTC-1
are fixed and independently verified; no remaining Critical/High or unresolved
scoped material findings. This does not complete the whole printable-job objective;
all original CAD, opaque-execution, stationary-material and full physical gates
listed above remain unchanged.
