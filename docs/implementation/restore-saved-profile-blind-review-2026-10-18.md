# Restore saved profile — independent blind review, 2026-10-18

## Independence and scope

Reviewed docs/specs/restore-saved-print-profile.md, tools/restore_saved_print_profile.py, tests/unit/test_restore_saved_print_profile.py and the actual restoration-receipt.json with pinned seed/model/executable/restored/sliced artifacts. Canonical material: DOCUMENT_CONTRACT; SPECIFICATION sections 18, 24A–27, 30, 32; Accepted ADR-0031; AGENTS and REVIEW_PROCESS already read in this independent session. Did not consult parent/research/implementation findings. No source/test edits, re-slicing, artifact overwrites, printer access, commits or subagents. Only this report was written.

## Finding BR-1 — JSON float conversion can silently change saved and unrelated setting values

- Severity: Medium.
- Location: tools/restore_saved_print_profile.py `_read_project` (`json.loads` without an exact decimal policy), `_json_bytes`, and restore_saved_profile settings reserialization.
- Affected behavior: Pure restoration accepts JSON decimal numbers and silently rounds or underflows them. This affects both transferred *_gcode values and unrelated model settings, despite claiming exact restoration and preservation.
- Evidence: A pinned in-memory project with `emit_machine_limits_to_gcode: 1e-400` and unrelated `untouched_number: 0.123456789012345678901` was passed as both model and seed. Successful output contained `emit_machine_limits_to_gcode: 0.0` and `untouched_number: 0.12345678901234568`. No rejection occurred. Because both input values are decoded before comparison/hashing, changed-key receipts also cannot expose this loss reliably.
- Violated requirement: Handoff “preserving exact original JSON values and types” and “Preserve every other setting.” Input pin validation proves identity of input bytes, not that subsequent decoding preserves numbers.
- Concrete failure scenario: A future accepted project contains a decimal JSON value outside binary64 precision or range; restoration emits a numerically different setting while reporting a successful restoration. Existing numeric testing covers an integer, not decimal underflow/precision.
- Remediation direction: Either explicitly reject decimal JSON numeric tokens in the bounded supported grammar before any transformation, or parse/serialize decimal values exactly while preserving JSON numeric kind and build receipts from that exact representation. Add precision/underflow cases for both restored and untouched keys. Do not silently normalize unsupported numeric inputs.
- Confidence: High; reproduced with Python 3.12.10. This does not invalidate the inspected actual artifact: its 776 top-level settings are strings/lists, and its independently verified transfer is exact.
- Proposed disposition: confirmed; adjudication belongs to the lead/specification owner.

## Actual artifact evidence

Read-only independent reconstruction and hash validation passed:

- All eight preserved-input before/after hashes agree with current files, including seed/model, original source/3MF, current-review.json, both view-only files and pinned executable.
- Restored-unsliced, separate source and sliced-project hashes match the receipt.
- Running the pure restoration on current pinned inputs in memory reproduces the stored restored-unsliced bytes exactly.
- All 17 saved *_gcode keys have exact original seed values/types; nine changed-key receipts and canonical old/new hashes agree with independent restoration.
- Every other settings value/type and every non-settings ZIP member is unchanged. Arc fitting remains the string `0`.
- The sliced 3MF embedded Metadata/plate_1.gcode equals separate plate_1.gcode exactly. Header matches the recorded 40 lines and identifies OrcaSlicer 2.5.0-dev. Inventory independently recomputes identically: 66 lexical opcodes, including manufacturer decimal opcodes.
- All three authority fields (`printable_authorized`, `physical_print_authorized`, `execution_verified`) are exactly false. Restored manufacturer's G2 and numerous unsupported commands remain inventory evidence only.

## Other paths checked

Both input pins are checked before archive transformation. Duplicate ZIP members and nested duplicate JSON keys reject; missing settings, malformed JSON/nonfinite constants, sliced archives and nonempty/ambiguous external postprocess settings reject on either input. Exact machine-program key sets are required. ZIP member content/order/metadata and archive comment are preserved by the restoration loop except settings serialization. Path validation handles resolved aliases and same-file hardlinks. Existing output folder rejects before writing; restored output is separate from original artifacts. The launch uses pinned executable, isolated datadir and explicit orient/arrange zero, no external shell or send/connect command. Return code, input preservation and embedded-source agreement gate completion. Timeout retains false-authority receipt and logs. Non-timeout I/O/launch errors can leave an incomplete false-authority research receipt/folder; no successful completion or physical authority is inferred from such failure.

## Executed checks

- `.\.venv\Scripts\python.exe --version`: Python 3.12.10, exit 0.
- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_restore_saved_print_profile -v`: exit 0, 9 tests pass.
- Read-only `@' ... '@ | .\.venv\Scripts\python.exe -` precision/underflow reproduction: exit 0, demonstrates BR-1.
- Read-only Python artifact verification: exit 0, independently checked every receipt hash and transfer/member/source/header/inventory invariant listed above. No slicing was repeated.

## Residuals and conclusion

One Medium finding requires disposition/fix or explicit narrowing of accepted numeric input grammar. No Critical/High defect found for this bounded offline operation, and the current restored artifact's association and preservation checks passed. No claim of full convergence: whole-suite/architecture gates were not independently repeated here. Pinned executable/hash and successful slicing do not prove firmware semantics, physical tool clearance, printer support, or safe printing. The current operation remains an unverified offline baseline; physical enablement and production mutation gates stay closed.

## Independent fix verification — 2026-10-18

Re-read only updated tools/restore_saved_print_profile.py and its unit tests; no parent/implementation conclusions consulted. Decimal parsing now prevents BR-1 numerical underflow/rounding, and recursive serialization preserves nested list/dict decimals. `.\.venv\Scripts\python.exe -m unittest tests.unit.test_restore_saved_print_profile -v` passed all 10 cases, exit 0. Additional read-only Python probes verified tiny/long decimals inside nested objects and arrays. Pure rerestoration from actual pinned inputs remains byte-identical to stored restored-unsliced.3mf, SHA256 `d9ed61e14793a06256ae947d713c3d14b82aea84057ceb02947468d055bdf31d`. No reslice or artifact write occurred.

BR-1 numeric-value-loss finding: fixed and independently verified for its demonstrated cases. One narrower residual type-preservation issue remains:

### BR-2 — zero-exponent numeric tokens lose decimal kind

- Severity: Low.
- Location: `_json_bytes`, Decimal branch, `return str(value).encode('ascii')`.
- Behavior/evidence: An accepted settings token `1e0` parses as Decimal but serializes as `1`; rereading with the same exact JSON policy produces int. Reproduced for both a transferred `emit_machine_limits_to_gcode` and an untouched nested list element. Exact numerical equality remains intact; this is a type/kind issue rather than the prior numerical corruption.
- Requirement: Exact saved values/types and untouched settings preservation. Existing new test explicitly asserts Decimal type for decimal tokens, but does not cover exponent-zero tokens.
- Failure scenario: A numeric consumer distinguishing decimal-form from integer-form JSON observes a kind change after restoration, although the numeric value is unchanged.
- Direction: Serialize Decimal values whose normal string contains neither decimal point nor exponent with an explicit decimal marker such as `.0`, and cover `1e0` in transferred/untouched nested settings. Alternatively, specification adjudication can explicitly define all JSON numbers as one type; do not imply preservation of the Python int/Decimal distinction while testing it selectively.
- Confidence: High; `.venv` Python 3.12.10 reproduction output reports Decimal → int.
- Proposed disposition: requires adjudication; no impact to current actual pinned string/list artifact or its verified hash.

No new Critical/High/Medium defect found during this fix check. Physical/runtime authority remains false and all prior scope limitations apply.

## Final independent BR-2 fix verification — 2026-10-18

Reviewed the current restore serializer and focused tests only, under the adjudicated requirement to preserve Decimal versus int category. Decimal integral strings now receive `.0` when needed; nonfinite rejection and recursive serialization remain intact. BR-2 disposition: **confirmed, fixed, independently verified**. BR-1 remains fixed. No new material defect identified.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_restore_saved_print_profile -v` → exit 0, all11 cases pass on exact repository Python3.12.10. Additional independent read-only probes covered `1e0`, `-0e0`, `-0.0`, `0e0`, `1.000`, `1e-400`, and a long decimal in both copied keys and untouched nested list/dict settings. Exact numeric value, Decimal category and signed-zero sign survived restoration. Existing integer-category focused test also passed.

Pure rerestoration from the actual pinned model/seed remains byte-identical to the existing artifact, SHA256 `d9ed61e14793a06256ae947d713c3d14b82aea84057ceb02947468d055bdf31d`. No slicing, artifact overwrite, source/test edit, or printer operation occurred. All earlier physical/runtime limitations remain; no execution or printing authority granted.
