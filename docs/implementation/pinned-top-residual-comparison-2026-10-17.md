# Pinned top-candidate residual comparison

Scope: continue the offline research implementation after the user accepted
the native display issue. This milestone connects the real pinned fixture to
the existing numerical comparison and renders its receipt. It does not enable
production candidate generation, Plan construction, injection, or printing.

## Contract and repository review

Base checkout: `06d4db8`, `codex/true-z-review-handoff`, with the preceding
uncommitted migration/diamond-display changes preserved. AGENTS.md,
DOCUMENT_CONTRACT, canonical SPECIFICATION/ARCHITECTURE, TEST_STRATEGY and
the implementation contract were checked before edits.

The existing implementation record
`planar-coupon-vertical-residual-results-2026-10-17.md` records repository
validation and authority for `compare_planar_coupon_vertical_residual` at
`9b4e4fb`. Its closed numerical contract remains unchanged. The candidate
generation review still requires a separate accepted production contract;
this task does not silently replace that contract or physical geometry with
Orca's display approximation. Disposition: validated for this fixture adapter,
exact interval aggregation and research display only.

## Implementation

- `tools/compare_top_surface_residual.py` verifies the 3MF, STL and source slice
  SHA-256 identities, constructs the transformed 8-vertex/12-triangle 3MF mesh,
  validates the display hypothesis and compares it to the complete original
  baseline. The STL is identity-checked; comparison geometry comes from 3MF.
- All 669 original extrusion segments are accounted for, including later
  layers. Only conservative disjoint XY bounds can discard irrelevant paths.
  For this region, 164 paths intersect those bounds. A continuous closed-cell
  dominance certificate then proves that 22 upper-layer paths dominate the
  remaining lower paths everywhere in the comparison rectangle. Lower paths
  are removed only after that proof, not by assuming a truncated baseline.
- The rectangle is partitioned into 32 closed rational X intervals with
  shared boundaries. Each tile uses the unchanged comparison engine and its
  bounded quadtree. Maximum lower/upper residual bounds across all tiles bound
  the maximum over the whole rectangle. Every tile must finish; any unresolved,
  cancelled or rejected tile suppresses all aggregate scores. Target planes
  must agree. Allocated leaf budgets do not exceed the global comparison limit.
- `audit_top_contact_cells.py` accepts cancellation for the optional dominance
  pass; unresolved/cancelled dominance retains the full baseline.
- `render_top_surface_3d_review.py` includes the comparison only if source IDs
  and the canonical JSON digest of the candidate plan match. It validates exact
  residual interval ordering and classification before displaying a favorable
  label. Changed candidates, different slices, unsafe flags, malformed bounds
  and partial results cannot revive an old score. The candidate remains an
  unverified reference line rather than a green accepted path.
- `tests/unit/test_top_surface_residual.py` covers real fixture binding, future
  layers, dominance/non-dominance, interval aggregation, deadlines, cancellation,
  tampered inputs, stale reports and unfavorable/partial display behavior.

No dependency or domain/engine/public Plan schema changed. Geometry uses exact
binary64 transformed mesh vertices and exact decimal source-bead inputs in the
pinned 3MF-build-plus-Orca-plate-offset fixture frame. This is not certification
of the centered production PrintObject adapter.

## Actual result

Reproduce in `C:\VSC\Smoothificator`:

```
.venv\Scripts\python.exe -m tools.compare_top_surface_residual
.venv\Scripts\python.exe -m tools.render_top_surface_3d_review
```

Policy: 4,096 comparison leaves, depth 12, 32 X partitions, 45-second deadline;
the dominance pass is separately bounded to 2,047 cell queries and shares the
same deadline/cancellation callback. The completed comparison used 1,031 leaves.

Candidate: top-07, X=120.3–129.7 mm, Y=127.336335 mm, Z=2.28 mm,
width 0.34 mm, nominal height 0.19 mm. Closed comparison rectangle:
X=[120.3,129.7], Y=[127.166335,127.506335] mm, area 3.196 mm².
Both baseline and augmented envelopes use the physical reference stadium
model with flat axial caps, not the diamond rendering model.

| Maximum absolute vertical top residual | Certified interval (mm, approximate display) |
| --- | --- |
| Original complete slice | [0.15692539982964548, 0.19106772068164943] |
| Same slice plus candidate | approximately 0.11305776169498327 |

Exact rational interval endpoints are in the JSON receipt. They are strictly
disjoint: local maximum residual reduction is at least 0.04386763813466222 mm.
The receipt therefore reports `complete / certified-reduction` for this
rectangle only. It keeps `full_surface_improvement_verified: false` and
`printable_authorized: false`.

Earlier attempts with one very elongated quadtree returned coverage-unresolved
or hit the deadline. Increasing a single-tree budget alone did not resolve
this efficiently. Closed X partitioning and certified dominance reduce work
without changing the numerical acceptance inequalities. Small-budget and
deadline paths remain tested and produce no favorable metrics.

Artifacts (ignored local files):

- `artifacts/geometry-review/top-surface-residual-comparison.json`: hashes,
  selected source line IDs, dominance certificate, budgets, exact intervals.
- `artifacts/geometry-review/top-surface-3d-review.html`: self-contained review.
- `artifacts/geometry-review/residual-preview-browser.png`: actual browser view.

## Validation and remaining work

Python 3.12.10. Syntax/import check and 43 architecture tests passed.
The focused residual/contact/coupon set passed 37 tests. The full suite passed
**666 tests in 74.511 seconds**, retained in
`artifacts/geometry-review/residual-full-tests.log`.
Generated JavaScript passed `node --check -`; `git diff --check` passed.
Lint/type tooling remains NOT CONFIGURED. No new package dependency was added.
`tools/build_validation_artifacts.py` passed for the tracked-source research
archive; this is not evidence that untracked fixture tools are in that archive.

Chrome loaded the generated page from a temporary loopback-only HTTP server.
The 3D canvas, actual comparison intervals, unverified candidate status and
scope warning were visually inspected. The upper-Z slider changed to 2.40 mm
and back to 2.20 mm while preserving the receipt. The final page was reloaded,
captured and inspected. The temporary tab and server were closed. In-app browser
was unavailable; a full-page CDP capture timed out, but the browser's regular
screenshot API succeeded and saved the evidence above.

This local vertical-top comparison is not the full bidirectional/normal surface
error metric or the influence-closed AffectedSurfaceDomain of ADR-0060. Candidate
side surfaces, full exposed region, support/physical bead feasibility, extrusion
intent and chronological nozzle/hotend clearance still need their own gates.
The next implementation scope is that broader geometry/support/clearance work,
not enabling export based on this local score. Source G-code SHA remains
`499ecc78586fea15694eea16a33bfebea761522aa0bf5eee9069e67c0ae1dd9e`.

No printer connection, printable output, commit/push, merge or release occurred.
`log_iotc.txt` was not edited, deleted or staged. To compare previous behavior,
use the retained old VIEW_ONLY files; production rollback is inapplicable.
