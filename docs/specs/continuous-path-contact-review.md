# Continuous nominal path contact audit

Repository disposition: validated for a tools-only bounded audit, not physical
authorization. Reuse the exact support-cell engine; do not replace its geometry
or infer firmware state. Parent-approved implementation scope is a pure function
and focused tests, followed by primary and independent review.

Inputs are exact rational quantized XY polyline points, a constant candidate
bottom plane, candidate execution order, and immutable exact nominal support
segments each carrying explicit execution order. Only sources strictly earlier
than the candidate may participate. No filtering by layer Z as a chronology
substitute. Validate identities/orders/types and explicit finite resource policy.

Partition each original segment by its rational parameter interval. Enclose each
piece in a closed XY box, padded by an explicit positive rational amount so axis
aligned pieces also have positive extents. Query existing
`query_exact_nominal_top_cell`. A lower bound at or above the bottom certifies the
entire piece; absent support or a strict upper bound below bottom certifies a gap
on that entire nonempty piece. Otherwise bisect the parameter interval. Never
infer a gap from an unrelated child of the enclosing box. Cover [0,1] without
holes for every polyline segment; positive point samples alone cannot pass.

Resource exhaustion, cancellation, max depth, or incomplete kernel outcomes
remain incomplete. A proven gap may refute complete contact even if other pieces
are unresolved, but report both. No silent candidate omission. Reports retain
interval witnesses, counts and explicit limits, and always have false physical
print authority. Proof concerns the nominal centerline bottom only, not full
bead footprint, contact area, head envelope, deformation or downstream clearance.

Tests must include oblique and axis aligned segments, flat supported path,
mid-segment gap with supported endpoints, exact touching boundary, future source
exclusion, resource/cancellation outcomes and input validation. Use the real
exact kernel for geometric regression tests. No source parser or CLI profile
restoration changes in this bounded implementation.
