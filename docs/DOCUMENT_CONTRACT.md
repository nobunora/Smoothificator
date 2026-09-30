# Documentation Contract and Precedence

This file defines how to resolve contradictions between project documents.

## Precedence
Highest to lowest:

1. **Accepted ADRs** — specific architectural/safety decisions; only within their stated scope.
2. **SPECIFICATION.md** — required product behavior and supported domain.
3. **ARCHITECTURE.md** — dependency direction, ownership, data boundaries.
4. **IMPLEMENTATION.md** — normative implementation contract consistent with 1-3.
5. **PLUGIN_REQUIREMENTS.md** — Orca/runtime/package compatibility constraints.
6. **ERROR_MODEL.md / ZAA_INTEGRATION.md** — normative technical models where referenced by implementation.
7. **ROADMAP.md / TEST_STRATEGY.md** — sequencing and release gates.
8. **ORCASLICER_PLUGIN_RESEARCH.md / DEPENDENCY_AUDIT.md / SMOOTHIFICATOR_ANALYSIS.md** — evidence/history; may describe rejected or superseded approaches.
9. **README.md** — summary only.

If a lower-precedence document conflicts with a higher one, follow the higher document and file a documentation-fix change before implementing behavior.

## Change responsibilities
Product behavior change:
ADR if required -> SPECIFICATION -> IMPLEMENTATION -> tests -> summaries.

Architecture change:
ADR -> ARCHITECTURE -> IMPLEMENTATION -> boundary tests.

Orca/API discovery:
research/audit -> ADR if behavior changes -> PLUGIN_REQUIREMENTS/IMPLEMENTATION.

Physical calibration finding:
ERROR_MODEL -> ADR if safety/semantics change -> SPECIFICATION/IMPLEMENTATION.

Roadmap never overrides a technical contract.

README never creates requirements.

## Coding-agent rule
Before starting a task, read:
1. accepted ADRs relevant to task;
2. SPECIFICATION;
3. ARCHITECTURE;
4. relevant IMPLEMENTATION section;
5. task-specific model/requirements docs.

Do not infer current behavior from historical/audit prose without checking higher-precedence documents.
