# Phase 0.5 Settings v2 implementation handoff

Status: SPEC_VALIDATED for this Settings-only slice; review evidence is
`docs/implementation/settings-v2-readiness-2026-10-16.md`. Not merge/release approval.

## Canonical Contract

ADR-0066's normative schema decision and initial research version registry own
this slice. ADR-0062/0064 own unchanged canonical bytes and identity projection.
The canonical manifest is `docs/AUDIT_REVISION_2026-10-16.json`; its blob SHA is
`09296e1337d783a210aabdff59750eb59aef6282`.

Manifest Git blob: `6daab8f3e35a03cc0cbc7bdda20dbe096d78950b` No historical manifest authorizes this
slice. An integrity check is not specification approval.

## Goal

Implement the complete research-only PluginSettingsV2 and its distinct
plugin-settings schema 2 fingerprint, preserving v1 exactly.

## Scope

- New frozen Settings DTOs in domain; reuse existing policy fragments unchanged.
- Explicit whitelisted projection in the existing application serializer.
- Version-aware plugin-settings hashing and typed identity comparison.
- V1 Plan remains v1 and rejects v2 Settings references.
- Boundary, completeness, independent canonical-vector and v1-regression tests.

## Non-goals

Plan v2, SurfaceBand/loop/anchor augmentation, Attempt evidence/history, live
Orca adapters, geometry, optimization, numeric time prediction, G-code mutation,
printing, merging and release. Missing Plan v2 contracts do not become implicit
choices in this slice.

## Requirements / Invariants

All 17 declared top-level fields in ADR-0066 are required, including explicit
None for a missing research ToolClearanceProfile and explicit false for physical
injection. Exact nested DTO classes are required. The shared finite-binary64
numeric contract may accept builtin integer inputs where exactly the existing
float-field projection converts to binary64; bool/nonfinite/overflow reject.
Directional weights may not both be zero. All new version strings use the ADR
registry. Legacy fragment validators remain unchanged. No defaults or migration.

Only plugin-settings gains root schema 2. Its payload schema marker must also be
2; raw mappings, wrong DTO versions and unsupported root/payload combinations
reject. The existing root grammar, SHA domain and v1 payload registry stay
unchanged. IdentityReference remains a vocabulary type; supported-version
acceptance belongs to application identity operations. Comparing unlike versions
must reject, never compare raw digest strings. A typed v2 identity alone is not
a valid v1 Plan reference. No field may be omitted from the explicit projection.

The initial time-model registry value is unavailable_v1; Settings validity does
not imply an AVAILABLE estimate or a fully ranked/printable plan.

## Acceptance Criteria

- Complete frozen Settings v2, deterministic full-field fingerprint.
- All existing v1 canonical/golden tests unchanged and passing.
- Independent v2 byte/digest vector, root/payload mismatch rejection.
- Every mutable leaf in a valid synthetic Settings fixture changes its v2
  fingerprint; version/literal-only fields reject unknown values instead.
- Unknown/missing fields, malformed nested values, numeric boundaries and
  physical_injection_requested=true fail closed.
- Neither v1 Plan construction nor legacy runtime behavior accepts v2 by accident.
- No unresolved material finding in this bounded slice; review disposition must
  be recorded separately before source edits.

## Validation

Use the existing isolated Python 3.12 environment, syntax/import checks,
architecture tests, focused v2/v1 identity tests, full regression and build
verification. Run Windows CI at the exact source SHA. Lint/type tools remain
NOT CONFIGURED; no dependency addition. Document integrity checks validate Git
blobs, not algorithm soundness or independent review status.

## Risks / Rollback

The primary risks are admitting schema 2 for unrelated identities and silently
changing v1 canonical bytes. Keep the patch bounded and reversible; no stored
v1 values are upgraded and no printer/file mutation occurs. Plan v2 and runtime
verifier readiness require separate handoffs and review.
