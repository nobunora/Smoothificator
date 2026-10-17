# Candidate generation repository review

Disposition: **spec-change-required**. This record is a review finding and a
recommended next scope, not an accepted numerical generator contract.

Reviewed against implementation 3cbdff6 and spec f0c318b: ADR-0005, ADR-0029,
ADR-0043, ADR-0063, SurfaceBandV2/SubEdgePathV2, SubEdgePath and Settings v2.
An independent specification reviewer reached the same disposition. No production
behavior was changed and no tests were required for this documentation-only step.

## Verified gap

SurfaceBandV2 carries source/boundary/residual-region identity references, not an
executable exposed-band geometry. Existing Settings define width/height bounds,
seam magnitude, physical regularity and search budgets, but do not close a
candidate-placement algorithm or band construction. The engine now provides
mesh validation, exact sections/stability, point and whole-segment material
classification. These are prerequisites, not a generator or finite-bead scorer.

ADR-0005 explicitly prohibits using a mesh boundary as the nozzle centerline or
assuming a fixed half-width offset is an exact surface solution. ADR-0029 puts
open execution geometry and any seam gap before scoring. ADR-0043 constrains
bead dimensions; ADR-0063 requires length/time and adjacent shape/flow checks.
Research DTO construction alone does not establish those conditions.

## Recommended bounded next specification

Define a versioned unscored proposal family for certified convex planar sections.
Naturally open parallel chords avoid inventing a closed-loop seam rule. A first
axis-aligned rational method can clip explicit chord positions against inward
halfplanes, accounting conservatively for the transverse footprint and explicit
endpoint trimming. Fresh whole-segment material validation is mandatory. This
restricted proposal method must reject unsupported concave input and remain
separate from feasible SubEdgePath/Plan evidence.

Before production implementation, close and independently validate:

1. Whether this bounded primitive consumes a fresh mesh section or an executable
   exposed-band domain; define band exposure/nesting proof before claiming band
   coverage. Existing identity references cannot stand in for geometry.
2. Exact direction/chord-position inputs, width, endpoint trimming, ordering,
   resource limits and cancellation. No guessed printer-specific defaults.
3. Immutable proposal/result types and closed failure reasons, with no execution
   authority or automatic registration as a scored Plan.
4. Finite-bead envelope and bidirectional error acceptance, including end caps
   and uncovered/changed surface regions. Footprint containment alone is not
   error improvement or support feasibility.
5. Effective-height, speed and flow provenance before checking bead bounds and
   regularity or promoting a proposal to planned intent.

Required fixtures include boundary/centerline separation, entire-footprint
containment, narrow regions, concave rejection, translation determinism, trimming
that leaves a segment too short, and geometrically interior proposals that still
fail support or finite-bead scoring. Finite bounded search must not claim global
optimality.

The recommendation follows the original improvement/preview/safe-output purpose;
no user choice is needed to keep unsupported geometry analysis-only. The next
task is an accepted bounded numerical contract, then implementation and independent
fixtures. Candidate generation, actual Orca preview and safe output remain open.
