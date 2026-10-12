# Implementation Contract

Implement a validated Adaptive Sub-Edge specification against the actual repository.

Handoff specification: `<spec-path>`
Canonical specification revision: `<sha>`
Implementation record: `<implementation-record-path>`

## Preconditions

- `AGENTS.md` has been read.
- Repository-review disposition is `validated`.
- No material specification/ADR conflict is unresolved.
- Current branch/repository state still matches the review assumptions.

If any precondition is false, stop and report the blocker.

## Required procedure

1. Confirm the exact specification/ADR revisions.
2. Identify owning modules and forbidden dependencies.
3. Derive the smallest reviewable implementation step.
4. Add/adjust focused tests with behavior changes.
5. Keep changes inside approved scope.
6. Preserve unrelated behavior and public/integration contracts.
7. Run quality checks in `docs/QUALITY_GATES.md`.
8. Run focused tests first, then broader tests according to risk.
9. Inspect final diff AND affected execution paths.
10. Update the implementation record with exact evidence.

## Stop conditions

Stop and return to specification adjudication if:
- repository/Orca reality contradicts the validated contract;
- an unapproved schema/API/config/safety change is needed;
- a required external contract cannot be verified;
- the affected surface materially expands;
- a safety gate would need to be weakened;
- a dependency is required but not approved/justified.

## High-risk rule

Do not enable physical printer injection merely because unit/integration tests pass.

The physical gate requires:
- all preceding `docs/TEST_STRATEGY.md` gates;
- exact supported fixture/profile;
- required independent review in `docs/REVIEW_PROCESS.md`.

## Required final report

Report:
- changed files and reasons;
- specification criteria satisfied;
- exact checks and outcomes;
- behavior/contract changes, if any;
- scope explicitly not changed;
- residual risks;
- unresolved questions;
- whether ready for independent review.
