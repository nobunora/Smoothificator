# Project Template Rules Adoption

Source reviewed: nobunora/project-template AGENTS.md and all rule documents reachable from it.

Purpose: record which template rules are adopted, adapted, deferred, or not applicable to Adaptive Sub-Edge.

## Adopted directly

- Evidence-first, targeted repository reads.
- Small focused diffs.
- Separate feature/refactor/formatting work.
- One responsibility/one owner.
- Explicit dependency direction and architecture tests.
- Typed boundary contracts and stable failure/reason codes.
- Immutable state where practical; explicit mutable-state owner.
- Fail-fast/fail-closed safety gates.
- No broad swallowed exceptions.
- No unexplained hard-coded values.
- No unreviewed dependency additions.
- Focused tests before broad tests.
- Exact command/result reporting.
- Specification/repository-review/implementation separation.
- Specification conflicts return to adjudication.
- Independent review for high-risk changes.
- Blind-review isolation and finding reconciliation.
- Convergence criteria stronger than "tests pass".
- Milestone/review evidence in repository.
- One coherent purpose per commit/diff where practical.
- Secrets and write permissions treated as explicit boundaries.

## Adapted for this repository

### Specification storage
Template prefers all specs under docs/specs/.

This repository already has a mature canonical docs/SPECIFICATION.md plus Accepted ADR hierarchy.

Decision:
- keep docs/SPECIFICATION.md as canonical system specification;
- use docs/specs/ for versioned GitHub/Codex handoff contracts that reference the canonical spec/ADR revision rather than duplicating detailed requirements.

### Static analysis
Template includes C/C++ clangd/clang-tidy tooling.

This project is primarily Python and uses Orca's C++ source only as an external compatibility reference.

Decision:
- adopt deterministic static-analysis principles;
- do not copy C/C++ analysis scripts into this repo;
- choose Python lint/type/dependency tooling during Phase 0.5 based on actual package/runtime needs.

### CodebaseMemory / repository graph
Adopt as optional routing acceleration when available.

Do not require a graph artifact for normal implementation or verification, and never treat graph output as authoritative.

### Standard scripts
Reserve doctor/check/typecheck/test/build/refactor:check/release:check intents.

Do not create empty/fake scripts before the actual toolchain exists.

### Multi-model orchestration
Use roles/capability tiers rather than hard-coding model names in permanent policy.

The expected initial implementation agent may be Codex/Luna, but repository rules remain model-independent.

## Deferred until needed

- Reusable Codex Skill creation rules: only if this project later creates a Skill.
- C/C++ compile_commands/clangd/clang-tidy local index tooling: only if this repository begins building/analyzing C++ directly.
- Deployment/publish automation: define when release channel exists.
- Large compatibility migration/dual-run machinery: define when v1 expands beyond initial profile family.

## Not adopted as a mandatory current requirement

- Copying project-template scripts/analyze.py or repo_query.py.
- Tracking a CodebaseMemory graph artifact.
- Running analyzers that are not installed/configured.
- Broad directory-wide repository reads during routine implementation.
- Model invocation from GitHub Actions.

## Added project-specific strengthening

Because this plugin emits physical-printer G-code:
- physical-print enablement requires independent blind review;
- unknown machine/profile/modal behavior fails closed;
- exact profile fixtures are release gates;
- execution-frame mapping and E conversion require source/fixture parity;
- injection is streaming, atomic, idempotent, and all-or-nothing;
- accepted safety semantics are ADR-controlled.
