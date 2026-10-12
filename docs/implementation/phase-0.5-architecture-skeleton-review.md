> Historical review — Superseded for implementation readiness by the 2026-10-01 revalidation against `docs/AUDIT_REVISION_2026-10-01.md`. Retained as chronological evidence.

# Phase 0.5 — Architecture Skeleton Repository Review

## Specification

- Handoff spec: `docs/specs/adaptive-subedge-v1.md`
- Canonical revision manifest: `docs/AUDIT_REVISION_2026-09-30.md`
- Manifest blob SHA: `2f21857a37f91b4bdadbaaa85b4600addc7c7a07`
- System spec: `docs/SPECIFICATION.md`
- Relevant ADRs: non-superseded ADR-0001 through ADR-0031; ADR-0010 is Superseded by ADR-0015.

## Repository Review Status

`validated`

This disposition applies only to Phase 0.5 architecture-skeleton implementation scope.

It does NOT authorize G-code injection or physical printing.

## Review Mode

Review-only. No production Python implementation was created or modified during this repository validation.

## Repository Evidence

### Current root

Existing production/reference code is limited to:
- `Smoothificator.py`
- `Smoothificator_Adaptive.py`

There are currently no:
- `adaptive_subedge/` package;
- `orca_plugin/` package;
- project Python packaging/build metadata;
- existing tests directory that would conflict with the proposed new package layout.

Therefore the Phase 0.5 package/module names do not collide with current repository paths.

### Legacy code boundary

Legacy Smoothificator scripts remain top-level reference/baseline artifacts.

The approved Phase 0.5 scope does not modify them.

This preserves the upstream baseline and avoids coupling the new architecture skeleton to the legacy regex/postprocessing implementation.

### License

Repository retains GNU GPL licensing.

No new dependency is approved by this review beyond the already-audited need to verify the target Orca Python/NumPy runtime in Phase 0.5.

Any actual dependency/tool addition must follow AGENTS/QUALITY_GATES dependency review.

### Canonical audit integrity

Re-fetched the 13 core normative files listed in `docs/AUDIT_REVISION_2026-09-30.md`.

Result:
- checked: 13
- mismatches: 0

ADR directory review:
- canonical files: 0001 through 0031
- duplicate ADR identifiers: 0
- ADR-0010 marked Superseded by ADR-0015

### External compatibility evidence

Phase 0.5 does not call Orca yet, but the package/schema design is based on the audited stock-Orca contracts documented in:
- `docs/ORCASLICER_PLUGIN_RESEARCH.md`
- Accepted ADRs
- OrcaSlicer source audit baseline `789f848694b955d293ca6b277d1c8046aa6f7436`

No Phase 0.5 contract requires a missing native Orca mutation API.

## Existing Contracts / Invariants

Phase 0.5 must preserve:

- dependency direction:
  `orca_plugin -> application -> engine -> domain`;
- domain/engine cannot import `orca_plugin`;
- immutable cross-boundary DTOs;
- one owner for serialization/hash;
- one owner for Orca config semantic resolution;
- one owner for Orca formatter quantization later;
- no final machine translation/final E/runtime status in plan hash;
- SubEdgePath constant-Z/open-plan semantics;
- SubEdgeSegment local geometric/commanded flow semantics;
- ToolClearanceProfile is explicit hardware/plugin configuration;
- ExecutionConfigFingerprint and PluginSettingsFingerprint are distinct;
- PlanExecutionStatus is separate mutable runtime state;
- typed expected failures / stable reason codes;
- no production Orca/G-code behavior in Phase 0.5.

## Conflicts / Gaps

### Material specification conflicts

None found for Phase 0.5.

### Expected implementation-time environment gaps

Not blockers:
- exact embedded Python version must be verified before final packaging metadata;
- lint/type tooling is not yet configured;
- no pyproject/wheel metadata exists yet;
- physical ToolClearanceProfile values are intentionally not known at Phase 0.5;
- exact production Orca/Bambu fixture is intentionally deferred.

These are documented later-phase or Phase 0.5 environment-verification tasks.

### GitHub branch-head API inconsistency

During the documentation audit, connector file/blob reads reflected the current working branch contents while a branch-head/public commit query returned stale public history.

Mitigation:
- the handoff is pinned to a per-file audited Git blob manifest rather than relying on that stale branch-head response.

This does not block local repository content implementation, but the implementation agent must verify the manifest blob hashes before editing.

## Approved Implementation Scope

Phase 0.5 may create:

```text
adaptive_subedge/
  domain/
  application/
  engine/       # package boundary only; no algorithms beyond types/contracts needed by skeleton
  ports/

orca_plugin/
  adapters/     # package boundary only
  compatibility/
  capabilities/
  ui/
  gcode/

tests/
  architecture/
  unit/
```

Initial implementation behavior:
- frozen DTOs/types;
- validated Settings;
- ToolClearanceProfile schema;
- stable reason/error taxonomy;
- both fingerprints;
- canonical serialization/hash;
- PlanStore/status store;
- architecture/import tests.

## Scope Explicitly Not Changed

- legacy Smoothificator scripts;
- Orca G-code;
- Orca source;
- printer profiles;
- optimizer;
- mesh sectioning;
- G-code parser/emitter;
- physical printer behavior;
- supported profile claims.

## Verification Plan

Exact commands are finalized after the Phase 0.5 implementation chooses the minimal Python test/tool setup.

Required categories:

```text
python syntax/import/package check
architecture/import-boundary tests
DTO immutability tests
Settings validation tests
fingerprint determinism tests
canonical serialization/hash tests
PlanStore bounds/status/concurrency tests
package/build check if packaging metadata is added
```

Lint/type tools that are not configured are reported as NOT CONFIGURED rather than installed opportunistically.

## Implementation Result

Not started in this review-only pass.

## Verification Evidence

Review-time evidence:
- canonical core blob-manifest check: PASS, 13/13 matched
- ADR identifier uniqueness: PASS, 0001–0031 unique
- root path/package collision review: PASS
- production code modified in review pass: NO

Behavioral tests: NOT APPLICABLE before Phase 0.5 implementation exists.

## Review Evidence

- Repository review disposition: `validated`
- Scope: Phase 0.5 only
- Critical/High unresolved findings in approved Phase 0.5 scope: 0
- Physical-injection review: NOT AUTHORIZED / NOT YET APPLICABLE

## Risks / Open Questions

- Avoid turning Phase 0.5 types into premature implementations of future Orca/G-code behavior.
- Do not invent ToolClearanceProfile physical dimensions.
- Do not choose final production Orca/profile compatibility in Phase 0.5.
- Do not add static-analysis dependencies before runtime/tooling review.
- Re-check audited blob manifest immediately before implementation begins.

## Next Gate

Phase 0.5 architecture-skeleton implementation may begin on a separate implementation branch/PR.

If implementation discovers a material contract contradiction, stop and return to specification adjudication.
