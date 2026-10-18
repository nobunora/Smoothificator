# Supplemental copy independent blind review — 2026-10-18

## Scope and independence

Reviewed the current dirty working tree on `codex/true-z-review-handoff` in `C:\VSC\Smoothificator`. This report was completed without reading parent, implementation, research, or other audit conclusions. No source/test edits, printer access, output-file composition, commit, push, merge, release, or CodebaseMemory process was performed. Existing dirty files and `log_iotc.txt` were preserved.

Authoritative material: AGENTS.md, docs/DOCUMENT_CONTRACT.md, docs/REVIEW_PROCESS.md, docs/specs/supplemental-copy-review.md; canonical SPECIFICATION sections 24/24A–27, 29, 32; Accepted ADR-0031. Inspected source: tools/supplemental_copy.py, tools/supplemental_z_hop.py, orca_plugin/gcode/linear_trace.py, and tests/unit/test_supplemental_copy.py. Imported existing fixture functions from tests/unit/test_supplemental_z_hop.py during execution.

## Result

No actionable material defect found in the bounded, synthetic, offline bytes-copy contract. This is a negative review with the coverage and limitations below, not a declaration of production/physical convergence. All physical-print and runtime-injection authority remains false.

## Paths and invariants traced

- Anchor factory validates exact bytes and initial MachineState, rejects existing markers, traces the entire source before accepting any boundary, hashes the complete original source, and reconstructs saved state from interpreted preceding commands.
- Composition reconstructs every supplied anchor rather than trusting dataclass construction; stale hash, forged saved state, incompatible initial context, bool/interior/negative offsets, duplicate/reverse offsets, and mutable/empty request collections fail before any result exists.
- Complete-line boundaries include byte zero and LF-terminated ends, preserve complete CRLF pairs, and exclude an unterminated final-line end. Byte zero and EOF insertion for terminated sources were exercised.
- Frozen records contain exact immutable tuples/Fractions/bytes for accepted execution inputs. Composer validation rejects unknown modal or numeric state, unsupported modes, zero retraction debt, malformed paths, and unsafe height/feed/rounding conditions. Equality alone is not treated as the full input validator.
- Each composed cycle raises before XY, unretracts saved debt, extrudes, retracts, returns through the ceiling, restores XYZ/logical E/feed, and is independently parsed from saved state. Exact final MachineState identity is checked before assembly.
- Assembly copies original slices in chronological order, records disjoint output spans, verifies exact deletion-based reconstruction, computes full-source/output SHA256, and replays the complete output against the original final state.
- Original comments, mixed LF/CRLF, and missing-final-newline tails remain byte-identical. Inserted blocks use the preceding complete line's newline (first line at offset zero). Original source execution records retain their command, raw bytes, before/after state and deposition values in independent probes.
- Repeat insertion is intentionally rejected by marker detection, including partial/canonical marker prefixes. No successful return can write the original, publish a PlanStore, invoke a runtime hook, or contact a printer: these modules expose bytes and immutable records only.

## Validation executed

Interpreter: `.\.venv\Scripts\python.exe --version` → Python 3.12.10, exit 0.

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_supplemental_copy.py -q` → exit 1, `No module named pytest`. No dependency was installed or rule suppressed.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_supplemental_copy -v` → exit 0, all 9 tests pass. Coverage includes mixed newline/comment/tail reconstruction, multiple insertions, EOF/zero anchors, malformed offsets, full-source unknown-command/encoding rejection, forged anchors, ordering/context rejection, unsupported states, marker rejection and independently detected bad composer output.

Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -` probes → exit 0:

- Five synthetic sources: empty bytes, one terminated motion, mixed CRLF/LF motions/comments, unterminated motion tail, and comment-only CRLF. Inserted at every LF-complete boundary plus byte zero: 11 insertions in total.
- For each output: independently removed reported spans, checked exact source bytes and output hash, parsed output, excluded inserted records by output offset, and compared every original execution record's `(raw, command, before, after, extruded_filament_mm)` to source replay. All identical.
- Independently rejected unknown trailing M981, duplicate X words, G92 XYZ remap, malformed numeric token, and non-ASCII comment bytes anywhere after an otherwise valid prefix.

## Residual uncertainty and authority

The reader/composer share the same strict synthetic modal model. Replay proves agreement with that model, not firmware behavior or formatter equivalence. Caller initial state is synthetic evidence only; real source outside this grammar remains unsupported and must not receive invented anchors. Opaque non-ASCII comments currently reject conservatively, which is explicitly retained by this bounded handoff rather than weakening parsing.

Chronological tool-clearance, actual physical support/contact, Orca integration, printer profile/firmware, runtime atomic replacement, final PlanStore publication, and physical print enablement were not validated or authorized. The canonical production requirements remain necessary at those gates. This report did not independently run architecture, whole-suite, packaging, or release checks; those remain the parent's verification responsibility. No finding disposition is needed because no actionable finding was identified. Review against this exact working tree must be repeated if the inspected implementation or contract changes materially.
