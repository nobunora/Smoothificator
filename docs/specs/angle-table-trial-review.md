# Parameter-keyed angle-table experimental trial

Status: SPEC_VALIDATED for the tools-only experimental implementation, subject to the parent adjudications below and final artifact verification.
Canonical specification revision: e6f049ecf1ea24a6372cd486a3245178ccee5ee3aecf1614d12694d586005dd9.
Extends only the tools-only scope of gui-native-paired-trial-review.md including its effective-material and post-hop deltas. All original input pins, byte preservation, numeric freeze, support, chronological material, source-state, package and independent-review gates continue unchanged. No canonical runtime or physical-print authority is created. No GUI, send or device action belongs to this task.

## User-adjudicated bounds

Current coupon remains the same 30 x 20 mm, 0..30 degree curved coupon and genuine saved GUI slice. Evaluate only the central X span after excluding 5 mm at each geometric X end; do not change source geometry or reslice. Width domain is inclusive 0.21..0.45 mm. Remaining exposed height is at least 0.08 mm. Physical height must be strictly less than actual saved layer height H, on the configured output XYZ grid: H=0.2 and grid=0.001 gives maximum 0.199 mm. Physical height, remaining height and width are independently validated after numeric freeze. Overlap is configurable 0..30 percent; current trial fixes 30 percent. No special curvature handling within the 0.45 mm footprint is required.

## Table ownership and key

A separate tools-owned pure section planner precomputes a finite parameter-keyed angle table. Key includes schema, layer height, width bounds/lattice, physical-height lattice, exposed minimum, overlap, numeric grid, angle domain/samples, finite search limits, epsilon and minimum improvement. Angles may be represented by exact slope/rise/base ratios rather than transcendental approximations; report degrees as diagnostics. Current source-step slope ratios may be included as explicit table knots once before placement. No full optimization occurs per source location.

Store topology (number/order of roots, parent links, upper count) explicitly. Upfront skip intervals are closed/open bounded sample intervals with explicit reasons; they are certified only for the declared discrete lookup domain, never a continuous proof. Topology changes partition table intervals. Interpolation is permitted only between identical topology and must pass bounded geometry, spill, objective, precision and height validation at lookup. Any failed/inter-topology interpolation rejects or uses a precomputed neighboring exact member; never silently interpolate path counts/parent links or trigger per-location optimization. Exact source-step knots are preferred for this trial.

## Objective and ranking

Score union geometry including the original floor. In the local finite triangle, original floor material covers the portion at or below Z=0; clipping union rectangles at Z=0 before symmetric-difference scoring removes buried overlap from the error. Count root/upper intersections once. Independently enforce each complete physical rectangle's outside fraction <=0.5 against its declared finite support triangle; buried material is not removed for this physical spill check. Record both quantities.

First find minimum error in the declared finite family. Admit candidates with error <= best_error + epsilon_fraction * unsupplemented_baseline_error (default epsilon_fraction=0.02). Among those choose minimum total paths, then minimum upper paths, then error and deterministic exact geometry tie key. Require (baseline_error - chosen_error) / baseline_error >= minimum_improvement_fraction (default 0.05); zero baseline skips explicitly. These defaults are configurable and fingerprinted, not claims of previously fixed user values or continuous/global optimality.

## Placement and acceptance

Instantiate immutable rectangles from table lookup, then bind freshly formatted root support from all earlier actual source beads and upper support from declared completed parents. Existing exact contact/freezer/material gates can reject table members; rejection does not authorize a hidden location optimizer. Record every source step and all table/cache identities, skips, topology transitions, improvement and computational counts.

Compare against trial-all26-posthop-v1 from the immutable source-input files in artifacts/gui-angle0to30-trial-v2. New outputs use a distinct angle-table trial basename, preserve source-input and previous artifacts and remain explicitly UNVERIFIED. Source extraction, post-hop chronology, original-byte recovery, whole actual-material/tool exclusion audits and genuine package MD5/readback remain mandatory. Tests cover validation, strict H and output-grid boundaries, union-floor buried overlap regression, spill independence, epsilon tie/ranking, minimum improvement, topology boundaries, skips, cache keys, cancellation and stale policy. Parent and independent implementation review are required before delivery.

## Parent adjudication and finite-domain amendment

Status: SPEC_VALIDATED for implementation with this amendment (2026-10-18).
Table domain is independent of actual coupon/source locations: exact slope bins from 0 through 1 in increments 0.01 (configured; expanded from the initial 0.58 range to include the eligibility transition). Lookup bins use their precomputed representative pattern, affine-scale horizontal coordinates to actual rise/slope, quantize, then boundedly validate; a failed validation skips with reason and never optimizes. This is a finite discretization with slope uncertainty at most configured bin width, not certified exact angular boundaries. Sample changes in topology and eligibility are reported as boundary brackets. Source-specific knots cannot fulfill this route. Current source steps may only diagnose/cross-check table behavior. Fixed-height placement and scaled horizontal rectangles require width/grid/spill/objective revalidation. Whole-row explicit finite templates are a permitted bounded family; minimum-error/epsilon selection must retain alternatives by total path and upper count rather than discard near-optimal simpler members early.

With exact 30% overlap and XYZ grid 0.001, only physical heights with representable 70% remaining height are legal: the largest is 0.19 mm although the nominal strict-H cap is 0.199 mm. The effective lattice maximum must be reported. H, overlap and precision change the table key and legal lattice.

## AT5 parent adjudication and source-bound finite-family ranking

Parent rejects first-feasible fallback as an epsilon-optimal claim. The new artifact-only v5 binding pass evaluates every retained precomputed member (winner plus up to64alternatives) through numeric freeze, physical spill, exact source root contact, parent contact and material-pair checks. Among the feasible formatted retained family it finds minimum actual floor-union error, admits error <= that minimum +0.02*actual unsupplemented baseline, then chooses minimum paths, minimum uppers, error and stable precomputed index. This does not optimize new geometric candidates per location; every candidate is precomputed generically. `lookup_angle_table` guarantees physically revalidated lookup, not final ranking. Physical lookup success cannot itself claim epsilon admission. Table fallbacks outside the original unconstrained section band may enter the freshly feasible-family band only through this explicit stage.

Reuses caller-pinned generic v4 table cache SHA256 a84bebff26f212d79b47c75c53376cb43f3e7b768577a48c14b8b792f6f47f9f. Artifact cache reads are capped16MB, parsed into bounded immutable DTOs and validated once against content/policy identity. v5 records actual feasible best error,epsilon limit,feasible count and selected table alternative index for each selected group. No source/test change was needed for this artifact-ranking adjudication. Final actual geometry/causal/package audits remain required.

## User-adjudicated root support gap tolerance (2026-10-18)

Latest explicit user instruction: "0.08mm以下の誤差による不整合は無視" and treat filled gaps as flat. Parent adjudication narrows this to a configurable nominal ROOT support gap tolerance0..0.08mm, current trial0.08mm. Zero retains strict contact. It does not change physical height/width/exposed-minimum/overlap bounds, child-parent contact, material intersections, source chronology, causal tool safety or package gates.

Artifact binding proves continuous source coverage at the actual root bottom plane minus configured tolerance using the unchanged public certified source-contact API and all strictly prior sources. This proves the root is within the declared vertical support-gap allowance everywhere along the span; it does NOT prove exact contact at the actual bottom and is labeled tolerance-qualified. It is an explicit experimental flattened-support assumption, not measured material filling or physical proof. Every selected root records actual bottom, queried lower plane, tolerance, continuous proof fingerprint and exact_actual_bottom_contact_proven=false when tolerance is positive. The source-binding policy fingerprint includes schema/table-policy/tolerance. Generic geometry table policy/cache remains unchanged; fresh all-retained-family source feasibility and actual formatted epsilon ranking are required under the new binding policy. Final material/tool/causal audits must be rebuilt for the new selected path set.

## User rejection of v7 and tapered stack amendment

The user rejected the v7 preview: inverted upper/lower sizes, apparent multiple
stacking and damaged original-line rendering. v7 is diagnostic only and is not
the next print candidate. Inspection confirms all 13 nominal children share the
parent width and three children are taller than their parent (0.15/0.12 and
0.13/0.12 mm). This is incompatible with the requested large-base/small-upper
topology, even before considering numeric rounding or viewer behavior.

For the corrected finite table, a child must have strictly smaller width than
its parent, its entire horizontal footprint must be contained in that parent,
and its physical height must be no greater than the parent's. These constraints
apply again after output numeric freeze, not just to ideal rectangles. Upper
width choices come from the declared bounded precomputed family; arbitrarily
shaving a microscopic amount off an equal-width upper is not the intended fix.
Width/height limits, remaining-height minimum and 0..30 percent overlap remain.
At most one child per root and no grandchildren are allowed. Undeclared material
overlap between separate roots or original terraces is not accepted as stacking.
A revised table identity must invalidate the old equal-width cache.

Original byte recovery alone does not prove equivalent preview geometry. The
corrected preview must compare original-path rendered/parser width and height
state against the unsupplemented source, including implicit consumer state
changed by supplemental extrusion. The original commands and physical source
state still must be preserved. Parent and independent review of the two failure
causes precede acceptance of a replacement preview.

## User-rejected v7 hierarchy and corrected finite topology

V7 is superseded and must not be delivered as the user's corrected hierarchy. Root cause is the finite template construction, not only E rounding: all13children used the SAME nominal width as their parent; three had larger physical height (.12parent with .15/.13child), giving a larger upper cross-sectional area. Independent E quantization can additionally invert equal nominal widths by micrometers. Existing support-graph validity and no-third-level parent links did not express the user's meaningful large-lower/small-upper geometry.

Parent-adjudicated correction: upper widths are selected from the explicit precomputed width lattice strictly below the parent's lattice width; upper physical height must be <=parent physical height. Center the narrower child in its declared parent. At numeric freeze independently require strict smaller actual E-implied width and actual XY interval containment; reject rather than shift/rescale a failed member. This yields a meaningful finite geometry family (default adjacent lattice differences0.04..0.05mm), not a tiny arbitrary post-placement margin. Parents at the minimum width cannot support a narrower legal upper and remain single-tier. Every upper must name a root from the same original terrace, and roots cannot name parents; at most two supplemental tiers per original terrace. Existing dimensions, overlap and0.08rootgap tolerance remain unchanged.

The source-independent table must be regenerated under a changed geometry-family policy identity; old caches cannot authorize the new family. Recompute all retained-family actual feasible epsilon rankings and fresh actual geometry/tool/package audits. Cross-terrace/no-undeclared-stack semantics need explicit parent disposition before the affected new guard is implemented; the proposed conservative ownership guard requires every emitted physical Y interval within its own original caller terrace's finite Y extent.
