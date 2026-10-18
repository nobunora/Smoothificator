# Exact-debt source derivation independent blind review — 2026-10-18

Disposition: **no material finding established within the frozen pure derivation/publication scope**. This is a bounded negative review, not physical approval or whole-job acceptance. Parent primary implementation conclusions were not consulted before this report.

Reviewed amended `docs/specs/exact-debt-source-derivation-review.md`, its validated repository review, full `tools/derive_exact_debt_source.py`, directly relevant tests and the explicitly pinned actual-family construction. Existing conditional body and strict arithmetic owners were inspected only as necessary. CURRENT compiler integration was not reviewed or executed in this stage.

Frozen owner SHA256: `5e889c968903932a9e63720143f29223bf325226fe4de9cb566d842012962a2c`; focused test SHA256: `89014b0e925d980057cf4d6aa839d71472769ede633e4e5ce71f273fcd898bb9`. Both still match after verification. No reusable source/test edits or baseline overwrites were made.

## Independent checks

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_exact_debt_source_derivation -v` — PASS,7 tests,8.683 seconds, Python3.12.10. This includes exact no-op, under/surplus wipe chains, malformed/profile/checksum/precision/resource/cancel rejection, reviewed-family sequence/pin failures, fresh writer forged/stale/no-overwrite failures, ZIP metadata preservation and actual106-restore reproduction.

Additional read-only Python stdin probes independently reconstructed actual inputs and reviewed family, derived source/project, replayed both bodies and asserted:

- Exactly48 source lines change. For all106 restore entries, replacing only the respective numeric E token by the same sentinel makes old/new complete raw lines byte-identical. Every other line, including metadata, is unchanged.
- All14985 positive moving events retain identical ordered before/after XYZ, raw E, feed, feature and complete raw command bytes. Width/height metadata cannot change because every metadata/comment line remains byte-identical. Body reconstruction independently succeeds with new descriptor/motion source identities.
- Derived source SHA `2aa69c3ebabc86442456486ee616d3caac2e30850142e670cd8d77937779f374`; derived project SHA `ea5639da549ddc8d4f49029b46561164c4edfa292885cb5e05c4753903a4c1c0`, matching the corrected research result.
- ZIP member names/order match; full CRC test passes; only embedded G-code and its required uppercase MD5 change. Independently checked timestamps, comments, extras, compression, internal/external attributes, create/extract versions/system, reserved and volume fields. All18 allowed flag changes are enumerated. Fresh MD5 is computed from the derived source, not copied from a receipt.
- Nonzero ordinary extra, nonzero filament ordinary extra, nonzero filament toolchange extra and firmware-retraction configurations reject. Duplicate E, unsupported positive-restore parameter and source/project/uncompressed-byte limits reject.

The first ad hoc actual-tuple probe referred to nonexistent event width/height attributes and stopped with AttributeError before assertions; corrected probe uses actual immutable event fields plus exact metadata/raw-byte preservation and passes. No failed probe was counted as verification.

## Negative review coverage

Admission is explicitly a finite externally reviewed family. Source/project/producer pins, ordered complete restore entries, raw hashes, scope occurrence, original debt and complete negative-chain hashes/amounts are freshly compared. The actual-family builder pins the complete research evidence bytes. These DTOs are an explicit caller-supplied admission premise, not a cryptographic review-signature system and not permission to infer ordinary intent from arbitrary matching command text. A newly asserted family needs its own review.

Profile resolution rejects unresolved/nonzero extra-prime and unsupported firmware retraction. Positive restores require the supported E/F-only form, saved amount/speed, actual object scope and known positive debt. Negative E is tied to supported ordinary or explicit wipe roles; ambiguous or incomplete chains reject. Arithmetic advances NEW state sequentially and checks fresh replay; G92 is not used to erase debt. Exact already-correct commands stay byte-identical. The actual final logical-E delta is explicitly −0.00007 mm, with final debt0.79999 retained.

Original checksum association, duplicate entries, supported flags/compression and bounded archive sizes are checked before cloning. Dependent checksum filenames outside the supported MD5 reject; the reviewed pinned archive is the supported dependency family. This is not a generic semantic validator for arbitrary vendor metadata or hidden dependencies. Existing producer-estimated material/time metadata stays old reference data, as the amended contract explicitly states.

Publication freshly derives from re-read original source/project bytes, compares the entire immutable result and refuses stale/forged results. Both files are fsynced in a private sibling staging directory before a single Windows no-replace directory rename. Existing targets reject; filesystem aliases resolving to original inputs reject; cancellation before publication leaves no partial published pair. Publication is intentionally Windows-specific. Source/project identity changes and opaque prefix/suffix obligations remain explicit.

Finite byte/event/change/number/precision limits and cancellation are explicit; parsing/profile/trace/archive work remains bounded by input/archive limits before per-event cancellation checks. This review does not claim immediate asynchronous interruption inside stdlib ZIP or the existing body parser.

## Residual gates

No CURRENT compiler/manifest reassociation, complete derived-job contact/spill/material/tool chronology, standard preview or executable opaque-end audit is accepted by this report. Those require separate fresh pinned results. Original f917 stationary surplus remains an unknown original ledger; the new baseline cannot relabel it. Physical/runtime/print authority remains false.

## Post-blind input-fix verification

After the initial report, parent identified a Low identity-category defect: custom equality objects could masquerade as family/source/raw SHA strings. Implementation also identified unsupported positive vertical-only Z/E extrusion and a missing separate producer-byte limit. These are confirmed defects in the initial snapshot; the prior negative review did not establish them. The corrected owner SHA is `41b04c831fac64116216525a8bdb45bad2bb2f483a097adbfc1c245248033b5f`, tests `4acc994079f26dde000698cf28d4af6dae9260c926bbe600f194ea5b1dc6340f`.

Independent delta verification: all four family identity fields and every restore/negative raw hash require exact `str` plus lowercase64-hex before equality. The focused custom-equality regressions pass. Additional Python stdin probes reject uppercase, bytes and truncated hashes for each family field. Positive E with unchangedXY now enters the strict restore branch and rejects changedZ; independent `G1 Z3.1 E.1 F6000` probe rejects. Explicit `max_producer_bytes` rejects an oversized producer before archive processing; a patched archive entry point proves it is not reached. Actual106/48/source2aa/projectea5639 regression still passes. Disposition: confirmed, fixed and independently verified for all three bounded input corrections. No new material delta defect established.

Combined final command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_exact_debt_source_derivation tests.unit.test_current_conditional_job -v` — PASS,10 tests,160.069 seconds, including all8 corrected derivation tests. CURRENT schema/integration review is separately recorded in `current-conditional-job-blind-review-2026-10-18.md`; this does not merge compilation success with geometry or execution acceptance.
