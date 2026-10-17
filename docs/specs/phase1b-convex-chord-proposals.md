# Phase 1B unscored convex chord proposals

Status: SPEC_VALIDATED for the bounded research geometry primitive.

Independent implementation-lead review checked the halfplane containment proof,
current source reason matrices, exact symbolic section route and private material
query ownership. Independent schema review found no conflict with ADR-0005,
ADR-0029, ADR-0043 or ADR-0063 within the explicit unscored scope. Draft findings
on version selection, singleton intervals, result matrices and exact rational
query reuse were resolved before adoption. The user authorized continuation and
the implementation lead approved canonical adoption.

Authority: ADR-0005 Closed unscored convex chord proposal primitive owns the exact
two DTOs, propose_convex_chords API, algorithm_version convex_axis_chords_v1,
halfplane clipping, endpoint trimming, result matrices and resource precedence.
ADR-0030 owns fresh embedding and whole-segment material queries; ADR-0059 owns
the reused exact symbolic section predicates.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `a2db5305551533b98df22a1436a35c5985e09b93`

Implement domain/convex_chords.py and engine/convex_chords.py. Extract private
material_side._classify_segment returning a closed classification string or
raising the existing typed stop; both the public segment API and new proposal
engine delegate to that owner after their own fresh same-call mesh validation.
Preserve all existing public material/section APIs and failure behavior.
Exact rational proposal endpoints never round through PrintPoint3.

Completed proposal sets require nonempty rows, one per sorted normalized input
position; every set command_z_mm is exact Fraction. Global unknown/rejection
discards all rows. Input position resource preflight precedes element scans.
No dependency, cache of trusted receipts, physical default or Plan registration.

Acceptance tests follow ADR-0005's numeric triangle/square examples and include
X/Y parity, concavity rejection, collinear forward section nodes, singleton versus
empty intervals, normalized duplicate positions, malformed oversized tuples,
deterministic order, exact rational endpoints, whole-centerline material checks,
global unknown/cancellation after earlier proposals, all-rejected nonempty sets,
and unchanged public segment/section behavior after private helper extraction.

The finite-width footprint lies in a closed planar convex section; the centerline
must be strictly inside material. This is not exposed-band reconstruction,
finite-bead surface scoring, support/flow/regularity validation, feasible-path
publication or safe G-code authority. Those integration gates remain unfinished.

The earlier phase1b-convex-chord-proposals-draft.md is historical only.
