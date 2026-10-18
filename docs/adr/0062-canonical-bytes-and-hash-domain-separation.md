# ADR-0062: Define exact canonical bytes, array endianness, and hash domain separation

Status: Accepted
Date: 2026-10-08

## Context

ADR-0049 correctly requires deterministic canonical serialization and SHA-256, but two details remain underspecified for Phase 0.5:

1. canonical array digests do not explicitly fix integer/float byte endianness and binary framing;
2. plan/config/settings/source digests use the same hash algorithm without an explicit cryptographic domain prefix.

If an implementation hashes native-endian ndarray bytes, semantically identical arrays can hash differently across architectures.

Without domain separation, different identity classes can theoretically produce the same canonical payload and therefore the same digest even though their semantic types differ.

## Decision

ADR-0049 remains the semantic owner of canonical serialization. This ADR fixes the exact byte-level framing required by the first implementation.

### Hash domain separation

Every authoritative digest is computed as:

SHA256( magic || 0x00 || domain_tag || 0x00 || canonical_payload )

where:
- magic is the exact ASCII byte string `AdaptiveSubEdgeCanonicalV1`;
- domain_tag is one exact ASCII identifier owned by the schema;
- canonical_payload is the canonical byte encoding for that identity.

Initial required domain tags:
- `plan`;
- `execution-config`;
- `plugin-settings`;
- `source-geometry`;
- `array` for nested canonical array digests, further qualified by the array semantic-type header.

Digest comparison MUST also check the expected identity type/schema; code must not compare arbitrary 64-hex values without typed context.

### Canonical scalar/tree grammar

Use one exact byte grammar.

Primitive tags are one ASCII byte:
- null: `n`;
- false: `b0`;
- true: `b1`;
- integer: `i` + canonical ASCII base-10 integer + `;`;
- float: `f` + canonical ASCII `float.hex()` token after -0 normalization + `;`;
- string: `s` + canonical ASCII decimal UTF-8 byte length + `:` + raw UTF-8 bytes.

Container encoding:
- list: `l` + decimal element count + `[` + encoded elements in order + `]`;
- mapping: `m` + decimal pair count + `{` + encoded string-key/value pairs in lexicographically sorted key order + `}`.

Counts/lengths use canonical non-negative base-10 ASCII with no leading zero except 0.

Strings are encoded exactly as supplied UTF-8 code points. No implicit Unicode NFC/NFD normalization occurs. If a field requires normalized Unicode, its owning schema must do so explicitly before serialization.

NaN and +/-Inf remain forbidden.

### Canonical array digest framing

Canonical array payload begins with exact ASCII header:

`ASE_ARRAY_V1`

followed by 0x00 and the semantic dtype tag.

Initial semantic dtype tags:
- `i64`;
- `f64`.

Then encode:
1. rank as unsigned 32-bit big-endian;
2. each dimension as unsigned 64-bit big-endian;
3. element values in C logical order.

Element encoding:

#### i64
- every value must fit signed 64-bit;
- encode two's-complement signed 64-bit in big-endian byte order.

#### f64
- convert to IEEE-754 binary64 semantic value;
- reject NaN/Inf;
- normalize -0.0 to +0.0;
- encode the resulting 64-bit IEEE-754 bit pattern in big-endian byte order.

Do NOT hash native ndarray raw bytes directly.

C-contiguous and F-contiguous arrays with the same logical shape/values therefore produce identical canonical array payloads.

The canonical array digest is:

SHA256( magic || 0x00 || `array` || 0x00 || array_payload )

and the parent canonical tree stores the array's semantic dtype, shape, and full 32-byte digest token under the versioned array schema.

### Root type/schema

Every top-level canonical identity root explicitly contains:
- identity type;
- schema version;
- canonical encoding version.

Unknown type/schema/encoding versions are never treated as equivalent.

### Serializer strictness

The serializer rejects:
- undeclared object/DTO types;
- undeclared fields when strict schema validation applies;
- missing required serializable fields;
- unordered containers not normalized by their owner;
- unsupported numeric dtypes;
- native-endian/raw-memory shortcuts.

## Requirements / invariants introduced

- Canonical hashes are independent of CPU byte order.
- Canonical arrays are independent of NumPy memory layout.
- Identity classes are cryptographically domain-separated.
- Typed identity comparison accompanies digest comparison.
- Exact byte fixtures are stable across processes/platforms implementing the contract.

## Alternatives considered

- Native ndarray.tobytes(): rejected due endianness/layout ambiguity.
- JSON canonicalization: rejected for floating/array contract complexity.
- Rely on schema root without hash domain prefix: workable but weaker and easier to misuse.
- Little-endian canonical bytes: possible, but big-endian network order is chosen explicitly; either would work if fixed.

## Safety / identity impact

High for Phase 0.5 plan/fingerprint determinism and idempotence identity.

## Compatibility impact

Changes canonical digest fixtures before implementation begins; no production hashes require migration.

## Performance / resource impact

Streaming array hashing is allowed; implementations need not materialize a second full byte copy.

## Observability impact

Diagnostic output may show identity type/schema plus shortened display digest, but authoritative comparison uses full SHA-256.

## Test / validation impact

Add golden byte/digest fixtures for:
- little-endian vs big-endian source arrays with same semantic values;
- C-order vs F-order memory layouts;
- i64 min/max;
- f64 +0/-0 equivalence;
- representative subnormal/normal finite floats;
- exact tree grammar bytes;
- different domains with identical canonical payload -> different digest;
- missing/unknown schema/type rejection;
- Unicode exact-code-point behavior.

At least one fixture should be independently reproduced outside the production serializer implementation.

## Migration / rollout

ADR-0049 remains authoritative except where this ADR specifies exact byte framing/domain separation.

Phase 0.5 MUST implement this contract before plan/fingerprint hashes are relied upon.

## Rollback / disable condition

Unknown/unsupported canonical encoding or identity domain => do not compare/inject as equivalent.

## Open questions

None for Phase 0.5.