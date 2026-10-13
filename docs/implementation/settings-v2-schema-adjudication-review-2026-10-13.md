# Settings v2 schema — primary adjudication review packet (2026-10-13)

Status: **Review-only / not validated / not an Accepted ADR**. This document is evidence for Draft PR #3 and must not be treated as the source of product requirements. Authority stays with accepted ADRs and docs/SPECIFICATION.md.

## Review baseline

- Accepted normative docs in `adaptive-subedge-design` commit `347098214979ff3efb5f669c6e3276c0c262d5a7`.
- Proposed ADR-0066 remains `Status: Proposed` on `proposed-settings-schema-v2-20261013`.
- Separate implementation Draft PR #2 has research-only `PluginSettings(schema_version="1")` with seven fields and a closed canonical root. Proposed ADR shall not silently alter it.
- This is a **primary review**; no blind independent review, physical fixture, NumPy runtime or current Orca executable was examined.

## Field-level provenance and classification

| Semantic settings group | Existing authoritative normative requirement | Current research-only DTO availability | v2 field contract status / evidence needed |
| --- | --- | --- | --- |
| `schema_version`, `surface_error_tolerance_mm`, `minimum_effective_bead_height_mm`, `candidate_seam_gap_mm` | SPECIFICATION §17; IMPLEMENTATION §§12–13 | All four in v1 PluginSettings | v1 names known; no automatic v2 compatibility presumed |
| `CandidateSegmentRegularityPolicy`: five minimum/adjacent fields and evidence identity | Accepted ADR-0063, IMPLEMENTATION §12 | Versioned frozen DTO in `domain/settings.py` | Five concrete names established; fixture-reviewed limits not supplied |
| `ToolClearanceProfile` radial curve, axial height, margins and fixture identity | SPECIFICATION §17, IMPLEMENTATION §13 | Frozen DTO, `PluginSettings.tool_clearance_profile` optional for research | Physical completeness/profile evidence gate needs target fixture verification |
| `ErrorEstimatorConfig` initial spacing/refinement factor/convergence tolerance/maximum levels/sign-tolerance version | Accepted ADR-0045, SPECIFICATION §17 | Standalone frozen DTO (not v1 fingerprint) | Required group; nested ownership/fingerprint inclusion not yet versioned |
| `SurfaceCorrespondencePolicy` distance/normal/interaction region/ray tolerance/fallback versions | Accepted ADR-0050, SPECIFICATION §17 | Standalone frozen DTO (not v1 fingerprint) | Group owner is ErrorEstimatorConfig; specific policy enum semantics and regional mapping need signoff |
| `MeshSectionPolicy` predicate/coplanar/join/quantization stability values | Accepted ADR-0059 | Standalone frozen DTO (not v1 fingerprint) | Sampling-convergence version is currently one identifier; exact runtime evidence/sampling rule needed |
| `max_subedge_acceleration_mm_s2`, `max_subedge_jerk_mm_s`, candidate speed cap | IMPLEMENTATION §12 and SPECIFICATION §17 | Not in v1 | **Open:** speed cap field name/units, positive bounds, fixture evidence, required policy |
| Candidate bead width/height bounds | IMPLEMENTATION §12; SPECIFICATION §17 | Not in v1 | **Open:** precise lower/upper fields and coupling to nominal bead model |
| Support coverage thresholds and tolerances | SPECIFICATION §17, IMPLEMENTATION §12 | `SupportCoverageMetrics` is a measurement DTO, not policy Settings | **Open:** settings owner, field list, numeric tolerances and metric provenance |
| Directional error weights and optimizer cost/risk | SPECIFICATION §17, Accepted ADR-0050 directional aggregation | Not in v1 | **Open:** weights, nonnegative/normalization contract, objective fields |
| Candidate execution/order policy | SPECIFICATION §17; ADR-0032 temporal support semantics | Plan has explicit order/dependencies; no complete plugin settings DTO | **Open:** which selectable policies legitimately belong in PluginSettings; immutable Plan semantics not duplicated |
| ExecutionConfigFingerprint input groups | IMPLEMENTATION §11, SPECIFICATION §18 | Separate mapping-based fingerprint research contract | **Separate owner:** resolved Orca semantics cannot silently become plugin-owned v2 fields |

## Identity and versioning review questions

1. **Version location:** ADR-0062 requires each identity root's `schema_version`, while existing v1 Settings also carries its own `schema_version`. An accepted v2 must explicitly define how those two values agree and reject mismatches. No assumption that changing only the DTO string automates the root version.
2. **Version compatibility:** v1 canonical payload fields and their SHA-256 domain preimage must remain unchanged. Unsupported v2 input must fail closed. A future v2 root must be distinct from v1; neither reused digest hex nor plan hash makes them interchangeable.
3. **Missing safety fields:** unknown printer-specific caps, tolerances and regularization limits cannot be populated with universal numbers or inherited from research fixtures.
4. **No circular policy ownership:** raw Orca override precedence belongs only to the resolved config adapter; optimizer/engine owns geometric evaluation; application owns canonical Settings fingerprint construction.
5. **Snapshot migration:** draft proposal recommends fresh analysis rather than reinterpreting v1 hashes; full semantics need review against accepted ADR-0037/0065 in-flight snapshots and epoch reset behavior. No physical injection while unresolved.
6. **Ports:** ARCHITECTURE lists representative method names but not exact signatures/cancellation/export-association semantics. Defining them without actual consumer and Orca evidence is out of scope.

## Review disposition

- Contract scope **spec-change-required** before integrating complete v2 into `PluginSettingsFingerprint`.
- Actual runtime/fixture compatibility **requires-further-evidence**.
- No approved schema-v2 implementation, accepted status, manifest restamping or merged PR is supported by this primary review.

## Required next review gate

Determine the missing field-level policy from source/fixtures, settle the semantic-version location, amend the proposed ADR, obtain a separate specification review and repository revalidation, then update canonical specification, implementation, audited manifest and handoff. Only after disposition `validated` may the v2 implementation begin. Draft PR #2 remains research-only and physical injection disabled.

## Concrete proposed v2 semantic projection — for specification review, NOT authority

The following is a complete **decision register of settings groups**, not a list of verified printer parameters. Each identifier marked **proposed** is a schema candidate; it is not a field implemented on PR #2. The `PluginSettingsV2` root version `"2"` is **proposed**, while the ADR-0062 canonical byte encoder and domain tags remain version `"1"`. Every numeric value below must be supplied explicitly and verified for its target fixture; **none has a physical default**.

| Proposed v2 name/ownership | Type/units and basic validation | Source requirement | Decision required before Accepted |
| --- | --- | --- | --- |
| `schema_version` | builtin `str`, exactly `"2"` | ADR-0062 versioned identity | Confirm root/DTO marker agreement and invalid old plans |
| `surface_error_tolerance_mm` | finite positive binary64, mm | SPECIFICATION §16–17; v1 implemented | Retain v1 name, never silently migrate |
| `minimum_effective_bead_height_mm` | finite positive binary64, mm | SPECIFICATION §17; v1 implemented | Confirm physical support semantics |
| `candidate_seam_gap_mm` | finite nonnegative binary64, mm | SPECIFICATION §17; v1 implemented | Confirm upper bound owner |
| `tool_clearance_profile` | exact immutable `ToolClearanceProfile` / `None` research-only | ADR-0061, ToolClearanceProfile contract | Physical mode requires independently reviewed fixture |
| `candidate_segment_regularity_policy` | exact versioned `CandidateSegmentRegularityPolicy` | Accepted ADR-0063 | Choose v1 `regularity_policy` retention/rename semantics |
| `error_estimator_config` | exact `ErrorEstimatorConfig` (mm, factor, levels, version) | Accepted ADR-0045 | Decide mandatory nested policy and convergence rules |
| `surface_correspondence_policy` | exact immutable nested `SurfaceCorrespondencePolicy` inside estimator | Accepted ADR-0050 | Ensure no duplicate top-level fingerprint owner |
| `mesh_section_policy` | exact `MeshSectionPolicy`, mm/version | Accepted ADR-0059 | Confirm section-sampling convergence version |
| `candidate_motion_limits` | **proposed** frozen `CandidateMotionLimits` with `max_candidate_speed_mm_s`, `max_subedge_acceleration_mm_s2`, `max_subedge_jerk_mm_s`; finite positive, mm/s, mm/s², mm/s | IMPLEMENTATION §12; SPECIFICATION §17 | Supported firmware jerk convention, tool/profile evidence; compare to ExecutionConfig limits |
| `candidate_bead_bounds` | **proposed** frozen `CandidateBeadBounds` with `min_candidate_width_mm`, `max_candidate_width_mm`, `min_candidate_effective_height_mm`, `max_candidate_effective_height_mm`; finite positive, ordered, mm | IMPLEMENTATION §12 and SPECIFICATION §17 | Nozzle/flow/width-to-height constraints and correct value source |
| `support_coverage_policy` | **proposed** frozen `SupportCoveragePolicy`, `required_support_coverage_ratio` finite `[0,1]`, plus **unresolved** support sampling/contact tolerance and algorithm version | SPECIFICATION §17, Gate F, ADR-0058 | Define the actual tolerance unit and metric semantics; measurement `SupportCoverageMetrics` is NOT Settings |
| `directional_error_weights` | **proposed** frozen `DirectionalErrorWeights`; independent nonnegative finite predicted→source/source→predicted weights | Accepted ADR-0050 and SPECIFICATION §16–17 | Define dimensionless normalization and optimization objective coupling; avoid sample-count weighting |
| `optimizer_cost_policy` | **proposed** frozen `OptimizerCostPolicy` incorporating residual error, path length, commanded volume, added time, complexity/risk cost | SPECIFICATION §16 | Fix units/scaling, lexicographic vs weighted objective, deterministic tie-break |
| `candidate_execution_policy` | **proposed** versioned identifier/DTO for allowable deterministic order, travel and support selection | SPECIFICATION §17; ADR-0032 | Identify which switches actually exist; do not duplicate immutable per-Plan execution order |
| `physical_injection_requested` | builtin bool, always false until separate physical gate | Existing Phase 0.5 research DTO/handoff | Retain v1 research disable regardless of v2 schema validity |

**Excluded by ownership**: raw Orca profile/config keys, per-object print transformations, resolved filament speed/flow, machine XYZ offsets, final emitted E and mutable attempt/status. These belong to resolved `ExecutionConfigFingerprint`, immutable plan intent or runtime attempt state, never to arbitrary `PluginSettings` `__dict__` hashing.

### Reviewer decision matrix (each item needs Accepted/spec rationale)

1. **D1 — nested Settings structure:** approve the above groups, fix every remaining identifier and precise type; decide whether nested `SurfaceCorrespondencePolicy` lives only in `ErrorEstimatorConfig`.
2. **D2 — numeric units and normalization:** finish coverage sampling tolerance units, motion/jerk dialect, direction weights/cost objective units and normalization, and which constraints are compulsory for analysis vs physical export.
3. **D3 — provenance and requiredness:** decide which research-only missing profiles produce analysis output but MUST remain non-injectable; no guessed physical defaults.
4. **D4 — canonical schema ID migration:** require exact v1/v2 root + DTO version match, unchanged tag/magic/byte grammar and separate golden vectors; old v1 Plan hashes never interpreted as v2.
5. **D5 — source of truth of final export config:** identify how late export properties are resolved and rechecked without hashing them twice in PluginSettings; review against ADR-0037/0065 before implementation.

Until D1–D5 are independently adjudicated in the specification workflow, **no v2 Settings class, migration path, or physical-mode permission may be implemented as if normative**.
