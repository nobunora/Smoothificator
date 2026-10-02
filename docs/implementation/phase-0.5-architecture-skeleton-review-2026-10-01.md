# Phase 0.5 — Architecture Skeleton Repository Revalidation — 2026-10-01

## Specification

- Handoff spec: `docs/specs/adaptive-subedge-v1.md`
- Handoff blob SHA: `a9e23c5a13deb7d871513a34546ef6bf76987c77`
- Canonical revision manifest: `docs/AUDIT_REVISION_2026-10-01.md`
- Manifest blob SHA: `06079655a3849d5d75df92244722ee03ae3a5632`
- System spec: `docs/SPECIFICATION.md`
- Full audit: `docs/FULL_CONSISTENCY_AUDIT_2026-10-01.md`
- Relevant ADRs: non-superseded ADR-0001 through ADR-0033; ADR-0010 is Superseded by ADR-0015.

## Repository Review Status

`validated`

This disposition applies only to Phase 0.5 architecture-skeleton implementation scope.

It does NOT authorize:
- Orca live integration;
- G-code mutation;
- physical printing.

## Review Mode

Review-only.

No production Python implementation was created or modified during this revalidation.

## Canonical Audit Integrity

Re-fetched every path listed in the 2026-10-01 audited manifest.

Result:
- manifest blob: `06079655a3849d5d75df92244722ee03ae3a5632`
- checked entries: 47
- mismatches: 0
- ADR files: 33
- duplicate ADR identifiers: 0
- ADR range: 0001–0033
- ADR-0010 supersession: retained by canonical contract

The handoff points to this exact manifest blob.

## Repository Evidence

Current repository root contains:
- governance/workflow directories;
- documentation;
- `Smoothificator.py`;
- `Smoothificator_Adaptive.py`;
- LICENSE/README.

It does NOT currently contain:
- `adaptive_subedge/`;
- `orca_plugin/`;
- a conflicting Python package tree;
- production test/package metadata that would collide with the Phase 0.5 structure.

Legacy Smoothificator scripts remain untouched reference/baseline artifacts.

## Phase 0.5 Contract After Design Review

Phase 0.5 must establish the data/ownership boundaries needed by later phases, including the final design-review additions:

- immutable domain DTOs;
- explicit centered slice-space semantics;
- separate geometric and commanded flow fields;
- constant-Z open SubEdgePath contract;
- segment-local support/height/flow intent;
- candidate seam/gap as immutable plan geometry;
- FinalSurfaceEnvelope versus ChronologicalSupportEnvelope separation;
- acyclic candidate support dependency/order metadata;
- ToolClearanceProfile schema;
- ExecutionConfigFingerprint;
- PluginSettingsFingerprint;
- immutable plan + separate runtime status;
- no final machine translation or final emitted E in the plan;
- deterministic canonical serialization/hash;
- PlanStore/status ownership;
- stable typed expected failures;
- architecture/import-boundary tests.

Phase 0.5 MUST NOT implement the later geometry/G-code algorithms behind those contracts.

## Existing Contracts / Invariants

Preserve:
- dependency direction: external adapters -> application -> engine -> domain;
- no Orca concrete types inside domain/engine;
- no G-code execution concerns inside optimizer/domain;
- one owner for configuration semantic resolution;
- one owner for serialization/hash;
- one owner for formatter parity later;
- no future material used as chronological support;
- support dependency graph acyclic;
- ToolClearanceProfile explicit and evidence-backed later, never guessed from nozzle diameter;
- binary byte-preserving G-code contract remains a later-phase adapter concern;
- physical injection remains fail-closed and fixture-gated.

## Conflicts / Gaps

### Material specification conflicts

None found for Phase 0.5.

### Expected later-phase gaps

Not Phase 0.5 blockers:
- exact production Orca release/commit;
- exact first Bambu fixture family;
- physical ToolClearanceProfile dimensions/evidence;
- empirical bead calibration;
- final Python lint/type tools;
- production performance/resource limits.

### Repository/API blockers

None for Phase 0.5.

No Phase 0.5 task requires a missing native Orca mutation API.

## Approved Implementation Scope

Phase 0.5 may create the package skeleton from `docs/ARCHITECTURE.md` and implement only the contract/data infrastructure necessary for:

- frozen DTOs;
- Settings validation;
- ToolClearanceProfile value schema;
- FinalSurfaceEnvelope / ChronologicalSupportEnvelope value contracts;
- support dependency/order metadata;
- reason/error taxonomy;
- both fingerprints;
- canonical serializer/hash;
- bounded thread-safe PlanStore;
- separate execution-status store;
- architecture/import-boundary tests.

## Scope Explicitly Not Changed

Do not implement yet:
- Orca live adapter;
- transform reconstruction algorithm;
- mesh sectioning/orientation algorithm;
- bead/error/optimizer algorithms;
- G-code parser/matcher/emitter;
- ToolClearance swept-volume validator;
- physical printer behavior;
- profile compatibility claims;
- legacy Smoothificator modification.

## Verification Plan

After Phase 0.5 implementation chooses the minimal test/tool environment, record exact commands for:

```text
python syntax/import/package checks
architecture/import-boundary tests
DTO immutability tests
Settings validation tests
fingerprint determinism tests
canonical plan serialization/hash tests
support dependency/order DTO invariant tests
PlanStore bounds/status/concurrency tests
package/build check if packaging metadata is added
```

Unconfigured lint/type analyzers are reported as NOT CONFIGURED and are not added opportunistically.

## Review Evidence

- Repository review disposition: `validated`
- Canonical manifest: 47/47 PASS
- ADR uniqueness: 33/33 unique
- Root/package collision review: PASS
- Production code modified in review pass: NO
- Critical/High unresolved findings in approved Phase 0.5 scope: 0
- Physical injection authorization: NO

## Risks / Open Questions

The most important implementation risk is premature behavior:
- Phase 0.5 types must not smuggle later Orca/G-code policy into domain code;
- support/order DTOs must encode contract semantics without implementing optimizer logic;
- ToolClearanceProfile must remain a schema, with no invented physical dimensions;
- compatibility constants must not be fabricated during Phase 0.5.

## Human Principle/Design Review

Completed: `docs/DESIGN_REVIEW_2026-10-01.md`.

The explanation-first review identified two material ambiguities before implementation:
- final completed surface versus chronological support state;
- downstream-only clearance versus complete plugin + original motion clearance.

They were resolved by ADR-0032 and ADR-0033 before the final audited manifest was stamped.

After those corrections, no additional material contradiction was found in the Phase 0.5 scope.

Residual uncertainties are explicitly later-phase empirical/compatibility gates, not hidden Phase 0.5 assumptions.

## Next Gate

Phase 0.5 architecture-skeleton implementation may begin on a separate implementation branch/PR.

If implementation later reveals a material contradiction, this `validated` disposition is invalidated and specification adjudication resumes.
