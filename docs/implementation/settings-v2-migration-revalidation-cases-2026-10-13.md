# Settings v2 fingerprint transition — candidate safety scenarios (2026-10-13)

Status: **Proposed/review-only**. Not an implementation test result or Accepted migration contract. Evidence: Accepted ADR-0037/0062/0064/0065 and SPECIFICATION §§17–18.

## Cases requiring adjudication

| Scenario | Required invariant from existing ADRs | Proposed fail-closed v2 behavior | Evidence / unresolved |
| --- | --- | --- | --- |
| v1 plan and same v1 settings in same plugin epoch | Exact typed matching required | v1 remains research-only, no v2 compatibility inferred | Existing v1 independent hash fixtures; no physical qualification |
| v1 plan, subsequently changed settings model to v2 | Different schema/type identity may not compare equal | Reject cross-schema match; fresh analysis under reviewed v2 | Exact v2 fields/schema not accepted |
| v2 config declared while identity_root still recognizes only v1 | Unknown version must reject | Reject with typed reason; no attempt to synthesize missing fields | v2 serializer not implemented, tests must keep v1 closed |
| Old v1 export selected before newer v2 generation | ADR-0037 permits retained immutable older snapshot; a newer generation alone is not disqualifying | Keep snapshot immutable but require matching **current** Settings fingerprint at validation start and immediately precommit; mismatch aborts | Exact Orca postprocess lifecycle fixture not verified |
| Bounded eviction before snapshot vs after | ADR-0065 differentiates pre-selection eviction vs already-held immutable snapshot | No resurrection after eviction; selected snapshot remains immutable, then apply new/old settings equality checks | PlanStore unit tests cover only in-memory part |
| PluginSessionEpoch reset | Old epoch not executable | Reject old snapshots irrespective of a matching digest | No persisted-plan replay |
| Same semantics but unsupported schema/encoding version | ADR-0062 type/schema/version must match | Reject rather than reinterpret or compare only raw SHA-256 | Independent golden fixture and negative tests needed |
| Runtime settings edited during export | ADR-0037 recheck before commit | Skip/abort with original file preserved | Requires future working-file/commit lock fixtures, not tested |
| Partial v2 fields or unspecified fixture limits | Missing/invalid values fail closed | Research-only; do not populate universal physical defaults | Field-by-field policy unresolved |
| Hash change due to config vs process status | ADR-0064 forbids runtime status/generation in identity | v2 settings affect typed fingerprint/plan; attempt records do not | v2 projection not finalized |

## Non-goals and next gate

This matrix clarifies risks but **does not** approve resetting a session on schema switch, invalidating already-selected snapshots, retaining v1 injection capability, or adding version migration utilities. Such transitions need explicitly reviewed policy and actual Orca fixture evidence.

Before accepting ADR-0066, reconcile the draft with ADR-0037/0065's late TOCTOU check, review unknown version behavior, construct independent v1/v2 golden vectors, and complete the canonical revision manifest/handoff review. No implementation-branch Settings schema change follows from this packet.
