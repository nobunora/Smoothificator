# Nominal bead-pair volume — independent blind review, 2026-10-18

## Independence and result

First independent review of this bounded stage. Inspected docs/specs/nominal-bead-volume-review.md, tools/audit_nominal_bead_overlap.py, tests/unit/test_nominal_bead_overlap.py, the exact stadium top-query implementation/domain DTO contract, SPECIFICATION12 and Accepted ADR-0048 including the explicit varying-Z/flat-cap convention. Actual outward fixture source/manifest/diagnostic provenance was checked through the pinned real regression. No parent implementation/primary findings consulted. No code/test edits, printer operations, original/source mutation or new slicing; only this report written.

No actionable material defect found in the bounded nominal pair-volume contract. No physical clearance or full-job safety conclusion follows.

## Reflection and geometric proof

At each fixed XY location the existing stadium section is vertically symmetric about command_z-height/2. With constant per-segment height h and linear command z(t), reflection z→-z therefore maps the command locus to h-z(t), preserving XY/width/height and flat axial endpoints. The implementation uses exactly this mapping; reflected top equals negative original bottom, including linear varying-Z structural segments. It does not introduce a parallel cap/distance model.

For a query box, negating reflected upper bounds yields original bottom lower bounds; negating reflected lower bounds yields original bottom upper bounds. Code reverses these inequalities correctly. Disjoint uses top_upper<=other_bottom_lower (zero-height touching admitted as disjoint interiors). Positive volume requires all four queries to establish full XY coverage and max(bottom_upper)<min(top_lower). Thus every positive-area overlap witness contains a strictly positive vertical interval uniformly across the entire box. Partial coverage or ambiguous sqrt bounds cannot prove overlap. Absent XY support can certify disjoint, and individual conservative upper/lower comparisons remain sufficient even without full-cell coverage.

Broad-phase XYZ envelopes are conservative: endpoint Z extrema extend down by h; horizontal/vertical segments preserve flat-cap axial limits; oblique XY uses the larger width/2-expanded AABB. Broad-phase separation/touching cannot exclude an interior intersection. It is never used to claim overlap.

## Partition, resources and cancellation

Only positive-area XY intersection boxes enter refinement. Every uncertain leaf splits exactly on its longer dimension into two closed rational boxes; children meet only on zero-area boundaries. Final coverage area is asserted; source construction retains each branch exactly once. Early positive witness retains all pending work as unresolved. Gap-free classification requires no overlap and no unresolved work; a proven overlap can coexist with unresolved/cancelled remainder, which the report exposes.

The query budget reserves four single-source queries per cell and never exceeds it. Explicit maxdepth/input-coordinate/sqrt precision limits remain conservative incomplete outcomes. Reflected input coordinates are also bit-checked. Kernel incomplete results are inspected before bounds, with no attempted arithmetic on missing bounds. Cancellation exact-bool checking is latched and checked before work, inside the real kernel, after queries and at report publication; cancellation cannot publish a new disjoint success. An already established overlap witness may remain overlap-proven with cancellation/unresolved state, correctly refuting disjoint interiors without claiming complete analysis.

Inputs, policy, reports, cells and segment geometry are immutable. Pair IDs must differ; parser/chronology association is intentionally caller-owned. Physical flags are init=False false.

## Executed evidence

Exact repository `.venv` Python3.12.10, verified previously in this independent session.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_nominal_bead_overlap -v` → exit0, all9 tests pass (0.269 seconds). Real-kernel coverage: identical/partial overlap, XY/Z separation and exact touching, oblique/reversed orientation, disjoint solids with overlapping broad AABBs, flat caps, varying-Z reflection, resource/cancellation behavior, malformed inputs and pinned ring25/future4.4 overlap.

Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -` final probe → exit0:

- Independently derived lateral stadium top/bottom for width0.4,height0.2,u0.18 (cap0.06) at two points on z2→2.4 structural slope and verified exact expected values lie within original/reflected certified bounds.
- For partial, oblique varying-Z and actual outward pairs, checked pair-order symmetry and reflecting both solids preserve overlap-proven classification.
- Verified leaf areas exactly cover the initial box and every distinct pair of leaf interiors is disjoint; positive witnesses have strictly ordered vertical bounds.
- Actual regression validates original source/manifest hashes and the diagnostic hash, explicit source14786/14787 commands/endpoints and candidate recipe before proving positive overlap.

An initial independent probe incorrectly demanded dyadic sqrt bounds equal a nondyadic rational cap exactly; it failed as expected for finite sqrt enclosure precision. Correcting the probe to exact rational containment passed. No source defect or test weakening was involved.

## Residuals

This pair audit does not select chronology, permit/reject intended contact, derive actual source bead widths, certify union-wide collision absence, measure overlap volume, or model nozzle/head/physical deformation. Any finite unresolved cell prevents a disjoint certificate; touching curved surfaces can therefore stay incomplete at configured limits. A positive pair witness refutes nominal interior disjointness even if its remaining partition is unresolved. Pinned provenance establishes the regression recipe, not physical execution or complete future-source coverage. Parent owns architecture/full-regression gates beyond these focused checks. No finding requires disposition; no physical/runtime authority or production convergence declared.
