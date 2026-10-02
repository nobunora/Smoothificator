# ADR-0031: Preserve original G-code bytes and line endings during streaming injection

Status: Accepted
Date: 2026-09-30

## Context

The postprocessor is intended to leave valid Orca output unchanged except for explicit Adaptive Sub-Edge insertion blocks.

Opening the whole file in text mode with replacement decoding or universal-newline translation can change:
- CRLF versus LF;
- non-ASCII/unknown bytes;
- malformed-but-preserved comments;
- final newline behavior.

That violates the all-or-nothing / unrelated-bytes-preserved contract and makes regression diffs less trustworthy.

## Decision

The v1 parser/emitter operates on the working G-code as a **binary line stream**.

### Parsing

- preserve each original raw line as bytes;
- parse only the ASCII-compatible G-code/token/comment subset required by the supported fixture;
- do not decode with errors=replace;
- unsupported non-ASCII content that affects command interpretation fails closed;
- opaque comment bytes that do not affect parsing may be preserved unchanged.

### Emission

- copy every original raw byte sequence unchanged and in order;
- add only explicit Adaptive Sub-Edge marker/command bytes at validated anchors;
- use the validated local newline convention from the anchor/file (LF or CRLF);
- never normalize the rest of the file.

### Temp file / replacement

- temp output is created in the same directory;
- copy/preserve original file mode/permissions required by the platform workflow;
- fsync/flush behavior is defined by AtomicWriter before replace where supported;
- atomic replace occurs only after sanity validation.

The sanity parser validates inserted blocks while still treating untouched original bytes as authoritative.

## Requirements / invariants introduced

- "original unchanged on failure" means byte-for-byte unchanged.
- successful output differs only by planned insertion byte ranges and any explicitly documented metadata effect.
- newline style is deterministic and fixture-tested.
- parser and emitter must not depend on locale/default text encoding.

## Alternatives considered

- UTF-8 text mode with errors=replace: rejected.
- Read/write all lines through Python text IO: rejected because newline normalization may occur.
- Normalize entire output deliberately: rejected as unrelated mutation.

## Safety impact

Medium for printer behavior, high for reproducibility and trustworthy diff validation.

## Compatibility impact

Requires binary-safe parser implementation.

## Performance / resource impact

Compatible with bounded-memory streaming.

## Observability impact

Record detected newline convention and original/temp file byte counts/hash summaries, not raw contents.

## Test / validation impact

Add:
- LF fixture;
- CRLF fixture;
- no-final-newline fixture;
- opaque non-ASCII comment bytes preserved;
- unsupported non-ASCII command token rejection;
- byte-identical failure paths;
- successful output diff contains only insertion block.

## Migration / rollout

Implement binary line handling from the first parser/injector version.

## Rollback / disable condition

If a platform/filesystem prevents verified atomic replacement semantics, injection is disabled for that environment until explicitly supported.

## Open questions

Platform-specific fsync/rename semantics are finalized in Phase 4F fixture tests.

Supersedes: any text-mode postprocessor assumption.
