# Adaptive Sub-Edge v1 Handoff Specification

## Canonical Contract

- System specification: `docs/SPECIFICATION.md`
- Architecture: `docs/ARCHITECTURE.md`
- Implementation contract: `docs/IMPLEMENTATION.md`
- Plugin/runtime requirements: `docs/PLUGIN_REQUIREMENTS.md`
- Error/physical model: `docs/ERROR_MODEL.md`
- Test strategy: `docs/TEST_STRATEGY.md`
- Full audit: `docs/FULL_CONSISTENCY_AUDIT_2026-10-02.md`
- Audited revision manifest: `docs/AUDIT_REVISION_2026-10-02.md`
- Audited revision manifest blob SHA: `5e3ab3d79d0c6bba831f377c334bc6df8d4441c7`
- ADRs: `docs/adr/0001-*.md` through `docs/adr/0041-*.md`
- ADR-0010 is Superseded by ADR-0015.

The audited blob manifest, rather than a possibly stale branch-head value, is the canonical revision reference for this handoff.

Before repository review, every blob listed in the manifest MUST still match.

If this handoff conflicts with higher-precedence canonical documents, follow `docs/DOCUMENT_CONTRACT.md` and return the conflict to specification adjudication.

## Goal

Implement Adaptive Sub-Edge v1 as a reviewable, deterministic stock-Orca Python plugin without silently changing the audited geometry, safety, G-code, or compatibility contracts.

The first implementation task is Phase 0.5 architecture skeleton only.

## Scope

Initial approved implementation scope:
- package/module tree from `docs/ARCHITECTURE.md`;
- frozen domain DTOs;
- typed errors/stable reason codes;
- validated plugin Settings;
- `ToolClearanceProfile` DTO/settings contract;
- explicit final-surface versus chronological-support DTO/contracts;
- candidate execution-order/support-dependency metadata contracts;
- `ExecutionConfigFingerprint`;
- `PluginSettingsFingerprint`;
- deterministic canonical serialization and plan hashing;
- bounded thread-safe PlanStore plus attempt-scoped InjectionAttemptStore;
- process-local AnalysisGenerationId / InjectionAttemptId lifecycle contracts;
- architecture/import-boundary tests.

Later work remains gated by `docs/ROADMAP.md` and requires its own implementation records.

## Non-goals

Phase 0.5 MUST NOT implement:
- Orca live-binding adapters;
- source mesh geometry algorithms;
- optimizer/surface-band algorithms;
- G-code parser/matcher/emitter;
- machine execution-frame logic;
- physical printer injection;
- custom Orca C++;
- modifications to legacy `Smoothificator.py` / `Smoothificator_Adaptive.py`;
- compatibility expansion beyond the audited v1 contract.

## Requirements / Invariants

Phase 0.5 must establish boundaries needed by later phases without pre-implementing them.

Required invariants:
- domain/engine independent from `orca_plugin`;
- immutable plan/value DTOs;
- no machine G-code coordinate values inside the immutable plan;
- no authoritative final emitted E in the plan;
- `SubEdgePath` is an explicit open constant-Z path;
- `SubEdgeSegment` owns local support/effective-height/geometric-flow/commanded-flow intent;
- candidate seam/gap is immutable plan geometry;
- geometric and commanded volume are different concepts;
- runtime execution evidence is attempt-scoped and separate from the immutable plan;
- no single mutable per-plan status is authoritative;
- execution and plugin-settings fingerprints have distinct ownership;
- `ToolClearanceProfile` is explicit plugin/hardware configuration, not inferred from nozzle diameter;
- printable source topology is one connected shell and simple target-section topology;
- support can come only from chronological pre-existing material; future material and cyclic support are forbidden;
- final physical clearance covers plugin-generated and resumed-original motion;
- source orientation/material side is an explicit validated contract rather than raw-normal trust;
- later G-code processing is binary/byte-preserving by contract;
- serializer/hash is deterministic and excludes runtime-only state;
- expected failures use typed reason codes;
- architecture rules are mechanically testable;
- no implementation component silently creates a second source of product policy.

## Affected Interfaces / Contracts

Phase 0.5 defines internal contracts that later support:
- Orca `posSimplifyPath` geometry snapshot;
- Orca `psGCodePostProcess` final execution;
- Script/UI preview capability;
- centered PrintObject slice-space geometry;
- immutable `SubEdgePlan`;
- both configuration fingerprints;
- future binary G-code execution adapter;
- downstream original-motion clearance using `ToolClearanceProfile`.

It MUST NOT yet couple the domain layer to Orca concrete types.

## Acceptance Criteria

Phase 0.5 is complete only when:
- package structure matches `docs/ARCHITECTURE.md`;
- all public cross-boundary DTOs are explicit and immutable where specified;
- units/coordinate semantics are encoded in names/types/documentation;
- canonical serialization is deterministic;
- identical semantic inputs produce identical fingerprints/hash;
- timestamps, runtime ObjectIDs, machine translation, final E, and execution status do not affect plan hash;
- PlanStore atomic publication/concurrency/bounds/current-session semantics are testable;
- InjectionAttemptRecord uniqueness/monotonic state/independence is testable;
- forbidden imports fail architecture tests;
- duplicate ADR identifier check is testable or covered by a deterministic repository check;
- no production Orca/G-code behavior has been implemented prematurely;
- required focused tests pass;
- exact commands/results are recorded in the implementation task record;
- no unresolved Critical/High review finding remains for the Phase 0.5 scope.

## Validation

Phase 0.5 repository-native validation should include, once its minimal tooling is established:
- Python syntax/import check;
- package import test;
- architecture/import-boundary tests;
- immutable DTO tests;
- Settings validation tests;
- ExecutionConfigFingerprint determinism tests;
- PluginSettingsFingerprint determinism tests;
- canonical plan serialization/hash tests;
- PlanStore publish/bounds/concurrency tests;
- InjectionAttemptStore uniqueness/monotonic-state tests;
- package/build check if packaging metadata is introduced.

Tool choice for lint/type checking is decided only after target Orca embedded runtime verification. A missing unconfigured analyzer is reported as NOT CONFIGURED, not silently installed.

## Risks / Rollback

Primary Phase 0.5 risks:
- encoding a stale/superseded field into DTOs;
- putting execution concerns into domain types;
- creating duplicate config-resolution ownership;
- serializing runtime-only state into plan identity;
- overengineering interfaces for future phases.

Rollback:
- Phase 0.5 is source-structure/contracts only;
- bounded commits should be independently revertible;
- no printer/file mutation exists at this phase.

Any repository reality that requires a material schema/safety/architecture change returns to specification adjudication before implementation.

## Open Questions

Not blockers for Phase 0.5:
- exact first production-compatible Orca release/commit;
- exact first Bambu fixture family;
- physical ToolClearanceProfile dimensions/evidence;
- empirical bead calibration;
- final lint/type tooling versions;
- production performance/resource budgets.

These are explicit later-phase gates, not permissions to invent values during Phase 0.5.
