# Source-contour proposals and shared numeric freezing

Disposition: parent repository review validated, 2026-10-18. Bounded offline
proposal implementation under current SPECIFICATION sections 12, 27-29 and
Accepted ADR0048; no production capability, source-state or physical approval
change. Existing exact contact-span and projection contracts remain owners of
their geometry. The actual seam0 fixture demonstrates feasible source-following
and inward-parallel paths that constant-radius paths cannot represent.

Implement a reusable tools-layer source-contour proposal factory. Inputs name
source/project digests, ordered exact finite closed structural contour segments,
path ID, floor/upper Z, physical width/height, remaining height, inward offset,
explicit pre-freeze minimum segment length and resource limits. Require exact
immutable values, closed connected nondegenerate simple contours, consistent
floor and unique segment identities. No ring IDs, coordinates or printer profile
values may be hardcoded. Zero offset and zero minimum segment length are legal.

For offset >0, intersect adjacent inward-shifted supporting lines using contour
orientation. Float arithmetic can propose coordinates only: serialize at declared
construction precision, quantize to policy XYZ precision, reject invalid geometry.
Remove grid duplicates and declared short edges deterministically before freezing,
record every removed source vertex and its reason. Revalidate closure, nonzero
segments, orientation and simplicity; reject unsupported collinear/degenerate
offsets explicitly rather than inventing rounded end volume. Bound input vertices
and validate cancellation. Never edit an already frozen path.

Lift the numeric emission calculation currently in
prepare_executable_ring_intents._emission to one tools-layer owner, retaining the
old ring wrapper's exact radial guard and return shape. Both old ring preparation
and new contour proposals use the shared owner. Freeze quantized XYZ, nearest E,
downward-capped F, per-segment E-implied physical width and volume rate. Enforce
existing configured dimensions, overlap 0..30%, remaining-height compensation,
saved max height, positive E and flow caps. Preserve old ring numeric outputs.
The G-code compositor continues executing immutable intents; it does not optimize.

The immutable proposal records input identities, contour segment identities,
offset and regularization provenance, policy identity and all frozen emission.
It carries no accepted/contact/future-volume/printable authority. Actual whole-span
contact, finite triangle spill, inter-path packing and chronological future volume
must be recomputed from the frozen path before later selection. Unknown outcomes
cannot become accepted. No source parser, anchor bypass or printable output here.

Verification: meaningful malformed/concave-or-unsupported/degenerate contour and
resource cases; both orientations and translated contours; zero offset; declared
short-edge coalescing before freeze; E width/remaining/overlap failures; exact
legacy emission parity. Recreate actual floor4.2 offset .212/width .251/height .18/
remaining .126 and five single-lane source-follow proposals from pinned fresh
seam0 source through the factory, recording contact and future certificates with
the existing owners. Record all differences rather than mutating reference files.
Focused tests and independent review precede whole-suite verification. This is
part of the continuing full-job planner, not completion of print readiness.
