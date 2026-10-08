# ADR-0049: Define canonical serialization and hashing bytes for Phase 0.5

Status: Accepted
Date: 2026-10-08

## Context

The project requires deterministic:
- SubEdgePlan hash / idempotence marker;
- ExecutionConfigFingerprint;
- PluginSettingsFingerprint;
- source geometry/config hashes.

Earlier documents required "canonical serialization" but did not define the canonical byte encoding.

Leaving JSON float formatting, dictionary ordering, negative zero, NumPy dtype/endian, or hash algorithm to the implementation agent can make semantically identical data produce different hashes across runs/platforms.

This is a direct Phase 0.5 contract and must be fixed before implementation.

## Decision

Use one canonical serialization owner: `adaptive_subedge/application/serialization.py`.

Use one hash owner: `adaptive_subedge/application/hashing.py`.

### Hash algorithm

All canonical identity digests use SHA-256.

External/user-facing plan hash is the lowercase 64-character hexadecimal SHA-256 digest.

Do not truncate the authoritative idempotence hash.

A shorter display id may be derived for UI only and MUST NOT be used for identity/safety decisions.

### Canonical object tree

Before byte encoding, convert supported domain values into a canonical tree containing only:
- null;
- bool;
- UTF-8 string;
- signed integer;
- canonical floating-point token;
- ordered list;
- string-keyed mapping.

Sets and unordered containers are forbidden at the serialization boundary unless converted by their owner to a deterministically sorted list with an explicit contract.

Enums serialize using their stable documented string value, never Python enum ordinal/name by accident.

### Mapping order

Mapping keys:
- must be strings;
- are sorted lexicographically by Unicode code point;
- duplicate keys are impossible/rejected.

### Integer encoding

Integers serialize as canonical base-10 text with:
- optional leading '-' only for negative values;
- no leading zeros except the value 0.

### Floating-point encoding

All plan/fingerprint floating values are finite IEEE-754 binary64 semantics.

Rules:
- NaN and +/-Inf are rejected before serialization;
- -0.0 is normalized to +0.0;
- finite values serialize as Python-compatible exact hexadecimal binary64 form equivalent to `float.hex()` after zero normalization;
- locale never participates.

Example tokens are strings tagged by the serializer schema, so a float token cannot collide with an ordinary user string.

### Text byte encoding

The canonical tree is encoded to UTF-8 using one versioned tagged grammar owned only by serialization.py.

No whitespace, pretty-printing, locale-dependent formatting, or platform newline participates in canonical bytes.

The exact encoder version is included in the canonical root as `canonical_encoding_version`.

### NumPy / array data

Large geometry arrays MUST NOT be serialized by arbitrary ndarray repr.

The owning adapter/application converts them into a canonical array digest:
- allowed semantic dtype is explicit;
- shape is included;
- integer geometry uses normalized signed 64-bit values;
- floating geometry uses normalized finite binary64 values;
- C-order logical element order;
- floating -0 normalized;
- array digest uses SHA-256 over a versioned type/shape/value stream.

SourceGeometryHash stores this canonical array digest plus the required transform/topology metadata.

### Dataclasses / DTOs

Serialization order is schema-defined, not Python `__dict__` order.

Only explicitly declared serializable fields participate.

Runtime-only fields such as:
- timestamps;
- AnalysisGenerationId;
- InjectionAttemptId;
- machine execution-frame translation;
- runtime execution status;
- final emitted E;
are excluded where the canonical plan contract says so.

### Plan identity

`plan_hash = sha256(canonical_plan_bytes)`.

Unless a later ADR requires a separate semantic id, `plan_id` SHOULD equal the authoritative full plan_hash or be a clearly derived display-only value. It MUST NOT introduce an independent random identity used for injection matching.

### Fingerprints

ExecutionConfigFingerprint and PluginSettingsFingerprint use:
- the same canonical scalar/tree encoding;
- explicit fingerprint schema/version;
- SHA-256.

Adding/removing/reinterpreting a fingerprint semantic requires a schema/version update and relevant compatibility review.

## Requirements / invariants introduced

- Same semantic input => byte-identical canonical serialization.
- Different runtime map insertion order => same hash.
- +0.0 and -0.0 => same canonical value.
- NaN/Inf => rejected.
- locale/platform/newline => no effect.
- no Python object repr participates in identity.
- one serializer/hashing owner.

## Alternatives considered

- Plain json.dumps on raw floats/ndarrays: rejected as insufficiently explicit.
- Pickle: rejected as non-portable/unsafe and implementation-dependent.
- External CBOR/MessagePack dependency: rejected for Phase 0.5; unnecessary dependency.
- Quantize all geometry to decimal micrometers before hashing: rejected because it could collapse semantically distinct high-precision plan values unless separately specified.

## Test impact

Add golden canonical-byte/hash fixtures for:
- reordered mappings;
- nested DTOs;
- +0.0 / -0.0 equivalence;
- smallest/large finite binary64 values;
- NaN/Inf rejection;
- enum stability;
- UTF-8 strings;
- array shape/dtype distinction;
- C/F-memory-layout logical equivalence;
- runtime-only field exclusion;
- plan hash reproducibility across fresh processes.

## Migration / rollout

Phase 0.5 implements this before any persisted/fixture plan hashes are relied upon.

## Rollback / disable condition

Unknown canonical encoding/schema version => do not compare/inject as if identities were equivalent.
