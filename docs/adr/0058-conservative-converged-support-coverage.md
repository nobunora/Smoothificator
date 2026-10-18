# ADR-0058: Make support-coverage acceptance conservative and converged

Status: Accepted
Date: 2026-10-08

## Context

ADR-0044 defines a deterministic SupportCoverageMetric using the candidate footprint and ChronologicalSupportEnvelope.

However, a fixed sampling grid can produce a false-positive support decision.

Example:
- a narrow unsupported slot exists inside the bead footprint;
- the slot is narrower than the current sample spacing;
- no sample lands inside the slot;
- supported_area_fraction is incorrectly reported as 1.0.

This is unacceptable because support is a hard printability gate, not only a quality estimate.

ADR-0045 already requires convergence for surface-error metrics. Support acceptance needs an equivalent fail-closed numerical contract.

## Decision

Replace any fixed-resolution "sample and trust" support acceptance with a versioned conservative adaptive procedure.

### Support query coordinates

Evaluate support in a deterministic candidate-local footprint frame:
- longitudinal coordinate along the segment;
- lateral coordinate across nominal bead width.

The authoritative support query still uses ChronologicalSupportEnvelope.

### Cell classification

Partition the candidate footprint into deterministic cells.

For each cell classify:

- PROVEN_SUPPORTED:
  the whole cell is conservatively proven to have valid underlying material/contact and effective-height bounds;

- PROVEN_UNSUPPORTED:
  any part required by the conservative cell bound is proven outside support/contact limits;

- UNRESOLVED:
  current geometric/numeric bounds cannot prove either state.

A cell MUST NOT be counted as supported merely because its center/corner samples are supported.

### Adaptive refinement

UNRESOLVED cells are subdivided deterministically.

Required settings:
- initial_support_cell_size_mm;
- support_refinement_factor;
- support_metric_convergence_fraction;
- support_width_convergence_mm;
- max_support_refinement_levels;
- minimum_support_cell_size_mm;
- support-query numeric tolerance/version.

All participate in PluginSettingsFingerprint.

### Conservative lower bounds

Acceptance uses conservative lower bounds:

- supported_area_fraction_lower_bound;
- minimum_contiguous_support_width_lower_bound_mm;
- minimum_effective_height_lower_bound_mm;
- maximum_effective_height_upper_bound_mm.

Unresolved cells at the maximum refinement level are treated as unsupported for hard acceptance.

### Convergence

At each refinement level compute the conservative metrics.

Hard support acceptance requires:
- all hard thresholds satisfied by lower/upper bounds;
- change in supported-area lower bound <= support_metric_convergence_fraction;
- change in contiguous-support-width lower bound <= support_width_convergence_mm;
- effective-height bounds stable within configured numeric tolerance;
- convergence achieved before max level.

Failure to converge => candidate non-injectable.

### Optional exact geometry path

A future/existing exact polygon/solid intersection implementation may replace adaptive subdivision only if it produces equal-or-more-conservative deterministic bounds under the same metric interface and passes parity fixtures.

No implementation may silently switch to a non-conservative point-sampling shortcut.

### Closed straight-footprint adaptive controller

The following bounded algorithm is `adaptive_nominal_support_v1`. It consumes
the actual nominal-bead query in ADR-0044 directly; a callback cannot provide
geometry proofs. It implements numerical support coverage for a straight,
constant-width, constant-command-Z candidate of arbitrary XY direction.
It does not implement source parsing, collision clearance, Plan integration,
physical validation, or the complete ChronologicalSupportEnvelope builder.

Exact public vocabulary (frozen, slotted immutable dataclasses; no defaults):

```python
SupportFootprint(start: PrintPoint2, end: PrintPoint2, width_mm: float,
                 command_z_mm: float, execution_order: int)
SupportCoverageSnapshot(supported_area_fraction_lower_bound: Fraction,
    minimum_contiguous_support_width_lower_bound_mm: Fraction,
    minimum_effective_height_lower_bound_mm: Fraction | None,
    maximum_effective_height_upper_bound_mm: Fraction | None,
    unresolved_area_fraction: Fraction, leaf_count: int)
AdaptiveSupportResult(state: str, reason: str,
    metrics: SupportCoverageSnapshot | None,
    levels_completed: int, cells_evaluated: int)

evaluate_support_coverage(footprint: SupportFootprint,
    sources: tuple[NominalSupportSegment, ...], *,
    bead_bounds: CandidateBeadBounds, thresholds: SupportCoverageThresholds,
    refinement_policy: SupportRefinementPolicy,
    numeric_policy: SupportQueryNumericPolicy,
    query_policy: SupportCellQueryPolicy, max_cells: int,
    cancelled: Callable[[], bool]) -> AdaptiveSupportResult
```

Use exact existing DTO classes, not subclasses. Footprint scalar construction
uses the existing finite binary64 numeric normalization (bool excluded), positive
width, nonzero XY length after normalization, and exact nonnegative integer
execution order. Width must be inside bead_bounds at evaluation. Every subsequent
geometric and metric operation uses exact Fraction values of normalized floats.
max_cells is an exact positive integer; cancelled must be callable and every
returned value must have exact bool type. Invalid policy/configuration/callback
values raise INVALID_SETTING; malformed geometry/query/result values raise
INVALID_GEOMETRY. Callback exceptions propagate. Existing source chronology and
source-count precedence remain owned by the cell query. No tolerance expands
height eligibility or coverage proofs.

Use local coordinates t in [0,1], v in [-w/2,w/2]. For d=end-start and D=d.d,
the actual world point is start+t*d+v*(-dy,dx)/sqrt(D). Enclose signed unit-normal
components using the existing engine support_cell._sqrt_bounds on dy²/D and
dx²/D with query_policy.sqrt_fraction_bits, exact signs and exact zero. Interval
map all four local-cell corners and take an outward rational world AABB.
Convert each lower bound downward and each upper bound upward to binary64:
round to float, compare its exact Fraction, then nextafter outward only if
needed. Any nonfinite bound/conversion stops with coordinate-range; never clamp.
Query that SupportCellXY using the existing source tuple, command Z, order,
bead bounds and query policy. A whole-AABB proof transfers to the contained
local cell. Extra AABB area can cause conservative unresolved/rejected results.
No corners-only sample or inward conversion is permitted.

Level indices are 0 through max_support_refinement_levels-1 inclusive; that
setting is the total maximum completed passes. Level l target side is the exact
s_l=initial_support_cell_size_mm/(support_refinement_factor**l). Initial grid
has n_t=ceil(sqrt(D)/s_0), n_v=ceil(w/s_0), both at least one, uniform exact local
partitions covering the entire domain. Compute ceil(sqrt(x)) exactly with
integer isqrt and rational square comparison, not a rounded length. At later
passes retain every proven-supported and proven-unsupported leaf. For each
unresolved leaf of sides dt,dv, propose n_t=max(1,ceil(sqrt(D*dt²/s_l²))) and
n_v=max(1,ceil(dv/s_l)). If a split axis would have child physical side smaller
than minimum_support_cell_size_mm, set that axis count to one. Longitudinal
minimum comparison uses D*(dt/n_t)²; lateral comparison is rational. Unchanged
unresolved cells are re-queried and consume budget. No rounding of the configured
factor to an integer is allowed. Initial boundary cells smaller than the minimum
are permitted; minimum restricts subsequent splits only.

Before allocating a grid or a pass's replacement cells, compute its prospective
query count and require cumulative cells_evaluated plus that count <= max_cells.
Otherwise stop resource-limit with the last complete snapshot. Increment
cells_evaluated after each returned cell query, including a cell query returning
resource-limit; that reason immediately stops the controller. Check cancellation
before each pass, each query, and each metric sweep event. Cancellation returns
cancelled with only the last fully completed snapshot. Partial-pass metrics
never replace it. Source-count overflow cannot be reinterpreted as coverage.
Zero-query passes are allowed only when all leaves are resolved, and require
at most one additional pass for convergence. Thus tiny refinement factors cannot
produce unbounded zero-work unresolved iteration. Level limits and query budget
are checked before expensive subdivisions; use bounded-count comparisons rather
than materializing huge grids or huge rational powers beyond the available budget.

Area lower bound is sum(dt*dv for supported leaves)/w; unresolved fraction uses
unresolved leaves identically. The length Jacobian cancels. Width lower bound is
the minimum, over every positive-length longitudinal slab, of the longest union
of supported lateral intervals. Sweep sorted exact t events with coordinate-
compressed v endpoints and a coverage-count segment tree storing covered prefix,
suffix and longest interval: O(N log N) time and O(N) storage for N leaves.
Process coincident events together; gaps yield zero. Closed proven rectangles
make this open-slab minimum conservative also at event lines and endpoints.
Point-only support adds no certified area/width. Height extrema are respectively
the minimum lower and maximum upper query height bounds over supported leaves
only. Both are None iff there are no supported leaves; these are not global
height bounds over unresolved or unsupported material.

After each entire pass, publish the snapshot and increment levels_completed.
Convergence requires two consecutive complete snapshots: absolute area and width
changes <= their refinement-policy tolerances, and both height-extrema changes
<= numeric_policy.support_query_length_tolerance_mm. Two absent height pairs are
stable, but cannot pass support. Any nonzero unresolved fraction prevents a
converged disposition even if thresholds would otherwise pass. With zero
unresolved fraction and convergence, all configured area/width thresholds and
inclusive bead height limits must pass and height extrema must exist to return
state numerically-supported, reason converged; otherwise return state
numerically-rejected, reason thresholds-failed. Check this before exhaustion at
the final permitted pass. A single permitted pass cannot converge. All other
returns have state incomplete and reason max-levels, resource-limit, cancelled,
or coordinate-range. No special minimum-cell outcome is needed: blocked leaves
remain unresolved and consume queries until a declared limit.

Snapshot fractions have exact Fraction type; area/unresolved are in [0,1] with
sum <=1, width >=0, leaf_count exact positive int; height bounds are a paired
ordered Fraction or paired None. Result counters are exact nonnegative ints;
metrics is None iff levels_completed=0. Completed dispositions require metrics,
at least two levels, zero unresolved, and the state/reason combinations above.
An incomplete result never authorizes support. This vocabulary is not registered
in Plan identity or standalone canonical serialization. Integration must pin
this algorithm and its numerical/resource policies in reviewed settings identity;
this independent numerical API introduces no physical defaults.

## Requirements / invariants introduced

- Hard support acceptance cannot depend on lucky sample placement.
- Unresolved fine-scale support is fail-closed.
- Support metric resolution/settings are explicit and fingerprinted.
- Same geometry/settings => identical refinement tree and result.
- Support convergence is distinct from surface-error convergence.

## Alternatives considered

- Fixed dense grid: rejected; no finite fixed grid guarantees detection of smaller unsupported features.
- Count unresolved cells as half supported: rejected for safety.
- Universal exact mesh boolean requirement: deferred; may be expensive and library-dependent.

## Safety impact

High. Prevents numerically missed unsupported gaps from becoming printable candidates.

## Compatibility impact

May reject candidates that older coarse sampling would have accepted.

## Performance / resource impact

Potentially significant near support boundaries. Use deterministic spatial acceleration and bounded refinement.

## Observability impact

Report:
- refinement levels used;
- unresolved area fraction;
- conservative support lower bounds;
- convergence result.

## Test / validation impact

Add:
- unsupported slit smaller than initial sample spacing -> reject;
- supported solid footprint -> converge/pass;
- unresolved boundary at max level -> reject;
- same result under deterministic traversal/order changes;
- parity against exact analytic support geometries;
- convergence threshold boundary tests.

## Migration / rollout

ADR-0044 remains the semantic owner of support metrics; this ADR supersedes any interpretation that a single fixed sampling resolution is sufficient for hard acceptance.

## Rollback / disable condition

Non-converged or unresolved support => non-injectable / Skipped.

## Open questions

Physical support thresholds still require fixture/calibration evidence.
