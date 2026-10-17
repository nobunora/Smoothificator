# Phase 1C planned-path numerical regularity gate

Status: SPEC_VALIDATED for bounded numerical path regularity.

Independent implementation-lead review checked existing SubEdgePath/segment and
policy semantics and ADR-0063's strict plan-time length versus inclusive time/step
limits. The two-pass failure order, new evaluator version and preserved legacy
DTO/hash behavior are consistent; no material conflict remains. Independent schema
review confirmed this scope cannot verify physical evidence or full bead bounds.

Authority: ADR-0063 Closed planned-path numerical regularity gate owns the exact
API, result matrix, policy version, arithmetic and cancellation precedence.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `7e96ba2c2f77717503fcee1e22e8c6de3ba3501e`

Implement domain/path_regularity.py and engine/path_regularity.py. Reuse existing
SubEdgePath/SubEdgeSegment and CandidateSegmentRegularityPolicy without modifying
their constructors or canonical serialization. Only the evaluator recognizes
planned_segment_regularity_v1. No physical defaults or dependencies.

Tests: exact squared-length threshold equality rejects; next representable valid
length passes; exact execution-time equality passes; exact adjacent Q/width/height
limits pass and exceedance rejects the correct pair. Include nonuniform speeds,
normalization-collapsed segments, huge/tiny normalized values, two-pass precedence,
single-segment paths and endpoints. A closed path must not be rejected by this
gate merely for closure, nor receive an implicit last-first comparison.

Check malformed types/versions and count-budget precedence. Exercise cancellation
before each expected failure return and success; cancellation removes offending
indices. Test shape-only result construction, unchanged v1 bytes and nonmutation.
No nonempty fixture reference may be promoted to verified physical evidence.

This is one numerical candidate-admission prerequisite. Openness/seam policy,
bead geometry/flow bounds, support, error, calibration and final emitted execution
checks remain separate obligations; complete/regular does not authorize a Plan.
