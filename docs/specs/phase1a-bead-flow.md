# Phase 1A — nominal bead and flow arithmetic

Status: SPEC_VALIDATED for the five arithmetic functions below. Implementation starts after the static Phase 0.5 interface checks and independent review pass.

Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `89ac5da0ca70561ea47496e1e2f5265b4abbf913`

Independent repository review: the implementation lead checked ADR-0048,
ERROR_MODEL sections 3–6, the empty engine package, CandidateBeadBounds,
finite_binary64, architecture direction and typed failure conventions. The
equations and operation order agree with those sources. No new dependency,
runtime authority or physical defaults are needed. The reviewed Phase 0.5
runtime handoff separates static interfaces from Phase 4 proof; only static
prerequisites apply to these pure functions. No material conflict was found.

## Scope and source basis

Implement five deterministic, standard-library mathematical functions in `adaptive_subedge/engine/flow_model.py`, with focused tests in `tests/unit/test_flow_model.py`. No Orca, G-code, filesystem, UI, optimizer or third-party dependency belongs in this module.

Authority: Accepted ADR-0048 (`docs/adr/0048-versioned-nominal-bead-solid.md`, Cross-section and Vertical placement); `docs/ERROR_MODEL.md` sections 3–6; `docs/IMPLEMENTATION.md` sections 10, 16–17. Reuse the existing exact `CandidateBeadBounds` class from `adaptive_subedge/domain/settings.py`, `finite_binary64` validation convention, and `ContractError`/`ReasonCode`.

This is the arithmetic subset of the nominal bead model, **not** an implementation of `NominalBeadSolidV1`. Sweeps, caps, unions, support search/refinement, collision, error estimates and physical feasibility remain unimplemented. All outputs remain research quantities. No function changes an injectable flag, constructs runtime validation evidence, or publishes a Plan.

## Exact public APIs

All parameters are required; no physical default, profile lookup or guessed bound is provided. Return values are builtin binary64 `float`, except the explicitly ordered tuple below. Use keyword-only bounds and flow-control parameters as shown.

```python
def candidate_geometric_line_flow(
    height_mm: float, width_mm: float, *, bounds: CandidateBeadBounds,
) -> float: ...

def bead_width_from_geometric_flow(
    height_mm: float, geometric_mm3_per_mm: float,
) -> float: ...

def zaa_local_bead(
    nominal_height_mm: float, nominal_geometric_mm3_per_mm: float,
    relative_z_offset_mm: float,
) -> tuple[float, float, float]: ...

def effective_candidate_height(
    command_z_mm: float, local_support_z_mm: float, *, bounds: CandidateBeadBounds,
) -> float: ...

def commanded_external_line_flow(
    geometric_mm3_per_mm: float, *, print_flow_ratio: float,
    filament_flow_ratio: float, set_other_flow_ratios: bool,
    outer_wall_flow_ratio: float,
) -> float: ...
```

### 1. Candidate geometric cross-sectional area

`candidate_geometric_line_flow` computes `h * (w - h * (1 - math.pi / 4))`, in mm³/mm (numerically mm²). Require positive finite h/w, w >= h, and inclusive candidate height/width bounds. Require a positive finite result. Equal width/height is the circular cross-section limit, not a degeneracy to reject.

`bounds` must have exact type `CandidateBeadBounds`; no subclass/mapping shortcut. This function enforces candidate bounds but does not claim the Settings or printer supplying those bounds have been physically validated. Existing bounds are not silently enlarged or clamped.

### 2. Width reconstructed from geometric line flow

`bead_width_from_geometric_flow` computes `q / h + h * (1 - math.pi / 4)` from positive finite h/q. Require positive finite derived width and w >= h. A requested q that produces w < h is outside the horizontal-major-axis stadium model and rejects; do not clamp it to a circle.

This function intentionally has no candidate bounds: it is also used for structural ZAA geometry, to which candidate-only Settings limits do not apply. A candidate caller must subsequently validate h/w through `candidate_geometric_line_flow`; the inverse alone is not candidate admission. It accepts no stale nominal width, calibration multiplier or global-flow setting.

### 3. ZAA local arithmetic

`zaa_local_bead` returns exactly `(local_height_mm, local_geometric_mm3_per_mm, effective_width_mm)`.

Compute in this documented binary64 operation order:

1. `h_local = h_nominal + relative_z_offset_mm`;
2. `ratio = h_local / h_nominal`;
3. `q_local = q_nominal * ratio`;
4. derive width using `bead_width_from_geometric_flow(h_local, q_local)`.

Require positive finite nominal h/q, finite signed offset, and positive finite local h, ratio, q and derived width. Negative offsets are allowed only when all resulting invariants hold. Zero offset preserves nominal h/q subject to normal binary64 arithmetic. No input for nominal path width is provided: the ADR makes local h/q authoritative and width derived. Candidate bounds, global flow ratios and XY/Z coordinate transforms do not enter this structural arithmetic. This function does not interpolate along a segment or prove the Orca adapter selected an eligible non-ironing/non-bridge segment.

### 4. Height above declared local support

`effective_candidate_height` computes `command_z_mm - local_support_z_mm`, requiring finite signed Z coordinates, a positive finite difference, and the exact bounds class with the difference inside inclusive candidate height bounds. Width bounds are not evaluated until a width exists in function 1.

The support Z is an explicit caller-supplied geometric value. This function neither queries nor verifies deposited support. In particular, it does not use the previous candidate's command Z, establish footprint coverage, or impose a pairwise candidate-Z separation. The research `0.08 mm` example from ERROR_MODEL is **not** a default.

### 5. Commanded external-surface line flow

`commanded_external_line_flow` computes sequentially:

`q_cmd = ((q_geom * print_flow_ratio) * filament_flow_ratio) * role_factor`

where `role_factor` is `outer_wall_flow_ratio` if the exact builtin bool `set_other_flow_ratios` is true, otherwise `1.0`. Require positive finite q and all three supplied ratios, including the outer ratio when disabled; this explicit argument remains a validated configuration value, not an ignored malformed input. Require each intermediate product and the final result to be positive finite. Ratios need not be <= 1; no undocumented ceiling is introduced.

This function changes commanded line volume only. It does not feed its result back into nominal width/height, emit E, account for firmware M221, establish empirical material volume, or apply volumetric-speed limits. Its name and signature limit the role formula to the external-surface candidate use case; it is not a generic formula for all Orca roles.

## Numeric and failure contract

- Accept only builtin int/float values accepted by `finite_binary64`; reject bool, numeric subclasses, strings, NaN, infinity and integers not representable as a finite binary64.
- Convert validated scalars to builtin float before arithmetic. No NumPy, Decimal or platform-dependent extended-precision route.
- Reject invalid inputs/results using `ContractError(ReasonCode.INVALID_GEOMETRY, ...)`; reject wrong bounds type or non-bool flow enablement using `INVALID_SETTING`. A `CandidateBeadBounds` constructor retains its existing own failure rules.
- Overflow, underflow-to-zero for required positive intermediates, inverted local height, and w < h are expected invalid geometry, never silent success. No numeric clipping, physical tolerance, epsilon widening, implicit rounding, or hidden repair.
- The expressions above define operation order; mathematical identities are tested with floating-point tolerances, not asserted bitwise inverses. Exact candidate bounds use the computed binary64 result. Do not introduce an unstated tolerance at a bound to make round trips pass.
- Helpers remain private and local to this module; the public API is limited to these five functions.

## Required verification

1. Independent formula examples: h=0.2, w=0.4 gives `0.04 + 0.01*pi`; the circular limit w=h gives `pi*h*h/4`. These are synthetic arithmetic fixtures, not recommended printer settings.
2. Forward/inverse parity across several representable interior dimensions, using explicit test-only relative/absolute floating-point tolerances. Test width>=height and candidate-bound rejection separately so parity tolerance never weakens admission checks.
3. Inclusive exact lower/upper h/w bounds, nearby out-of-range inputs, wrong bounds type, w<h, nonpositive dimensions, invalid scalar types, nonfinite inputs, huge integer conversion, overflow and positive underflow-to-zero rejection.
4. ZAA positive/negative/zero offsets, local h<=0 rejection, reconstructed width consistency with local h/q, and a case proving stale nominal width would differ. Check that candidate bounds and command-flow ratios cannot alter the structural formula.
5. Height above supplied support: translated coordinate pairs with the same effective height, negative absolute Z inputs where the difference is valid, support at/above nozzle rejection, difference overflow, explicit height bounds. Do not assert that synthetic support exists physically.
6. Commanded flow: enable/disable outer factor, exact bool requirement, positive ratios below/above one, disabled malformed outer ratio rejection, zero/negative/nonfinite/overflow/underflow cases, and unchanged independent geometric area/width when only ratios vary.
7. Deterministic repeat outputs and domain/engine architecture checks. Syntax/package check → architecture → focused tests → regression/build only when integrated. No configured lint/type tool means NOT CONFIGURED, not PASS.

## Review questions and recommended disposition

- **Candidate versus structural bounds:** recommended separation above. Applying candidate limits to source ZAA would reject unrelated valid source data; omitting limits from candidate area would violate ERROR_MODEL.
- **Arithmetic versus full solid:** approve only these five primitives. Calling them a complete bead solid would falsely claim vertex union/cap/support behavior absent here.
- **Eligibility:** no injectable path is opened. Phase 0.5 research schema completion alone must not be reported as installed runtime verification; its outstanding gates remain documented separately before Phase 1A authorization.

Repository review must check the existing engine layout, numeric/error conventions, CandidateBeadBounds implementation, accepted source formulas and Phase 0.5 prerequisite disposition before marking this handoff SPEC_VALIDATED. No implementation accompanies this draft.
