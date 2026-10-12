# ADR-0064: Construct plan identities without self-reference and fix nested-array tokens

Status: Accepted
Date: 2026-10-13

## Context

ADR-0049/0062 require exact canonical bytes and domain-separated SHA-256. The immutable `SubEdgePlan` DTO also exposes `plan_id/hash`. Serializing a plan hash inside the bytes from which that same hash is derived would create an identity cycle.

ADR-0062 defines a 32-byte canonical array digest in the parent tree but the canonical tree grammar has no raw-bytes scalar. A platform-independent, uniquely typed tree representation must be fixed before Phase 0.5 fixtures are implemented.

## Decision

### Canonical content versus derived identity

- `SubEdgePlan` has an immutable, versioned semantic **identity content** projection separate from derived `plan_hash` / `plan_id` fields.
- The plan identity root uses the ADR-0062 canonical tagged-tree grammar and has exactly these string keys: `identity_type`, `schema_version`, `canonical_encoding_version`, `payload`.
- For the plan root, `identity_type` is `subedge-plan`; `schema_version` and `canonical_encoding_version` are explicit versioned string values, never implicit implementation defaults.
- The `payload` contains only explicitly declared semantic plan fields in a stable schema. It MUST include referenced source-geometry/config/plugin-settings typed identities, immutable candidate paths/segments, seam/gap, support/order, anchors, injectability/reasons and metrics as required by their schema.
- The `payload` MUST exclude `plan_hash`, `plan_id`, `AnalysisGenerationId`, `InjectionAttemptId`, time stamps, mutable status, final machine mapping, final emitted E and nondeterministic runtime objects.
- Compute `plan_hash = SHA256(magic || 0x00 || "plan" || 0x00 || canonical_plan_identity_root_bytes)` exactly as ADR-0062 requires. ADR-0049's earlier unprefixed shorthand is superseded **only for the hash preimage**.
- `plan_id` is the same full authoritative plan hash; UI-only shortened IDs may be derived but must not participate in matching or identity.
- Construct the semantic content and canonical bytes first, compute hash second, then publish the frozen plan. Recomputing identity from the semantic projection MUST reproduce the stored hash. A mismatched supplied hash/ID is rejected; do not repair silently.
- Fingerprints/source-geometry identities use their separate ADR-0062 domain tags and an explicitly typed versioned root. No cross-domain hash comparison is permitted.

### Nested canonical array token

Where a declared identity schema uses a canonical array digest as a tree value, encode it as an ordinary string-keyed mapping with **exactly**:
- `array_schema_version`: string `ASE_ARRAY_V1`;
- `dtype`: string `i64` or `f64`;
- `shape`: ordered list of non-negative integer dimensions;
- `digest_hex`: 64-character lowercase ASCII hexadecimal SHA-256 of the exact ADR-0062 domain-separated binary array payload.

Raw digest bytes are not inserted into the tagged tree. Rank is the length of `shape`; validate rank/dimensions against ADR-0062's fixed binary framing and bounds. Unknown schema/dtype, malformed digest, inconsistent shape, or noncanonical representation is rejected.

This is the typed **tree token** for an array already hashed under the `array` domain. It does not alter the binary array payload, semantic dtype conversion, big-endian requirement, or C-logical ordering in ADR-0062.

## Ownership

`adaptive_subedge/application/serialization.py` exclusively owns the plan identity projection, root field ordering by canonical map rules, and nested array token formation. `adaptive_subedge/application/hashing.py` exclusively owns domain-separated digest computation and typed digest comparison. Domain DTOs contain no independent hash implementation.

## Tests and acceptance

Phase 0.5 MUST cover:
1. plan semantic bytes independent of `plan_id/hash` construction (no self-reference);
2. hash/plan_id equality and supplied-ID mismatch rejection;
3. identity changes when a semantic candidate/order/anchor/config field changes;
4. generation/runtime/machine-E/status fields excluded;
5. nested array token's exact four fields, lowercase 64-hex digest and dtype/shape;
6. same semantic array across endianness and C/F layouts yields same token;
7. independently computed golden byte/hash vectors including domain prefixes;
8. invalid root keys/type/schema/encoding and unknown array token versions fail closed.

## Supersession

Refines ADR-0049 and ADR-0062 only at the identified identity-construction and nested-array-tree representation gaps. Their other requirements remain authoritative.
