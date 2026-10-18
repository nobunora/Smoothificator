# Research Plan v2 graph, identity and shared publication

Prerequisite specification commit: 197fb5d. The implementation lead reviewed
the schema before source changes and corrected a planar-only loop restriction:
maximum_path_z_mm now retains nonplanar ZAA paths. Exact contract and review
disposition are in phase05-plan-v2.md and ADR-0067.

Implemented the complete eighteen-field research Plan graph, SurfaceBand and
typed region registry, loop chronology, per-segment support provenance, explicit
interpath transitions, and declared error/time/volume outcomes. Constructors
check canonical registry order, reference membership, source/settings identity,
nesting cycles, chronological lower-Z support, anchor intervals and transitions.
These checks validate declarations, not source topology or physical feasibility.

The application has an explicit Plan-v2-only projection and dedicated create/
verify APIs. Projected data is rebuilt and graph-validated before hashing. V1
bytes/constructors remain unchanged; new leaf DTOs still reject public standalone
semantic_tree projection. PlanStore publishes both envelope versions through
their verifier; v2 remains permanently non-injectable and never enters execution
selection. No second plan or mutable status store was created.

Windows Python 3.12.10: syntax and 41 architecture tests PASS; 14 focused graph
and 9 identity/store tests PASS. Independent implementation reviewer ran all
23 focused tests and reported PASS with no actionable finding. The independent
test-owned ADR-0062 encoder agrees with the production bytes and fixed fixture
digest 49c00d428a56c246f2ac5f8db69a1de1387eb78eaa1911c3845c68756c004399.
Full regression: 336 tests PASS. 83 canonical manifest blobs PASS.
Lint/type remain NOT CONFIGURED.

Phase 0.5 still needs its commit-lock interface and explicit B6 static diagnostic
contract. Actual I/O/matcher/TOCTOU validation belongs to Phase 4; no fake proof
issuer is supplied. No geometry engine, Orca adapter, G-code writer, printer
operation, security change or deletion outside C: was performed by this change.
The source-based Orca preview and cancellation limitations are documented in
orca-full-pipeline-api-review-2026-10-16.md. Full pipeline completion is not claimed.
