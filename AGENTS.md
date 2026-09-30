# AGENTS.md

Repository rules for human and AI implementation work.

Read this file first. Then read only the documents required by the current task.

## 1. Sources of truth

Operational/process rules:
1. AGENTS.md
2. docs/DOCUMENT_CONTRACT.md
3. task-specific .codex contract when supplied

Product/technical precedence is defined by docs/DOCUMENT_CONTRACT.md.

Accepted ADRs are authoritative within their scope. Do not silently override them in code.

## 2. Evidence-first repository work

- Start with repository metadata and changed-file lists.
- Search for the target symbol/path before opening broad files.
- Read targeted ranges when possible.
- Do not scan generated/cache/build/artifact directories for context.
- Treat unknown compatibility, firmware, Orca API, geometry, and G-code behavior as unknown until verified.
- External/Orca contracts that affect safety require source or fixture evidence.
- A graph/index/search result is routing evidence, not source-of-truth evidence.

If CodebaseMemory or an equivalent repository index is available, use it to route investigation, then confirm material claims from source/tests/runtime evidence. Do not require or rebuild such an index solely for a bounded verification task.

## 3. Change discipline

- One task, one purpose.
- Keep feature work, refactoring, formatting, and dependency upgrades separate.
- Make the smallest reviewable change that satisfies the approved specification.
- Preserve unrelated behavior and public/integration contracts.
- No opportunistic cleanup during verification or safety fixes.
- Do not leave debug code, commented-out implementations, temporary bypasses, or unfinished TODOs.
- Do not add dependencies unless the need, license, maintenance/security cost, runtime impact, and testability are understood and documented.
- Never weaken tests or safety gates merely to make a change pass.

## 4. Architecture and responsibility

Follow docs/ARCHITECTURE.md.

Hard rules:
- domain/engine code does not import Orca, UI, filesystem, or G-code adapters;
- Orca live objects terminate in orca_plugin/adapters/;
- G-code code executes immutable plans; it does not optimize geometry;
- UI consumes immutable plan/status data; it does not own policy;
- entrypoints/capabilities stay thin;
- one business/technical meaning has one authoritative owner;
- do not create generic manager/helper/service/utils dumping grounds;
- mutable state has one explicit owner;
- important dependency rules must have architecture/import tests.

Before moving a responsibility across boundaries, write/update an ADR if the move changes architecture or safety semantics.

## 5. Naming and units

Use project/domain vocabulary.

Prefer names that state:
- physical meaning;
- coordinate frame;
- units;
- scope/state.

For geometry/printing values, include units when ambiguity is plausible, e.g. z_mm, width_mm, flow_mm3_per_mm.

Avoid vague new names such as data, result, item, value, temp, payload, manager, helper, util, processor, service, or handler when a domain-specific name is possible.

Do not rename existing public/integration fields only for style.

## 6. Configuration and constants

- Do not scatter hard-coded printer/profile/safety values.
- Values fixed by design must be named constants and documented.
- Values that may change belong in validated Settings/config/profile data.
- Compatibility keys and external field names are contracts.
- Settings relevant to injection must participate in the configured fingerprint/validation contract.

## 7. Expected failures and exceptions

- Use typed expected failures/stable reason codes across boundaries.
- Do not broadly catch and silently discard exceptions.
- If an exception is intentionally ignored, catch the exact type and document why it is safe.
- Unexpected failures at injection boundaries must fail closed and preserve original G-code.
- Never convert uncertainty into successful injection.

## 8. Specification-to-implementation workflow

Implementation MUST follow the GitHub handoff workflow.

State flow:

DRAFT_SPEC
-> SPEC_REVIEW
-> SPEC_READY
-> REPOSITORY_REVIEW
-> SPEC_VALIDATED
-> IMPLEMENTATION
-> VERIFICATION
-> IMPLEMENTATION_REVIEW
-> READY_TO_MERGE

If repository evidence contradicts the specification:
- stop the affected implementation work;
- report the conflict;
- revise/adjudicate specification/ADR first;
- re-run repository review as needed.

Do not let an implementation agent silently redefine requirements.

Current system specification: docs/SPECIFICATION.md.
GitHub handoff specs live under docs/specs/.
Implementation review/task records live under docs/implementation/.

Specification work and production implementation should normally use separate branches/PRs.

## 9. Repository review before implementation

Before production implementation:
- read the approved specification and relevant Accepted ADRs;
- validate it against actual repository/Orca/plugin reality;
- trace affected interfaces, configuration, execution paths, tests, and external contracts;
- record disposition: validated, spec-change-required, or blocked;
- do not modify production code during the review-only pass.

Use .codex/repository-review.md when handing this phase to Codex.

Implementation may start only with disposition validated and no unresolved material conflict.

## 10. Implementation agent contract

Use .codex/implementation.md.

Before editing:
- confirm repository state still matches review assumptions;
- identify owning modules and forbidden dependencies;
- derive the smallest reviewable implementation step;
- identify focused tests and failure cases first.

Stop and return to specification adjudication if:
- the repository materially contradicts the validated spec;
- implementation needs an unapproved contract/schema/safety change;
- an external contract cannot be verified;
- affected scope materially expands.

## 11. Bounded verification mode

When the task is specifically verification/test/reproduction/reporting:
- treat the supplied implementation and acceptance criteria as the working contract;
- start from changed files/diff and directly relevant tests;
- use targeted symbol/search evidence;
- avoid rediscovering the whole architecture;
- do not broaden into refactoring or implementation without authorization.

Default extra source-read budget after changed files and directly relevant tests: 3 source/config files unless the task explicitly authorizes broader investigation.

If the root cause cannot be established within the authorized evidence boundary, report INCONCLUSIVE rather than guessing.

## 12. Quality audit order

Before broad tests, run applicable independent checks in this order:
1. environment/doctor checks;
2. syntax/import/package checks;
3. architecture/import-boundary checks;
4. lint/static diagnostics if configured;
5. type checks if configured;
6. dependency-use/license checks if configured;
7. focused tests;
8. broader regression/integration tests;
9. build/package check.

A missing tool is a configuration gap, not permission to add a dependency or suppress rules.

Record exact command, tool/version when material, exit status, and diagnostics.

See docs/QUALITY_GATES.md.

## 13. Testing rules

Test:
- normal cases;
- malformed/missing inputs;
- physical/numeric boundary values;
- regression cases;
- compatibility gates;
- cancellation/error paths;
- idempotence/atomicity;
- external/firmware/plugin failure paths.

Run nearest tests first.

Never claim a command/test ran if it did not. If it cannot run, state the reason and exact command a human should run.

Physical printing is a release-style gate: it may only occur after the required software/fixture gates in docs/TEST_STRATEGY.md pass for the exact target profile.

## 14. High-risk review and convergence

G-code mutation and physical printer behavior are high-risk changes.

Before first physical-print enablement and before production release:
- perform normal implementation review;
- perform an independent blind review using docs/REVIEW_PROCESS.md;
- reconcile findings only after the blind report is complete;
- require no unresolved Critical or High findings;
- require every confirmed finding to have a disposition;
- require specification/source agreement and required checks to pass.

A clean test suite or "no issues found" alone is not convergence.

## 15. Review findings

Material findings include:
- severity;
- location;
- affected behavior;
- evidence;
- violated requirement/invariant;
- concrete failure scenario;
- remediation direction;
- confidence.

Allowed dispositions:
confirmed, rejected, duplicate, superseded, accepted-risk, requires-further-evidence.

## 16. File/function cohesion

- Prefer one main responsibility per file/function.
- Keep entrypoints thin.
- Do not add abstractions for hypothetical future needs.
- Split modules because responsibilities differ, not to reduce line count.
- Target focused, reviewable files; docs/ARCHITECTURE.md contains project size/cohesion guidance.

## 17. Scripts and repeatable commands

Prefer stable repository scripts over ad hoc command sequences once tooling exists.

Reserved intent names:
- doctor: environment check
- check: quick verification
- typecheck: static typing
- test: main tests
- build: package/build
- refactor:check: serial refactor gate
- release:check: serial release gate

Do not create scripts until their toolchain/contract is actually used.

## 18. Records and reports

For each implementation milestone or risky gate, record:
- changed files;
- why;
- exact checks/commands;
- results;
- limitations;
- risks;
- next step.

Use docs/implementation/ for task evidence and docs/records/ for concise chronological milestone notes.

Final implementation reports should include:
- change summary;
- design intent;
- alignment with approved spec;
- alternatives rejected;
- files changed;
- scope not changed;
- checks/results;
- human-confirmation points;
- remaining risks;
- explicit behavior changes and rollback implications.

## 19. Commit/diff discipline

- One commit should express one coherent sentence/purpose.
- Separate behavior changes from refactors when practical.
- Avoid formatting churn.
- Keep generated artifacts separate and last when they are intentionally tracked.
- Inspect the final diff and affected execution paths before declaring completion.

## 20. Security and secrets

- Do not put secrets, API keys, credentials, private payloads, or sensitive raw logs into code, prompts, fixtures, comments, or reports.
- Use least privilege for automation.
- Do not run write-capable model automation on untrusted fork code with repository secrets.
- Treat external URLs/files/plugin inputs as untrusted at their boundary.

## 21. Read next

For implementation:
1. docs/DOCUMENT_CONTRACT.md
2. relevant docs/specs handoff specification
3. docs/SPECIFICATION.md
4. relevant Accepted ADRs
5. docs/ARCHITECTURE.md
6. relevant docs/IMPLEMENTATION.md sections
7. docs/TEST_STRATEGY.md
8. task-specific implementation record

For repository review use .codex/repository-review.md.
For implementation use .codex/implementation.md.
For independent high-risk review use docs/REVIEW_PROCESS.md.
