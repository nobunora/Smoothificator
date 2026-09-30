# Documentation Contract and Precedence

This file defines how to resolve contradictions between project documents.

## Operational precedence

For how work is performed:

1. `AGENTS.md` — repository work discipline and agent process.
2. Task-specific `.codex/` contract when explicitly used.
3. `docs/QUALITY_GATES.md` / `docs/REVIEW_PROCESS.md` — verification and convergence process.
4. Task implementation record under `docs/implementation/`.

These process documents do not override product/technical requirements.

## Product / technical precedence

Highest to lowest:

1. **Accepted ADRs** — specific architectural/safety decisions, within their stated scope.
2. **SPECIFICATION.md** — canonical product behavior and supported domain.
3. **ARCHITECTURE.md** — dependency direction, ownership, data boundaries.
4. **IMPLEMENTATION.md** — normative implementation contract consistent with 1-3.
5. **PLUGIN_REQUIREMENTS.md** — Orca/runtime/package compatibility constraints.
6. **ERROR_MODEL.md / ZAA_INTEGRATION.md** — normative technical models where referenced.
7. **docs/specs/*.md handoff specs** — bounded implementation/review scope and acceptance criteria; MUST reference the canonical revision and MUST NOT override 1-6.
8. **ROADMAP.md / TEST_STRATEGY.md / QUALITY_GATES.md / REVIEW_PROCESS.md** — sequencing, validation and release gates.
9. **FULL_CONSISTENCY_AUDIT_2026-10-01.md / FULL_CONSISTENCY_AUDIT_2026-09-30.md / ORCASLICER_PLUGIN_RESEARCH.md / DEPENDENCY_AUDIT.md / SMOOTHIFICATOR_ANALYSIS.md / PROJECT_RULES_ADOPTION.md** — evidence/history/process-adoption record; may describe rejected/superseded approaches.
10. **README.md** — summary only.

If a lower-precedence document conflicts with a higher one, follow the higher document and fix the documentation before implementing behavior.

## Change responsibilities

Product behavior change:
ADR if required -> SPECIFICATION -> IMPLEMENTATION -> tests -> summaries.

Architecture change:
ADR -> ARCHITECTURE -> IMPLEMENTATION -> architecture tests.

Orca/API discovery:
research/audit -> ADR if behavior changes -> PLUGIN_REQUIREMENTS/IMPLEMENTATION.

Physical calibration finding:
ERROR_MODEL -> ADR if safety/semantics change -> SPECIFICATION/IMPLEMENTATION.

Task scoping:
canonical contract -> docs/specs handoff spec -> repository review -> docs/implementation task record.

Roadmap never overrides a technical contract.

README never creates requirements.

Implementation records never become a second product specification.

## Coding-agent rule

Before implementation work:
1. read `AGENTS.md`;
2. read the supplied handoff spec under `docs/specs/`;
3. confirm the canonical specification revision referenced by that handoff;
4. read relevant Accepted ADRs;
5. read `SPECIFICATION.md`;
6. read `ARCHITECTURE.md`;
7. read relevant `IMPLEMENTATION.md` sections;
8. read `TEST_STRATEGY.md` / `QUALITY_GATES.md`;
9. read the task implementation record.

Do not infer current behavior from historical/audit prose without checking higher-precedence documents.

## Specification-to-implementation gate

Production implementation MUST NOT start until:
- the current specification consistency audit is complete;
- the handoff specification references the audited canonical revision;
- a review-only repository validation has disposition `validated`;
- material specification conflicts are resolved;
- an implementation task record names the approved scope and verification plan.

If repository evidence later invalidates the contract, stop affected implementation and return to adjudication.

## Consistency invariants

Before implementation or release:
- ADR identifiers MUST be unique.
- Every normative hook name, coordinate convention, flow convention, and printable safety gate MUST agree across canonical documents.
- Historical/audit documents may describe rejected approaches only when clearly labeled.
- README must not contain behavior absent from higher-precedence documents.
- Handoff specs must not copy detailed requirements in a way that creates an independent owner.
- Implementation records must not silently redefine requirements.
- A coding agent encountering ambiguity MUST stop that work item and report the conflicting documents.

## Project-template adoption

The imported process rules and project-specific adaptations are recorded in `docs/PROJECT_RULES_ADOPTION.md`.
