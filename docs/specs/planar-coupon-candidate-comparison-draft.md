# Draft: bounded planar coupon candidate comparison

Status: DRAFT_SPEC. No repository-review disposition or implementation authority.

Independent read-only review returned `spec-change-required`. Before this can
advance, distinguish upper-envelope facets from side-boundary contacts, prove
the evaluation cell's exposure and interval geometry, specify one reusable
nominal bead-solid top-query owner, and close exact containment of candidate
end caps in nonrectangular cells. A missing baseline strip cannot be scored as
an improvement under the current whole-region coverage rule. The narrower
`phase1b-planar-cell-top-coverage-draft.md` resolves only the first proof
prerequisite and does not authorize this broader candidate comparison.

Canonical basis: `docs/SPECIFICATION.md` at the audited revision in
`docs/AUDIT_REVISION_2026-10-16.json` (manifest Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`). Accepted ADR-0005,
ADR-0030, ADR-0043, ADR-0047, ADR-0048, ADR-0059 and ADR-0060 retain their
authority. This handoff must be adjudicated against those contracts before
implementation. It proposes an analysis-only result, not a Plan, a printable
candidate, or the canonical `ErrorEstimator`.

## Bounded question and existing owners

For a single closed convex coupon whose target top is provably one plane over a
bounded XY region, can one or more width-bounded candidate lines reduce a
**restricted top-height residual** relative to explicitly supplied nominal
structural lines? Report a comparison only when both cases are certified over
the same whole region. This metric is deliberately not ADR-0047's bidirectional
normal-aware surface error and cannot satisfy its tolerance gate.

Reuse the existing exact section/embedding owners, the two-height
`derive_convex_section_difference` cells, and `propose_convex_chords` /
`propose_convex_band_preview` where their input and output contracts apply.
Do not duplicate their clipping, material-side, width-partition, or finite
footprint algorithms. The only new geometric work is proving the target coupon
top is a single plane across the entire evaluation region, mapping each
reused line footprint to the difference cells, and bounding the restricted
residual of the nominal bead union. If the existing APIs cannot represent a
needed position or width exactly, reject that candidate set rather than
silently introducing a second chord owner.

## Input and output contract to close in specification review

Use one fresh mesh validation for the call; never trust a caller-created
section/difference DTO as proof. Inputs must identify the exact bounded coupon
region, lower/upper Z, explicit candidate command Z, the source mesh, and
**explicit nominal structural segments** in the same mesh/world coordinate
frame. A mesh section is not a substitute for the sliced structural baseline.
The caller must provide validated finite positive minimum/maximum width and
effective-height bounds, with every candidate satisfying `width >= height`
per ADR-0043. No nozzle-derived universal maximum is invented. Enumerate a
finite, sorted, deterministic set of X/Y equal-band alternatives and bounded
line counts using existing chord owners. Multiple lines are required when one
allowed-width line cannot cover the chosen transverse span; if no feasible
partition exists, report no candidate. No arbitrary epsilon, rounding repair,
or hidden unbounded search is permitted.

A proposed immutable result carries: disposition/reason; source and baseline
identity digest/coordinate provenance; exact coupon region and target-plane
proof reference; the ordered candidate line geometry with each width, height,
command Z and closed footprint; baseline and candidate restricted residual
intervals; a comparison label (`certified-reduction`, `no-certified-reduction`,
or `unknown`); and resource/cancellation diagnostics. The concrete DTO/API,
budget parameters and stable reason matrix remain **open** until repository
review establishes existing nominal-segment and bead-solid interfaces. Do not
publish a false success-shaped empty candidate on unresolved geometry.

## Mathematical acceptance boundary

1. Prove every source facet intersecting the closed target region belongs to
   the same nonvertical graph `z = a*x + b*y + c`, with exact rational
   coefficients and correct outward/material orientation. Detect uncovered XY
   points, overlap, competing facet heights, holes and non-planar boundaries;
   any such case is unknown/rejected, not a sampled-plane inference. The two
   endpoint sections alone never prove this condition, including a possible
   middle-Z bulge.
2. Require each candidate's closed planar footprint to be contained in a
   derived exact difference cell or a proven union of cells, and retain strict
   whole-centerline material-side validation from the existing chord owner.
   Equal bands cover only their explicitly guaranteed common rectangle.
   No width-zero line or claim that a union of open gaps is covered by endpoint
   samples is allowed.
3. Construct both baseline and baseline-plus-candidate nominal solids from the
   same ADR-0048 stadium sweep, flat axial caps, local width/height and union
   rule. Segment chronology, support, clearance, flow, regularity, machine
   motion and physical extrusion remain outside this research result.
4. On the **entire closed coupon region**, account for every point where either
   top envelope is absent. Do not score only places where candidate material
   exists. Compute certified lower/upper bounds for the maximum absolute
   vertical distance from the planar target to each nominal top envelope,
   refining deterministically within an explicit finite budget. Missing top
   coverage is unresolved/infeasible, never zero error. The region must also
   contain every candidate-induced exposed top change and its nominal width/end
   influence; otherwise comparison is unknown. This top-only closure is still
   narrower than ADR-0060's full affected-surface domain.
5. Report `certified-reduction` only when the candidate interval's upper bound
   is **strictly less** than the baseline interval's lower bound. Overlap,
   numerical non-convergence, unknown coverage, or exhausted budget yields
   `unknown`; equality is not an improvement. Never translate this label into
   `E_max`, a physical safety claim, or injection authority.

Use exact Fraction topology, clipping and plane predicates. Where square roots
and nominal bead arcs prevent exact rational extrema, use outward-rounded
certified numeric intervals with explicit precision/refinement limits. A
floating-point sample maximum alone is not a certified upper bound. Candidate
selection remains deterministic under equivalent mesh triangle permutations
and input line ordering, subject to stable source identity semantics.

## Acceptance fixtures and explicit non-claims

- Sloped convex coupon with a known single planar top, one allowed width, and
  then a narrower maximum requiring multiple ordered lines: finite footprints,
  width/height bounds and line count are checked independently.
- Structural baseline supplied as segments rather than reconstructed from
  sections; identical geometry after segment reordering yields the same score.
- Narrow unfilled strip, line end cap, and candidate reaching a coupon edge:
  no missing or affected top area disappears from the metric.
- Middle-height bulge, nonplanar facet, hole, competing target heights,
  ambiguous orientation, nonnested sections and candidate footprint escaping
  the difference cells: no scored success.
- Certified disjoint residual intervals give reduction; overlapping intervals
  and exact equality do not. Precision/resource exhaustion and cancellation
  publish no partial authoritative geometry or score.

This research result does not establish ADR-0047 bidirectional error, ADR-0060
full side/neighbor influence closure, calibrated widths, support, collision,
G-code consistency, safe export, or same-plan Orca preview. Those gates require
separate validated specifications and implementation. Native Preview may label
unscored lines `Custom` only; it must never display this restricted comparison
as a validated surface-improvement percentage.
