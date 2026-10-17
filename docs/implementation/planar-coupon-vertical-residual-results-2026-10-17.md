# Planar coupon vertical residual comparison: implementation result

Disposition: restricted research comparison PASS on explicit nominal inputs.
It does not establish actual Orca slice identity, full surface improvement or
printability.

Authority: `docs/specs/planar-coupon-vertical-residual-comparison-draft.md`
at spec commit `f0a1a31` (`SPEC_VALIDATED`), accepted ADR-0047/0048/0060
scope boundaries. Independent read-only repository review against MAIN
`9fb2605` returned `validated` after closing rectangle-bit preflight and
the exact target/top failure mapping.

The new domain receipt records two certified intervals for the maximum
absolute **vertical top** residual over the same closed rectangle. The engine
first revalidates the source mesh and proves a planar top in the same call.
It then evaluates the same structural baseline tuple alone and with exact
candidate segments on one shared bounded quadtree. Whole-cell top bounds
give upper residual bounds; exact point top intervals give lower bounds.
Only strict disjoint intervals can certify a reduction. Missing coverage,
resource exhaustion, cancellation and target ambiguity publish no favorable
score. Source-mesh and slice IDs are caller assertions, not proven Orca
provenance. Candidate width/Z are explicit nominal inputs, not calibrated
profile values.

Independent implementation review found an unknown target-rejection reason
could be translated into ordinary target-unresolved. The engine now accepts
only the closed certified reason list and raises INVALID_GEOMETRY for unknown
reasons. Added tests cover actual/unknown target rejection, interval overlap,
one split and leaf limit, and cancellation after a prior leaf. Final blind
review found no material issue.

Windows `.venv/Scripts/python.exe` (Python 3.12.10) validation:

- `-m compileall -q adaptive_subedge tests tools`: PASS.
- Architecture/import-boundary suite: 43 PASS.
- Coupon, exact-top and planar-top focused modules: 29 PASS.
- Full `unittest discover -s tests -p test_*.py -q`: 618 PASS.
- Canonical manifest integrity at implementation commit `9b4e4fb`: 85 Git
  blobs PASS (integrity only, not spec approval).
- `tools/build_validation_artifacts.py`: PASS, exact-head research ZIP SHA-256
  `060b2abb17ccccf3e4277767adace7029a2166cfb46e694b66938e84b4f72b4b`;
  extracted isolated source import PASS. The ZIP is non-installable.
- `tools/build_preview_plugin.py --output-dir artifacts/package-check`:
  PASS, check wheel SHA-256
  `50d3d40c482afc34eb71e4e700b945fed1bd1064ef75db5c7d0075fdbcf11cf4`;
  isolated `python -I` import of the new comparison API PASS. This wheel was
  not installed or runtime-tested inside Orca.
- Lint/type analyzers: NOT CONFIGURED; no dependency added.

No Plan,
Orca callback, G-code, printer or unrelated log file was changed. Before
product improvement can be claimed, candidate placement must be bound to
an actual source-model region and explicit slicer baseline, with full
ADR-0047/0060 geometry, support and side-effect gates. Same-plan native
Preview and validated G-code output remain unresolved.

## Adjacent-line midpoint probe (2026-10-17)

A reproducible exploratory call used the analytic frustum from
`tests/unit/test_section_difference.py`, not an Orca slice. Two X-directed
structural centerlines ran from X=1 to X=3 mm at (Y,Z)=(0.25,0.25) and
(0.75,0.75) mm, each with 0.6 mm nominal width and 0.2 mm height. The
candidate joined their midpoint positions at (Y,Z)=(0.5,0.5) mm with
0.3 mm nominal width and 0.2 mm height. The target rectangle was
X=[1.5,2.5], Y=[0.45,0.55] mm on the planar face Z=Y. The ignored scratch
reproducer is
`tests/unit/test_coupon_residual.py::CouponResidualTests.test_adjacent_line_midpoint_requires_full_structural_baseline`;
run the module with `.venv/Scripts/python.exe -m unittest
tests.unit.test_coupon_residual -q`.

With **both** adjacent structural lines in the baseline, baseline and
augmented maximum vertical residual intervals were identical:
`[129601637/536870912, 664695683/2684354560]` mm (148 leaves,
`interval-overlap`). With only the lower line in an artificial baseline,
the interval changed from `[8589803517/21474836480, 2/5]` mm to exactly
`1/20` mm (one leaf, `certified-reduction`). Thus midpoint placement is a
possible candidate heuristic, but cannot itself certify benefit against the
full sliced baseline. Width/footprint, support, and Orca slice provenance
remain unverified; this probe authorizes no injection or printing.
