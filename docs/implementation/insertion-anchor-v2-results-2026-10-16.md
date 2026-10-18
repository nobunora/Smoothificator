# Standalone insertion anchor v2 implementation

Scope: the SPEC_VALIDATED phase05-insertion-anchor.md handoff and ADR-0067's
closed standalone vocabulary. Prerequisite specification commit: 3700568.
Full remaining work and completion conditions are in completion-plan-2026-10-16-ja.md.

Implemented a frozen/slotted eight-field InsertionAnchorV2 in the domain layer.
It rejects missing/extra fields, non-exact or blank strings, mutable/empty or
duplicate loop IDs, invalid layers, unsupported signature schema, and nonpositive
or nonfinite/overflow/subclass tolerance values. It preserves supplied loop order.

This is a vocabulary for later Plan v2 integration. It does not implement a
matcher, authorize a matching profile, verify snapshot membership or grant
injection authority. Canonical projection deliberately rejects it. V1 stays
unchanged. No dependency, Orca API, G-code or printer behavior changed.

Verification on isolated Windows Python 3.12.10:
- Syntax/import compilation: PASS.
- Architecture/import checks: 41 PASS.
- Focused anchor tests: 8 PASS.
- Full suite: 305 PASS, including existing v1 identity vectors.
- Canonical manifest: 83 blobs PASS for the new handoff.
- Independent implementation reviewer: PASS, no actionable findings;
  separately executed all 8 focused tests.
- Lint/type/dependency analyzers: NOT CONFIGURED per QUALITY_GATES; no new
  project dependency or suppression was introduced.

Specification and implementation are separate commits/PRs. Rollback consists of
reverting the standalone DTO/test addition; no persisted-data migration is needed.
Remaining: SurfaceBand/StructuralLoopReference v2 contracts, exact Plan v2
projection and provenance/travel intent, application-owned evidence validation,
then the geometry engine and Orca pipeline listed in the completion plan.
