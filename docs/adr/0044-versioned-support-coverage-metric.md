# ADR-0044: Define a versioned deterministic support-coverage metric

Status: Accepted
Date: 2026-10-08

## Context

The closed straight-footprint controller in ADR-0058 defines the executable
adaptive integration of this ADR's actual nominal-bead cell query, including
arbitrary-direction footprint enclosure and minimum contiguous width. It does
not replace the source-envelope builder or confer physical/injection authority.

Current v1 documents correctly separate ChronologicalSupportEnvelope from FinalSurfaceEnvelope, but still use phrases such as "sufficient overlap/contact" without defining one authoritative metric.

That leaves a serious implementation ambiguity:
two implementations could accept/reject the same candidate using different support interpretations.

Physical support thresholds are empirical, so hard-coding an arbitrary percentage during architecture work is also unacceptable.

## Decision

Introduce one versioned `SupportCoverageMetric` owned by the engine contract.

For each candidate segment:

1. construct the candidate XY footprint from its finite bead width and centerline segment;
2. query ChronologicalSupportEnvelope over that footprint using deterministic sampling/integration;
3. classify footprint locations as support-eligible only when the local support top produces a valid effective bead-height/contact state;
4. compute at minimum:
   - `supported_area_fraction`;
   - `minimum_contiguous_support_width_mm`;
   - `minimum_effective_height_mm`;
   - `maximum_effective_height_mm`;
5. compare these values with validated plugin Settings.

Required settings include:
- `min_support_area_fraction`;
- `min_support_contact_width_mm`;
- support-query numeric tolerance/version.

These settings participate in PluginSettingsFingerprint.

No universal physical defaults are claimed except where a research fixture explicitly supplies them.

For physical injection, support thresholds are fixture/calibration evidence and are independently reviewed.

## Closed nominal-bead cell query — 2026-10-16

The support metric's local eligibility means vertical support eligibility:
material exists at the XY location, and command_z minus the highest chronological
nominal top lies inclusively within the configured candidate height bounds.
This adopts the existing h_eff=nozzle_z-support_z relation. It is not measured
adhesive contact area or literal intersection with the candidate's curved
underside. No numeric query tolerance becomes an invented physical gap allowance.
Solid collision/overbuild and calibrated physical support remain separate gates.

Implement this bounded query over the actual ADR-0048 segment top, not rectangle
patch substitutes. This is the cell-query provider only, not the adaptive
controller, area/contiguous-width integration or full ChronologicalSupportEnvelope.

### Required immutable vocabulary and API

All DTOs are frozen/slotted with all fields required and no defaults. Strings
are exact builtin nonblank values; tuples/nested types are exact; floats use the
existing finite-binary64 convention (bool/subclasses/overflow/nonfinite reject).

| DTO | Exact fields and constraints |
| --- | --- |
| SupportCellXY | x_min_mm, x_max_mm, y_min_mm, y_max_mm: finite binary64 with strictly positive extents |
| NominalSupportSegment | segment_id: str; start,end: exact PrintPoint3; width_mm,height_mm: finite with width>=height>0; source_kind: str literal structural or candidate; execution_order: builtin int>=0 |
| SupportCellQueryPolicy | version: str literal nominal_bead_cell_bounds_v1; sqrt_fraction_bits: builtin int in [1,4096]; max_source_segments: builtin int>=1 |
| SupportCellQueryResult | state: str; top_z_lower_mm,top_z_upper_mm,effective_height_lower_mm,effective_height_upper_mm: exact Fraction or None; reason: str |

The input segment XY endpoints must differ after binary64 conversion. Sources
are an exact tuple with unique segment IDs; their order does not affect results.
All sources must have execution_order strictly smaller than the query order.
Candidate sources additionally have identical start/end Z and strictly smaller
command Z than the query. Structural sources may slope and may have high local
tops; retain them so earlier obstructing material cannot disappear. This query
does not admit same-Z candidate vertical support. A separate collision query
must still consider material excluded from this required-support input set.

```python
def query_nominal_support_cell(
    cell: SupportCellXY, sources: tuple[NominalSupportSegment, ...], *,
    command_z_mm: float, execution_order: int,
    height_bounds: CandidateBeadBounds, policy: SupportCellQueryPolicy,
) -> SupportCellQueryResult: ...
```

The query validates the exact existing CandidateBeadBounds class and uses its
height bounds only; validating candidate width belongs to the candidate caller.
command_z is finite and execution_order an exact nonnegative int. Convert numeric
inputs to binary64 and then exact Fraction before subtraction/products; no float
geometric intermediate is a predicate. The module owns no I/O or mutable state.

### Deterministic certified algorithm

For each segment let d=end.xy-start.xy and D=dot(d,d)>0. At the four world-XY cell
corners compute exact affine t=dot(p-start,d)/D and c=cross(p-start,d). Their min/
max are exact ranges on the entire rectangle. Derive squared lateral distance
range q: lower=0 if c spans zero, otherwise min(c_min**2,c_max**2)/D; upper=
max(c_min**2,c_max**2)/D. A segment is proven disjoint if t_max<0, t_min>1 or
q_min>(w/2)**2. Otherwise it is potentially present. Full footprint coverage
requires t_min>=0, t_max<=1 and q_max<=(w/2)**2. Touching boundaries remain present.
These marginal bounds may overestimate an intersection; never declare coverage
from them unless the full conditions hold.

For possible segments clamp the t range to [0,1] and bound the linear nozzle Z
exactly. Let g(q) be the nonnegative cross-section top offset above z(t)-r:
g(q)=r for q<=a*a; otherwise sqrt(r*r-(sqrt(q)-a)**2). It is nonincreasing on
0<=q<=(a+r)**2. An upper top bound is nozzle_z_upper-r+upper(g(q_min)). For a
fully covering segment a lower top bound is nozzle_z_lower-r+lower(g(q_max)).
The flat-center branch returns r exactly, without applying a square-root
approximation to r*r. Thus a wholly flat-center-covered cell retains its exact
affine nozzle-Z interval even at low precision. Clamp every curved g upper bound
to the known exact r; a rounding enclosure must not exceed the nominal top.
Correlation between t and q may be lost only outward, never by a point estimate.

For rational x=n/d>=0 and b=sqrt_fraction_bits, k=isqrt((n << (2*b)) // d).
The square-root lower bound is k/2**b; upper equals lower if lower**2==x,
otherwise (k+1)/2**b. For g's nested square roots, propagate interval arithmetic:
subtract a, clamp distance lower/upper to >=0, square nonnegative bounds, subtract
from r*r with reversed endpoints, clamp the radicand bounds to >=0 and apply
the same outward square-root rule. The exact radicand is nonnegative in domain;
clamping a negative conservative lower bound to zero cannot assert positivity.
No epsilon, math.sqrt or rounded unit tangent substitutes for these bounds.

Union upper is max of the upper top bounds of EVERY potentially present segment,
including partial overlaps. If at least one segment fully covers the cell, union
lower is max of the lower bounds of fully covering segments. Otherwise union
lower is unavailable. This initial provider deliberately leaves seam-only union
coverage unresolved even when multiple partial segments together cover the cell.
It does not invent a general union-coverage proof.

Effective-height lower=command_z-union_upper, upper=command_z-union_lower where
the respective top bound exists. Results retain exact rational, possibly negative
height bounds; do not force them into nonnegative ConservativeSupportBounds or
round them inward. Return proven-supported only with full coverage and both
height bounds inside the configured inclusive interval. Return proven-unsupported
if no segment is potentially present, or height_lower>configured_max, or a known
height_upper<configured_min. Otherwise return unresolved. Known unsupported and
unresolved remain distinct; neither supplies supported area to a future controller.

### Result states, resources and limits

state is exactly proven-supported, proven-unsupported or unresolved. reason is
respectively height-within-bounds; disjoint or height-outside-bounds; or
coverage-unresolved, height-unresolved or resource-limit. Disjoint and resource-
limit results have all four bounds None. For other results top upper and height
lower exist; top lower and height upper are either both present or both None.
Every present lower/upper pair is ordered. A fully covering result has both pairs;
partial-coverage unresolved has only upper-top/lower-height. These are arithmetic
results, never runtime VALIDATED receipts or physical authorization.

Validation precedence is explicit: first validate the top-level exact cell,
sources tuple, policy and CandidateBeadBounds types, and finite query command Z
and exact nonnegative query order. Then, if source count exceeds the policy cap,
return unresolved/resource-limit without scanning source elements, IDs or
chronology and with all bounds None. Within budget validate exact source types,
unique IDs and chronology before geometric work. Malformed policy/bounds types
or settings use ContractError(INVALID_SETTING); malformed cell/query/source/
result geometry, container types or chronology use ContractError(INVALID_GEOMETRY).
No malformed case becomes successful support evidence.
The fixed maximum precision of 4096 fraction bits bounds shift allocations for
finite-binary64 input arithmetic; it is a computational ceiling, not a physical
default. Every policy field is explicit. This provider is not connected to Plan
selection or fingerprinted Settings yet; before such integration, its version,
precision and resource-policy effect must be part of the approved planning
identity. Do not silently bypass existing Settings version registries.

Tests must independently establish flat-center/curved-side/circular limits,
sloped structural Z, flat axial caps, rotated segments, reversal symmetry,
subnormal/extreme inputs, partial high overlaps, seam coverage unresolved,
empty input, bad chronology, exact height boundaries, precision tightening and
resource exhaustion. No new dependency is needed. Local query success does not
mean adaptive convergence, full support integration or physical safety.

## Same-Z and dependency semantics

The metric consumes only ChronologicalSupportEnvelope material.

It therefore preserves ADR-0032:
- no future material;
- no cyclic dependency;
- same-Z candidates cannot provide required vertical support to one another in v1.

## Requirements / invariants introduced

- One support metric owner.
- "Sufficient support" is never a free-form implementation judgment.
- Missing/unvalidated physical support thresholds => analysis-only.

## Test impact

Add analytic fixtures for:
- fully supported footprint;
- partial support;
- narrow disconnected contact;
- same area fraction but insufficient contiguous width;
- future-material exclusion;
- lower-candidate support;
- deterministic results under segment reversal/canonicalization.

## Rollback / disable condition

Support metric fails to converge/resolve => candidate infeasible.


## Refinement note

ADR-0058 is the canonical hard-acceptance refinement contract. Fixed-resolution sampling alone is insufficient; conservative bounds and convergence are required.
