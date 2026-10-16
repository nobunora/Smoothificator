# Phase 0.5 runtime-interface skeleton handoff

Status: SPEC_VALIDATED for static runtime vocabulary and commit-lock port only.

Repository review: the implementation lead independently checked the closed
ADR against the existing AttemptRevision/InjectionAttemptStore and ADR-0061.
Unknown/rejected diagnostics introduce no proof authority or mutable owner.
The concrete verifier/provider remains Phase 4 as required by the roadmap.
No unresolved conflict in this bounded interface scope; production edits follow
this disposition. This is not a certification of runtime validation.

Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `44b4a13d7ffe1456d664a1b1d2af610bd1302f7a`

## Contract and scope

ADR-0067's Closed Phase 0.5 runtime-interface skeleton section owns exact DTO
fields, subject roles, state rules and port signature. ADR-0061 owns the future
same-working-file commit critical section. Refresh the canonical manifest and
record its exact Git blob after review, before production implementation.

Implement only ValidationEvidence, AttemptDiagnosticSnapshot and
WorkingFileCommitKey as frozen domain vocabulary, plus the ports-layer
WorkingFileCommitLockRegistry Protocol. Reuse existing IdentityReference,
ReasonCode and AttemptRevision. No concrete filesystem/locking implementation,
new dependency, second store or mutable evidence cache.

## Decisions and rationale

The original roadmap requires commit-lock interface only during Phase 0.5.
Actual path resolution, source digest/TOCTOU, matcher and atomic commit belong
to Phase 4. Non-injectable research Plans can support Phase 1 mathematics
without pretending those later guarantees exist.

The diagnostic shape binds four distinct check results to one immutable attempt
revision. Unknown and rejected are expressible without false success; validated
is reserved and always rejected. A DTO cannot certify that its revision was
store-issued. Actual verifier-to-store evidence transitions, authorization and
atomic attachment remain a later reviewed application boundary. Existing store
retention/revision ownership remains unchanged rather than introducing an
unbounded parallel diagnostic history.

An opaque commit key names the future resolver's output; it is neither a path
canonicalizer nor proof that the path was verified. Protocol shape tests are
not evidence of mutual exclusion or filesystem correctness.

## Required acceptance

- Required/exact immutable fields, malformed strings/types/identity roles.
- Unknown/rejected rules and unconditional validated rejection; no success
  factory, token, public proof flag or bypass.
- Four independent check slots; derived attempt ID/revision cannot conflict with
  their single immutable AttemptRevision; no authoritative state mutation.
- New DTOs rejected by standalone and Plan-v2 canonical projection paths.
- Exact Protocol signature and legal dependency boundaries; no concrete no-op
  lock, filesystem access or new store/cache.
- Syntax/import, architecture, focused/full regression, package and exact-source
  CI; independent implementation review; unchanged v1/v2 vectors and lifecycle.

## Completion language and exclusions

This closes static Phase 0.5 runtime-interface obligations only. Do not claim
full B6 verification, source-file proof, installed-Orca compatibility, executable
matching, real commit locking, cancellation or physical readiness. Those remain
Phase 4 work. Phase 1A may start after the actual skeleton exit gates pass;
unavailable physical evidence is not a reason to postpone pure mathematical
engine work.
