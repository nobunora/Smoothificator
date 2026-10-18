# Exact contact span — independent blind review, 2026-10-18

## Scope and independence

Reviewed docs/specs/exact-contact-span-review.md, additive ExactNominalTopBounds reason, public query_exact_nominal_top_span and existing shared bound core, optional exact-span continuous-contact mode, tests/unit/test_exact_nominal_top_span.py and actual source-offset64.UNVERIFIED.json. Existing ADR-0048 whole-segment geometry and ADR-0044 exact support bounds are authoritative. No parent primary findings consulted. No code/test changes, artifact overwrite, slicing or printer operations; only this report written.

No actionable material defect identified in this additive research API/mode. No physical support, footprint, clearance or real-source anchor authority is established.

## Whole-line correctness

The new public function validates two distinct immutable exact Fraction XY endpoints, then calls the existing exact core with those endpoints and a span-specific whole-domain reason. This is not acceptance from two independent point samples. For each source, longitudinal projection t and signed lateral cross coordinate are affine over the complete query span; extrema are attained at its endpoints. Squared lateral minimum is zero when that affine range crosses zero, otherwise the smaller endpoint square; maximum is the larger endpoint square. The shared core's cap bounds and linear nozzle-Z bounds therefore enclose every point on the entire span. Treating t/cap extrema independently is conservative even when correlated.

A full lower bound requires one source's flat-cap footprint to contain the whole queried span. Different sources covering only opposite endpoints cannot provide that lower bound; the explicit gap test remains unresolved until parameter subdivision exposes absence. Source unions retain all intersecting upper bounds, never just a chosen lower support. VaryingZ and rounded lateral section calculations use the same authoritative owner. No new geometry/sqrt implementation or tolerance is introduced.

ExactNominalTopBounds adds only one-segment-covers-span to full-bounded reasons. Existing point/cell entrypoints and full reasons are unchanged. The old padded-axis-box mode remains the default, uses the same positive padding and cell owner, and passed its unchanged geometric tests.

## Tool integration and provenance

Explicit policy query_geometry_mode selects exact-span. Each queried parameter piece has exact interpolated endpoints; span mode does not construct or publish a fictitious padded box. Terminal interval witnesses retain the actual span; complete queried_spans retains parent and terminal query provenance, including a queried parent subsequently split. Unqueried resource remainder has neither queried span nor cell. cells_queried/spans_queried/query_count are mode-consistent.

Every original segment still starts at [0,1], subdivision is exact in its original parameter, and final leaves are checked for contiguous complete coverage. Chronology admits only strictly earlier source orders; future/same-order data cannot satisfy contact. Existing input/source/query/depth/kernel limits, exact-bool cancellation latch and false authority are preserved. Cancellation/incomplete kernel outcomes precede bound interpretation. Whole-piece gap classification uses bounds on that line, never off-line box children.

## Executed validation

Exact repository `.venv` Python3.12.10, verified earlier in this independent session.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_exact_nominal_top_span tests.unit.test_continuous_path_contact -v` → exit0, all16 tests pass (0.056 seconds). Real kernel tests cover oblique whole-span support, separated endpoint supports/midspan gap, partial coverage, varyingZ, rounded sides, malformed endpoints/duplicate sources, resource/cancellation, span query provenance and partition, future exclusion, plus all10 prior default-mode tests.

Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -` → exit0. Verified every actual receipt pin against current files and exact embedded source association. Reconstructed chronological source inputs from nominal rows (earlier than explicit source order15994), retaining every potentially bottom-reaching source and rejecting only conservative spatial AABB separation. For all64 candidate edges, reconstructed exact policy/path/source inputs and reran the real auditor. Every complete report equals the stored report structurally, including all rational bounds, queried/terminal spans, partition counts and false authority flags. All64 paths prove nominal centerline contact with zero unresolved/gap leaves using exactly80 queries.

The actual receipt records24,860 prior padded-box queries versus80 exact-span queries. This audit independently reproduced the80-query result; it did not rerun the earlier24,860-query computation. Prior source-offset geometry and its source-row provenance were independently checked in the preceding certificate audit; candidate geometry is unchanged here.

## Residuals

The source adapter/prefilter remains caller-owned. Excluding earlier sources whose maximum commandZ is strictly below candidate bottom cannot create support above that bottom, and radius-expanded XY envelopes conservatively exclude spatially disjoint sources. This research top-contact criterion permits penetration; it is not a full volumetric intersection or support-area metric. Actual startup/debt/conditional execution and physical head clearance are separate. Union-supported spans may remain conservative unresolved when no individual source covers a sufficiently refined piece; finite limits never convert that uncertainty into success. Parent owns architecture/full-regression checks. No findings require disposition; no production/physical convergence declared.
