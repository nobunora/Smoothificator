# One exact-rational nominal bead top kernel

Status: SPEC_VALIDATED for this bounded research-only nominal top kernel.
Independent specification and read-only repository review against MAIN
`dbea325` returned `validated`: the existing support-cell stadium/arcs remain
the sole bead-math owner, `ChordProposal` provides exact XY but no width/Z,
and the proposed adapter correctly treats those as explicit unproven inputs.
Manifest: `docs/AUDIT_REVISION_2026-10-16.json`, Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`. No implementation or
printable authority follows for a candidate's width/Z provenance.

Canonical basis: `docs/SPECIFICATION.md` at
`docs/AUDIT_REVISION_2026-10-16.json` (manifest Git blob
`7c0e2b4787f9cb6df8f62786ea2c9bc3d1dc9688`). ADR-0048 owns the
stadium-sweep solid and union top; ADR-0043 owns printable candidate bounds.
This mathematical kernel does not validate calibrated Settings ranges or
authorize injection. It extends the existing support-cell bead-math owner,
not a second solid implementation.

## Existing source boundary and closed proposed API

At MAIN `dbea325`, `engine/support_cell.py` owns `_segment_top_bounds`,
`_cap_bounds` and outward `_sqrt_bounds`. `NominalSupportSegment` stores
finite-binary64 structural input; `ChordProposal` stores exact Fraction XY.
The former may normalize its binary64 fields by `Fraction(float(x))`; the
latter must never round through float. Preserve existing public
`query_nominal_support_cell` and `query_nominal_structural_top_point/cell`
signatures, reason matrices and tested results.

```python
# adaptive_subedge/domain/support_cell.py
@dataclass(frozen=True, slots=True)
class ExactNominalTopSegment:
    segment_id: str
    start_xyz_mm: tuple[Fraction, Fraction, Fraction]
    end_xyz_mm: tuple[Fraction, Fraction, Fraction]
    width_mm: Fraction
    height_mm: Fraction
    source_kind: str  # structural | candidate

@dataclass(frozen=True, slots=True)
class ExactTopCellXY:
    x_min_mm: Fraction
    x_max_mm: Fraction
    y_min_mm: Fraction
    y_max_mm: Fraction

@dataclass(frozen=True, slots=True)
class ExactNominalTopBounds:
    state: str
    reason: str
    top_z_lower_mm: Fraction | None
    top_z_upper_mm: Fraction | None

# adaptive_subedge/engine/support_cell.py
def exact_top_segment_from_structural(
    source: NominalSupportSegment,
) -> ExactNominalTopSegment: ...

def exact_top_segment_from_chord(
    proposal: ChordProposal, *, segment_id: str,
    command_z_mm: Fraction, width_mm: Fraction, height_mm: Fraction,
) -> ExactNominalTopSegment: ...

def query_exact_nominal_top_point(
    x_mm: Fraction, y_mm: Fraction,
    sources: tuple[ExactNominalTopSegment, ...], *,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    cancelled: Callable[[], bool],
) -> ExactNominalTopBounds: ...

def query_exact_nominal_top_cell(
    cell: ExactTopCellXY,
    sources: tuple[ExactNominalTopSegment, ...], *,
    max_sources: int, max_coordinate_bits: int, sqrt_fraction_bits: int,
    cancelled: Callable[[], bool],
) -> ExactNominalTopBounds: ...
```

All DTOs are frozen/slotted without defaults. Exact Fraction coordinates,
positive width/height, `width>=height`, nonzero XY segment length, nonblank
ID and closed source kind are required. Candidate start/end Z must be equal;
structural Z may vary linearly per ADR-0048. `ExactTopCellXY` has strictly
positive extents. A structural adapter accepts only exact
`NominalSupportSegment` with `source_kind="structural"` and converts each
existing finite-binary64 coordinate/width/height to Fraction once. A chord
adapter accepts only `ChordProposal(state="proposed",reason="unscored")`;
it takes the proposal's exact XY endpoints unchanged and uses exact supplied
Z/width/height. Neither adapter trusts a preview as proof of material side,
cell coverage, physical width calibration or slicer identity. Rejected chords
cannot become segments. Segment IDs are supplied for traceability, unique
within a query; lexicographic ID and source tuple order never determine top.

## One kernel, query semantics

Factor the private arithmetic into `_segment_top_bounds_exact`, accepting
`ExactNominalTopSegment` and a tuple of one or four exact XY corners. Keep
the existing `_segment_top_bounds` name/signature as a thin adapter that
normalizes its binary64 `NominalSupportSegment` by `Fraction(float(x))` and
delegates to `_segment_top_bounds_exact`. Existing support and structural-top
APIs continue to call their old wrapper, preserving their outputs and
conservative coverage rules. The new exact query calls the same exact
kernel directly. The exact chord never passes through `PrintPoint3`, the
binary64 source DTO or float.
`_cap_bounds` and `_sqrt_bounds` remain single owners of the outward square-
root enclosure. No duplicated tangent/cap equation, XY capsule, along-path
interpolation, or generic nearest-surface approximation is permitted.

Use ADR-0048's closed flat axial interval and rectangular XY projection:
for exact path parameter `t∈[0,1]`, lateral distance `u`, `r=h/2`,
`a=(w-h)/2`, the segment top is nozzle `z(t)` for `u<=a`, or
`z(t)-r+sqrt(r²-(u-a)²)` for `a<u<=a+r`; otherwise absent. `z(t)` is linear
for structural and constant for candidate. At a point, return the maximum
of all present source top enclosures. At a closed rectangular cell, take the
max upper bound of every conservatively intersecting segment, and a max
lower bound only from segments individually covering all four corners.
Different partial segments may cover the union, but that alone is not a
full-coverage proof. Side and axial boundary equality count as present.
Irrational arcs are enclosed by exact rational lower/upper Fractions using
the chosen `sqrt_fraction_bits`; no float conversion follows source
normalization. A present zero/negative Z is a real top value, not absence.

Output reason matrix: `absent/disjoint` (both bounds None),
`full-bounded/covered-point`, `full-bounded/one-segment-covers-cell` (both
ordered Fractions), `unresolved-partial/union-coverage-unproven` (only upper
Fraction), `incomplete/resource-limit` and `incomplete/cancelled` (no bounds).
DTO validates the matrix, not the geometric proof. A point cannot return
`unresolved-partial`; a cell cannot return `covered-point`. Empty sources
return absent. No candidate-vs-baseline score is produced.

## Finite work and cancellation

`max_sources` and `max_coordinate_bits` are required exact positive ints;
`sqrt_fraction_bits` is exact int in `[1,4096]`. Require exact tuple and
callable cancellation; callback must return exact bool and its exceptions
propagate. Malformed query/segment/adapter inputs raise `INVALID_GEOMETRY`;
malformed budgets/callback raise `INVALID_SETTING`. Preflight source tuple
length before element inspection. Before source arithmetic, check
`bit_length()` of numerator and denominator for every supplied Fraction in
query XY/cell, segment endpoints, width and height against
`max_coordinate_bits`; over-budget returns `incomplete/resource-limit`
without top bounds. The structural adapter's finite-binary64 normalization
can be inspected under this same query budget; construction alone conveys
no resource authority. No per-source hidden retries or unbounded refinement.

At most `max_sources` sources and four XY corners per source are processed.
The fixed exact operations and integer-square-root enclosures use bounded
input bit lengths and at most 4096 fractional precision bits; the total
output numerator bit length also depends on the bounded input magnitude.
Check cancellation
before each source, immediately before/after each fixed kernel call, before
every expected return and after result construction. Existing support API
is unchanged and need not gain cancellation. The current kernel has no
inner callback; do not claim interruption during one bounded invocation.
Cancellation after a prior source or before resource/rejection publication
publishes `incomplete/cancelled` with no bounds. Unexpected exceptions
propagate and no partial successful result escapes.

## Independent acceptance and non-claims

- The structural adapter reproduces binary64 normalization exactly, including
  a sloped structural segment. Existing support and structural-top tests stay
  byte-for-byte semantically equivalent after the private refactor.
- A proposed chord with a nonbinary rational endpoint remains that Fraction
  through the kernel; compare with a fixture where float roundtrip would
  move the footprint boundary. Rejected chord cannot be adapted.
- Candidate width equals height circular-section limit; width below height,
  zero XY length, nonconstant candidate Z and missing source ID reject.
- Flat axial endpoint/outer side contact are present. Just outside is absent.
  Overlapping structural and candidate solids use top maximum, not sum.
- One segment covers a whole exact rational rectangle; two partial segments
  remain unresolved. Empty and disjoint cases return absent.
- Exact coordinate-bit and source-count budget equality succeed; one over
  returns resource-limit. Tight and looser root precision outward-enclose
  the same irrational top. Cancel before/after kernel and final publication.

This kernel proves only conservative **nominal top** bounds for explicit
segments. No source-mesh correspondence, printable width calibration,
surface error, support, collision, chronology, Plan, G-code or Orca Preview
authority follows. Whether existing support owners can be refactored without
changing previous results is a repository-review gate; any conflict returns
the draft to specification adjudication.
