# ADR-0066 (PROPOSED): Version PluginSettings fingerprint when expanding the complete plugin-owned Settings contract

Status: **Proposed — NOT ACCEPTED, NOT IMPLEMENTATION AUTHORITY**
Date: 2026-10-13
Scope: `PluginSettings` identity schema and future Phase 0.5 Settings DTO integration only.
Reconciliation required against Accepted ADR-0045/0049/0050/0059/0062/0063/0064/0065, `docs/SPECIFICATION.md`, `docs/IMPLEMENTATION.md` and installed Orca runtime evidence.

## Problem / existing evidence

The current PR #2 implementation defines seven fields in a research-only `PluginSettings(schema_version="1")`, whose `PluginSettingsFingerprint` is computed from the full closed v1 DTO. That v1 DTO does **not** include the already-approved `ErrorEstimatorConfig`, `SurfaceCorrespondencePolicy`, `MeshSectionPolicy` and other required plugin-owned settings groups.

Inserting additional fields into the same v1 semantic projection silently changes hashes produced under the same schema version, violates explicit versioned identity assumptions, and risks comparing unequal plans as if their settings were equivalent. Reusing research-only numeric thresholds as universal physical defaults is prohibited by ADR-0063.

This ADR proposes migration semantics. It does not yet commit to exact final field names/types for every currently unresolved optimizer/coverage/fixture setting.

## Proposed decision (subject to review)

1. **Immutable versioned identity roots.** Preserve the ADR-0062 domain tag `plugin-settings`, magic `AdaptiveSubEdgeCanonicalV1`, tagged tree grammar, and canonical encoding version `"1"`. Add a distinct **PluginSettings semantic schema version** for the complete Phase 0.5 settings model, provisionally `"2"`. Existing v1 semantic bytes and digests MUST remain unchanged for the same v1 inputs. A version 1 and a version 2 root MUST NOT be considered equivalent even if other values match.
2. **Explicit typed complete projection.** The v2 projection MUST be a declared immutable schema containing all plugin-owned settings that can influence candidate creation, support, error scoring, optimizer, movement/safety gates or execution policy. No `__dict__` or raw Orca config may silently enter its tree. Every field MUST have a normative name, type, units, validation and serializable inclusion/exclusion rationale before Accepted status.
3. **Required groups already fixed by higher-precedence documents** (no new defaults or limits introduced here):
   - Surface geometry goal and error tolerance, candidate seam/gap and minimum effective bead height.
   - ToolClearanceProfile, hardware evidence identity and margins.
   - CandidateSegmentRegularityPolicy five fixture-derived segment-length/time/rate/width/height limits and evidence identity (ADR-0063).
   - Candidate speed cap, acceleration/jerk caps, candidate width/height bounds and other approved physical constraints.
   - Support-coverage thresholds, numeric tolerance/version and temporal support contract settings.
   - ErrorEstimatorConfig sample spacing/refinement/convergence/research limits (ADR-0045).
   - Nested SurfaceCorrespondencePolicy region-neighborhood/ray/normal/fallback settings (ADR-0050).
   - MeshSectionPolicy predicate/coplanar/join/quantization stability settings (ADR-0059).
   - Explicit directional error cost/optimizer weights, cost/risk policy, and deterministic execution policy.
4. **Distinct owner from Orca execution identity.** Resolved Orca machine/process/filament semantics remain owned by `ExecutionConfigFingerprint` and the Orca config adapter. Do not duplicate their raw override precedence or permit plugin-settings identity to stand in for resolved final export config.
5. **No implicit upgrade.** v1 plans/fingerprints cannot be upgraded to v2 using guessed/default values or by reinterpreting existing digest hex. Until v2 is Approved, audited and implemented, the whole Phase 0.5 plugin remains research-only / no physical injection. Unsupported/unknown version/field => typed invalid configuration and Skipped at later execution boundary.
6. **Fixture evidence remains external proof.** Schema-valid numeric settings alone do not certify a physical fixture; fixture calibration, Orca runtime and blind-review gates stay independent. No version of Settings can bypass them.
7. **New plan semantic identity.** Changing the plugin-settings typed identity reference changes the `SubEdgePlan` hash under the existing plan-domain hashing contract. Derived plan_hash/id, runtime epoch/generation/status and machine E remain excluded; `plan_id == plan_hash`.

## Primary schema inventory (review only)

A field-level provenance matrix, unresolved mandatory caps/weights/coverage policy, and the v1-versus-v2 identity-version issue are recorded at [the adjudication review packet](../implementation/settings-v2-schema-adjudication-review-2026-10-13.md). This reference supports review only; it does **not** make missing field names or numeric limits normative. The review packet does not grant Accepted status.

The v1 canonical root currently uses `schema_version="1"`, and its payload includes a separate `PluginSettings.schema_version="1"`. Candidate decision **for review**: a completed v2 must use a typed `plugin-settings` root with `schema_version="2"` and an unambiguous v2 DTO schema marker also equal to `"2"`. The root encoder's `canonical_encoding_version="1"` remains unchanged unless the actual tagged-byte grammar changes. Mismatched root/DTO versions must fail closed. This is a **proposal**, not authorization to modify the currently registered `identity_root` allowed versions.

The in-flight snapshot / settings-TOCTOU / eviction and epoch transition cases are captured separately in [the proposed migration scenario review](../implementation/settings-v2-migration-revalidation-cases-2026-10-13.md). It is a review packet, **not** a new transition requirement or physical release authorization.

## Required remaining decisions before Acceptance

- Name every missing settings field and fix its domain type, range, unit and required-vs-optional status using canonical `SPECIFICATION` and `IMPLEMENTATION` without ambiguous unions.
- Choose where the semantic schema version is carried: v2 PluginSettings DTO field and versioned `plugin-settings` root; ensure exactly one authoritative version choice and reject contradictory versions.
- Specify optimizer weights and support-coverage policy as immutable sub-DTOs only after independently checking existing accepted ADR requirements and fixture evidence.
- Define defaults: **none** for unresolved safety/physical thresholds; where research-only values are permitted, tag their evidence mode and ensure they never satisfy physical injection authorization.
- Define migration strategy for previously generated v1 plans: recommended **do not migrate**; invalidate/reanalyze within active PluginSessionEpoch, but adjudicate against ADR-0065 reset/eviction details.
- Pin Python embedded runtime and NumPy integration evidence before packaging changes.
- Resolve exact Port interfaces only from actual analyzer and adapter usage; no speculative PlanRepository/MeshSectionProvider/Cancellation API changes based on this proposal.

## Rejected alternatives

- Extend v1 semantic settings without schema version change: rejected (silent digest meaning change).
- Hash entire arbitrary plugin/Orca settings mapping or Python repr: rejected (uncontrolled, nondeterministic identity and duplicate Orca override ownership).
- Treat the existence of research DTOs as full v2 coverage: rejected (missing physical and optimizer values).
- Universal printer safety defaults to expedite compilation: rejected (unmeasured hardware behavior).

## Acceptance / tests / audit gates (not yet executed for v2)

1. Reconcile all field names/semantics against Accepted ADRs and canonical specification, update SPECIFICATION / IMPLEMENTATION / ARCHITECTURE if a real contract delta is approved.
2. Audit and restamp the 81-entry canonical blob manifest + new ADR provenance (avoid self-referential handoff SHA).
3. Perform a review-only repository revalidation with disposition `validated` before production v2 implementation.
4. Golden v1 fingerprint vectors unchanged; v2 typed root distinct, complete field sensitivity, order-independent canonical mapping, unknown/missing/invalid values rejected.
5. V2 plan hashes change iff declared semantic settings change; old v1 plan cannot be mistaken for v2, and runtime status/generation remain excluded.
6. Independently review full v2 Settings/port boundaries; printer injection remains disabled until the separate physical/Orca gates pass.

## Status / next action

**PROPOSED only.** Review this ADR and settle its open field-schema and migration decisions on a dedicated design PR. Do not mark Accepted automatically or merge into the current audited implementation baseline. No production code change is authorized solely by this proposal.

## 2026-10-15 requester review disposition (direction-level approval only)

Requester approves S1–S5 and S7–S9 as documented in `docs/implementation/settings-v2-schema-adjudication-review-2026-10-13.md` on this design branch, including preserving v1 identity, complete typed plugin-owned policy coverage, versioned numeric support query, dialect-aware motion limits, two-direction error weights, explicit execution policy, analysis-only with missing calibration evidence, and no inferred v1-to-v2 migration.

**S6 changes requested, NOT approved.** A geometric error-only optimizer was proposed by the requester on grounds that time/material/path complexity may be functions of error. This is not generally an exact functional dependency; different path lengths, order, accelerations and bead widths may yield equal error but different cost. Reviewer must adjudicate error-first lexicographic optimization vs quality-threshold-constrained secondary execution-time/material cost. Exact error function, tie tolerance, secondary-cost measurements and deterministic ordering remain open. See the referenced review packet for bounded alternatives.

Requester direction is not independent ADR acceptance or complete mathematical specification. Status remains Proposed. Do not implement schema-v2 or alter v1 bytes until remaining field/type decisions and formal review are complete.

## 2026-10-15 S6 revised optimizer objective — proposed, not Accepted

Requester's revised preference: specified surface-error threshold has absolute precedence, then minimize structural complexity, estimated time, and added material, in that order. Requester also directed complexity to be modeled before choosing the optimization methodology. This replaces the previous undifferentiated weighted residual-error/length/time/volume objective **for review only**.

### Formal constrained lexicographic proposal

Let `P` be one immutable candidate plan, `S` the source, `E_→(P)` and `E_←(P)` the ADR-0047/0050 bidirectional, converged maximum surface-error metrics, and `epsilon` the configured tolerance in mm. Define feasibility:

`F = {P: E_→(P) <= epsilon and E_←(P) <= epsilon and all support/clearance/geometry/motion/flow and numerical convergence gates PASS}`.

If `F` is empty the engine reports a stable typed `INFEASIBLE` result in analysis, without inventing or injecting an unsafe fallback. Any nonconvergent/unresolved geometric/support/collision or required error check makes that candidate infeasible. Directional weights can rank diagnostic/soft residual error only if an independently reviewed role is identified; they cannot weaken the two maximum-error hard gates.

For each `P in F`, propose immutable complexity tuple
`C(P)=(N_added_paths, N_added_segments, N_independent_travel_or_restart_transitions)`.
Each element must be a finite, nonnegative integer counted using a versioned canonical plan grammar. Splitting/reparameterizing a geometrically equivalent path must not allow a scorer to conceal actual commands or breaks; exact path and transition definitions require independent review. Use no arbitrary weighted sum of these counts. This tuple is a **proposal**, not a claim that it is the optimal complexity metric.

Let `T(P)` be separately computed finite, nonnegative estimated **added** execution time in seconds for the selected resolved machine configuration (including finite acceleration and travel/restart effects); it is NOT determined by `C(P)` alone. Let `V_cmd(P)` be finite, nonnegative **added commanded** extrusion volume in mm^3 (not geometric deposited bead volume). Neither quantity may be assigned a guessed universal machine constant, derived from the error alone, or inferred as a mere weight on complexity. Model version, capability, calibration/evidence identity and normalized units participate in complete versioned settings/execution ownership.

**Selection:** `P* = argmin_lex [C(P), T(P), V_cmd(P), K(P)]` for `P in F`, where `K(P)` is a deterministic canonical semantic byte-key tie-breaker (no runtime object identity). The objective makes quality a hard first-tier condition; *within the tolerance*, it does NOT prefer lower residual error over simpler candidates. If the requester later requires strict residual-error ordering even within tolerance, this is a distinct policy and requires a revised comparator.

### Mathematical counterexample to error-only sufficiency

For two feasible plans with identical converged `E_→/E_←`, choose different travel/restart order or bead cross-sections: `C`, `T` and `V_cmd` can differ despite equal error. Likewise two plans with the same path/segment counts may have different length or kinematics. Therefore there is no general single-valued universal relationship `(C,T,V_cmd)=f(E)`, even though correlations often arise from finer geometry. Modeling before choosing the comparator is justified.

### Review blockers and fail-closed cases

- Verify that path/segment/restart counts reflect the actual immutable plan and do not reward fake coalescing or punish semantically equivalent representation.
- Specify whether `T` is a portable planning estimate vs resolved machine/profile estimate; input precedence and provenance must not double-count Orca-resolved execution configuration. Model uncertainty must not masquerade as exact time.
- Specify `V_cmd` under existing geometric-vs-commanded-flow separation. Include any intentionally omitted priming/retraction volume only by an explicit versioned rule.
- Use an explicitly reviewed total ordering for binary64 score values and stable semantic ties (no epsilon-based non-transitive pairwise sort). Numeric convergence tolerances are distinct from score-comparison equality; NaN/Inf/missing measures reject scoring, not treated as zero.
- Define how a valid research candidate lacking target-specific `T` may be reported without declaring a globally optimal printable selection; this is a pending analysis-mode policy, not permission to guess time.
- This paragraph must not silently override higher-precedence canonical SPECIFICATION until specification approval; implementation remains blocked by the full Settings v2 contract, revised manifest/handoff and validated repository review. The staged SPECIFICATION/IMPLEMENTATION text on this PR is a **proposed revision**, not a merged contract.

## 2026-10-15 S6 requester decision — APPROVED optimization policy direction

The requester explicitly approved the balance of the proposed S6 strategy after reviewing the model: configured bidirectional maximum surface-error bound and all safety/physical feasibility checks are **hard constraints**, then rank feasible plans in strict lexicographic order by **structural complexity**, **estimated added time**, **commanded added material volume**; use a stable semantic identity for exact ties. This replaces the earlier S6 change-request status **at the policy level**. The established distinction between complexity and machine-dependent time remains necessary even where correlated.

The specification proposal on this branch (`docs/SPECIFICATION.md`, `docs/IMPLEMENTATION.md`) contains the staged requirement. Do not introduce an objective with a free trade-off between quality bound and execution cost. The three-part complexity tuple (added paths, segments, independent transitions) is the current candidate **definition to validate**, not independently established equivalence to physical complexity. Require a deterministic canonical counting grammar that resists representation tricks, and a validated, versioned time estimator. Exact comparator types, unknown-time analysis-only behavior, numerical ties and model provenance remain technical acceptance checks. `min` over a bounded candidate search means optimal **within explored eligible candidates**, not proof of global optimality; record search budget and completeness assumptions.

This requester approval does **not** make ADR-0066 Accepted: the full v2 schema, numeric support-query tolerance, dialect-specific motion policy, predictor ownership and independent specification/repository reviews remain required. No code, v1 hash, G-code or printer behavior is authorized by this policy alone.

## 2026-10-15 field-complete *candidate* contract for SPEC_REVIEW (not Accepted)

This section translates user-approved S1–S9 **directions** into a reviewable v2 type/validation proposal. It adds **no** defaults, Python classes, authoritative root changes or printer permissions. Existing Accepted ADR field names and research DTOs take precedence. Each line is either **A** (an already-accepted field/meaning), **P** (new exact candidate to approve), or **E** (needs a specific external or algorithmic evidence gate). "A" does not mean the proposed v2 DTO composition is already Accepted.

### V2 typed root (P)

\`PluginSettingsV2\` is a frozen, slots-enabled, *closed* dataclass (no dict/extra fields), with exactly the following proposed top-level fields:

| Field | Type, status, provenance |
| --- | --- |
| \`schema_version\` | exact str \`"2"\`, required (P); must equal plugin-settings root schema version; canonical encoder remains version \`"1"\` |
| \`surface_error_tolerance_mm\` | finite binary64 >0, required (A for v1 meaning, P for v2 composition) |
| \`minimum_effective_bead_height_mm\` | finite binary64 >0, required (A) |
| \`candidate_seam_gap_mm\` | finite binary64 >=0, required (A); a separate maximum is not invented |
| \`regularity_policy\` | exact \`CandidateSegmentRegularityPolicy\`, required (A ADR-0063); preserve existing field name rather than rename merely for style |
| \`tool_clearance_profile\` | exact \`ToolClearanceProfile | None\` (P); None only in research/non-injectable mode, never evidence of clearance |
| \`candidate_bead_bounds\` | exact \`CandidateBeadBounds\`, required (A ADR-0043 fields, P inclusion) |
| \`support_coverage_thresholds\` | exact \`SupportCoverageThresholds\`, required (A ADR-0044 fields, P inclusion) |
| \`support_refinement_policy\` | exact \`SupportRefinementPolicy\`, required (A ADR-0058 fields, P inclusion) |
| \`support_query_numeric_policy\` | proposed exact \`SupportQueryNumericPolicy\`, required (P); see below |
| \`error_estimator_config\` | exact \`ErrorEstimatorConfig\`, required (A ADR-0045), already contains the *sole* \`SurfaceCorrespondencePolicy\` (A ADR-0050) |
| \`mesh_section_policy\` | exact \`MeshSectionPolicy\`, required (A ADR-0059) |
| \`candidate_motion_limits\` | proposed discriminated motion-limit type, required (P/E) |
| \`directional_error_weights\` | proposed \`DirectionalErrorWeights\`, required only if an approved search/scoring use is defined (P; **blocker X1**) |
| \`optimizer_cost_policy\` | proposed \`OptimizerCostPolicy\`, required (P) |
| \`candidate_execution_policy\` | proposed \`CandidateExecutionPolicy\`, required (P) |
| \`physical_injection_requested\` | exact bool, **false in Phase 0.5**, required (A for v1 guard, P inclusion) |

Every field is part of the v2 semantic fingerprint (including None as an explicit distinct value). Exact built-in types only, no bool-as-number, no NaN/Inf, negative zero normalized by existing canonical encoder; reject missing/unexpected fields, unknown enum versions, mismatched nested DTO identities and cyclic values. No research-only \`ConservativeSupportBounds\` outcome or runtime attempt state may be included. V1 root, v1 payload, digest domain prefix and golden vectors remain **byte-for-byte identical**; v1 and v2 never compare equal or undergo implicit upgrade. Plan v1/v2 schema versions are separately owned by ADR-0067.

### New nested value candidates and mechanical validation

1. \`SupportQueryNumericPolicy\` (P): \`version: str\` (nonempty versioned semantics), \`support_query_length_tolerance_mm: float\` (finite >0); applies to conservative support-cell geometric predicates and ADR-0058 effective-height-bound **stability comparisons** only. The accepted \`support_metric_convergence_fraction\` and \`support_width_convergence_mm\` retain their separate existing meanings. This single-tolerance model is **a design hypothesis**, not proof of sound conservative geometry (E); if error bounds require multiple predicate tolerances, amend the typed schema **before** approval.
2. \`CandidateMotionLimits\` (P/E): motion is a tagged sum type, not an unlabeled bare jerk float. Common \`max_candidate_speed_mm_s: float >0\` and \`max_subedge_acceleration_mm_s2: float >0\`. For the source-required classical jerk convention, \`ClassicJerkCorneringLimit\` contains \`model_version: str\` and \`max_subedge_jerk_mm_s: float >0\`; any junction-deviation or other dialect requires a *separate* dimensionally correct tagged type and source evidence before support. Reject an unsupported dialect or mismatched value/units, never reinterpret junction deviation (mm) as classic jerk (mm/s). Printer-specific limit values have no default (E).
3. \`DirectionalErrorWeights\` (P): \`pred_to_src_weight: float >=0\`, \`src_to_pred_weight: float >=0\`, finite, not both zero, no inferred physical unit. Exact normalized combination/roundoff rule **and purpose** must be reviewed; never replace independent hard directional maxima with weighted averages. See conflict X1.
4. \`OptimizerCostPolicy\` (P): \`version: str\`; \`quality_mode: literal "hard_bidirectional_max"\`; \`rank_mode: literal "lex_complexity_time_commanded_volume"\`; \`complexity_counter_version: str\`; \`time_estimator_model_version: str\`; \`commanded_volume_accounting_version: str\`; \`tie_break_version: str\`. All versions nonempty/recognized. No arbitrary cost weights, no arbitrary epsilon comparator, no automatic renaming of v1 identity. Current *candidate* structural-complexity ranking is added paths, added segments, independent travel/restart transitions, in that order. Counts are nonnegative exact integers from a versioned canonical plan grammar and need representation-invariance review (E).
5. \`CandidateExecutionPolicy\` (P): \`version: str\` and \`ordering_policy_id: str\`, both nonempty **allowlisted** identifiers whose complete rules must be documented (E). The Settings policy may select how to plan; the selected ordered paths and temporal support dependencies live in immutable Plan (ADR-0032/0065). No runtime working-file state or raw Orca config belongs here.

### S6 strict comparator, eligibility and exceptional outcomes (P)

Let \`Q(P)\` require both converged bidirectional maxima \`E_pred_to_src_max_mm <= surface_error_tolerance_mm\` **and** \`E_src_to_pred_max_mm <= surface_error_tolerance_mm\`, plus already-accepted geometry, chronological support (ADR-0044/0058), contact, collision, tool clearance and resolved motion gates. A candidate with false/unknown/nonconverged **any** hard gate is not physically eligible. A lower weighted error never compensates for a gate failure.

For a bounded enumerated candidate set \`S\`, define \`F = {P in S : Q(P)}\`. For candidates with complete ranked evidence:
\`score(P) = (added_path_count, added_segment_count, independent_transition_count, estimated_added_time_s, added_commanded_volume_mm3, canonical_semantic_bytes(P))\`.
Use native lexicographic integer order, exact finite binary64 numeric order after canonical -0 normalization, and unsigned lexicographic *byte* order for the final semantic key; no pairwise tolerance comparisons (which may be nontransitive). When all scores agree and canonical bytes are identical, treat the plans as equivalent (do not choose by timestamp, enumeration order or object identity). A full SHA digest alone is **not** a total collision-free tie-break; compare canonical bytes in true digest collision cases. Counts/metrics derived from immutable planned intent cannot include wall-clock times, runtime attempt state or final machine E.

\`F\` empty: typed \`NO_FEASIBLE_CANDIDATE\` **proposed** analysis outcome, no injectable fallback. A nonconverged candidate is excluded with a stable reason/evidence. Time/model missing: report \`TIME_ESTIMATE_UNAVAILABLE\` as a proposed **analysis-only, rank-incomplete** result; do not invent a zero or infinity or claim that the candidate is an optimal physically executable selection. Overflow/nonfinite/negative time or commanded volume: reject ranking with a typed stable reason; never coerce NaN/Inf. Search budget exhausted: return best **among examined complete eligible candidates**, with explicitly incomplete-search provenance; never claim global optimality.

### Identified cross-source conflicts / blockers to close before Accepted

- **X1 (High, ADR-0066 / SPECIFICATION §17):** S5 approves directional *optimizer* weights, but approved S6 compares **only hard error pass, then complexity/time/volume**. Without a specified separate use (e.g., deterministic proposal/search exploration or diagnostic reporting), the two weights would affect hashes without the selected ranking; inventing a hidden weighted error term would violate S6. Reviewer must approve an explicit role or revise the S5 field. Hard directional maximum limits are never weighted.
- **X2 (High, ADR-0067 / current PlanSemanticContent):** existing Plan v1 requires a finite \`estimated_added_time_s\`; it cannot express unknown time, and its ErrorMetrics contains only summary \`e_max_mm\`, not independently testable directional maxima/convergence. Do not add placeholders or relax Plan v1: either the v2 Plan owns explicit directional convergence and typed optional time evidence, or analysis-only unresolved time lives outside the Plan; adjudicate with ADR-0067.
- **X3 (High, implementation):** physical time model, classic-jerk vs firmware dialect, canonical complexity grammar and exact commanded-volume accounting do not yet have verified consumers/fixtures. Proposal is type-level and cannot imply a calibrated time prediction or printable authorization.
- **X4 (High, implementation):** a \`CandidateMotionLimits\` cornering variant must not double-count a resolved \`ExecutionConfigFingerprint\` property. Plugin-owned user caps and Orca-resolved machine caps must be independently compared with a documented precedence rule.

### Required source-backed tests before schema implementation acceptance

Golden v1 settings and Plan identity unchanged; v2 root/DTO mismatch rejected; every field affects declared v2 fingerprint; all invalid numeric/type/enum/None conditions rejected or analysis-only; unknown dialect fails closed; directional maxima individually enforced; equal-quality but distinct complexity ordered; equal complexity but distinct time ordered; exact tie handled by canonical bytes; inaccessible time never ranked as 0; nonconverged support/error cannot be selected; no early physical injection; old v1 plan never treated as v2. These are **planned acceptance tests, not tests already run**.

**Disposition:** \`SPEC_REVIEW / SPEC-CHANGE-REQUIRED\` for the complete v2 schema, pending X1–X4 and independent spec review. This text is candidate normative language within an **unaccepted** ADR, not authority for source implementation.
