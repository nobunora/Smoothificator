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
- Lint/type analyzers: NOT CONFIGURED; no dependency added.

Exact-head package/build and CI results are recorded after commit. No Plan,
Orca callback, G-code, printer or unrelated log file was changed. Before
product improvement can be claimed, candidate placement must be bound to
an actual source-model region and explicit slicer baseline, with full
ADR-0047/0060 geometry, support and side-effect gates. Same-plan native
Preview and validated G-code output remain unresolved.
