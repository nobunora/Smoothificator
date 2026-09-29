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
Decision:
Alternatives considered:
Safety impact:
Compatibility impact:
Test impact:
Migration:
Supersedes:

Implementation MUST NOT precede Accepted status for safety/architecture changes.
