# Adaptive Sub-Edge v1 Handoff Specification

## Canonical Contract

- System specification: `docs/SPECIFICATION.md`
- Architecture: `docs/ARCHITECTURE.md`
- Implementation contract: `docs/IMPLEMENTATION.md`
- Test strategy: `docs/TEST_STRATEGY.md`
- Accepted ADRs: `docs/adr/0001-*.md` through `docs/adr/0011-*.md`
- Canonical revision / commit: use the final specification-audit commit before repository implementation starts.

If this handoff file conflicts with the canonical documents above, follow `docs/DOCUMENT_CONTRACT.md` and return the conflict to specification adjudication.

## Goal

Produce a reviewable, testable stock-Orca Python plugin implementation of Adaptive Sub-Edge v1 without silently changing the approved geometry, safety, G-code, or compatibility contracts.

## Scope

- Phase 0.5 architecture/package skeleton.
- Pure Python domain/application/engine boundaries.
- Immutable plan/status/config-fingerprint contracts.
- Later gated phases defined by `docs/ROADMAP.md`.
- Stock Orca SlicingPipeline + Script capability architecture.
- Analysis-only behavior outside the explicitly supported printable profile/geometry envelope.

## Non-goals

- Rewriting accepted product/safety semantics during implementation.
- Custom Orca C++ changes.
- Broad compatibility expansion beyond the approved v1 gates.
- Opportunistic refactoring of legacy Smoothificator scripts.
- Physical printing before all preceding gates and independent review pass.

## Requirements / Invariants

- Implement only from a repository-review disposition of `validated`.
- Preserve the dependency direction and ownership rules in `docs/ARCHITECTURE.md`.
- Preserve all Accepted ADR decisions.
- Use deterministic immutable plan/config fingerprints.
- Keep geometry optimization independent from Orca/G-code adapters.
- Fail closed on unknown compatibility, modal, coordinate-frame, or profile state.
- Preview and injection consume the same immutable plan.
- No physical printer injection until the exact fixture/profile software gates pass.
- Any newly discovered material repository/API conflict returns to specification adjudication.

## Affected Interfaces / Contracts

- Orca Python Plugin System / SlicingPipeline.
- `posSimplifyPath` geometry snapshot.
- `psGCodePostProcess` working-file mutation.
- Script/UI preview capability.
- Bambu/Orca G-code fixture/profile assumptions.
- SubEdgePlan / ExecutionConfigFingerprint schema.
- G-code coordinate/extrusion conversion contracts.
- Repository quality/review gates.

## Acceptance Criteria

For each implementation phase:
- approved source-boundary rules are mechanically testable;
- focused tests pass before broader tests;
- required architecture/quality gates pass or are explicitly BLOCKED/NOT CONFIGURED;
- implementation record contains exact commands and results;
- no unresolved Critical/High review finding remains at a phase declared complete;
- physical-print gate remains disabled until the test/review contract explicitly permits it.

## Validation

Use the phase-specific commands defined after Phase 0.5 tooling is established.

At minimum:
- architecture/import-boundary tests;
- deterministic serialization/hash tests;
- focused unit tests;
- Orca adapter fixture tests;
- golden G-code/parser/injector tests before printer enablement;
- package/build check;
- independent blind review before first physical injection.

## Risks / Rollback

Primary risks:
- incorrect Orca compatibility assumptions;
- coordinate-frame mismatch;
- incorrect flow/E conversion;
- invalid support/collision model;
- unsafe G-code state restoration;
- stale/mismatched plan injection.

Rollback rule:
- injection must fail closed and preserve original Orca G-code;
- implementation changes are phase-gated and should be reversible by reverting the bounded implementation commit/PR.

## Open Questions

- Exact initial pinned Orca commit/release and Bambu profile fixture set are finalized during the dedicated fixture-acquisition phase.
- Exact Python lint/type tooling is finalized during Phase 0.5 after environment verification.
