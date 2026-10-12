# Repository Review Contract

Review the repository against the supplied handoff specification before implementation.

Handoff specification: `<spec-path>`
Canonical specification revision: `<sha>`

## Required procedure

1. Read `AGENTS.md`.
2. Read the handoff specification and its canonical references.
3. Read relevant Accepted ADRs.
4. Use targeted repository search; do not scan unrelated files.
5. Trace affected interfaces, dependency boundaries, tests, config, Orca/plugin contracts, G-code/profile contracts, and packaging paths.
6. Compare repository reality with every material requirement and acceptance criterion.
7. Use deterministic evidence where available.
8. Do NOT modify production source, tests, configuration, specification, or ADRs in this review-only pass.

## Required output

Record:
- disposition: `validated`, `spec-change-required`, or `blocked`;
- affected paths and why;
- existing contracts/invariants;
- repository/API conflicts or missing constraints;
- missing tests/fixtures/tooling evidence;
- proposed implementation boundary;
- exact evidence for material findings;
- commands/checks run;
- files read beyond the primary task packet when relevant;
- unresolved questions;
- smallest recommended next action.

Do not silently resolve a specification conflict in implementation terms.

If material evidence requires broader investigation than the task authorizes, report the exact symbols/files needed next rather than guessing.
