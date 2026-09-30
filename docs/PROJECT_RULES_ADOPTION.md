# Project Template Rules Adoption

Source repository: `nobunora/project-template`
Source revision audited: `e5a9bce833f0c6badc6d8620b0ea10f74b7d5f9c`

## Rule-source manifest reviewed

The following rule path was fully traversed from project-template `AGENTS.md`:

- `AGENTS.md`
- `docs/00_index.md`
- `docs/core/index.md`
- `docs/ops/index.md`
- `docs/dev/index.md`
- `docs/records/README.md`
- `docs/01_principles.md`
- `docs/02_design_and_boundaries.md`
- `docs/03_naming.md`
- `docs/04_testing.md`
- `docs/05_safety_and_pokayoke.md`
- `docs/06_code_review.md`
- `docs/07_bad_patterns.md`
- `docs/08_report_template.md`
- `docs/09_scripts.md`
- `docs/10_development_playbook.md`
- `docs/11_refactor_and_release.md`
- `docs/12_records_and_milestones.md`
- `docs/13_architecture_quality.md`
- `docs/14_skill_creation.md`
- `docs/15_codebase_memory_and_quality.md`
- `docs/15_model_orchestration.md`
- `docs/16_blind_review_protocol.md`
- `docs/17_repo_index_and_query.md`
- `docs/18_static_analysis.md`
- `docs/19_chat_github_codex_workflow.md`
- `docs/specs/README.md`
- `docs/specs/SPEC_TEMPLATE.md`
- `docs/implementation/README.md`
- `docs/implementation/TASK_TEMPLATE.md`
- `.codex/README.md`
- `.codex/repository-review.md`
- `.codex/implementation.md`
- `.github/workflows/spec-ready-gate.yml`
- `.github/PULL_REQUEST_TEMPLATE/spec.md`
- `.github/PULL_REQUEST_TEMPLATE/implementation.md`
- `scripts/README.md`

The C/C++ helper implementations themselves were not copied; their governing rules were reviewed through the referenced rule documents.

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
