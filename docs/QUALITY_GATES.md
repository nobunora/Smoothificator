# Quality Gates

This document adapts the project-template quality-audit rules to this Python/Orca plugin project.

## 1. Principle
Passing tests are evidence, not proof.

Independent structural/static checks should run before broad behavioral tests so architecture or typing defects are not hidden by happy-path tests.

## 2. Gate order

Use the narrowest applicable checks first:

1. Environment / runtime compatibility
2. Python syntax/import/package validation
3. Architecture/import-boundary validation
4. Lint/static diagnostics, once a project tool is selected
5. Type checking, once a project tool is selected
6. Dependency-use/license/security review for dependency changes
7. Focused unit tests
8. Integration/golden-fixture tests
9. Full regression suite
10. Wheel/package build
11. Physical printer gate, only when docs/TEST_STRATEGY.md permits it

Run conflicting watchers/dev servers serially.

## 3. Phase 0.5 tooling rule

Do not add Ruff, mypy/pyright, dependency analyzers, or other tooling merely because this document names their categories.

During Phase 0.5:
- inspect the actual package structure/runtime;
- choose the smallest useful toolchain;
- document versions/configuration;
- justify any new dependency;
- add deterministic repository scripts only after the command contract is known.

Until a tool is configured, report that category as NOT CONFIGURED rather than pretending it passed.

## 4. Diagnostic triage

Every diagnostic is classified as one of:
- verified defect;
- safe cleanup in current scope;
- deliberate compatibility/boundary behavior;
- tooling/configuration gap;
- pre-existing advisory debt;
- insufficient evidence.

Do not:
- bulk auto-fix unrelated diagnostics;
- weaken a rule to hide a current defect;
- add suppression without evidence;
- add a dependency just to make a report look clean.

Fix verified defects in scope, then rerun the exact failing check first.

## 5. Architecture checks

At minimum enforce:
- domain/engine cannot import orca_plugin;
- engine cannot import G-code modules;
- UI cannot import optimizer/live Orca adapter modules;
- G-code injector cannot import optimizer/source-mesh algorithms;
- duplicate ADR identifiers fail;
- forbidden cyclic dependencies fail.

Architecture tests are distinct from behavioral tests.

## 6. Type/runtime checks

Run type checks with the same project interpreter/environment used for plugin development.

The currently audited Orca plugin examples use Python >=3.12 and NumPy. The actual Phase 0.5 environment must verify this assumption before packaging metadata is finalized.

Do not confuse package distribution names with Python import names when checking dependency use.

## 7. Dependency changes

Before adding a dependency record:
- why standard library/current dependencies are insufficient;
- maintenance activity;
- license compatibility with GPLv3 project;
- known security risk;
- wheel/platform availability for Orca's embedded Python;
- runtime/package size impact;
- testability and fallback behavior.

Dependency additions are separate reviewable changes where practical.

## 8. G-code/fixture gate

For every supported Orca/printer/profile family:
- exact version/commit/profile metadata is recorded;
- source fixture is retained;
- parser-state expectations are explicit;
- expected output is deterministic;
- failure fixtures exist;
- config fingerprint keys are verified;
- execution-frame mapping is validated.

No fixture => analysis-only mode.

## 9. Reporting

For each gate record:
- command;
- tool/version when relevant;
- exit status;
- concise diagnostics;
- PASS / FAIL / NOT CONFIGURED / BLOCKED;
- whether failure is caused by current change or environment/pre-existing debt.

Never claim a gate passed without execution evidence.
