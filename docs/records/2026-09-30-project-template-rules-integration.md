# 2026-09-30 — Project-template rules integration

## Milestone

Integrated applicable repository/agent workflow rules from `nobunora/project-template` revision `e5a9bce833f0c6badc6d8620b0ea10f74b7d5f9c`.

## Changed areas

- Added root `AGENTS.md`.
- Added quality and independent-review contracts.
- Added GitHub/Codex specification -> repository-review -> implementation workflow.
- Added handoff specification/template and implementation record template.
- Added PR templates and deterministic `codex-ready` specification gate.
- Added generated/cache/build ignore rules.
- Strengthened Architecture and ADR contracts with ownership, failure containment, observability, resource, rollback, and review requirements.
- Updated Roadmap/Test Strategy/Document precedence for repository validation and blind review.

## Checks performed

- Confirmed all handoff-spec headings required by the GitHub gate are present.
- Confirmed repository-review Codex contract is read-only.
- Confirmed implementation contract requires `validated` repository review.
- Confirmed Roadmap places repository validation before Phase 0.5 implementation.
- Confirmed physical-print Test Strategy includes independent review gate.
- Confirmed Implementation source tree includes execution-frame module.
- Confirmed ADR identifiers are unique from 0001 through 0011.

## Adaptations

Not copied as mandatory tooling:
- project-template C/C++ clangd/clang-tidy scripts;
- tracked CodebaseMemory graph artifact;
- unconfigured analyzers.

Python lint/type tooling will be chosen only after Phase 0.5 runtime/environment verification.

## Known limitation

`docs/specs/adaptive-subedge-v1.md` intentionally does not yet contain the final audited canonical commit SHA.

It MUST be updated after the requested full-text consistency audit and before the `codex-ready` / repository-review gate.

## Next step

Run the full specification/document consistency audit, fix any remaining contradictions, freeze the audited canonical revision, update the v1 handoff spec SHA, then perform the review-only repository validation.
