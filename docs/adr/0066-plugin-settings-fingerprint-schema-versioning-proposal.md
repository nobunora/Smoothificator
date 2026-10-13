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
