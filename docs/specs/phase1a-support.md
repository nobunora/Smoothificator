# Phase 1A conservative support geometry

Status: DRAFT_SPEC. This is an executable mathematical proposal for review, not
authority to implement or to claim calibrated support. No canonical ADR edited.

## Canonical basis and a necessary geometry correction

ADR-0044 owns area fraction, minimum contiguous width and effective-height
metrics over ChronologicalSupportEnvelope. ADR-0058 requires whole-cell proofs,
conservative bounds and converged refinement; its optional exact-geometry path
permits equal-or-more-conservative deterministic bounds with parity fixtures.
ROADMAP Phase 1A includes both the metric and adaptive refinement/convergence.

ADR-0048's stadium is the transverse vertical cross-section, not the XY
footprint. A constant-width straight segment with flat axial caps has a
rectangular XY footprint. A capsule/stadium in XY would invent rounded end caps
and is rejected. Polyline unions, curved support surfaces, variable-Z structural
beads and source-mesh queries need their own correct provider later.

Existing reusable types: SupportCoverageThresholds, CandidateBeadBounds,
SupportRefinementPolicy, SupportQueryNumericPolicy, ConservativeSupportBounds.
Their validators/accepted ranges must not be changed to simplify this algorithm.

## Recommended bounded first provider: exact flat rectangular support

Implement genuine geometry and arithmetic in engine/support.py, using only
standard-library Fraction/math. Operate in a caller-supplied segment-local frame:
candidate footprint x in [0,length_mm], y in [-width_mm/2,width_mm/2]. All inputs
are finite binary64 interpreted exactly as rationals after existing conversion;
no float geometric intermediates, approximate predicates or point-sampling proof.
Do not claim this module computes the world-to-local transform.

Proposed exact immutable input vocabulary:

```python
FlatSupportPatch(
    patch_id: str, x_min_mm: float, x_max_mm: float,
    y_min_mm: float, y_max_mm: float, top_z_mm: float,
    source_kind: str, source_execution_order: int,
    source_command_z_mm: float,
)
LocalCandidateFootprint(
    length_mm: float, width_mm: float, command_z_mm: float,
    execution_order: int,
)
```

Positive rectangle extents/length/width; exact nonblank unique IDs; source_kind
is structural or candidate; indices are exact nonnegative ints. A provider
accepts only already chronological patches: earlier execution order and strictly
lower source_command_z_mm than candidate command_z_mm. Invalid chronological
inputs reject rather than quietly becoming support. Require top_z_mm <=
source_command_z_mm. These inputs describe idealized flat-top material regions,
not certificates that a bead or mesh actually has that shape.

At any covered point, support top is the MAXIMUM top_z of all covering patches.
Never choose a lower overlapping patch to hide an invalid higher obstruction.
Effective height is candidate command_z minus this top. A location is eligible
only when it is covered and height lies inclusively within supplied
CandidateBeadBounds height bounds. Candidate width must satisfy the supplied
width bounds. No tolerance expands support or valid-height intervals.

### Exact arrangement algorithm and metric definition

Clip rectangles to the candidate footprint. Form sorted unique exact x/y break
coordinates from footprint and clipped patch edges. On each open elementary
rectangle the covering set and top height are constant; determine coverage by
exact interval containment of the ENTIRE cell, not a center sample. Accumulate
eligible area exactly and divide by exact length*width.

For each longitudinal x strip, union adjacent eligible lateral intervals and
take its longest contiguous interval. The minimum of these longest widths over
all strips is the proposed minimum-contiguous-width metric. Include every x
event line (including footprint ends), evaluated against closed patch intervals,
in the width minimum: a zero-area contact failure must not be hidden by an area
average. Include arrangement edges/vertices when determining top-height extrema
or finding contact violations; area remains the measure of the 2D cells only.
Disconnected strips cannot be added to invent one wide contact interval.

Effective-height extrema are over supported/eligible locations. If there are no
eligible locations, return no height-bound value, not invented zero height.
No numerical support pass is possible in that case even if thresholds are zero.
An empty patch set produces area/width zero and an explicit unsupported result.

Convert exact rational lower bounds to binary64 downward and upper bounds upward:
convert to float, compare its exact Fraction to the rational, and use nextafter
toward the appropriate infinity only when needed. Reject nonfinite output range.
Do not rely on ordinary nearest rounding for a conservative bound.

### Proposed public functions

```python
measure_flat_support_exact(candidate, patches, *, bead_bounds) -> ExactSupportResult
evaluate_flat_support_adaptive(
    candidate, patches, *, bead_bounds, thresholds,
    refinement_policy, numeric_policy, max_cells,
) -> AdaptiveSupportResult
```

ExactSupportResult contains available conservative bounds (or None when no
eligible height exists), exact-query model version, unsupported/contact flags
and no physical authorization. AdaptiveSupportResult additionally records levels,
unresolved area upper fraction, termination reason and numerical convergence.
No result writes an injectable flag, creates VALIDATED evidence or publishes Plan.
Precise result field spellings are to be closed in the reviewed implementation
handoff; this DRAFT focuses on substantive algorithms and mathematical ownership.

## Adaptive refinement using that actual geometry provider

Keep the subdivision, bound aggregation, convergence and termination controller
independent from rectangle geometry. Its internal cell-query boundary returns
whole-cell eligible/unsupported/unresolved classification and conservative
height bounds for an exact cell; a provider must document and test the geometric
proof behind each classification. Initially wire only the exact flat-patch
provider. Do not expose a public arbitrary callable that can mint a trusted
supported classification, or interpret Python Protocol conformance as a
conservativeness certificate. Later nominal-bead providers can reuse the same
controller after proof/parity review; every current result remains research-only.

Use the same rectangle arrangement oracle on each candidate-local cell. A whole
cell is PROVEN_SUPPORTED only if the arrangement proves full eligible coverage
with valid height bounds. A wholly ineligible cell is PROVEN_UNSUPPORTED; a
mixed cell is UNRESOLVED and contributes zero supported area/width until refined.
Never infer whole-cell validity from four corners. Conservative upper bounds on
unresolved area count complete unresolved cells.

Start with a deterministic rectilinear grid whose maximum side is the supplied
initial_support_cell_size_mm. At each level, subdivide unresolved cells to maximum
side initial_size / factor**level using exact rational divisions and ceiling
counts. This honors every existing finite factor >1, including nonintegers;
do not silently replace it with a dyadic factor. Clip terminal grid cells exactly
to the footprint. Preserve already-proven cells, and derive width lower bounds
from whole-supported rectangles via the same longitudinal arrangement operation.

At least two completed evaluations are necessary for convergence. Require area,
width and both effective-height bound changes within their supplied tolerances,
AND hard thresholds satisfied, AND no unresolved cells for a successful numerical
result. The last condition conservatively resolves ADR-0058's fail-closed
unresolved-support rule. Never report convergence merely because unresolved cells
produce an unchanged zero lower bound. Stop before exceeding refinement-level or
minimum-cell limits; report incomplete/nonconverged rather than accepting.

PROVEN_UNSUPPORTED is distinct from UNRESOLVED: known uncovered area contributes
zero and may be permitted by explicit area/width thresholds; unresolved geometry
always prevents hard acceptance. A narrow-slit rejection fixture must specify
thresholds that actually disallow that slit (for example full-area support), or
end with unresolved cells. Do not invent a universal rule that all partial
support is forbidden, nor count an unknown cell as proven uncovered to bypass
the fail-closed rule.

max_cells is an explicit positive integer computational ceiling, checked before
grid allocation. Exceeding it is an incomplete calculation, never a success or
an altered numeric bound. Do not allow huge valid refinement factors to allocate
unbounded lists. Cancellation similarly returns/raises incomplete without a
numerical success result. Computational ceilings cannot loosen physical settings.

## Tests and evidence required

- Full flat rectangle: exact area=1, width=width, known constant height;
  two-level supported adaptive convergence without corner-sampling assumptions.
- Partial support and disconnected contact with equal areas but unequal longest
  contiguous widths; exact arrangement expected values calculated independently.
- Slit narrower than initial spacing, including a slit missing every corner:
  coarse cell is unresolved; no false full coverage or converged acceptance.
- Higher overlapping patch invalidates height; cannot select lower support.
- Future/same-Z source rejection and valid lower candidate contribution.
- Rectangle order/IDs do not affect metrics; mirrored longitudinal local input
  (segment reversal) gives identical results; duplicate IDs reject.
- Boundary contact/zero-area event-line cases, extreme/subnormal inputs and
  directed rounding: lower <= independently exact quantity <= upper.
- Adaptive lower bounds never exceed exact arrangement result; unknown cells at
  maximum refinement, minimum-cell stop and resource exhaustion stay incomplete.
- Noninteger refinement factor, deterministic traversal and no-refinement baseline
  preserve existing Settings semantics; no physical threshold defaults.

## Decisions to adjudicate and recommended disposition

### Actual nominal-bead provider: the next necessary contract

The material ambiguity is not how to subdivide rectangles. ADR-0044 says valid
effective-height/contact state but does not define whether contact means literal
intersection with the candidate's curved underside, a vertical-support test, or
a permissible gap. These differ even for a flat plate: a stadium cross-section
touches it only across its central flat bottom (zero width in the circular
limit), whereas its projected footprint spans the full width. A numeric query
tolerance cannot silently become a physical gap/contact allowance.

Recommended canonical decision: define this metric as **vertical support
eligibility**, not measured adhesive contact area. At every candidate footprint
location let z_support be the highest surface of the chronological nominal bead
union. Eligible iff material exists there and candidate_command_z-z_support lies
within the supplied candidate height bounds, inclusively. The metric reports the
resulting area, contiguous width and height bounds. Actual nominal-solid
intersection/overbuild/collision remains a separate hard geometry gate. This
chooses the existing h_eff=nozzle_z-support_z contract, adds no physical default
or invented tolerance, and allows the required min/max effective-height report
to have a consistent meaning across curved support surfaces. If literal
underside contact is desired instead, that is a distinct physical-model change
requiring calibration/geometry semantics, not an implementation shortcut.

For a straight nominal source segment with width w, height h and flat axial caps,
let r=h/2, a=(w-h)/2 and u be signed lateral distance from its centerline. For
0<=t<=1 along the segment, use top envelope:

```text
z_support(t,u) = z_nozzle(t)                         if abs(u) <= a
              = z_nozzle(t)-r+sqrt(r*r-(abs(u)-a)^2) if a < abs(u) <= a+r
              = absent                             otherwise
```

At axial endpoints retain the flat cap; never extend a capsule beyond t in
[0,1]. Union top is max of all present segment tops, not a sum or average. Constant
source width/height within a supplied segment follow ADR-0048's segment-local
model. Proposed explicit nonplanar convention: z_nozzle(t) is linear between the
normalized immutable start/end nozzle Z coordinates; width/height do not gain
hidden interpolation. This permits ZAA sloped structural segments. The source
adapter must prove those coordinates/segment-local h match its normalized Orca
semantics; unsupported zero-XY-length segments reject and require separate
modeling. No source API evidence is invented by this mathematical definition.

Implement a reusable cell query over the actual set of these segment sweeps:

1. Use exact binary64 rational XY/Z inputs. For world point p and segment vector
   d, axial parameter is dot(p-start,d)/dot(d,d); squared lateral distance is
   cross(p-start,d)^2/dot(d,d). Do not round a unit tangent and call it exact.
2. Derive certified interval bounds over the WHOLE queried cell, including
   axial-domain clipping and curved-side transitions. Rational outward square-root
   enclosures can use integer isqrt/dyadic bisection; every refinement tightens
   enclosures. Candidate-local/world transforms must also carry enclosures of
   their exact input-derived basis, not silently rounded coordinates.
3. A lower bound on union top needs proven material coverage of the whole cell.
   A single fully covering segment is sufficient; otherwise prove union coverage
   by a finite conservative partition. Corner coverage is insufficient. Every
   potentially intersecting segment contributes to the top upper bound, so a
   higher overlapping bead cannot be ignored.
4. Convert top bounds to effective-height bounds and classify supported only if
   the entire height interval meets supplied bounds. Proven empty/ineligible
   regions contribute zero. Uncertain coverage, axial clipping or height bounds
   stay UNRESOLVED and use the reusable adaptive controller; no false success.

This certified interval provider is feasible with the standard library, but is
substantive geometry work and requires independent analytic fixtures: flat-center
and curved-side tops, circle limit, sloped ZAA locus, flat caps, overlap maxima,
union coverage across a seam, exact-boundary heights, reversal and rotated inputs.
Rectangle fixtures are only the controller oracle, not a substitute for these
tests or a claim of full Phase1A support. A geometry dependency is optional only
if its conservative arithmetic/union contract is independently established;
ordinary floating intersections or a callback returning PROVEN_SUPPORTED are
not certificates. Recommend adjudicating the vertical-eligibility and linear
source-locus conventions above, then implementing this real provider and its
controller as the next substantive support milestone.

1. **Metric ambiguity:** ADR-0044 does not specify whether minimum contiguous
   width means the minimum over longitudinal slices of their longest interval.
   Adopt the explicit definition above (including event lines); canonicalize it
   as a versioned engine metric before implementation. It is a substantive metric
   decision, not an arbitrary numerical default.
2. **Provider scope:** approve exact flat rectangular material as the first real
   executable provider and analytic oracle. It is not the full nominal-bead or
   mesh ChronologicalSupportEnvelope. No dependency is needed for this slice.
   Do not mark complete support of curved/ZAA material from its tests.
3. **Refinement termination:** fix initial evaluation=level0, successive levels
   1..max_levels-1, with success strictly before exhaustion; max_levels=1 can
   produce diagnostics only. Honor the existing factor>1 DTO rather than narrowing
   it. Any later interpretation change needs a versioned policy decision.
4. **Resource ceiling:** accept explicit max_cells as a computation budget that
   only causes incomplete results, or add it to fingerprinted engine policy if
   callers use it to change candidate selection. Never let it alter an accepted
   metric's mathematical definition.

Material blocker for full Phase1A support completion is the conservative query
provider over the actual nominal bead union and its exact contact-height model,
not lack of a geometry package. Flat rectangles can be implemented and rigorously
tested now after the four decisions and exact API/result schema are approved.
General curved surfaces require certified interval/solid bounds or a separately
reviewed geometry dependency; ordinary floating polygon intersections alone do
not establish conservative support. Physical fixture/calibration remains later
and does not block this pure mathematical implementation.
