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
