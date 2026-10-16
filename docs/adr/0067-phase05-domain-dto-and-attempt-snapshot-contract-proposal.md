# ADR-0067 (SPECIFICATION OWNER APPROVED): Complete Phase 0.5 DTO contracts and process-local attempt/snapshot association

Status: **Accepted by delegated specification owner (schema/policy scope only) on PR #5; independent review, manifest/handoff, and SPEC_VALIDATED pending; physical injection prohibited**
Date: 2026-10-14
Design branch: `proposed-phase05-dto-attempt-20261014`
Related: Accepted ADR-0037, 0049, 0061, 0062, 0064, 0065; jointly specification-owner-approved ADR-0066 in Draft PR #5 (not yet merged into canonical base).
Scope: Phase 0.5 contracts ONLY — no Orca adapter, G-code execution or physical printer authorization.

## Normative schema decision — consolidated 2026-10-16

The following is the specification-owner-approved contract, moved verbatim from the delegated decision record at Git revision `515c2a97fd51dd9590be93678524337d63447731`. This ADR owns these requirements; implementation records document provenance and do not override this ADR. No acceptance status, physical permission or implementation gate is changed.

B1 (D1-D4/D10): SurfaceBand has unique nonempty surface_band_id, typed source_geometry identity, typed immutable target_boundary_ref and residual_error_region_ref, chronological_support_reference_ids and optional nesting_parent_band_id. References include exact type/schema/full lowercase digest and centered PrintObject frame identity, with mm units. Analysis-owner validation (NOT mere DTO construction) proves references exist in the same immutable snapshot, temporal support is earlier than its consumer, and nesting has no cycle. This is a vocabulary contract, not a topology/support algorithm. Final ARCHITECTURE source tree is a later-phase target; no placeholder G-code/Orca/optimizer executable files in Phase 0.5.

B2 (D3/D4): StructuralLoopReferenceV2 adds finite positive length, six finite ordered PrintObject bounds in mm, versioned winding/material-side policy, at least three non-collinear matching anchors under a versioned predicate, canonical shape algorithm version and full 64-lowercase-hex digest. Do not infer material side from raw normals. InsertionAnchorV2 adds structural interval, boundary signature/schema version, finite positive matching_tolerance_mm and matching_profile_id. Planner path/segment support provenance and explicit travel/restart intent are immutable. These fields DO NOT certify real Orca matching.

B3 (D5): PlanSemanticContentV2 uses subedge-plan identity root schema_version="2" (independent of Settings root), unchanged encoding version "1", full hash-free semantic projection and derived plan_id == plan_hash. Plan v1 source/bytes stay unchanged. V2 includes typed source/execution/settings identity references, frozen geometry, temporal support/order, v2 loop/anchor metadata, separate directional/convergence evidence, and tagged estimated-time availability. Exclude runtime attempt/session/generation, final emitted E, machine offsets and timestamps.

B4 (D5/D6): BidirectionalSurfaceErrorMetrics retain separate direction max/RMS/p95 (already present as standalone DTO in PR #2). A separate ErrorConvergenceEvidence record has UNKNOWN / CONVERGED / FAILED, estimator policy identity, refinement count and evidence reference. Constructing a DTO with CONVERGED cannot substitute for actual estimator verification. Both directional maxima must be independently converged before physical acceptance. Existing v1 summary ErrorMetrics does not prove either direction.

B5 (X2): AddedTimeEvidence is a disjoint tagged union: AVAILABLE(finite nonnegative estimated_added_time_s, predictor model version, typed resolved ExecutionConfig identity, evidence reference) OR UNAVAILABLE(stable failure reason, immutable nonempty missing-dependency IDs). Reject mixed variants, missing evidence and numeric 0/None/NaN/Inf as placeholders for unknown. Geometry-feasible candidates with missing required time make full comparison RANKING_INCOMPLETE / ANALYSIS_ONLY; do not silently exclude them then claim a globally or physically optimal choice. Geometry may still be reported for research.

B6 (D6-D9): ValidationEvidence has UNKNOWN / VALIDATED / REJECTED, typed validated subject when applicable, policy version, stable reason and evidence reference. Only the application-owned verifier may transition to VALIDATED after actual proof. Attempt checks are distinct for compatibility descriptor, Settings fingerprint, ExecutionConfig fingerprint and source-working-file identity. Missing => UNKNOWN, never PASS. InjectionAttemptStore remains the single owner of monotonic state and immutable revisions, with explicitly caller-configured bounded retention (no unbounded log). Do not modify Plan hash with attempt data.

The implemented PlanStore.begin_postprocess_attempt is retained as the ADR-0065 atomic PlanSnapshot+unique Attempt issuance owner. V2 may add an opaque process-local snapshot_issue_id minted under the same critical section and checked against actual issued snapshot identity; no invented Orca callback UUID. New analysis generation or post-snapshot eviction does not mutate an issued snapshot; epoch reset invalidates old-session eligibility.

## Closed research Plan v2 graph and identity — 2026-10-16

This section closes B1-B5's research Plan representation and canonical projection.
It incorporates the standalone loop, anchor and analysis-evidence vocabulary
below. It does not assert execution, topology, convergence or physical proof.
All new DTOs are frozen/slotted, with required fields and no implicit defaults.
Builtin strings are nonblank, tuple fields require exact tuples and exact nested
classes, IDs are case-sensitive, duplicate IDs reject, numeric fields use the
existing finite-binary64 convention and integer fields reject bool/subclasses.
No raw mappings or live Orca objects substitute for declared DTOs.

### Exact graph vocabulary

Every frame below is the literal `centered_printobject_mm_v1`. IdentityReference
always includes exact type/schema/encoding and full lowercase SHA-256. Source
references are source-geometry/1/1, execution references execution-config/1/1,
and Settings references plugin-settings/2/1. Comparison includes the complete
typed identity, not its digest alone.

| DTO | All required fields |
| --- | --- |
| GeometryRegionReferenceV2 | identity: IdentityReference; source_geometry: IdentityReference; coordinate_frame: str |
| SupportReferenceV2 | reference_id: str; contributor_kind: str; contributor_id: str |
| SurfaceBandV2 | surface_band_id: str; source_geometry: IdentityReference; target_boundary_ref: GeometryRegionReferenceV2; residual_error_region_ref: GeometryRegionReferenceV2; chronological_support_reference_ids: tuple[str,...]; nesting_parent_band_id: str or None |
| StructuralLoopContextV2 | loop_id: str; structural_interval_id: str; layer_index: int>=0; execution_order: int>=0; maximum_path_z_mm: finite binary64 |
| SegmentSupportIntentV2 | support_reference_ids: tuple[str,...]; settings_identity: IdentityReference; evidence_reference: str or None |
| SubEdgePathV2 | path: exact existing SubEdgePath; surface_band_id: str; insertion_anchor_id: str; segment_support: tuple[SegmentSupportIntentV2,...] |
| PlannedTransitionV2 | from_path_id: str; to_path_id: str; kind: str; policy_version: str |

GeometryRegionReferenceV2.identity has type `surface-boundary` or
`residual-error-region`, schema `1`, encoding `1`. These two identities are
typed references to future analysis-owned immutable geometry, not new public
hashing domains or a claim that an engine exists. Reject any other role/version.
target_boundary_ref requires surface-boundary; residual_error_region_ref
requires residual-error-region. Both source identities equal their band's
source_geometry. The frame is required on every region reference. Region
identity and source identity together bind a registry entry to one snapshot;
the containing analysis remains responsible for the actual referenced geometry.

SupportReferenceV2.contributor_kind is exactly `structural-loop` or
`candidate-path`; contributor_id names the corresponding loop_id or path_id.
IDs are distinct within their own namespace. SegmentSupportIntentV2 records
immutable planning inputs and optional reproducible analysis evidence, not a
VALIDATED/PASS outcome. Its settings identity must equal the Plan's Settings
identity. None means evidence unavailable; a nonblank string does not prove
support. Empty support lists are allowed for incomplete research analysis and
cannot be interpreted as a physically supported candidate.

SubEdgePathV2 reuses the unchanged v1 SubEdgePath/SubEdgeSegment numeric and
continuity constraints. segment_support has exactly one entry per path segment,
in segment order. It adds no machine XYZ, emitted E or runtime status. A future
engine can implement path-level support by repeating an immutable intent value
for its segments; no inference discards segment-local contributor differences.

PlannedTransitionV2.kind is one of `continuous`, `travel`, `restart`,
`travel-restart`; policy_version is exactly `declared_interpath_intent_v1`.
These declare intent between successive candidate paths, not safe travel
coordinates, extrusion amounts or verified G-code. There is exactly one entry
for each adjacent pair of candidate paths in execution order and no entry for
an empty/single-path Plan. Continuous contributes zero to the interpath
travel/restart count; each other entry contributes one, including travel-restart.
Restart within a path must first be represented as an explicit path split.
Initial/final transitions to structural G-code are not interpath transitions
and are excluded from this count, not from later time/safety verification.

### Closed PlanSemanticContentV2 projection

PlanSemanticContentV2 has exactly these eighteen required fields:

| Field | Exact type / constraint |
| --- | --- |
| schema_version | builtin str literal `2` |
| plugin_version | nonblank builtin str |
| compatibility_descriptor_id | nonblank builtin str; declaration, not validated compatibility |
| source_geometry | IdentityReference(source-geometry,1,1,digest) |
| execution_config | IdentityReference(execution-config,1,1,digest) |
| plugin_settings | IdentityReference(plugin-settings,2,1,digest) |
| geometry_regions | tuple[GeometryRegionReferenceV2,...] |
| support_references | tuple[SupportReferenceV2,...] |
| surface_bands | tuple[SurfaceBandV2,...] |
| structural_loops | tuple[StructuralLoopReferenceV2,...] |
| structural_loop_contexts | tuple[StructuralLoopContextV2,...] |
| candidate_paths | tuple[SubEdgePathV2,...] |
| anchors | tuple[InsertionAnchorV2,...] |
| transitions | tuple[PlannedTransitionV2,...] |
| directional_error | exact DirectionalErrorEvidence |
| added_time | exact TimeEstimateUnavailable or TimeEstimateAvailable |
| volumes | exact PlannedVolumesV2 |
| analysis_outcome | exact ResearchPlanOutcomeV2 |

PlannedVolumesV2 has exactly geometric_volume_mm3 and commanded_volume_mm3,
both finite binary64 >=0. They are separately declared planned measures; the
future engine proves their agreement with geometry and commanded flow.
ResearchPlanOutcomeV2 has exactly injectable (builtin bool, must be false) and
reason (builtin str in `phase05-analysis-only`, `ranking-incomplete`,
`unverified-geometry`, `infeasible`). No constructor grants a feasible/optimal
classification. If added_time is unavailable, reason must be ranking-incomplete
unless reason is infeasible or unverified-geometry. An available value has its
existing evidence requirements and must name the exact Plan execution identity.
It remains research evidence, not an installed time predictor; current Settings'
unavailable_v1 cannot produce it through the real planning pipeline. Both
directional convergence policy identities must equal plugin_settings.

All registry-like tuple orders are canonical and checked, not silently sorted:
geometry_regions by (identity.identity_type, identity.digest_hex);
support_references by reference_id; surface_bands by surface_band_id;
structural_loops and structural_loop_contexts by loop_id; anchors by anchor_id.
String sorting is Python Unicode codepoint order, without Unicode normalization.
Support reference ID lists are unique and sorted by the same rule. Candidate
paths are strictly increasing by path.execution_order. Transitions follow their
adjacent candidate pair order. Loop points, matching anchors, segments and
insertion-anchor structural_loop_ids retain their existing meaningful order.
All tuples may be empty where the invariants below permit; no fabricated geometry
or success evidence is required to represent an empty research result.

### Required containing-graph checks

1. Region keys are unique; every region and band has the exact Plan source
   identity. Each band's target/residual value equals a complete registry entry.
   Registry membership proves the declaration exists in this immutable graph,
   not that an external mesh is closed or its digest has been verified.
2. Loop contexts cover structural_loops one-to-one, with no extra/missing IDs.
   maximum_path_z_mm equals the maximum binary64 point Z of its loop, allowing
   nonplanar ZAA structural loops. This is a conservative path-coordinate bound,
   not a bead/support envelope or proof of deposited material.
   Context execution orders and candidate path execution orders together are
   unique nonnegative chronological event indices; gaps are allowed.
3. Band parent IDs exist, are not self, and form an acyclic forest. This checks
   declared nesting only; geometric containment is the future engine's proof.
4. Every support reference resolves to a declared loop or candidate path.
   Each segment and band support ID resolves to that support registry. Every
   candidate has an existing band and insertion anchor. Bands may be unused
   diagnostic regions; their support chronology is checked when they have
   consumers and does not become a success assertion when they have none.
5. For each candidate, union its band's and all its segments' support IDs.
   Each contributor must have a smaller global execution_order AND strictly
   lower height than the consumer candidate's command_z_mm: use a structural
   contributor's maximum_path_z_mm or a candidate contributor's command_z_mm.
   Candidate contributor path IDs in
   this union must equal the base path.support_dependency_path_ids set. Thus
   missing, self, future, same-Z and cyclic candidate support rejects. Preserve
   the existing base path dependency ordering; require it lexically sorted.
6. Each anchor loop ID resolves to a contextualized loop; all those contexts'
   structural_interval_id equals target_structural_interval_id. The anchor
   layer_index equals each of those context layer_index values. Each candidate
   path.interval_id equals its anchor.target_structural_interval_id, and every
   loop of its anchor has execution_order smaller than the candidate's. This is
   a declared layer/interval mapping, not final G-code insertion proof.
7. Transitions exactly cover adjacent candidates, without duplicates or dangling
   endpoints. The derived research complexity counts are len(candidate_paths),
   sum(len(p.path.segments)), and count(kind != continuous). Do not store a second
   independently supplied complexity tuple or claim representation-optimality.
8. Enforce all exact nested types, reference roles/versions, immutable shapes,
   directional/time identity consistency and non-injectable outcome above.

### Identity and ownership

SubEdgePlanV2 has exactly content:PlanSemanticContentV2, plan_hash:str,
plan_id:str. Derived IDs are identical full lowercase hashes. The application
serializer declares the complete explicit Plan-v2-root-context projection above,
including all new nested DTOs and existing loop/anchor/evidence fields. It does
not add these types to the public standalone semantic_tree registry: standalone
semantic_tree calls still reject the new loop/anchor/evidence/Plan-v2 objects.
Only identity_root(subedge-plan, exact PlanSemanticContentV2, schema_version=2)
enters this explicit context. The earlier standalone exclusion remains intact;
this section authorizes their nested projection inside the complete v2 root.
Support/reference/analysis
evidence strings included in a Plan must be deterministic immutable planning
provenance, never invocation IDs, timestamps or mutable runtime evidence.
Use the existing subedge-plan root with schema `2`, encoding `1` and ADR-0062
`plan` digest domain. Payload schema_version must also be `2`. Exclude derived
plan_hash/plan_id, session/generation/attempt state, final machine offsets/E and
timestamps. There is no v1 migration or registration change to v1 payloads.

Provide dedicated create_plan_v2/verify_plan_v2 application boundaries: construct
the validated semantic graph, project, compute hash, then create the frozen
envelope; mismatched caller-supplied IDs reject. Root validation dispatches on
both identity_type and schema_version, with closed nested validation, exact
projected scalar tokens and tagged time variants. Only plugin-settings and
subedge-plan gain schema 2 support; other roots remain schema 1. Unknown fields,
versions, raw-map shortcuts, cross-domain payloads and mixed v1/v2 references
reject. Generic typed identity comparison may compare two matching Plan-v2
identities but never equate different schema versions. Legacy create_plan,
verify_plan and all v1 bytes retain their current contracts.

PlanStore remains the single publication/session/retention owner and accepts
verified v1 or v2 envelopes for immutable snapshots and preview. Its publication
validation dispatches to the corresponding verify_plan or verify_plan_v2; do not
introduce a parallel store. PlanSemanticContentV2 exposes a read-only injectable
property returning analysis_outcome.injectable (always false), not a nineteenth
payload field. begin_postprocess_attempt and eligible continue selecting only
injectable plans, so research v2 entries cannot enter an execution candidate
snapshot. General snapshots may contain both envelope types. Publish/generation,
bounded retention, reset and issued-snapshot ownership remain existing behavior.
Physical admission needs a separate accepted compatibility/geometry/runtime-
verifier contract. This explicit research outcome and eligibility check prevent
new DTOs from silently enabling injection. This closes the
research Plan representation; it does not claim the remaining runtime proof
verifier or installed Orca gates are complete.

## Closed standalone structural-loop vocabulary — 2026-10-16

This closes B2's standalone StructuralLoopReferenceV2 representation, not its
source-derived geometry proof or the complete Plan v2 projection. The DTO is
frozen/slotted and has exactly these thirteen required fields, with no defaults:

| Field | Exact type / constraint |
| --- | --- |
| loop_id | nonblank builtin str |
| points | builtin tuple of at least three exact PrintPoint3 values |
| seam_gap_allowance_mm | finite binary64 >=0 |
| loop_length_mm | finite binary64 >0; supplied length, not a computed proof |
| bounds_print_space_mm | builtin six-tuple of finite binary64: xmin,xmax,ymin,ymax,zmin,zmax |
| coordinate_frame | builtin str literal `centered_printobject_mm_v1` |
| winding_orientation | builtin str: `unknown`, `cw_xy`, or `ccw_xy` |
| winding_policy_version | builtin str literal `declared_xy_winding_v1` |
| material_side_policy_version | nonblank builtin str naming the external orientation/material-side policy |
| matching_anchor_points_print_space_mm | builtin tuple of at least three exact PrintPoint3 values |
| anchor_predicate_version | builtin str literal `exact_binary64_cross_product_v1` |
| shape_canonicalization_version | nonblank builtin str naming the external shape algorithm |
| canonical_shape_hash | builtin str of exactly 64 lowercase ASCII hexadecimal characters |

Numeric validation uses the existing finite-binary64 convention: builtin int
inputs are interpreted after conversion to float; bool, numeric subclasses,
overflow and nonfinite values reject. Coordinate comparisons below use those
binary64 values, with signed zero equivalent. The point sequence represents a
cyclic loop: the closing last-to-first edge is implicit, so all points must be
distinct and a repeated closing endpoint rejects. Preserve point/anchor order;
do not rotate, reverse, simplify, snap or otherwise canonicalize supplied geometry.
The bounds must have ordered axis extrema and equal the coordinate-wise extrema
of points. All anchors must lie within these bounds; anchors need not be vertices
of points because a later matcher may choose interpolated locations. Anchor
coordinates must be distinct. These are local representation checks, not a
simple-loop, planar-loop, contour-membership or mesh-topology proof.

The anchor predicate is defined completely here: convert each coordinate to its
finite binary64 value, then interpret that value as its exact rational number.
Let a and b be the first two (distinct) anchors. Require at least one remaining
anchor c for which the exact 3D cross product (b-a) x (c-a) is nonzero. Do not use
float intermediate subtraction/multiplication, an epsilon, rounded area or a
norm/square-root comparison. Arbitrary-precision rational arithmetic gives a
deterministic predicate even at subnormal/extreme magnitudes. This checks affine
noncollinearity only: an almost-collinear triple may pass and does not establish
numerical conditioning or a physically sufficient matcher baseline.

cw_xy/ccw_xy denote a caller's declaration when viewed from +Z toward the XY
plane; unknown explicitly represents an unresolved declaration. This DTO does
not derive or certify winding from point order or normals. The material-side
and shape-algorithm version strings are opaque references, not an allowlist of
supported algorithms. A syntactically valid supplied digest does not establish
that its source geometry was canonicalized. ADR-0030's source topology/orientation
and independent inside/outside validation, ADR-0050's material-side use and
ADR-0059's simple-loop/no-hole/no-branch/no-self-intersection contract remain
future analysis-owner obligations. Unknown orientation remains non-injectable.
Length agreement, anchor-on-contour membership, winding agreement, material-side
proof and digest/algorithm agreement must be established by that owner; no DTO
constructor or property grants validated/injectable/matched authority.

Keep this standalone type outside canonical serialization and PlanStore until
the complete Plan v2 schema is accepted. Do not register the new frame/policy
names as supported source-geometry hashing or physical matching algorithms.
Existing StructuralLoopReference, v1 bytes and hash roots remain unchanged.
Required focused checks include malformed fields, repeated points/anchors,
incorrect/reversed bounds, outside anchors, exactly collinear rejection,
noncollinear subnormal/extreme-coordinate acceptance without float overflow,
unknown frame/predicate/winding values, immutability, canonical rejection and
unchanged v1 projection. No numerical engine or Orca integration is introduced.

## Closed standalone insertion-anchor vocabulary — 2026-10-16

B2's standalone InsertionAnchorV2 has exactly eight required fields:
anchor_id, structural_loop_ids, layer_index, boundary_signature,
target_structural_interval_id, boundary_signature_schema_version,
matching_tolerance_mm, matching_profile_id. It is frozen/slotted, with no defaults.
All string values are exact builtin nonblank strings. structural_loop_ids is an
exact nonempty tuple of distinct nonblank builtin strings, preserving order.
layer_index is an exact builtin int >=1. matching_tolerance_mm is finite binary64
and >0 (bool/subclasses/overflow reject under existing numeric conventions).

The sole initial boundary_signature_schema_version is
`opaque_boundary_signature_v1`: a research token vocabulary, NOT a matching or
signature-generation algorithm. boundary_signature is opaque and MUST NOT be
interpreted as proof of matching. matching_profile_id names a future verifier's
profile; construction does not resolve or approve that profile.

This DTO remains outside canonical serialization and PlanStore until the full
Plan v2 projection is closed. No validated/injectable property is present.
The analysis owner must later prove loop/interval membership in the same source
snapshot; no DTO construction or string equality proves geometric correspondence.
Existing v1 constructors, projected bytes, and hash roots remain unchanged.
This closes the standalone vocabulary only, not all of B2 or Phase 0.5.

## Closed analysis-evidence and bounded-history slice — 2026-10-16

This slice concretizes B4/B5 and the retention portion of B6. It does not define
the remaining Plan v2 projection, geometry references, runtime proof verifier,
or new snapshot token. Existing atomic PlanStore issuance remains the owner.

All evidence values are frozen/slots with required fields, exact declared DTO
classes and builtin strings/integers. Float inputs use the existing finite
binary64 convention; bool, numeric subclasses and nonfinite/overflow reject.
Evidence references are nonblank immutable identifiers, not proof by themselves.

| DTO | Exact fields and constraints |
| --- | --- |
| TimeEstimateAvailable | tag literal `available`; estimated_added_time_s finite >=0; predictor_model_version nonblank str other than `unavailable_v1`; resolved_execution_config exact IdentityReference(execution-config,1,1,full digest); evidence_reference nonblank str |
| TimeEstimateUnavailable | tag literal `unavailable`; reason one of `time-model-unavailable`, `missing-execution-config`, `missing-model-evidence`; missing_dependency_ids nonempty duplicate-free tuple of nonblank builtin str |
| ErrorConvergenceEvidence | state one of `unknown`, `converged`, `failed`; estimator_policy exact IdentityReference(plugin-settings,2,1,full digest); refinement_count exact int >=0; evidence_reference nonblank str or None; reason declared string below or None |
| DirectionalErrorEvidence | metrics exact BidirectionalSurfaceErrorMetrics; pred_to_src exact ErrorConvergenceEvidence; src_to_pred exact ErrorConvergenceEvidence |

UNKNOWN requires count=0, evidence=None and reason=None. CONVERGED requires
count>=1, nonblank evidence and reason=None. FAILED requires a reason from
`refinement-budget-exhausted`, `missing-error-evidence`, `invalid-error-domain`;
count may be zero and evidence may be absent. Both direction records must name
the same typed estimator policy identity. One converged direction never stands
in for the other. No constructor/property returns printable/validated/feasible
authorization; future estimator/application ownership remains required.

These DTOs are standalone, deliberately NOT registered in canonical projection
until a complete Plan v2 contract is reviewed. No bare time Optional/zero sentinel,
mixed tagged alternatives, v1 Plan/Settings changes or synthetic successful proof.
The available DTO is a data vocabulary, not a currently supported predictor:
Settings' only installed time model remains unavailable_v1.

### Opt-in bounded Attempt history

InjectionAttemptStore remains the single state owner. Add keyword-only
`max_attempts` and `max_revisions_per_attempt`. Either both are omitted/None
(legacy behavior, no retained revision history), or both are exact positive
builtin ints. Partial/zero/bool/noninteger values reject. Bounded mode stores an
immutable `AttemptRevision(revision:int>=0, record:InjectionAttemptRecord)`.
Begin creates revision 0; each successful monotonic transition adds 1, even after
older revisions were pruned. Failed operations never change records/history.

At capacity, begin evicts the earliest-created terminal attempt and its history;
active attempts are never evicted. If all retained attempts are active, reject
begin with INVALID_STATE_TRANSITION. Validate new record and detect duplicate
UUID before evicting anything. Every operation uses the existing AttemptStore
lock; PlanStore -> AttemptStore lock order remains unchanged. Preserve rollback
on failed atomic issuance. Returned immutable history survives subsequent pruning.
`history(attempt_id)` returns a tuple, empty for an unknown/evicted ID or legacy
mode; malformed IDs reject. Revision envelopes stay runtime-only and excluded
from canonical projection. This adds no validation-evidence success transition;
legacy AttemptState progression remains unchanged and is not a printer gate.

Bounded retention must not allow an evicted ID to be reused: append a store-owned
monotonically increasing issuance sequence to the generated UUID in bounded
mode. IDs remain opaque strings. Reject a generated UUID that duplicates any
currently retained UUID before eviction; a previously evicted UUID may recur
only with a different sequence suffix. Increment sequence only on successful
publication. This prevents stale callbacks addressing a different new attempt
without requiring an unbounded tombstone set. Legacy ID formatting is unchanged.

## Historical proposal and rationale (non-normative)

All sections below preserve proposal history. Their Proposed/approval-pending statements and candidate alternatives do not override the normative decision above. Unspecified exact contracts remain unresolved; this move does not invent missing fields, version registries or validation algorithms.

## Current proposed disposition at integrated PR #5 (2026-10-15)

Requester approved D1–D10 **design directions**, not final typed contract sign-off. The early baseline passage below saying atomic PlanStore snapshot/attempt issuance is absent is **historical**: implementation PR #2 now implements and tests `PlanStore.begin_postprocess_attempt` under Accepted ADR-0065. This proposal adds only unapproved immutable provenance, richer validation evidence, v2 directional quality metrics and tagged time-availability semantics. See `docs/implementation/phase05-unified-contract-review-2026-10-15.md`.

The previously separate Settings v2 PR #3 and DTO/Attempt PR #4 shared canonical-document edits; Draft PR #5 is their integrated specification review. No old Plan/Settings v1 bytes are changed; no Orca adapter, G-code mutation or physical injection is authorized. Status remains Proposed until source/fixture issues are resolved and reviewed.


## Current specification-owner approval — controlling scope

**Approved by delegated specification owner on 2026-10-15:** the schema-level Domain/Attempt decisions in [phase05-delegated-specification-decisions-2026-10-15.md](../implementation/phase05-delegated-specification-decisions-2026-10-15.md), including typed immutable SurfaceBand references, Plan v2 identity and directional evidence, tagged available/unavailable time, attempt validation UNKNOWN/VALIDATED/REJECTED, bounded revision history, and runtime-only atomic issued-snapshot provenance. **This approval controls over old conflicting "not approved" or "not yet implemented" historical paragraphs below**; the existing ADR-0065 PlanStore atomic issuance is already implemented. Accepted ADR-0037/0047/0062/0064/0065 remain authoritative.

**Separate verification status:** approved as a design/typed schema decision **on this Draft PR only**, not an independent review, proven topology/Orca matcher, implementation or physical printer authority. The final v2 DTO projection, canonical test vectors and source validation remain required in the regular specification/repository review workflow before production edits. Keep legacy v1 canonical bytes unchanged.

## Context

The initial Phase 0.5 code on Draft PR #2 contains deterministic immutable Plan DTOs, typed canonical identities, a bounded process-local PlanStore and independent InjectionAttemptStore (204 Python 3.12 tests PASS at source commit `e345b9a9850e0203f1b441d6eb3f2692faa921c3`). It does not yet match all domain/attempt fields listed in ARCHITECTURE §3 / IMPLEMENTATION §13 / ADR-0037, and its separately invoked `PlanStore.snapshot()` and `InjectionAttemptStore.begin()` do not establish one atomic selection-attempt association required by Accepted ADR-0065.

The current canonical `SubEdgePlan` identity root has schema `"1"` and a complete closed byte/field contract. Adding meaning-changing Plan fields under that schema without versioning risks breaking reproducibility. Unsupported Orca session IDs, hardware defaults and platform working-file identities must not be invented to fill this gap.

This ADR is a **review packet** seeking precise remaining decisions. It is not a declaration that new DTO fields, method signatures or terminal statuses are already approved.

## Proposed decisions, with unresolved exact schemas

### D1. Represent a SurfaceBand in immutable domain vocabulary

ARCHITECTURE §3 and IMPLEMENTATION §13 require a SurfaceBand containing:
- target material boundary;
- residual error region;
- support and nesting metadata.

Candidate schema **for review only**:
- `surface_band_id: str` (exact nonempty),
- `target_boundary_reference_ids: tuple[str,...]` (immutable, declared frame/meaning pending),
- `residual_error_region_reference_id: str` (exact nonempty),
- `support_relation_reference_ids: tuple[str,...]` (acyclic temporal meaning pending),
- `nesting_parent_band_id: str | None` (optional, no ambiguous CSG semantics).

**Decisions required:** whether SurfaceBand owns references or geometry, whether a closed outer boundary is a StructuralLoopReference or another topology-aware type, what a residual error region actually contains, and what metadata belongs in final/chronological envelopes instead. Do not add fields to the current plan identity before reviewing the precise schema and version.

### D2. Resolve missing structural loop, candidate and anchor metadata

IMPLEMENTATION §13 lists `StructuralLoopReference` canonical closed geometry, length/bounds/orientation, seam-gap, non-collinear anchors and shape hash. The research DTO currently has loop ID, point tuple, seam-gap and string shape hash. The following need field-level decisions:
- `length_mm` / `bounds_print_space_mm` / winding-orientation + material-side version;
- non-collinear matching anchors and how to identify them without encoding mutable Orca objects;
- `SubEdgeSegment` support-validation metadata; candidate `SubEdgePath` travel/ordering metadata beyond existing `execution_order` and support dependency IDs;
- `InsertionAnchor` exact validated boundary-signature and matching tolerance/profile ownership.

**Required separation:** centered PrintObject print-space geometry and immutable planned intent belong in the plan. Final machine XYZ, final emitted E and mutable postprocess result MUST NOT enter its canonical hash.

**Version gate:** if these semantic fields are added to the canonical plan payload, adjudicate a new typed plan root schema version and full cross-version comparison/migration semantics under ADR-0062/0064; do NOT silently extend the current `subedge-plan` schema `"1"`.

### D3. Include attempt-scoped compatibility and fingerprint validation evidence

Accepted ADR-0037 and IMPLEMENTATION §13 require attempt identity, selected plan hash, working-file identity, status/reason **and** compatibility descriptor, fingerprint validation result, source-file identity result and final disposition.

Current `InjectionAttemptRecord` has only 5 fields. Proposed **for review** to keep one application-owned immutable history:
- `attempt_id`: UUID/opaque unique process-local string, never a plan hash;
- `selected_plan_hash`: optional 64 lowercase hex;
- `source_working_file_identity`: platform-authorized opaque identity, **not** fabricated path-key verification;
- `compatibility_descriptor_id`: validated value or explicit unresolved reason;
- `plugin_settings_validation` and `execution_config_validation`: immutable typed gate outcomes, with versions / identity references and failure code;
- `source_file_identity_validation`: immutable recorded check outcome; size/digest/high-resolution metadata only after actual platform evidence;
- `state`, `reason` and terminal outcome;
- future ADR-0061 commit-lock wait/key evidence is a later execution DTO, not a new Phase 0.5 G-code writer.

**Decisions required:** exact record fields/types, when a gate may be Unknown versus Rejected, whether updates create new record versions under monotonic transition, and which evidence can remain empty in research-only/no-injection mode. Unsupported evidence never becomes a boolean PASS.

### D4. Associate an issued snapshot with one unique postprocess attempt atomically

Accepted ADR-0065 already requires each invocation to atomically snapshot eligible current-epoch plans and a unique InjectionAttemptId, releasing PlanStore lock before long work; ADR-0037 requires attempt-scoped independent mutable status.

**Proposed implementation ownership, subject to source and deadlock review:**
- `PlanStore` remains the **only** owner of publication epoch, bounded retention, candidate list and snapshot issuance. `InjectionAttemptStore` remains the **only** owner of attempt records and monotonic updates.
- An application-level operation representing **one entry** to a supported `psGCodePostProcess` invocation coordinates an atomic `(issued_snapshot, attempt_id)` pair. The operation must not accept caller-supplied untrusted epoch/ID or duplicate existing attempt IDs.
- Mutual lock-order/acquisition and rollback of an unsuccessful pair creation must be specified; no partially associated attempt may become executable.
- A new generation after issuing the pair does not invalidate an in-flight snapshot; eviction after issuance does not mutate it; epoch reset invalidates stale session selections.
- No use of raw code-level newest generation as an eligibility criterion.
- The authoritative attempt record includes a reference/provenance token tying it to the exact issued snapshot. Candidate plan list remains immutable; mutable terminal status stays entirely in InjectionAttemptStore.
- Plan selection requires a distinct later unique structural matcher and two fingerprint checks; **an atomically issued attempt ID is not proof of Orca runtime compatibility or printability**.

**Decisions required:** exact public/private operation signature, lock ordering and coordinator lifetime, whether record creation errors roll back snapshot issuance, how preview-only/candidate-free invocations are recorded, and how reset interleaves with an already-held eligible snapshot.

**External evidence condition:** integration must use a source-verified Orca hook and documented invocation lifecycle, not a guessed Orca session key. Pure-process coordination can be unit-tested in isolation, but integration cannot be certified from those tests alone.

### New pinned Orca source evidence for D4

A direct inspection of the previously audited Orca source commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873` is documented in [the pinned postprocess invocation review](../implementation/phase05-orca-postprocess-invocation-review-2026-10-14.md). `PostProcessor.cpp` constructs `SlicingPipelineContext` and calls `cap->execute(ctx)` for each selected plugin capability. The context exposes a working `gcode_path` and resolved config fallback but no native unique invocation ID. An application-generated unique attempt ID at each supported hook entry is therefore source-consistent, without fabricating a native Orca session identifier. **The application-level atomic snapshot/attempt API and its lock/error rollback design remain unapproved and unimplemented**; installed-target runtime fixture evidence is still missing.

### Pure-process implementation progress (does not accept this ADR)

Draft implementation PR #2 now includes the narrow, already-Accepted ADR-0065 primitive `PlanStore.begin_postprocess_attempt(attempt_store, source_working_file_identity)` at commit `e437c85bed70a828ebdfe4bad3694457b9cc9e58`, with six in-memory rollback/concurrency tests and [Python 3.12 CI 210/210 PASS](https://github.com/nobunora/Smoothificator/actions/runs/38421826772). Under the PlanStore lock it issues only eligible current-epoch candidates alongside a newly created attempt record. This does **not** wire an actual Orca export invocation, determine a real filesystem identity/commit lock, or resolve the richer attempt validation evidence DTO schema. Those D3/D4 points remain **Proposed** and need a separate accepted contract before further implementation.

### D5. Clarify architectural file-tree milestone boundary

ARCHITECTURE §2 lists the eventual engine, ports, adapters, preview and G-code modules. The Phase 0.5 handoff expressly **forbids implementing** source mesh, optimizer, Orca live bindings and G-code parser/emitter.

**Proposed resolution:** treat the Section 2 source tree as a **target architecture** and Phase 0.5 acceptance as ownership/import boundaries, complete *approved* DTOs and the application-level immutable/snapshot lifecycle; only create actual modules required by a reviewed concrete contract, never placeholder G-code or optimizer services. Clarify the handoff before marking the milestone complete.

## Alternatives rejected at proposal stage

- Unversioned change to `PlanSemanticContent` or `PluginSettings` root schema `"1"`.
- Generic free-form DTO metadata or Python repr in canonical identity.
- Storing mutable attempt status on `SubEdgePlan` or deriving attempt identity from `plan_hash`.
- Treating `snapshot()` + `begin()` as atomic without a shared ownership/lock contract.
- Using an imagined Orca export-session ID or reconstructing an evicted plan from G-code.
- Adding no-op placeholder Orca/G-code modules solely to make the listed package tree look complete.

## Specification reviewer checklist

An explicit six-decision approval sequence integrating this proposal with Proposed ADR-0066 is maintained at [Phase 0.5 specification approval checklist](../implementation/phase05-spec-approval-checklist-2026-10-14.md). It requires a separate reviewer disposition on Plan identity versioning, Settings ownership, public DTO semantics, attempt evidence states, snapshot-to-invocation provenance and the Phase 0.5 target package tree. **The checklist is NOT an Accepted ADR and does not authorize schema changes or physical injection.**

## Acceptance gates before any implementation of this proposal

1. Source-review D1–D5 with concrete field types, units, meaning and owner; reconcile relevant Accepted ADRs and canonical SPECIFICATION / IMPLEMENTATION / ARCHITECTURE in a separate approved specification revision.
2. If a schema change is approved, define unique root version and deterministic golden vectors for v1 vs new plan/attempt metadata; keep legacy v1 vectors byte-identical.
3. Restamp the audited manifest/handoff without a circular self-reference; perform a fresh repository review with disposition `validated` for the new scope.
4. Add standalone in-memory snapshot/attempt concurrency and failure-atomicity tests and normal architecture/DTO checks. Never count a research-only matched snapshot as actual Orca postprocess proof.
5. Keep physical injection disabled until actual runtime fixtures, a complete execution config, working-file commit-lock proof and independent blind review pass the later safety gates.

**Final status: PROPOSED.** No changed versioned schema, Python implementation or print capability is authorized by this ADR. Reviewer acceptance and source-backed Orca integration are still required.

## 2026-10-15 requester-approved design directions (not normative field schema)

The requester approved D1–D10: SurfaceBand typed immutable geometry references, separate target/residual/support/nesting relationships, loop canonical geometry/matching anchors in PrintObject coordinates, typed insertion signatures and immutable candidate dependency/order data, distinct Plan schema version for semantic additions preserving v1 bytes, attempt validation UNKNOWN/VALIDATED/REJECTED evidence, immutable monotonic attempt snapshots, already implemented process-local atomic snapshot+attempt issuance with immutable provenance, epoch versus generation separation, and Phase 0.5 source-tree limited to reviewed modules without speculative Orca/G-code/optimizer stubs.

Full decision detail and remaining field-level gate are recorded in `docs/implementation/phase05-spec-approval-checklist-2026-10-14.md` on this branch (commit `b7de60621b8b34ca7513319ec5e9e958d235b584`). In particular, exact references/geometry types, validation transitions, coordinate normalization and schema root still require formal source-of-truth definitions before implementation. Existing process-local issuance is not new work. ADR-0067 remains Proposed, not independently reviewed/Accepted; no live plugin, G-code or physical injection is authorized.

## 2026-10-15 field-level candidate DTO contracts for SPEC_REVIEW (not Accepted)

This candidate typed schema implements **design direction only** for requester-approved D1–D10, preserving the accepted v1 Plan/Settings bytes and ADR-0037/0062/0064/0065 process separation. Every *new* identifier below is **Proposed** until exact field-level review; existing names/semantics in the current code are labeled existing. No actual geometry algorithm, Orca adapter, G-code injector or physical mode is authorized.

### D1–D2: immutable SurfaceBand references (proposed v2 domain vocabulary)

\`SurfaceBand\` is a frozen, slots-enabled value, **referencing** other immutable objects, not embedding mutable Orca/mesh objects:
- \`surface_band_id: str\`: nonempty, unique in containing analysis; no reliance on Python object ID;
- \`source_geometry: IdentityReference\`: typed immutable source-geometry identity, exact known version;
- \`target_boundary_ref: SurfaceBoundaryReference\`: typed identity of immutable, *closed* target boundary/contour set in the centered PrintObject print-space frame (mm);
- \`residual_error_region_ref: ResidualErrorRegionReference\`: typed immutable reference to the affected region (must identify a finite, closed domain; optional holes/topological components explicitly versioned);
- \`chronological_support_reference_ids: tuple[str, ...]\`: ordered/canonical ids of pre-existing support contributors, never future/same-Z candidates;
- \`nesting_parent_band_id: str | None\`: optional strict parent. Validate referential integrity and acyclicity at the **containing analysis** boundary, not just in one dataclass's __post_init__.

\`SurfaceBoundaryReference\` and \`ResidualErrorRegionReference\` are candidate distinct discriminated reference classes with \`identity_type\`, \`schema_version\`, \`digest_hex\`, and explicit centered print-space frame ID, no arbitrary string-only pointer. Reference validation needs a closed-world registry of immutable referenced geometry at the analysis boundary. Existence of a reference **does not certify** that the underlying polygon/mesh is closed, manifold or supported: those are separate engine checks. Geometry ownership, holes, material-side and source normal conventions must reconcile Accepted ADR-0050/0059 before this is final.

### D3–D4: loop, anchor, path and segment typed augmentation (new Plan root required)

Existing \`StructuralLoopReference(loop_id, points, seam_gap_allowance_mm, canonical_shape_hash)\` stays untouched in v1. The v2 candidate adds (all proposal):
- \`loop_length_mm: float\` finite >0; \`bounds_print_space_mm: (xmin,xmax,ymin,ymax,zmin,zmax)\` six finite binary64 with ordered axis extrema;
- \`winding_orientation: enum\` with validated material-side convention/version; orientation cannot be guessed from raw mesh normals;
- \`matching_anchor_points_print_space_mm: tuple[PrintPoint3, ...]\` length >=3, non-collinear under a specified versioned geometric predicate/tolerance; canonical shape signature and anchor selection must be deterministic for equivalent contours;
- \`shape_canonicalization_version: str\` and full 64-lowercase-hex \`canonical_shape_hash\` (the v1 nonempty unvalidated string cannot stand in as proof).

Existing \`SubEdgePath\` retains its open constant-command-Z segments, execution_order and support_dependency_path_ids. A v2 candidate adds explicitly typed preplanned travel/restart **intent** and a \`support_provenance_id\`/support validation reference to path or segment as required by the accepted chronological metric; it must not store the *later* postprocess validation PASS or final machine E. In particular, path splits must be canonicalized before optimizer complexity counts; planner metadata must not permit fake segment coalescing for ranking.

Existing \`InsertionAnchor(anchor_id, structural_loop_ids, layer_index, boundary_signature)\` stays untouched in v1. V2 candidate adds \`target_structural_interval_id: str\`, \`boundary_signature_schema_version: str\`, \`matching_tolerance_mm: float\` finite >0, \`matching_profile_id: str\` with source/fixture provenance. The *meaning* of the G-code matcher profile is a later phase, so no fabricated physical matcher PASS. All anchor loop ids must exist in the exact selected source geometry and the v2 semantic Plan.

### D5: type-versioned Plan without silent v1 mutation

Any added \`SurfaceBand\` references, loop/anchor/path metadata, directional error metrics, time-evidence semantics or score grammar that enter \`PlanSemanticContent\` require a distinct typed \`subedge-plan\` root schema (candidate \`"2"\`) and explicit v2 DTO projection. This is **independent** of the \`plugin-settings\` root version proposal in ADR-0066. Retain the ADR-0062 byte-grammar \`canonical_encoding_version="1"\` unless its actual grammar changes. A Settings v2 digest may be referenced by a Plan v2; do not change the existing v1 Plan root and byte vectors. \`plan_id == plan_hash\` remains derived from a hash-free projection (ADR-0064). No timestamp, PluginSessionEpoch, generation, mutable attempt evidence, machine coordinates, or final emitted E in Plan identity.

**Mandatory cross-source conflict (High):** current \`ErrorMetrics\` on Plan v1 contains only summary \`e_max_mm\`, \`e_rms_mm\`, \`e_p95_mm\`, \`signed_mean_mm\`. It cannot independently prove the two directional hard maxima required in SPECIFICATION §16 / ADR-0047; introduce a separate v2 **directional converged error result** (at least both maxima, both RMS and p95, signed bias diagnostics, method/convergence evidence reference), or require a referenced immutable authoritative estimator result. Do not silently reinterpret existing summary fields. Existing v1 \`estimated_added_time_s: float\` similarly cannot represent unresolved machine prediction: propose a discriminated v2 time-evidence value \`TimeEstimateAvailable(estimated_added_time_s >=0, model_version, resolved_config_identity)\` versus \`TimeEstimateUnavailable(reason_code)\`, never NaN/Inf/0 as an unknown sentinel. Unavailable time must not result in a claimed time-ranked optimal printable Plan. Exact inclusion/exclusion of research-only outcomes in Plan identity must be decided before acceptance.

### D6–D7: independent immutable attempt validation evidence

Proposed \`ValidationEvidence\` is a frozen discriminated value:
- \`state: UNKNOWN | VALIDATED | REJECTED\`;
- \`validated_subject: IdentityReference | None\` (typed subject and schema, not an arbitrary digest alone);
- \`validation_policy_version: str\` nonempty/recognized;
- \`reason: ReasonCode | None\`, explicitly typed;
- \`evidence_reference: str | None\` (not proof by mere nonempty string; validated status requires actual validation at the owning boundary).

\`UNKNOWN\` may have no validated subject, must NOT be conflated with success; \`REJECTED\` requires a stable failure reason; \`VALIDATED\` requires an actual subject, policy version and reproducible evidence established **at the validation boundary**. Do not accept \`VALIDATED\` from user-supplied string alone. Attempt records carry separate evidence for compatibility descriptor, plugin settings, execution config and source working-file identity. The existing \`AttemptState\` monotonically transitions STARTED -> VALIDATED -> EMITTED_TEMP -> SANITY_PASS -> COMMITTED, with terminal SKIPPED/FAILED/FATAL where existing rules allow; never mark \`AttemptState.VALIDATED\` solely because the evidence DTO was constructed. A proposed monotonically increasing \`record_revision: int >=0\` and immutable snapshot history must be specified if historical evidence is required; the current store retains only latest immutable snapshots, so historical history storage is a **new responsibility with bounded retention rules** to review. No mutable status field is added to \`SubEdgePlan\`.

### D8–D9: issuance provenance, reset and generation

Keep current implemented \`PlanStore.begin_postprocess_attempt\` lock order **PlanStore then AttemptStore** and its rollback/duplicate-UUID rejection. An issued in-process snapshot and attempt record are a pair, not independent snapshots stitched later. Propose a \`snapshot_issue_id\` (opaque, process-local, unique, minted atomically) carried in a typed immutable issuance envelope and referenced by the attempt's history. This token is **runtime-only**, never in the Plan semantic hash. Validate it against the store-owned actual issued snapshot identity, not just a caller-supplied string. An empty eligible set is explicitly non-injectable/terminal Skipped upon later selection, not an excuse to resurrect evicted plans. A newer AnalysisGenerationId alone does not revoke already-held valid snapshot; PluginSessionEpoch reset invalidates old eligibility. Do not invent an Orca-supplied invocation UUID; pinned source exposes \`execute(ctx)\` only. The exact wrapper and lifecycle require implementation-level review (do not replace the working in-process pairing merely for naming).

### D10: explicit Phase 0.5 package boundary

\`ARCHITECTURE §2\` names **final target modules**; Phase 0.5 acceptance requires only meaningful reviewed frozen Domain DTOs, Application identity/store and necessary Ports/interfaces plus mechanically enforced imports. No empty \`orca_plugin/gcode\`, adapter, optimizer, numerical SurfaceBand estimator or executable fixture tests are introduced to satisfy a directory checklist. No legacy script edits, Physical Injection or G-code mutation.

### Proposed validation matrix before production implementation

- Immutable typed DTO/frozen nested shape; nonempty/duplicate/foreign IDs, cycle/self-nesting, closed geometry reference mismatch, non-collinear anchors, invalid bounds/winding, machine-vs-centered coordinate confusion -> typed fail-closed.
- Both directional converged maxima must independently satisfy quality bound; summary \`ErrorMetrics.e_max_mm\` alone never authorizes a candidate.
- V1 Plan bytes and plugin-settings root remain byte-identical; a v2 Plan semantic change alters v2 hash only; unsupported version or unknown required field rejects.
- Unavailable time cannot be represented as a fabricated positive or zero duration; no printable lexicographic selection without the required ranking model.
- Attempt evidence UNKNOWN must not be VALIDATED; reject missing subject/policy/evidence for claimed success; preserve monotonic existing AttemptState; reject stale session/snapshot issue token; duplicate UUID fails without overwriting prior attempts.
- Concurrent publish/reset/eviction vs issuance must not create eligible stale attempts. All rollback failures and malformed inputs are tested; no Orca runtime or G-code executed.

**SPEC_REVIEW disposition:** approved requester **directions**, candidate exact schemas presented here, but independent review and cross-ADR conflict resolution are still outstanding. Do not mark ADR-0067 Accepted or start production v2 Plan/Attempt schema implementation until a reviewed canonical revision, audited manifest, revised handoff, and REPOSITORY_REVIEW \`validated\` exist.


## 2026-10-15 unified specification resolution of X2 (candidate, SPEC_REVIEW)

The cross-ADR reviewed approach for the old mandatory `PlanSemanticContent.estimated_added_time_s` is a separate v2 `AddedTimeEvidence` **tagged union**: `AVAILABLE` has finite nonnegative seconds with time predictor version, exact typed resolved execution-config identity and immutable provenance; `UNAVAILABLE` has an explicit stable reason and missing dependency identifiers. Never use `0`, NaN, Inf, an Optional bare float or a guessed speed-only constant to stand for unavailable. Keep v1 bytes unchanged. See `docs/implementation/phase05-unified-contract-review-2026-10-15.md` for complete proposed state transitions/exception matrix.

Unknown time does not imply invalid geometry: it may produce a research-only analysis, but it cannot be ranked across all feasible candidate plans or become printable under user-approved S6. Separate the geometry-feasible and full-rankable sets, and flag RANKING_INCOMPLETE whenever any relevant geometric candidate cannot be ranked. New directional converged error evidence remains mandatory for a v2 hard bidirectional check. Source-file and Attempt evidence continue to be runtime-only and cannot contaminate Plan identity. The exact v2 placement is not yet Accepted; independent review remains required.
