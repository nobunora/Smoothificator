# Standalone insertion anchor v2 handoff

Scope: ADR-0067's Closed standalone insertion-anchor vocabulary section only.
Canonical sources: docs/adr/0067-phase05-domain-dto-and-attempt-snapshot-contract-proposal.md,
docs/IMPLEMENTATION.md, docs/ARCHITECTURE.md and docs/DOCUMENT_CONTRACT.md.
Manifest: docs/AUDIT_REVISION_2026-10-16.json.
Manifest Git blob: `89ac5da0ca70561ea47496e1e2f5265b4abbf913`

Repository review: independent reviewer traced B2 and current geometry/plan and
serializer/hash boundaries. The standalone vocabulary has no dependency on a
live Orca object, algorithm, new dependency, or physical default. The review
identified two decisions: opaque schema literal and deferred canonical projection.
The owning ADR now records both explicitly. Independent final recheck disposition:
validated (SPEC_VALIDATED for this standalone DTO only), 2026-10-16. The reviewer
confirmed B2 agreement, exact field validation, deferred registration and retained
analysis-owner membership proof. No material finding remains in this slice.

Acceptance: exact required fields, frozen/slots, malformed/blank/subclass/duplicate
input rejection, finite positive tolerance, unknown schema rejection, canonical
projection rejection, unchanged v1 vectors. No source, loop, interval, profile,
or geometric proof is implied. Full Plan v2 and matcher remain excluded.
