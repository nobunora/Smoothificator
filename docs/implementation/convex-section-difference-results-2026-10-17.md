# Exact two-section difference: implementation result

Disposition: bounded planar research primitive PASS; surface improvement and
printability are not claimed.

Authority: `docs/specs/phase1b-convex-section-difference.md` at specification
commit `4828031` (SPEC_VALIDATED), accepted ADR-0005/0030/0059. Independent
repository review against MAIN `88c527b` returned `validated`; exact private
embedding/section interfaces, reason matrices, import boundaries and automatic
package source collection matched the handoff.

The new domain DTO admits only exact ordered Fraction heights, closed
dispositions, canonical strictly convex cells and area-consistent complete
results. The engine validates one fresh embedding, takes lower/upper exact
sections, proves upper-section containment in the lower section, then partitions
the planar difference by upper-edge halfplanes. It emits only positive-area
canonical cells, checks exact area conservation and publishes no partial data
on rejection, exhaustion or cancellation. It does not infer any printable
centerline or change the existing section/material/chord APIs.

An independent implementation review found a cancellation boundary after
expected failures and one after DTO construction. Both now return an empty
`incomplete/cancelled` result. It also requested cancellation at every polygon
traversal and a separate cell-interior non-overlap check; both were added.
The reviewer found no remaining material issue after the final fix.

Validation on Windows, Python 3.12.10:

- `python -m compileall -q adaptive_subedge tests tools`: PASS.
- Architecture/import-boundary suite: 43 PASS.
- New DTO and engine tests: 16 PASS, including exact frustum/triangle area,
  skewed nonbinary rational intersections, shared boundaries, nonnested
  rejection, lower-section early stop, exact clip-budget boundary, all-stage
  cancellation and an outward middle-height bulge with equal endpoints.
- Full suite: 582 PASS.
- Preview wheel source/package build in ignored `artifacts/package-check`:
  PASS. This check package is not the separately installed runtime wheel;
  the existing native Custom-only display evidence belongs to the prior build.
- Lint/type analyzers: NOT CONFIGURED; no dependency was added.

Remaining: two isolated planar sections do not prove continuous nesting,
exposed facets, bead support, physical fit or improvement. No Orca baseline
overlay, Plan, G-code injector, export or printer operation was enabled. The
same-plan native Preview research handoff remains DRAFT_SPEC with unresolved
source/provenance and A1-mini modal-command constraints.
