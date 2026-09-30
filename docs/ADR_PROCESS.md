# Architecture Decision Record (ADR) Process

## Purpose
Prevent implementation convenience from silently changing safety or architecture.

Create docs/adr/NNNN-title.md when a change:
- changes module responsibility/dependency direction
- changes SubEdgePlan schema
- changes G-code safety/atomicity
- relaxes supported geometry/state gates
- changes Orca hook usage
- changes preview/injection identity contract
- introduces native/custom Orca dependency
- changes minimum Z safety semantics

ADR template:

# ADR-NNNN: Title
Status: Proposed | Accepted | Superseded
Date:

Context:
Evidence / source contract:
Decision:
Requirements / invariants introduced:
Alternatives considered:
Safety impact:
Compatibility impact:
Performance / resource impact:
Observability impact:
Test / validation impact:
Migration / rollout:
Rollback / disable condition:
Open questions:
Supersedes:

Implementation MUST NOT precede Accepted status for safety/architecture changes.


## Identifier and lifecycle rules

- ADR numbers are repository-global and MUST be unique.
- Never create a second file with an existing ADR number.
- Next ADR number is one greater than the highest existing canonical ADR.
- Accepted ADR content MUST NOT be silently repurposed.
- If a decision changes materially, create a new ADR and mark the prior ADR Superseded with an explicit reference.
- File deletion of an Accepted ADR is allowed only to remove an accidental duplicate whose decision is already represented by the retained canonical ADR set; document that cleanup in DEPENDENCY_AUDIT.md.
- CI/document checks MUST fail on duplicate ADR numbers.

## Source-evidence rule

When an ADR depends on Orca implementation details, record:
- source file/function;
- observed behavior;
- tested/audited Orca commit or version where practical.

If later Orca source contradicts an Accepted ADR assumption, stop implementation for the affected area and create a superseding ADR before code changes.


## Review rule

Before accepting a high-risk ADR, verify:
- authoritative owner is clear;
- non-ownership is clear;
- inputs/outputs/units are explicit;
- failure and rollback behavior are explicit;
- implementation can be validated deterministically;
- the decision does not introduce a second policy owner;
- physical/G-code safety impact has an evidence plan.

For hardware/G-code safety semantics, an Accepted ADR should receive independent review before the implementation gate it controls is enabled.
