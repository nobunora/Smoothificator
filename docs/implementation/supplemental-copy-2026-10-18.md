# Synthetic supplemental copy implementation

Contract: `docs/specs/supplemental-copy-review.md`; parent repository-review
disposition: validated for synthetic offline composition only. Quality-error
improvement remains deferred. No physical/runtime authority is granted.

## Changes and intent

- `tools/supplemental_copy.py`: frozen source-bound synthetic anchors and
  insertion requests; entire-source strict validation; immutable byte-copy
  result with source/output hashes and inserted output spans. Revalidates
  constructor-supplied anchors, checks chronological unique offsets and one
  explicit synthetic initial context, replays every composed cycle and the
  entire output, and verifies removing insertion spans reconstructs the source.
- `tests/unit/test_supplemental_copy.py`: mixed-newline/comment preservation,
  missing final newline, EOF/zero boundaries, multiple blocks, immutable false
  authority flags, hashes, malformed/unknown source after the anchor, forged
  state/hash, unsafe boundaries, repeated markers and failed cycle replay.

The preceding line selects inserted LF/CRLF; byte-zero insertion uses the first
line. No insertion splits CRLF or an unterminated final line. Original bytes
are concatenated directly, never decoded and rewritten. Existing strict parser
still rejects non-ASCII source, including comments. Bare-CR insertion boundaries
are unsupported. Caller initial states remain synthetic assertions.

Rejected alternatives: guessed real anchors; broad command ignoring; changes to
production parser/gates; output filesystem replacement; newline normalization.
No dependencies added. No production modules, runtime hooks, source files or
printer state changed. Existing dirty work and `log_iotc.txt` preserved.

## Executed checks

Required project interpreter:
`C:\VSC\Smoothificator\.venv\Scripts\python.exe --version`
-> Python 3.12.10, exit 0.

Required-environment rerun (2026-10-18):

1. `& 'C:\VSC\Smoothificator\.venv\Scripts\python.exe' -m py_compile tools/supplemental_copy.py tests/unit/test_supplemental_copy.py`
   -> PASS, exit 0.
2. `& 'C:\VSC\Smoothificator\.venv\Scripts\python.exe' -m unittest discover -s tests/architecture -q`
   -> PASS, 45 tests, exit 0.
3. `& 'C:\VSC\Smoothificator\.venv\Scripts\python.exe' -m unittest tests.unit.test_supplemental_copy tests.unit.test_supplemental_z_hop tests.unit.test_print_source_inspection -q`
   -> PASS, 42 tests, exit 0.

Prior extra-interpreter checks below used `python --version` -> Python 3.14.7.
These are supplementary only; they do not replace project Python 3.12 evidence.

1. `python -m py_compile tools/supplemental_copy.py tests/unit/test_supplemental_copy.py`
   -> PASS, exit 0.
2. `python -m unittest discover -s tests/architecture -q`
   -> PASS, 45 tests, exit 0.
3. `python -m unittest tests.unit.test_supplemental_copy tests.unit.test_supplemental_z_hop tests.unit.test_print_source_inspection -q`
   -> PASS, 42 tests, exit 0.

No configured doctor, lint or type-check command was established for this
bounded tools-only change; no tooling/dependencies installed. Full regression
is assigned to the parent after audit/corrections. No build/package or physical
test performed. No real-source execution certificate is produced.

## Review status and risks

Ready for parent source/test audit and independent review; not ready for physical
printing. This is an in-memory experiment, not the canonical bounded-memory
streaming injector or immutable PlanStore publication. Existing composer
precision policy, firmware/profile parity, actual anchors, support and
chronological downstream tool-body clearance remain uncertified. Removing this
tools-only module would remove copy composition without changing production
behavior. No commit, push, merge or release performed.
